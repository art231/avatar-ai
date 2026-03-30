#!/usr/bin/env python3
"""
Simple test to verify basic functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing basic imports...")

try:
    import numpy as np
    print("✅ numpy imported successfully")
except ImportError as e:
    print(f"❌ numpy import failed: {e}")

try:
    import librosa
    print("✅ librosa imported successfully")
except ImportError as e:
    print(f"❌ librosa import failed: {e}")

try:
    import soundfile as sf
    print("✅ soundfile imported successfully")
except ImportError as e:
    print(f"❌ soundfile import failed: {e}")

try:
    import torch
    print("✅ torch imported successfully")
    print(f"   Torch version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ torch import failed: {e}")

try:
    from scipy import signal
    print("✅ scipy.signal imported successfully")
except ImportError as e:
    print(f"❌ scipy import failed: {e}")

print("\nTesting AudioProcessor imports...")
try:
    from services.audio_processor import AudioProcessor
    print("✅ AudioProcessor imported successfully")
    
    # Try to create instance
    processor = AudioProcessor(device="cpu")
    print("✅ AudioProcessor instance created")
    
    # Check FFmpeg
    ffmpeg_available = processor.check_ffmpeg_available()
    print(f"✅ FFmpeg check: {'available' if ffmpeg_available else 'not available'}")
    
except ImportError as e:
    print(f"❌ AudioProcessor import failed: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error creating AudioProcessor: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Basic import test completed!")