import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """Application settings for LoRA Trainer service."""
    
    # Application
    app_name: str = "AvatarAI LoRA Trainer"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8188"))
    
    # Paths
    base_dir: Path = Path(__file__).parent
    data_dir: Path = Path(os.getenv("DATA_DIR", "/data"))
    models_dir: Path = Path(os.getenv("MODELS_DIR", "/app/models"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "/data/output"))
    input_dir: Path = Path(os.getenv("INPUT_DIR", "/data/input"))
    
    # LoRA Training
    base_model: str = os.getenv("BASE_MODEL", "runwayml/stable-diffusion-v1-5")
    lora_rank: int = int(os.getenv("LORA_RANK", "32"))
    lora_alpha: int = int(os.getenv("LORA_ALPHA", "16"))
    learning_rate: float = float(os.getenv("LEARNING_RATE", "1e-4"))
    num_train_epochs: int = int(os.getenv("NUM_TRAIN_EPOCHS", "10"))
    train_batch_size: int = int(os.getenv("TRAIN_BATCH_SIZE", "1"))
    gradient_accumulation_steps: int = int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "4"))
    mixed_precision: str = os.getenv("MIXED_PRECISION", "fp16")
    resolution: int = int(os.getenv("RESOLUTION", "512"))
    
    # Validation
    min_images: int = int(os.getenv("MIN_IMAGES", "10"))
    max_images: int = int(os.getenv("MAX_IMAGES", "50"))
    max_image_size_mb: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    supported_image_formats: List[str] = [".jpg", ".jpeg", ".png", ".bmp"]
    
    # ComfyUI Integration
    comfyui_host: str = os.getenv("COMFYUI_HOST", "localhost")
    comfyui_port: int = int(os.getenv("COMFYUI_PORT", "8188"))
    comfyui_workflow_path: Path = Path(os.getenv("COMFYUI_WORKFLOW_PATH", "/app/workflows/default.json"))
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    redis_task_queue: str = os.getenv("REDIS_TASK_QUEUE", "lora_training_tasks")
    
    # Task management
    max_training_time_minutes: int = int(os.getenv("MAX_TRAINING_TIME_MINUTES", "120"))
    task_timeout_seconds: int = int(os.getenv("TASK_TIMEOUT_SECONDS", "3600"))
    
    # GPU
    use_gpu: bool = os.getenv("USE_GPU", "True").lower() == "true"
    gpu_memory_limit_mb: Optional[int] = int(os.getenv("GPU_MEMORY_LIMIT_MB")) if os.getenv("GPU_MEMORY_LIMIT_MB") else None
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Path = Path(os.getenv("LOG_FILE", "/app/logs/lora_trainer.log"))
    
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
        settings.log_file.parent
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
ensure_directories()