import os
import uuid
import json
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

import cv2
import numpy as np
import torch
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from loguru import logger

# Import config and services
try:
    from config import settings
    from services.face_analyzer import FaceAnalyzer
except ImportError:
    # Fallback config for development
    class Settings:
        app_name = "AvatarAI Media Analyzer"
        app_version = "1.0.0"
        debug = True
        host = "0.0.0.0"
        port = 5005
        data_dir = Path("/data")
        models_dir = Path("/app/models")
        output_dir = Path("/data/output/media")
        input_dir = Path("/data/input/media")
        log_level = "INFO"
        log_file = Path("/app/logs/media_analyzer.log")
        supported_image_formats = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
        supported_video_formats = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
        max_file_size_mb = 100
        min_face_quality_score = 0.7
        min_resolution = [256, 256]
    
    settings = Settings()
    
    # Fallback FaceAnalyzer
    class FaceAnalyzer:
        def __init__(self, device="cpu"):
            self.device = device
            self.logger = logger
        
        def analyze_image(self, image_path):
            raise NotImplementedError("FaceAnalyzer not properly imported")
        
        def align_and_save_faces(self, image_path, faces, output_dir):
            return faces
        
        def validate_image(self, image_path):
            return True, "Simulated validation"
        
        def health_check(self):
            return {"model_loaded": False, "device": self.device}

