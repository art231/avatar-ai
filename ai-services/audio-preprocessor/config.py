from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # Service configuration
    app_name: str = "AvatarAI Audio Preprocessor"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Audio processing settings
    default_sample_rate: int = 22050
    default_target_lufs: float = -23.0
    min_audio_duration: float = 5.0  # seconds
    max_audio_duration: float = 30.0  # seconds
    
    # File storage
    input_dir: str = "/data/input"
    output_dir: str = "/data/output"
    max_file_size_mb: int = 100
    
    # Quality thresholds
    min_snr_db: float = 20.0
    max_peak_db: float = -1.0
    max_clipping_percentage: float = 0.1
    
    # Model settings
    demucs_model_name: str = "htdemucs"
    use_gpu: bool = True
    
    # FFmpeg settings
    ffmpeg_path: str = "ffmpeg"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()