import os
import uuid
import json
import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

import cv2
import numpy as np
import torch
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from loguru import logger

# Import config and services
try:
    from config import settings
    from services.lipsync_processor import LipSyncProcessor
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    # Fallback config for development
    class Settings:
        app_name = "AvatarAI Lip Sync Service"
        app_version = "1.0.0"
        debug = True
        host = "0.0.0.0"
        port = 5006
        data_dir = Path("/data")
        models_dir = Path("/app/models")
        output_dir = Path("/data/output/lipsync")
        input_dir = Path("/data/input/lipsync")
        logs_dir = Path("/app/logs")
        log_level = "INFO"
        log_file = Path("/app/logs/lipsync_service.log")
        supported_video_formats = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
        supported_audio_formats = [".wav", ".mp3", ".aac", ".flac", ".ogg"]
        max_file_size_mb = 500
        default_model = "muse_talk"
        available_models = ["muse_talk", "wav2lip"]
        default_quality = "high"
        default_sync_accuracy = 0.9
        device = "cpu"
    
    settings = Settings()
    
    # Fallback LipSyncProcessor
    class LipSyncProcessor:
        def __init__(self, processor_type: str = "muse_talk"):
            self.processor_type = processor_type
            self.logger = logger
        
        def process(self, video_path, audio_path, output_path, quality="high", sync_accuracy=0.9):
            return False
        
        def health_check(self):
            return {
                "processor_available": False,
                "processor_type": self.processor_type,
                "error": "No processor initialized"
            }
        
        def get_available_models(self):
            return [
                {
                    "name": "muse_talk",
                    "description": "MuseTalk - High-quality lip sync with facial expression preservation",
                    "quality": "high",
                    "supported_formats": ["mp4", "avi", "mov"],
                    "processing_time": "medium",
                    "accuracy": 0.95
                },
                {
                    "name": "wav2lip",
                    "description": "Wav2Lip - Fast lip sync with good accuracy",
                    "quality": "medium",
                    "supported_formats": ["mp4", "avi", "mov", "webm"],
                    "processing_time": "fast",
                    "accuracy": 0.85
                }
            ]

# Initialize logger
logger.add(
    settings.log_file,
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

# Global instances
lip_sync_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Startup
    global lip_sync_service
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server: {settings.host}:{settings.port}")
    logger.info(f"Data directory: {settings.data_dir}")
    
    # Initialize lip sync service
    try:
        lip_sync_service = LipSyncProcessor(processor_type=settings.default_model)
        logger.info(f"Lip sync service initialized with processor type: {settings.default_model}")
    except Exception as e:
        logger.error(f"Failed to initialize lip sync service: {e}")
        lip_sync_service = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down lip sync service")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Lip Sync service for AvatarAI - Synchronize lips in video with audio using AI models",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class LipSyncRequest(BaseModel):
    """Request model for lip sync."""
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    model_name: str = settings.default_model
    output_format: str = "mp4"
    quality: str = "high"  # low, medium, high
    sync_accuracy: float = 0.9  # 0.0 to 1.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "wav2lip",
                "output_format": "mp4",
                "quality": "high",
                "sync_accuracy": 0.9
            }
        }

class LipSyncResponse(BaseModel):
    """Response model for lip sync."""
    success: bool
    task_id: str
    output_path: str
    video_info: Dict[str, Any]
    processing_time: float
    sync_quality: float
    message: str
    created_at: datetime

class HealthResponse(BaseModel):
    """Health check response."""
    service: str
    status: str
    version: str
    timestamp: datetime
    details: dict

# API endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    if lip_sync_service is None:
        service_health = {"service": "LipSyncService", "status": "not_initialized"}
    else:
        service_health = lip_sync_service.health_check()
    
    health_details = {
        "service_health": service_health,
        "models_dir": "exists" if settings.models_dir.exists() else "missing",
        "data_dir": "exists" if settings.data_dir.exists() else "missing",
        "available_models": settings.available_models
    }
    
    status = "healthy" if all([
        lip_sync_service is not None,
        settings.models_dir.exists(),
        settings.data_dir.exists()
    ]) else "unhealthy"
    
    return HealthResponse(
        service=settings.app_name,
        status=status,
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        details=health_details
    )

