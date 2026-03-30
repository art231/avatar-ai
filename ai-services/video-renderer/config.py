import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any

class Settings(BaseSettings):
    """Application settings for Video Renderer service."""
    
    # Application
    app_name: str = "AvatarAI Video Renderer"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "5007"))
    
    # Paths
    base_dir: Path = Path(__file__).parent
    data_dir: Path = Path(os.getenv("DATA_DIR", "/data"))
    models_dir: Path = Path(os.getenv("MODELS_DIR", "/app/models"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "/data/output/video"))
    input_dir: Path = Path(os.getenv("INPUT_DIR", "/data/input/video"))
    
    # Video Generation Models
    base_model: str = os.getenv("BASE_MODEL", "runwayml/stable-diffusion-v1-5")
    video_model: str = os.getenv("VIDEO_MODEL", "wan2.1")
    controlnet_model: str = os.getenv("CONTROLNET_MODEL", "lllyasviel/sd-controlnet-openpose")
    upscaler_model: str = os.getenv("UPSCALER_MODEL", "RealESRGAN_x4plus")
    
    # Video Generation Parameters
    fps: int = int(os.getenv("FPS", "24"))
    resolution_width: int = int(os.getenv("RESOLUTION_WIDTH", "512"))
    resolution_height: int = int(os.getenv("RESOLUTION_HEIGHT", "512"))
    num_frames: int = int(os.getenv("NUM_FRAMES", "240"))  # 10 seconds at 24fps
    guidance_scale: float = float(os.getenv("GUIDANCE_SCALE", "7.5"))
    num_inference_steps: int = int(os.getenv("NUM_INFERENCE_STEPS", "50"))
    
    # ControlNet Parameters
    controlnet_conditioning_scale: float = float(os.getenv("CONTROLNET_CONDITIONING_SCALE", "0.8"))
    controlnet_guidance_start: float = float(os.getenv("CONTROLNET_GUIDANCE_START", "0.0"))
    controlnet_guidance_end: float = float(os.getenv("CONTROLNET_GUIDANCE_END", "1.0"))
    
    # Upscaling
    upscale_factor: int = int(os.getenv("UPSCALE_FACTOR", "2"))
    upscale_method: str = os.getenv("UPSCALE_METHOD", "RealESRGAN")
    
    # ComfyUI Integration
    comfyui_host: str = os.getenv("COMFYUI_HOST", "localhost")
    comfyui_port: int = int(os.getenv("COMFYUI_PORT", "8188"))
    comfyui_workflow_path: Path = Path(os.getenv("COMFYUI_WORKFLOW_PATH", "/app/workflows/default.json"))
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    redis_task_queue: str = os.getenv("REDIS_TASK_QUEUE", "video_rendering_tasks")
    
    # Task management
    max_generation_time_minutes: int = int(os.getenv("MAX_GENERATION_TIME_MINUTES", "60"))
    task_timeout_seconds: int = int(os.getenv("TASK_TIMEOUT_SECONDS", "3600"))
    
    # GPU
    use_gpu: bool = os.getenv("USE_GPU", "True").lower() == "true"
    gpu_memory_limit_mb: Optional[int] = int(os.getenv("GPU_MEMORY_LIMIT_MB")) if os.getenv("GPU_MEMORY_LIMIT_MB") else None
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Path = Path(os.getenv("LOG_FILE", "/app/logs/video_renderer.log"))
    
    # Supported input formats
    supported_video_formats: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    supported_image_formats: List[str] = [".jpg", ".jpeg", ".png", ".bmp"]
    supported_pose_formats: List[str] = [".json", ".npy", ".pkl"]
    
    # Output formats
    output_video_format: str = os.getenv("OUTPUT_VIDEO_FORMAT", "mp4")
    output_codec: str = os.getenv("OUTPUT_CODEC", "h264")
    output_bitrate: str = os.getenv("OUTPUT_BITRATE", "5000k")
    
    # Quality settings
    quality_presets: Dict[str, Dict[str, Any]] = {
        "low": {
            "resolution": [256, 256],
            "fps": 15,
            "num_inference_steps": 25,
            "upscale": False
        },
        "medium": {
            "resolution": [512, 512],
            "fps": 24,
            "num_inference_steps": 35,
            "upscale": False
        },
        "high": {
            "resolution": [768, 768],
            "fps": 30,
            "num_inference_steps": 50,
            "upscale": True,
            "upscale_factor": 2
        },
        "ultra": {
            "resolution": [1024, 1024],
            "fps": 60,
            "num_inference_steps": 75,
            "upscale": True,
            "upscale_factor": 4
        }
    }
    
    # Default quality preset
    default_quality_preset: str = os.getenv("DEFAULT_QUALITY_PRESET", "medium")
    
    # Frame interpolation
    enable_frame_interpolation: bool = os.getenv("ENABLE_FRAME_INTERPOLATION", "False").lower() == "true"
    interpolation_model: str = os.getenv("INTERPOLATION_MODEL", "RIFE")
    interpolation_factor: int = int(os.getenv("INTERPOLATION_FACTOR", "2"))
    
    # Post-processing
    enable_color_correction: bool = os.getenv("ENABLE_COLOR_CORRECTION", "True").lower() == "true"
    enable_stabilization: bool = os.getenv("ENABLE_STABILIZATION", "False").lower() == "true"
    enable_background_removal: bool = os.getenv("ENABLE_BACKGROUND_REMOVAL", "False").lower() == "true"
    
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
        settings.comfyui_workflow_path.parent
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
ensure_directories()