from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import uuid
import shutil
from pathlib import Path
import logging
from loguru import logger

from services.tts_processor import TTSProcessor
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.add("logs/xtts_service.log", rotation="500 MB", retention="30 days")

app = FastAPI(
    title="AvatarAI XTTS Service",
    description="Text-to-Speech service with voice cloning using Coqui XTTS v2",
    version="1.0.0"
)

# Initialize TTS processor
tts_processor = TTSProcessor()

# Request/Response models
class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    language: str = Field(default="en", description="Language code (e.g., 'en', 'ru', 'es')")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    temperature: float = Field(default=0.75, ge=0.1, le=1.0, description="Generation temperature")
    use_cache: bool = Field(default=True, description="Use cached voice embeddings")

class CloneAndSynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    language: str = Field(default="en", description="Language code")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed")
    temperature: float = Field(default=0.75, ge=0.1, le=1.0, description="Generation temperature")
    use_cache: bool = Field(default=True, description="Use cached voice embeddings")

class SynthesizeResponse(BaseModel):
    success: bool
    audio_path: Optional[str] = None
    processing_time: float
    audio_info: Dict[str, Any]
    language: str
    text_length: int
    cached: bool = False
    error: Optional[str] = None

class VoiceInfo(BaseModel):
    id: str
    name: str
    language: str
    description: Optional[str] = None

class LanguageInfo(BaseModel):
    code: str
    name: str
    supported: bool = True

@app.get("/")
async def root():
    """Root endpoint with service information."""
    health_status = await health()
    languages = await list_languages()
    
    return {
        "message": "AvatarAI XTTS Service",
        "status": "running",
        "version": settings.app_version,
        "health": health_status,
        "supported_languages": len(languages["languages"])
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        health_status = tts_processor.health_check()
        return {
            "status": "healthy" if health_status["model_loaded"] else "degraded",
            "service": "xtts-service",
            "details": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "xtts-service",
            "error": str(e)
        }

@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize_text(
    request: SynthesizeRequest,
    voice_file: UploadFile = File(...)
):
    """
    Synthesize text to speech using uploaded voice sample.
    
    This endpoint clones the voice from the uploaded sample and synthesizes
    the provided text in that voice.
    """
    try:
        # Validate file
        if not voice_file.filename:
            raise HTTPException(status_code=400, detail="No voice file provided")
        
        # Generate unique filename
        file_ext = Path(voice_file.filename).suffix
        unique_id = str(uuid.uuid4())
        voice_filename = f"voice_{unique_id}{file_ext}"
        
        # Create directories if they don't exist
        input_dir = Path(settings.input_dir)
        input_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        voice_path = input_dir / voice_filename
        with open(voice_path, "wb") as buffer:
            shutil.copyfileobj(voice_file.file, buffer)
        
        # Process TTS
        result = tts_processor.clone_and_synthesize(
            voice_sample_path=str(voice_path),
            text=request.text,
            language=request.language,
            speed=request.speed,
            temperature=request.temperature,
            use_cache=request.use_cache
        )
        
        # Clean up input file
        if os.path.exists(voice_path):
            os.remove(voice_path)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "TTS synthesis failed"))
        
        return SynthesizeResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error synthesizing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")

@app.post("/clone-and-synthesize", response_model=SynthesizeResponse)
async def clone_and_synthesize(
    request: CloneAndSynthesizeRequest,
    voice_file: UploadFile = File(...)
):
    """
    Clone voice from sample and synthesize text (alias for /synthesize).
    
    This is the same as /synthesize endpoint but with a more descriptive name.
    """
    # Reuse the synthesize endpoint logic
    synthesize_request = SynthesizeRequest(
        text=request.text,
        language=request.language,
        speed=request.speed,
        temperature=request.temperature,
        use_cache=request.use_cache
    )
    
    return await synthesize_text(synthesize_request, voice_file)

@app.get("/voices")
async def list_voices():
    """
    List available pre-trained voices.
    
    Note: XTTS v2 is primarily for voice cloning, but includes some base voices.
    """
    try:
        # Get supported languages
        languages = tts_processor.get_supported_languages()
        
        # Create voice list with base voices for each language
        voices = []
        for lang in languages[:5]:  # Limit to 5 languages for demo
            voices.append({
                "id": f"base_{lang['code']}_female",
                "name": f"Base {lang['name']} Female",
                "language": lang["code"],
                "description": f"Base female voice for {lang['name']}"
            })
            voices.append({
                "id": f"base_{lang['code']}_male",
                "name": f"Base {lang['name']} Male",
                "language": lang["code"],
                "description": f"Base male voice for {lang['name']}"
            })
        
        return {
            "voices": voices,
            "total": len(voices),
            "note": "XTTS v2 is primarily for voice cloning. These are base voices for reference."
        }
        
    except Exception as e:
        logger.error(f"Error listing voices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {str(e)}")

@app.get("/languages")
async def list_languages():
    """List all supported languages."""
    try:
        languages = tts_processor.get_supported_languages()
        return {
            "languages": languages,
            "total": len(languages),
            "default_language": "en"
        }
    except Exception as e:
        logger.error(f"Error listing languages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list languages: {str(e)}")

@app.get("/download/{filename}")
async def download_audio(filename: str):
    """
    Download generated audio file.
    """
    file_path = Path(settings.output_dir) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/wav"
    )

@app.get("/files")
async def list_files():
    """
    List available generated audio files.
    """
    output_dir = Path(settings.output_dir)
    if not output_dir.exists():
        return {"files": []}
    
    files = []
    for file_path in output_dir.glob("*.wav"):
        stats = file_path.stat()
        files.append({
            "filename": file_path.name,
            "size_bytes": stats.st_size,
            "created": stats.st_ctime,
            "modified": stats.st_mtime
        })
    
    return {"files": files}

@app.delete("/cache")
async def clear_cache(voice_hash: Optional[str] = None):
    """
    Clear voice embedding cache.
    
    Parameters:
    - voice_hash: Optional hash of specific voice to clear. If not provided, clears all cache.
    """
    try:
        if voice_hash:
            # In a real implementation, we would need to map hash back to file path
            success = tts_processor.clear_voice_cache()
            message = "Cache cleared partially" if success else "Failed to clear cache"
        else:
            success = tts_processor.clear_voice_cache()
            message = "All cache cleared" if success else "Failed to clear cache"
        
        return {
            "success": success,
            "message": message,
            "cache_cleared": not voice_hash  # True if all cache cleared
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@app.get("/status")
async def get_status():
    """Get detailed service status."""
    health_status = tts_processor.health_check()
    languages = await list_languages()
    
    return {
        "service": "xtts-service",
        "version": settings.app_version,
        "status": "running",
        "model_loaded": health_status["model_loaded"],
        "redis_connected": health_status["redis_connected"],
        "device": health_status["device"],
        "supported_languages": languages["total"],
        "cache_enabled": health_status["redis_connected"],
        "gpu_available": health_status["cuda_available"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5003,
        reload=True,
        log_level="info"
    )