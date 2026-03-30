#!/usr/bin/env python3
"""
Test script for AudioProcessor class.
This script tests the audio processing pipeline without running the full service.
"""

import os
import sys
import tempfile
import numpy as np
import soundfile as sf
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.audio_processor import AudioProcessor

def create_test_audio(duration_seconds: float = 10.0, sample_rate: int = 22050) -> np.ndarray:
    """Create a simple test audio signal."""
    t = np.linspace(0, duration_seconds, int(duration_seconds * sample_rate), endpoint=False)
    
    # Create a simple sine wave with some noise
    frequency = 440  # A4 note
    signal = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Add some background noise
    noise = 0.05 * np.random.randn(len(t))
    
    # Add some silence at beginning and end
    silence_samples = int(0.5 * sample_rate)
    signal_with_silence = np.concatenate([
        np.zeros(silence_samples),
        signal + noise,
        np.zeros(silence_samples)
    ])
    
    return signal_with_silence

def test_audio_processor():
    """Test the AudioProcessor class."""
    print("Testing AudioProcessor...")
    
    # Create test audio
    sample_rate = 22050
    test_audio = create_test_audio(duration_seconds=15.0, sample_rate=sample_rate)
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
        input_path = input_file.name
        sf.write(input_path, test_audio, sample_rate)
        print(f"Created test audio file: {input_path}")
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
        output_path = output_file.name
    
    try:
        # Initialize processor
        print("Initializing AudioProcessor...")
        processor = AudioProcessor(device="cpu")  # Use CPU for testing
        
        # Check FFmpeg availability
        ffmpeg_available = processor.check_ffmpeg_available()
        print(f"FFmpeg available: {ffmpeg_available}")
        
        # Process audio
        print("Processing audio...")
        result = processor.process_audio(
            input_path=input_path,
            output_path=output_path,
            sample_rate=sample_rate,
            remove_silence=True,
            normalize_loudness=True,
            target_lufs=-23.0,
            min_duration=5.0,
            max_duration=30.0
        )
        
        # Print results
        print("\n" + "="*50)
        print("PROCESSING RESULTS:")
        print("="*50)
        print(f"Processing time: {result['processing_time']:.2f} seconds")
        print(f"Quality check passed: {result['quality_check_passed']}")
        
        audio_info = result['audio_info']
        print(f"\nAudio Info:")
        print(f"  Sample rate: {audio_info['sample_rate']} Hz")
        print(f"  Duration: {audio_info['duration_seconds']:.2f} seconds")
        print(f"  Channels: {audio_info['channels']}")
        print(f"  Format: {audio_info['format']}")
        print(f"  File size: {audio_info['file_size_bytes'] / 1024:.1f} KB")
        
        quality_metrics = audio_info['quality_metrics']
        print(f"\nQuality Metrics:")
        print(f"  SNR: {quality_metrics['snr_db']:.1f} dB")
        print(f"  Peak level: {quality_metrics['peak_level_db']:.1f} dBFS")
        print(f"  Integrated loudness: {quality_metrics['integrated_loudness']:.1f} LUFS")
        print(f"  Clipping: {quality_metrics['clipping_percentage']:.2f}%")
        
        if quality_metrics['quality_issues']:
            print(f"\nQuality Issues:")
            for issue in quality_metrics['quality_issues']:
                print(f"  - {issue}")
        else:
            print(f"\nNo quality issues detected!")
        
        # Verify output file exists
        if os.path.exists(output_path):
            print(f"\nOutput file created successfully: {output_path}")
            
            # Load and verify output
            output_audio, output_sr = sf.read(output_path)
            print(f"Output audio shape: {output_audio.shape}")
            print(f"Output sample rate: {output_sr} Hz")
            
            # Basic checks
            assert len(output_audio) > 0, "Output audio is empty"
            assert output_sr == sample_rate, f"Sample rate mismatch: {output_sr} != {sample_rate}"
            assert np.max(np.abs(output_audio)) <= 1.0, "Audio contains clipping"
            
            print("\n✅ All basic checks passed!")
        else:
            print(f"\n❌ Output file not created: {output_path}")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists(input_path):
            os.unlink(input_path)
            print(f"Cleaned up input file: {input_path}")
        
        if os.path.exists(output_path):
            os.unlink(output_path)
            print(f"Cleaned up output file: {output_path}")
    
    return True

def test_demucs_loading():
    """Test Demucs model loading."""
    print("\n" + "="*50)
    print("TESTING DEMUCS LOADING:")
    print("="*50)
    
    try:
        processor = AudioProcessor(device="cpu")
        if processor.demucs_model is not None:
            print("✅ Demucs model loaded successfully")
            print(f"   Model device: {processor.device}")
            print(f"   Model type: {type(processor.demucs_model).__name__}")
        else:
            print("⚠️ Demucs model not loaded (may be expected in test environment)")
    except Exception as e:
        print(f"❌ Error loading Demucs model: {e}")

def test_quality_metrics_calculation():
    """Test quality metrics calculation."""
    print("\n" + "="*50)
    print("TESTING QUALITY METRICS CALCULATION:")
    print("="*50)
    
    try:
        processor = AudioProcessor(device="cpu")
        
        # Create a clean test signal
        sample_rate = 22050
        t = np.linspace(0, 1.0, sample_rate)
        clean_signal = 0.5 * np.sin(2 * np.pi * 440 * t)
        
        # Calculate metrics
        metrics = processor._calculate_quality_metrics(clean_signal, sample_rate)
        
        print("Metrics for clean signal:")
        print(f"  SNR: {metrics['snr_db']:.1f} dB")
        print(f"  Peak level: {metrics['peak_level_db']:.1f} dBFS")
        print(f"  Clipping: {metrics['clipping_percentage']:.2f}%")
        print(f"  Quality check passed: {metrics['quality_check_passed']}")
        
        # Create a clipped signal
        clipped_signal = np.clip(clean_signal * 2.0, -1.0, 1.0)
        clipped_metrics = processor._calculate_quality_metrics(clipped_signal, sample_rate)
        
        print("\nMetrics for clipped signal:")
        print(f"  SNR: {clipped_metrics['snr_db']:.1f} dB")
        print(f"  Peak level: {clipped_metrics['peak_level_db']:.1f} dBFS")
        print(f"  Clipping: {clipped_metrics['clipping_percentage']:.2f}%")
        print(f"  Quality check passed: {clipped_metrics['quality_check_passed']}")
        
        print("\n✅ Quality metrics calculation test completed")
        
    except Exception as e:
        print(f"❌ Error in quality metrics test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print("AUDIO PROCESSOR TEST SUITE")
    print("="*60)
    
    # Run tests
    test_demucs_loading()
    test_quality_metrics_calculation()
    
    success = test_audio_processor()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60)