@app.post("/sync", response_model=LipSyncResponse, tags=["Sync"])
async def sync_lips(
    video_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    model_name: str = Form(settings.default_model),
    output_format: str = Form("mp4"),
    quality: str = Form("high"),
    sync_accuracy: float = Form(0.9)
):
    """Synchronize lips in video with audio."""
    try:
        # Validate files
        if not video_file.filename or not audio_file.filename:
            raise HTTPException(status_code=400, detail="Both video and audio files are required")
        
        # Check file sizes
        video_file.file.seek(0, 2)
        video_size = video_file.file.tell()
        video_file.file.seek(0)
        
        audio_file.file.seek(0, 2)
        audio_size = audio_file.file.tell()
        audio_file.file.seek(0)
        
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        if video_size > max_size_bytes or audio_size > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        # Validate file extensions
        video_ext = Path(video_file.filename).suffix.lower()
        audio_ext = Path(audio_file.filename).suffix.lower()
        
        if video_ext not in settings.supported_video_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported video format: {video_ext}. Supported: {settings.supported_video_formats}"
            )
        
        if audio_ext not in settings.supported_audio_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format: {audio_ext}. Supported: {settings.supported_audio_formats}"
            )
        
        # Validate model
        if model_name not in settings.available_models:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model: {model_name}. Available: {settings.available_models}"
            )
        
        # Generate unique task ID
        task_id = f"lipsync_{uuid.uuid4()}"
        
        # Create directories
        settings.input_dir.mkdir(parents=True, exist_ok=True)
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded files
        video_filename = f"{task_id}_video{video_ext}"
        audio_filename = f"{task_id}_audio{audio_ext}"
        output_filename = f"{task_id}_synced.{output_format}"
        
        video_path = settings.input_dir / video_filename
        audio_path = settings.input_dir / audio_filename
        output_path = settings.output_dir / output_filename
        
        with open(video_path, "wb") as f:
            content = await video_file.read()
            f.write(content)
        
        with open(audio_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        # Start processing
        start_time = datetime.utcnow()
        
        # Process lip sync using the service
        if lip_sync_service is None:
            raise HTTPException(status_code=500, detail="Lip sync service not initialized")
        
        # Create new processor with selected model if different from default
        if model_name != lip_sync_service.processor_type:
            try:
                lip_sync_service = LipSyncProcessor(processor_type=model_name)
                logger.info(f"Switched to processor type: {model_name}")
            except Exception as e:
                logger.error(f"Failed to switch processor type: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to initialize model: {model_name}")
        
        # Process lip sync
        success = lip_sync_service.process(
            video_path, audio_path, output_path, quality, sync_accuracy
        )
        
        message = "Lip sync completed successfully" if success else "Lip sync failed"
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Get video info
        video_info = await get_video_info(output_path if success else video_path)
        
        # Clean up input files
        if not settings.debug:
            try:
                video_path.unlink()
                audio_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete input files: {e}")
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Lip sync processing failed: {message}")
        
        return LipSyncResponse(
            success=True,
            task_id=task_id,
            output_path=str(output_path),
            video_info=video_info,
            processing_time=processing_time,
            sync_quality=sync_accuracy,
            message=message,
            created_at=start_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to synchronize lips: {e}")
        raise HTTPException(status_code=500, detail=f"Lip sync failed: {str(e)}")

@app.post("/sync/batch", tags=["Sync"])
async def sync_lips_batch(
    files: List[UploadFile] = File(...),
    model_name: str = Form(settings.default_model),
    output_format: str = Form("mp4")
):
    """Synchronize lips for multiple video-audio pairs."""
    # Expect files in pairs: video1, audio1, video2, audio2, ...
    if len(files) % 2 != 0:
        raise HTTPException(status_code=400, detail="Files must be in video-audio pairs")
    
    results = []
    for i in range(0, len(files), 2):
        video_file = files[i]
        audio_file = files[i + 1]
        
        try:
            # Reuse the single sync endpoint logic
            result = await sync_lips(
                video_file=video_file,
                audio_file=audio_file,
                model_name=model_name,
                output_format=output_format,
                quality="high",
                sync_accuracy=0.9
            )
            results.append(result.dict())
        except Exception as e:
            results.append({
                "success": False,
                "video_filename": video_file.filename,
                "audio_filename": audio_file.filename,
                "error": str(e)
            })
    
    return {
        "batch_id": f"batch_{uuid.uuid4()}",
        "total_pairs": len(files) // 2,
        "successful": len([r for r in results if r.get("success", False)]),
        "failed": len([r for r in results if not r.get("success", True)]),
        "results": results
    }

@app.get("/task/{task_id}/result", tags=["Tasks"])
async def get_sync_result(task_id: str):
    """Get lip sync result for a specific task."""
    # Look for output file
    output_pattern = f"{task_id}_synced.*"
    output_files = list(settings.output_dir.glob(output_pattern))
    
    if not output_files:
        raise HTTPException(status_code=404, detail=f"Result not found for task {task_id}")
    
    output_path = output_files[0]
    
    # Get video info
    video_info = await get_video_info(output_path)
    
    return {
        "task_id": task_id,
        "output_path": str(output_path),
        "video_info": video_info,
        "download_url": f"/download/{output_path.name}"
    }

@app.get("/download/{filename}", tags=["Tasks"])
async def download_video(filename: str):
    """Download processed video file."""
    file_path = settings.output_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="video/mp4"
    )

@app.get("/models", tags=["Models"])
async def list_models():
    """List available lip sync models."""
    if lip_sync_service is None:
        models = []
    else:
        models = lip_sync_service.get_available_models()
    
    return {
        "models": models,
        "default_model": settings.default_model,
        "recommended_model": settings.default_model
    }

@app.get("/capabilities", tags=["Models"])
async def get_capabilities():
    """Get service capabilities."""
    return {
        "supported_formats": {
            "video": settings.supported_video_formats,
            "audio": settings.supported_audio_formats,
            "output": ["mp4", "avi", "mov", "webm"]
        },
        "max_file_size_mb": settings.max_file_size_mb,
        "processing_modes": ["single", "batch"],
        "quality_presets": ["low", "medium", "high", "very_high"],
        "sync_accuracy_range": {"min": 0.1, "max": 1.0, "default": 0.9}
    }

async def get_video_info(video_path: Path) -> Dict[str, Any]:
    """Get video information."""
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return {"error": "Failed to open video"}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            "resolution": f"{width}x{height}",
            "fps": fps,
            "frame_count": frame_count,
            "duration_sec": duration,
            "file_size": video_path.stat().st_size if video_path.exists() else 0,
            "format": video_path.suffix[1:] if video_path.suffix else "unknown"
        }
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return {"error": str(e)}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": request.url.path,
            "method": request.method
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "Contact administrator",
            "path": request.url.path,
            "method": request.method
        }
    )

if __name__ == "__main__":
    """Run the application directly (for development)."""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
