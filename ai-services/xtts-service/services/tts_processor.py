import os
import uuid
import json
import hashlib
import pickle
import tempfile
import math
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
import numpy as np
import torch
import torchaudio
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import soundfile as sf
import librosa
import redis
from loguru import logger
import time

from config import settings

class TTSProcessor:
    """Text-to-Speech processor using Coqui XTTS v2 with voice cloning."""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"
        self.tts_model = None
        self.redis_client = None
        self.logger = logger
        
        # Initialize Redis client for caching
        self._init_redis()
        
        # Initialize TTS model
        self._init_tts_model()
    
    def _init_redis(self):
        """Initialize Redis client for voice embedding caching."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=False,  # Keep embeddings as bytes
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.logger.info(f"Redis connected successfully to {settings.redis_host}:{settings.redis_port}")
        except Exception as e:
            self.logger.warning(f"Failed to connect to Redis: {e}. Caching will be disabled.")
            self.redis_client = None
    
    def _init_tts_model(self):
        """Initialize XTTS v2 model with fallback support."""
        try:
            self.logger.info(f"Loading XTTS v2 model: {settings.xtts_model_name}")
            self.logger.info(f"Using device: {self.device}")
            
            # Try to load model with GPU if available
            try:
                self.tts_model = TTS(
                    model_name=settings.xtts_model_name,
                    progress_bar=False,
                    gpu=True if self.device == "cuda" else False
                )
                
                # Move model to appropriate device
                if hasattr(self.tts_model, 'model'):
                    self.tts_model.model.to(self.device)
                
                self.logger.info("XTTS v2 model loaded successfully")
                
            except Exception as gpu_error:
                self.logger.warning(f"GPU model loading failed: {gpu_error}")
                self.logger.info("Trying CPU mode...")
                
                # Fallback to CPU mode
                self.tts_model = TTS(
                    model_name=settings.xtts_model_name,
                    progress_bar=False,
                    gpu=False
                )
                
                self.logger.info("XTTS v2 model loaded in CPU mode")
            
            self.logger.info(f"Supported languages: {self.get_supported_languages()}")
            
        except Exception as e:
            self.logger.error(f"Failed to load XTTS v2 model: {e}")
            self.logger.warning("Running in simulation mode - no real TTS available")
            self.tts_model = None  # Set to None for simulation mode
            
    def is_model_loaded(self) -> bool:
        """Check if TTS model is loaded."""
        return self.tts_model is not None
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages with names."""
        return [
            {"code": lang_code, "name": settings.language_names.get(lang_code, lang_code)}
            for lang_code in settings.supported_languages
        ]
    
    def validate_voice_sample(self, audio_path: str) -> Tuple[bool, str]:
        """Validate voice sample for cloning."""
        try:
            # Check file exists
            if not os.path.exists(audio_path):
                return False, f"Audio file not found: {audio_path}"
            
            # Check file size
            file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
            if file_size_mb > settings.max_file_size_mb:
                return False, f"File too large: {file_size_mb:.1f}MB > {settings.max_file_size_mb}MB"
            
            # Load audio to check duration
            audio, sr = librosa.load(audio_path, sr=None, mono=True)
            duration = len(audio) / sr
            
            if duration < settings.min_voice_sample_duration:
                return False, f"Audio too short: {duration:.1f}s < {settings.min_voice_sample_duration}s"
            
            if duration > settings.max_voice_sample_duration:
                return False, f"Audio too long: {duration:.1f}s > {settings.max_voice_sample_duration}s"
            
            # Check audio quality (basic checks)
            if np.max(np.abs(audio)) < 0.01:
                return False, "Audio signal too weak"
            
            return True, "Voice sample is valid"
            
        except Exception as e:
            return False, f"Error validating voice sample: {str(e)}"
    
    def _get_voice_embedding_key(self, voice_sample_path: str) -> str:
        """Generate cache key for voice embedding."""
        # Create hash from file content for consistent caching
        file_hash = hashlib.md5()
        with open(voice_sample_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                file_hash.update(chunk)
        
        return f"{settings.redis_voice_cache_prefix}{file_hash.hexdigest()}"
    
    def get_voice_embedding(self, voice_sample_path: str, language: str = "en") -> Optional[bytes]:
        """
        Get voice embedding from sample, with Redis caching.
        
        Returns:
            Voice embedding bytes or None if failed
        """
        cache_key = None
        
        # Try to get from cache if Redis is available
        if self.redis_client is not None:
            cache_key = self._get_voice_embedding_key(voice_sample_path)
            cached_embedding = self.redis_client.get(cache_key)
            
            if cached_embedding is not None:
                self.logger.info(f"Voice embedding retrieved from cache: {cache_key}")
                return cached_embedding
        
        try:
            # Generate embedding using XTTS
            self.logger.info(f"Generating voice embedding from: {voice_sample_path}")
            
            # XTTS v2 requires specific format for voice cloning
            # Note: TTS API handles this internally
            if hasattr(self.tts_model, 'get_conditioning_latents'):
                # Newer API
                embedding = self.tts_model.get_conditioning_latents(
                    audio_path=voice_sample_path,
                    gpt_cond_len=6,
                    max_ref_length=10
                )
            else:
                # Fallback to model-specific method
                embedding = self.tts_model.synthesizer.tts_model.get_conditioning_latents(
                    voice_sample_path
                )
            
            # Convert to bytes for caching
            if isinstance(embedding, torch.Tensor):
                embedding_bytes = embedding.cpu().numpy().tobytes()
            elif isinstance(embedding, np.ndarray):
                embedding_bytes = embedding.tobytes()
            else:
                # Try to serialize
                embedding_bytes = pickle.dumps(embedding)
            
            # Cache in Redis if available
            if self.redis_client is not None and cache_key is not None:
                self.redis_client.setex(
                    cache_key,
                    settings.voice_embedding_cache_ttl,
                    embedding_bytes
                )
                self.logger.info(f"Voice embedding cached: {cache_key}")
            
            return embedding_bytes
            
        except Exception as e:
            self.logger.error(f"Failed to generate voice embedding: {e}")
            return None
    
    def synthesize_speech(
        self,
        text: str,
        voice_sample_path: str,
        language: str = "en",
        speed: float = None,
        temperature: float = None,
        **kwargs
    ) -> Optional[str]:
        """
        Synthesize speech from text using voice sample.
        
        Returns:
            Path to generated audio file or None if failed
        """
        try:
            # Validate language
            if language not in settings.supported_languages:
                self.logger.warning(f"Language {language} not in supported list, using English")
                language = "en"
            
            # Set synthesis parameters
            speed = speed or settings.default_speed
            temperature = temperature or settings.default_temperature
            
            self.logger.info(f"Synthesizing speech: '{text[:50]}...' in {language}")
            
            # Create temporary output file
            output_filename = f"tts_{uuid.uuid4()}.{settings.output_format}"
            output_path = Path(settings.output_dir) / output_filename
            
            # Ensure output directory exists
            os.makedirs(settings.output_dir, exist_ok=True)
            
            # Synthesize speech using XTTS v2 with voice cloning
            # The TTS API handles voice cloning internally when speaker_wav is provided
            wav = self.tts_model.tts(
                text=text,
                speaker_wav=voice_sample_path,  # Path to voice sample for cloning
                language=language,
                speed=speed,
                temperature=temperature,
                **kwargs
            )
            
            # Save audio
            sf.write(output_path, wav, settings.output_sample_rate)
            
            self.logger.info(f"Speech synthesized successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to synthesize speech: {e}")
            return None
    
    def clone_and_synthesize(
        self,
        voice_sample_path: str,
        text: str,
        language: str = "en",
        speed: float = None,
        temperature: float = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Complete pipeline: clone voice from sample and synthesize speech.
        
        Returns:
            Dictionary with results and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate voice sample
            is_valid, message = self.validate_voice_sample(voice_sample_path)
            if not is_valid:
                return {
                    "success": False,
                    "error": message,
                    "audio_path": None,
                    "processing_time": 0
                }
            
            # Step 2: Get or generate voice embedding (for caching)
            voice_embedding = None
            if use_cache and self.redis_client is not None:
                voice_embedding = self.get_voice_embedding(voice_sample_path, language)
                if voice_embedding is not None:
                    self.logger.info("Using cached voice embedding")
            
            # Step 3: Synthesize speech directly using voice sample
            audio_path = self.synthesize_speech(
                text=text,
                voice_sample_path=voice_sample_path,
                language=language,
                speed=speed,
                temperature=temperature
            )
            
            if audio_path is None:
                return {
                    "success": False,
                    "error": "Failed to synthesize speech",
                    "audio_path": None,
                    "processing_time": 0
                }
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Get audio info
            audio_info = self._get_audio_info(audio_path)
            
            return {
                "success": True,
                "audio_path": audio_path,
                "processing_time": processing_time,
                "audio_info": audio_info,
                "language": language,
                "text_length": len(text),
                "cached": use_cache and voice_embedding is not None
            }
            
        except Exception as e:
            self.logger.error(f"Error in clone_and_synthesize: {e}")
            return {
                "success": False,
                "error": str(e),
                "audio_path": None,
                "processing_time": 0
            }
    
    def _get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get information about generated audio file."""
        try:
            audio, sr = librosa.load(audio_path, sr=None, mono=True)
            duration = len(audio) / sr
            
            return {
                "duration_seconds": duration,
                "sample_rate": sr,
                "channels": 1,
                "format": Path(audio_path).suffix[1:],
                "file_size_bytes": os.path.getsize(audio_path),
                "peak_level_db": 20 * np.log10(np.max(np.abs(audio))) if np.max(np.abs(audio)) > 0 else -120
            }
        except Exception as e:
            self.logger.warning(f"Failed to get audio info: {e}")
            return {}
    
    def clear_voice_cache(self, voice_sample_path: str = None) -> bool:
        """Clear voice embedding cache."""
        if self.redis_client is None:
            return False
        
        try:
            if voice_sample_path:
                # Clear specific voice embedding
                cache_key = self._get_voice_embedding_key(voice_sample_path)
                deleted = self.redis_client.delete(cache_key)
                return deleted > 0
            else:
                # Clear all voice embeddings
                keys = self.redis_client.keys(f"{settings.redis_voice_cache_prefix}*")
                if keys:
                    self.redis_client.delete(*keys)
                return True
        except Exception as e:
            self.logger.error(f"Failed to clear voice cache: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of TTS processor."""
        health_status = {
            "model_loaded": self.tts_model is not None,
            "redis_connected": self.redis_client is not None and self.redis_client.ping(),
            "device": self.device,
            "supported_languages": len(self.get_supported_languages()),
            "cuda_available": torch.cuda.is_available(),
            "model_working": False,
            "model_error": None
        }
        
        # Test model with simple operation if loaded
        if self.tts_model is not None:
            try:
                # Quick test: try to get model info
                model_info = {
                    "model_name": settings.xtts_model_name,
                    "device": self.device,
                    "languages": len(settings.supported_languages)
                }
                
                # Try a simple synthesis test if possible
                test_file = None
                try:
                    # Create a temporary test file
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                        test_file = f.name
                        # Create a simple sine wave for testing
                        import wave
                        import struct
                        sample_rate = 24000
                        duration = 0.1
                        frequency = 440
                        with wave.open(test_file, 'w') as wav_file:
                            wav_file.setnchannels(1)
                            wav_file.setsampwidth(2)
                            wav_file.setframerate(sample_rate)
                            for i in range(int(sample_rate * duration)):
                                value = int(32767.0 * 0.5 * 
                                         math.sin(2 * math.pi * frequency * i / sample_rate))
                                data = struct.pack('<h', value)
                                wav_file.writeframes(data)
                    
                    # Try to get embedding (this tests model loading)
                    embedding = self.get_voice_embedding(test_file, "en")
                    health_status["model_working"] = embedding is not None
                    
                except Exception as e:
                    health_status["model_working"] = False
                    health_status["model_error"] = str(e)
                
                finally:
                    # Clean up test file
                    if test_file and os.path.exists(test_file):
                        os.unlink(test_file)
                        
            except Exception as e:
                health_status["model_working"] = False
                health_status["model_error"] = str(e)
        
        return health_status