# Initialize logger
logger.add(
    settings.log_file,
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

# Global instances
face_analyzer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Startup
    global face_analyzer
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server: {settings.host}:{settings.port}")
    logger.info(f"Data directory: {settings.data_dir}")
    
    # Initialize face analyzer with InsightFace
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        face_analyzer = FaceAnalyzer(device=device)
        logger.info(f"Face analyzer initialized on {device}")
    except Exception as e:
        logger.error(f"Failed to initialize face analyzer: {e}")
        face_analyzer = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down media analyzer service")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Media Analyzer service for AvatarAI - Analyze photos and videos for face detection, alignment, and quality assessment",
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
class MediaAnalysisResponse(BaseModel):
    """Response model for media analysis."""
    success: bool
    task_id: str
    media_type: str
    file_info: Dict[str, Any]
    analysis_results: Dict[str, Any]
    processing_time: float
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
    health_details = {
        "face_analyzer": "initialized" if face_analyzer else "not_initialized",
        "models_dir": "exists" if settings.models_dir.exists() else "missing",
        "data_dir": "exists" if settings.data_dir.exists() else "missing"
    }
    
    status = "healthy" if all([
        face_analyzer is not None,
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

@app.post("/analyze", response_model=MediaAnalysisResponse, tags=["Analysis"])
async def analyze_media(
    file: UploadFile = File(...),
    media_type: str = Form("image"),
    analysis_types: str = Form("face_detection,quality_assessment"),
    align_faces: bool = Form(True),
    output_format: str = Form("json")
):
    """Analyze media file (image or video)."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        
        if media_type == "image":
            if file_ext not in settings.supported_image_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported image format: {file_ext}. Supported: {settings.supported_image_formats}"
                )
        elif media_type == "video":
            if file_ext not in settings.supported_video_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported video format: {file_ext}. Supported: {settings.supported_video_formats}"
                )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported media type: {media_type}")
        
        # Generate unique filename and save file
        task_id = f"analysis_{uuid.uuid4()}"
        input_filename = f"{task_id}{file_ext}"
        input_path = settings.input_dir / input_filename
        
        # Ensure directories exist
        settings.input_dir.mkdir(parents=True, exist_ok=True)
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse analysis types
        analysis_types_list = [t.strip() for t in analysis_types.split(",")]
        
        # Start analysis
        start_time = datetime.utcnow()
        
        if media_type == "image":
            analysis_results = await analyze_image(
                input_path, task_id, analysis_types_list, align_faces
            )
        else:  # video
            analysis_results = await analyze_video(
                input_path, task_id, analysis_types_list, align_faces
            )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # File info
        file_info = {
            "filename": input_filename,
            "original_name": file.filename,
            "size_bytes": file_size,
            "media_type": media_type,
            "extension": file_ext,
            "path": str(input_path)
        }
        
        # Clean up input file (optional, could keep for debugging)
        if not settings.debug:
            try:
                input_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete input file {input_path}: {e}")
        
        return MediaAnalysisResponse(
            success=True,
            task_id=task_id,
            media_type=media_type,
            file_info=file_info,
            analysis_results=analysis_results,
            processing_time=processing_time,
            message="Media analysis completed successfully",
            created_at=start_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze media: {e}")
        raise HTTPException(status_code=500, detail=f"Media analysis failed: {str(e)}")

async def analyze_image(
    image_path: Path,
    task_id: str,
    analysis_types: List[str],
    align_faces: bool
) -> Dict[str, Any]:
    """Analyze single image using InsightFace."""
    logger.info(f"Analyzing image: {image_path}")
    
    if face_analyzer is None:
        raise ValueError("Face analyzer not initialized")
    
    try:
        # Analyze image with InsightFace
        analysis = face_analyzer.analyze_image(image_path)
        
        # Align faces if requested
        if align_faces and "face_alignment" in analysis_types and analysis["faces"]:
            aligned_dir = settings.output_dir / f"{task_id}_aligned_faces"
            updated_faces = face_analyzer.align_and_save_faces(
                image_path, analysis["faces"], aligned_dir
            )
            analysis["faces"] = updated_faces
        
        # Validate image meets requirements
        is_valid, message = face_analyzer.validate_image(image_path)
        if not is_valid:
            raise ValueError(f"Image validation failed: {message}")
        
        # Save results
        results_path = settings.output_dir / f"{task_id}_results.json"
        with open(results_path, "w") as f:
            json.dump(analysis, f, indent=2, default=str)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise

async def analyze_video(
    video_path: Path,
    task_id: str,
    analysis_types: List[str],
    align_faces: bool
) -> Dict[str, Any]:
    """Analyze video file by sampling key frames."""
    logger.info(f"Analyzing video: {video_path}")
    
    if face_analyzer is None:
        raise ValueError("Face analyzer not initialized")
    
    # Open video
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Failed to open video: {video_path}")
    
    # Get video info and codec before releasing
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    
    # Simple codec detection
    codec = "unknown"
    try:
        # Try to get fourcc code
        fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)])
    except:
        pass
    
    # Sample key frames (first, middle, last)
    key_frames = [0, frame_count // 2, frame_count - 1]
    key_frames = [f for f in key_frames if f < frame_count]
    
    frames_analysis = []
    best_face_quality = 0
    faces_detected = 0
    
    for frame_idx in key_frames:
        # Set frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if not ret:
            continue
        
        # Save frame as temporary image for analysis
        temp_frame_path = settings.output_dir / f"{task_id}_frame_{frame_idx}.jpg"
        cv2.imwrite(str(temp_frame_path), frame)
        
        try:
            # Analyze frame
            frame_analysis = face_analyzer.analyze_image(temp_frame_path)
            
            # Extract face information
            frame_faces = []
            for face in frame_analysis.get("faces", []):
                faces_detected += 1
                best_face_quality = max(best_face_quality, face["quality_score"])
                
                frame_faces.append({
                    "face_id": face["face_id"],
                    "bounding_box": face["bounding_box"],
                    "quality_score": face["quality_score"],
                    "detection_confidence": face["detection_confidence"]
                })
            
            frames_analysis.append({
                "frame_index": frame_idx,
                "timestamp_sec": frame_idx / fps if fps > 0 else 0,
                "faces": frame_faces
            })
            
            # Clean up temp file
            if temp_frame_path.exists():
                temp_frame_path.unlink()
                
        except Exception as e:
            logger.warning(f"Failed to analyze frame {frame_idx}: {e}")
            continue
    
    cap.release()
    
    # Validate video has at least one face
    if faces_detected == 0:
        raise ValueError("No faces detected in the video")
    
    results = {
        "video_info": {
            "resolution": [width, height],
            "fps": fps,
            "frame_count": frame_count,
            "duration_sec": duration,
            "codec": codec
        },
        "summary": {
            "faces_detected": faces_detected,
            "best_face_quality": best_face_quality,
            "key_frames_analyzed": len(frames_analysis),
            "pose_changes": 0  # Could be extended with pose estimation
        }
    }
    
    if "face_detection" in analysis_types:
        results["frames"] = frames_analysis
    
    # Save results
    results_path = settings.output_dir / f"{task_id}_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    return results

@app.get("/capabilities", tags=["Analysis"])
async def get_capabilities():
    """Get available analysis capabilities."""
    return {
        "capabilities": [
            "face_detection",
            "face_alignment",
            "quality_assessment",
            "pose_estimation",
            "age_gender_estimation",
            "emotion_analysis"
        ],
        "supported_formats": {
            "images": settings.supported_image_formats,
            "videos": settings.supported_video_formats
        },
        "max_file_size_mb": settings.max_file_size_mb,
        "min_face_quality_score": settings.min_face_quality_score,
        "min_resolution": settings.min_resolution
    }

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