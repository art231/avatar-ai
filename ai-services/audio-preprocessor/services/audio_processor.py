import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
import torch
import torchaudio
from demucs import pretrained
from demucs.apply import apply_model
from demucs.audio import AudioFile, convert_audio
import logging
from loguru import logger

class AudioProcessor:
    """Audio processor for cleaning, normalizing, and quality checking audio samples."""
    
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.demucs_model = None
        self.logger = logger
        
        # Initialize Demucs model for vocal separation
        try:
            self.demucs_model = pretrained.get_model('htdemucs')
            self.demucs_model.to(self.device)
            self.logger.info(f"Demucs model loaded successfully on {self.device}")
        except Exception as e:
            self.logger.warning(f"Failed to load Demucs model: {e}. Will use basic processing.")
    
    def process_audio(
        self,
        input_path: str,
        output_path: str,
        sample_rate: int = 22050,
        remove_silence: bool = True,
        normalize_loudness: bool = True,
        target_lufs: float = -23.0,
        min_duration: float = 5.0,
        max_duration: float = 30.0
    ) -> Dict:
        """
        Process audio file with full pipeline:
        1. Load and validate audio
        2. Separate vocals from noise (Demucs)
        3. Remove silence
        4. Normalize loudness
        5. Check quality metrics
        6. Export to target format
        
        Returns:
            Dict with processing results and audio info
        """
        processing_start = librosa.get_clock()
        
        try:
            # Step 1: Load and validate input audio
            self.logger.info(f"Loading audio from {input_path}")
            audio, orig_sr = self._load_audio(input_path)
            
            # Step 2: Resample if needed
            if orig_sr != sample_rate:
                audio = librosa.resample(audio, orig_sr=orig_sr, target_sr=sample_rate)
                self.logger.info(f"Resampled from {orig_sr}Hz to {sample_rate}Hz")
            
            # Step 3: Validate duration
            duration = len(audio) / sample_rate
            if duration < min_duration:
                raise ValueError(f"Audio too short: {duration:.1f}s < {min_duration}s minimum")
            if duration > max_duration:
                raise ValueError(f"Audio too long: {duration:.1f}s > {max_duration}s maximum")
            
            # Step 4: Separate vocals from noise using Demucs
            if self.demucs_model is not None:
                self.logger.info("Separating vocals from noise using Demucs...")
                vocals = self._separate_vocals(audio, sample_rate)
            else:
                self.logger.warning("Demucs not available, using original audio")
                vocals = audio
            
            # Step 5: Remove silence if requested
            if remove_silence:
                self.logger.info("Removing silence...")
                vocals = self._remove_silence(vocals, sample_rate)
            
            # Step 6: Normalize loudness if requested
            if normalize_loudness:
                self.logger.info(f"Normalizing loudness to {target_lufs} LUFS...")
                vocals = self._normalize_loudness(vocals, sample_rate, target_lufs)
            
            # Step 7: Trim to valid duration again after processing
            vocals = self._trim_to_valid_duration(vocals, sample_rate, min_duration, max_duration)
            
            # Step 8: Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(vocals, sample_rate)
            
            # Step 9: Export to WAV format
            self.logger.info(f"Exporting to {output_path}")
            sf.write(output_path, vocals, sample_rate, subtype='PCM_16')
            
            # Step 10: Get final audio info
            final_duration = len(vocals) / sample_rate
            processing_time = librosa.get_clock() - processing_start
            
            audio_info = {
                "sample_rate": sample_rate,
                "duration_seconds": final_duration,
                "channels": 1,
                "format": "WAV",
                "bit_depth": 16,
                "quality_metrics": quality_metrics,
                "file_size_bytes": os.path.getsize(output_path)
            }
            
            self.logger.info(f"Audio processing completed in {processing_time:.2f}s")
            self.logger.info(f"Quality metrics: SNR={quality_metrics['snr_db']:.1f}dB, "
                           f"Peak={quality_metrics['peak_level_db']:.1f}dBFS, "
                           f"LUFS={quality_metrics['integrated_loudness']:.1f}LUFS")
            
            return {
                "processing_time": processing_time,
                "audio_info": audio_info,
                "quality_check_passed": quality_metrics["quality_check_passed"]
            }
            
        except Exception as e:
            self.logger.error(f"Audio processing failed: {e}")
            raise
    
    def _load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file using librosa."""
        try:
            audio, sr = librosa.load(file_path, sr=None, mono=True)
            return audio, sr
        except Exception as e:
            raise ValueError(f"Failed to load audio file {file_path}: {e}")
    
    def _separate_vocals(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Separate vocals from background noise using Demucs."""
        try:
            # Convert to tensor for Demucs
            audio_tensor = torch.from_numpy(audio).float().unsqueeze(0).unsqueeze(0)
            audio_tensor = audio_tensor.to(self.device)
            
            # Apply Demucs model
            with torch.no_grad():
                sources = apply_model(
                    self.demucs_model,
                    audio_tensor,
                    device=self.device,
                    shifts=1,
                    split=True,
                    overlap=0.25,
                    progress=False
                )
            
            # Demucs returns: [batch, sources, channels, time]
            # Sources order: ['drums', 'bass', 'other', 'vocals']
            vocals = sources[0, 3, 0].cpu().numpy()
            
            # Normalize vocals
            if np.max(np.abs(vocals)) > 0:
                vocals = vocals / np.max(np.abs(vocals)) * 0.9
            
            return vocals
            
        except Exception as e:
            self.logger.warning(f"Vocal separation failed: {e}. Using original audio.")
            return audio
    
    def _remove_silence(self, audio: np.ndarray, sample_rate: int, threshold_db: float = -40.0) -> np.ndarray:
        """Remove silence from beginning and end of audio."""
        # Convert to dB
        audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
        
        # Find non-silent regions
        non_silent = audio_db > threshold_db
        
        if not np.any(non_silent):
            return audio
        
        # Find first and last non-silent samples
        indices = np.where(non_silent)[0]
        start_idx = indices[0] if len(indices) > 0 else 0
        end_idx = indices[-1] if len(indices) > 0 else len(audio)
        
        # Add small padding (100ms)
        padding = int(0.1 * sample_rate)
        start_idx = max(0, start_idx - padding)
        end_idx = min(len(audio), end_idx + padding)
        
        return audio[start_idx:end_idx]
    
    def _normalize_loudness(self, audio: np.ndarray, sample_rate: int, target_lufs: float = -23.0) -> np.ndarray:
        """Normalize audio loudness using FFmpeg's loudnorm filter."""
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
                input_path = input_file.name
                sf.write(input_path, audio, sample_rate)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                output_path = output_file.name
            
            # Use FFmpeg for loudness normalization (EBU R128)
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-af', f'loudnorm=I={target_lufs}:TP=-1.5:LRA=11:print_format=json',
                '-ar', str(sample_rate),
                '-ac', '1',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.logger.warning(f"FFmpeg loudnorm failed: {result.stderr}. Using simple normalization.")
                # Fallback to simple peak normalization
                return self._simple_normalize(audio, target_db=-1.0)
            
            # Load normalized audio
            normalized_audio, _ = librosa.load(output_path, sr=sample_rate, mono=True)
            
            # Cleanup temp files
            os.unlink(input_path)
            os.unlink(output_path)
            
            return normalized_audio
            
        except Exception as e:
            self.logger.warning(f"Loudness normalization failed: {e}. Using simple normalization.")
            # Fallback to simple peak normalization
            return self._simple_normalize(audio, target_db=-1.0)
    
    def _simple_normalize(self, audio: np.ndarray, target_db: float = -1.0) -> np.ndarray:
        """Simple peak normalization as fallback."""
        peak = np.max(np.abs(audio))
        if peak > 0:
            target_linear = 10 ** (target_db / 20)
            gain = target_linear / peak
            return audio * gain
        return audio
    
    def _trim_to_valid_duration(
        self, 
        audio: np.ndarray, 
        sample_rate: int,
        min_duration: float,
        max_duration: float
    ) -> np.ndarray:
        """Trim audio to valid duration range."""
        duration = len(audio) / sample_rate
        
        if duration <= max_duration:
            return audio
        
        # If too long, take the middle portion
        target_samples = int(max_duration * sample_rate)
        start = (len(audio) - target_samples) // 2
        return audio[start:start + target_samples]
    
    def _calculate_quality_metrics(self, audio: np.ndarray, sample_rate: int) -> Dict:
        """Calculate audio quality metrics."""
        metrics = {}
        
        # Calculate SNR (Signal-to-Noise Ratio)
        try:
            # Estimate noise floor using median filter
            noise_estimate = signal.medfilt(np.abs(audio), kernel_size=201)
            signal_power = np.mean(audio ** 2)
            noise_power = np.mean(noise_estimate ** 2)
            
            if noise_power > 0:
                snr_db = 10 * np.log10(signal_power / noise_power)
            else:
                snr_db = 60.0  # Very clean signal
        except:
            snr_db = 0.0
        
        metrics["snr_db"] = snr_db
        
        # Calculate peak level
        peak_linear = np.max(np.abs(audio))
        peak_db = 20 * np.log10(peak_linear) if peak_linear > 0 else -120.0
        metrics["peak_level_db"] = peak_db
        
        # Calculate integrated loudness (simplified)
        # Using RMS as approximation for LUFS
        rms = np.sqrt(np.mean(audio ** 2))
        integrated_loudness = 20 * np.log10(rms) if rms > 0 else -120.0
        metrics["integrated_loudness"] = integrated_loudness
        
        # Check for clipping
        clipping_samples = np.sum(np.abs(audio) > 0.999)
        clipping_percentage = (clipping_samples / len(audio)) * 100
        metrics["clipping_percentage"] = clipping_percentage
        
        # Quality checks
        metrics["quality_check_passed"] = (
            snr_db >= 20.0 and          # SNR ≥ 20 dB
            peak_db <= -1.0 and         # No clipping (peak ≤ -1 dBFS)
            duration >= 5.0 and         # Minimum 5 seconds
            duration <= 30.0 and        # Maximum 30 seconds
            clipping_percentage < 0.1   # Less than 0.1% clipping
        )
        
        metrics["quality_issues"] = []
        if snr_db < 20.0:
            metrics["quality_issues"].append(f"Low SNR: {snr_db:.1f}dB < 20dB")
        if peak_db > -1.0:
            metrics["quality_issues"].append(f"Clipping detected: peak {peak_db:.1f}dBFS > -1dBFS")
        if clipping_percentage >= 0.1:
            metrics["quality_issues"].append(f"Excessive clipping: {clipping_percentage:.2f}%")
        
        return metrics
    
    def check_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available in the system."""
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False