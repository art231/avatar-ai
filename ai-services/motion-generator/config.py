import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any

class Settings(BaseSettings):
    """Application settings for Motion Generator service."""
    
    # Application
    app_name: str = "AvatarAI Motion Generator"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "5002"))
    
    # Paths
    base_dir: Path = Path(__file__).parent
    data_dir: Path = Path(os.getenv("DATA_DIR", "/data"))
    models_dir: Path = Path(os.getenv("MODELS_DIR", "/app/models"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "/data/output"))
    input_dir: Path = Path(os.getenv("INPUT_DIR", "/data/input"))
    
    # Motion Generation Models
    motion_model: str = os.getenv("MOTION_MODEL", "unimotion")
    pose_estimation_model: str = os.getenv("POSE_ESTIMATION_MODEL", "dwpose")
    smpl_model_path: Path = Path(os.getenv("SMPL_MODEL_PATH", "/app/models/smpl"))
    
    # Motion Generation Parameters
    default_duration_sec: int = int(os.getenv("DEFAULT_DURATION_SEC", "10"))
    fps: int = int(os.getenv("FPS", "24"))
    resolution_width: int = int(os.getenv("RESOLUTION_WIDTH", "512"))
    resolution_height: int = int(os.getenv("RESOLUTION_HEIGHT", "512"))
    
    # Pose Estimation
    pose_detection_threshold: float = float(os.getenv("POSE_DETECTION_THRESHOLD", "0.5"))
    max_pose_points: int = int(os.getenv("MAX_POSE_POINTS", "17"))
    
    # Motion Smoothing
    smoothing_window: int = int(os.getenv("SMOOTHING_WINDOW", "5"))
    interpolation_method: str = os.getenv("INTERPOLATION_METHOD", "cubic")
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    redis_task_queue: str = os.getenv("REDIS_TASK_QUEUE", "motion_generation_tasks")
    
    # Task management
    max_generation_time_minutes: int = int(os.getenv("MAX_GENERATION_TIME_MINUTES", "30"))
    task_timeout_seconds: int = int(os.getenv("TASK_TIMEOUT_SECONDS", "1800"))
    
    # GPU
    use_gpu: bool = os.getenv("USE_GPU", "True").lower() == "true"
    gpu_memory_limit_mb: Optional[int] = int(os.getenv("GPU_MEMORY_LIMIT_MB")) if os.getenv("GPU_MEMORY_LIMIT_MB") else None
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Path = Path(os.getenv("LOG_FILE", "/app/logs/motion_generator.log"))
    
    # Supported input formats
    supported_video_formats: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    supported_image_formats: List[str] = [".jpg", ".jpeg", ".png", ".bmp"]
    
    # Output formats
    output_video_format: str = os.getenv("OUTPUT_VIDEO_FORMAT", "mp4")
    output_pose_format: str = os.getenv("OUTPUT_POSE_FORMAT", "json")
    
    # Default motion presets
    default_motion_presets: Dict[str, Dict[str, Any]] = {
        "idle_talking": {
            "description": "Natural idle motion while talking",
            "head_movement": "subtle",
            "body_movement": "minimal",
            "hand_gestures": "occasional",
            "intensity": 0.3
        },
        "presentation": {
            "description": "Presentation-style gestures",
            "head_movement": "moderate",
            "body_movement": "moderate",
            "hand_gestures": "frequent",
            "intensity": 0.6
        },
        "conversation": {
            "description": "Natural conversation motion",
            "head_movement": "moderate",
            "body_movement": "light",
            "hand_gestures": "moderate",
            "intensity": 0.5
        },
        "enthusiastic": {
            "description": "Enthusiastic speaking motion",
            "head_movement": "high",
            "body_movement": "moderate",
            "hand_gestures": "frequent",
            "intensity": 0.8
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create singleton instance
settings = Settings()

# Ensure directories exist
def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        settings.data_dir,
        settings.models_dir,
        settings.output_dir,
        settings.input_dir,
        settings.log_file.parent,
        settings.smpl_model_path
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
ensure_directories()