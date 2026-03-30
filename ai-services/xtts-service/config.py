from pydantic_settings import BaseSettings
from typing import Optional, List, Dict
from enum import Enum

class Language(str, Enum):
    """Supported languages for XTTS v2."""
    ENGLISH = "en"
    RUSSIAN = "ru"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    POLISH = "pl"
    TURKISH = "tr"
    DUTCH = "nl"
    CZECH = "cs"
    ARABIC = "ar"
    CHINESE = "zh-cn"
    JAPANESE = "ja"
    HUNGARIAN = "hu"
    KOREAN = "ko"
    HINDI = "hi"

class Settings(BaseSettings):
    """Application settings for XTTS Service."""
    
    # Service configuration
    app_name: str = "AvatarAI XTTS Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # XTTS v2 model configuration
    xtts_model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    model_cache_dir: str = "/app/models"
    use_gpu: bool = True
    gpu_device: int = 0
    
    # Audio settings
    default_sample_rate: int = 24000
    output_format: str = "wav"
    output_sample_rate: int = 24000
    
    # Voice cloning settings
    min_voice_sample_duration: float = 6.0  # seconds
    max_voice_sample_duration: float = 30.0  # seconds
    voice_embedding_cache_ttl: int = 86400  # 24 hours in seconds
    
    # Redis cache configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_voice_cache_prefix: str = "voice_embedding:"
    
    # Supported languages
    supported_languages: List[str] = [
        "en", "ru", "es", "fr", "de", "it", "pt", "pl", 
        "tr", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko", "hi"
    ]
    
    # Language mappings
    language_names: Dict[str, str] = {
        "en": "English",
        "ru": "Russian",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "pl": "Polish",
        "tr": "Turkish",
        "nl": "Dutch",
        "cs": "Czech",
        "ar": "Arabic",
        "zh-cn": "Chinese",
        "ja": "Japanese",
        "hu": "Hungarian",
        "ko": "Korean",
        "hi": "Hindi"
    }
    
    # Synthesis settings
    default_speed: float = 1.0
    default_temperature: float = 0.75
    default_length_penalty: float = 1.0
    default_repetition_penalty: float = 5.0
    default_top_k: int = 50
    default_top_p: float = 0.85
    
    # File storage
    input_dir: str = "/data/input"
    output_dir: str = "/data/output"
    max_file_size_mb: int = 100
    
    # API settings
    max_concurrent_requests: int = 5
    request_timeout_seconds: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()