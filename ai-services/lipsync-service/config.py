import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "AvatarAI Lip Sync Service"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "5006"))
    
    # Paths
    data_dir: Path = Path(os.getenv("DATA_DIR", "/data"))
    models_dir: Path = Path(os.getenv("MODELS_DIR", "/app/models"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "/data/output/lipsync"))
    input_dir: Path = Path(os.getenv("INPUT_DIR", "/data/input/lipsync"))
    logs_dir: Path = Path(os.getenv("LOGS_DIR", "/app/logs"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Path = logs_dir / "lipsync_service.log"
    
    # File formats
    supported_video_formats: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    supported_audio_formats: List[str] = [".wav", ".mp3", ".aac", ".flac", ".ogg"]
    
    # Limits
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    
    # Models
    default_model: str = os.getenv("DEFAULT_MODEL", "muse_talk")
    available_models: List[str] = ["muse_talk", "wav2lip"]
    
    # Processing
    default_quality: str = "high"
    default_sync_accuracy: float = 0.9
    
    # GPU/CPU
    device: str = os.getenv("DEVICE", "cuda" if os.getenv("CUDA_VISIBLE_DEVICES") else "cpu")
    
    # MuseTalk specific
    muse_talk_model_path: Path = models_dir / "muse_talk"
    muse_talk_checkpoint: str = os.getenv("MUSE_TALK_CHECKPOINT", "muse_talk.pth")
    muse_talk_config: str = os.getenv("MUSE_TALK_CONFIG", "musetalk.json")
    
    # Wav2Lip specific
    wav2lip_model_path: Path = models_dir / "wav2lip"
    wav2lip_checkpoint: str = os.getenv("WAV2LIP_CHECKPOINT", "wav2lip.pth")
    
    # Additional models for enhanced processing
    dwpose_model_path: Path = models_dir / "dwpose"
    dwpose_checkpoint: str = os.getenv("DWPOSE_CHECKPOINT", "dw-ll_ucoco_384.pth")
    
    face_parse_model_path: Path = models_dir / "face-parse-bisent"
    face_parse_checkpoint: str = os.getenv("FACE_PARSE_CHECKPOINT", "79999_iter.pth")
    face_parse_backbone: str = os.getenv("FACE_PARSE_BACKBONE", "resnet18-5c106cde.pth")
    
    whisper_model_path: Path = models_dir / "whisper"
    whisper_checkpoint: str = os.getenv("WHISPER_CHECKPOINT", "tiny.pt")
    
    # Enhanced processing flags
    use_dwpose: bool = os.getenv("USE_DWPOSE", "true").lower() == "true"
    use_face_parse: bool = os.getenv("USE_FACE_PARSE", "true").lower() == "true"
    use_whisper: bool = os.getenv("USE_WHISPER", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()