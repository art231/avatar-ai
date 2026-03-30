import os
import uuid
import json
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from loguru import logger

from config import settings
from services.video_renderer import VideoRenderer, RenderConfig, RenderTask

# Initialize logger
logger.add(
    settings.log_file,
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

# Global instances
video_renderer: Optional[VideoRenderer] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Startup
    global video_renderer
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server: {settings.host}:{settings.port}")
    logger.info(f"Data directory: {settings.data_dir}")
    
    # Initialize video renderer
    try:
        video_renderer = VideoRenderer()
        logger.info("Video renderer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize video renderer: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down video renderer service")
    if video_renderer:
        # Cleanup old tasks on shutdown
        video_renderer.cleanup_old_tasks()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Video Renderer service for AvatarAI - Generate high-quality avatar videos",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class RenderVideoRequest(BaseModel):
    """Request model for rendering video."""
    user_id: str
    avatar_id: str
    lora_path: str
    prompt: str
    negative_prompt: Optional[str] = ""
    pose_data_path: Optional[str] = None
    reference_image_path: Optional[str] = None
    duration_sec: Optional[int] = 10
    quality_preset: Optional[str] = settings.default_quality_preset
    config: Optional[RenderConfig] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "avatar_id": "avatar_456",
                "lora_path": "/data/output/lora/avatar_456.safetensors",
                "prompt": "a person talking naturally, high quality, detailed face",
                "negative_prompt": "blurry, distorted, low quality",
                "pose_data_path": "/data/output/motion/pose_sequence.json",
                "reference_image_path": "/data/input/avatar_456.jpg",
                "duration_sec": 10,
                "quality_preset": "medium",
                "config": {
                    "resolution": [512, 512],
                    "fps": 24,
                    "num_inference_steps": 35,
                    "guidance_scale": 7.5,
                    "upscale": False
                }
            }
        }

class UpscaleVideoRequest(BaseModel):
    """Request model for upscaling video."""
    user_id: str
    avatar_id: str
    input_video_path: str
    upscale_factor: Optional[int] = settings.upscale_factor
    quality_preset: Optional[str] = "high"
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "avatar_id": "avatar_456",
                "input_video_path": "/data/output/video/raw_avatar.mp4",
                "upscale_factor": 2,
                "quality_preset": "high"
            }
        }

class RenderTaskResponse(BaseModel):
    """Response model for render task."""
    task_id: str
    status: str
    progress: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    metadata: dict = {}

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
    if not video_renderer:
        raise HTTPException(status_code=503, detail="Video renderer not initialized")
    
    health_details = video_renderer.health_check()
    
    return HealthResponse(
        service=settings.app_name,
        status="healthy" if health_details.get("status") == "healthy" else "unhealthy",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        details=health_details
    )

@app.post("/render", response_model=RenderTaskResponse, tags=["Rendering"])
async def render_video(
    request: RenderVideoRequest,
    background_tasks: BackgroundTasks
):
    """Render video with avatar and motion."""
    if not video_renderer:
        raise HTTPException(status_code=503, detail="Video renderer not initialized")
    
    try:
        # Generate task ID
        task_id = f"render_{uuid.uuid4()}"
        
        # Use default config if not provided
        config = request.config or RenderConfig()
        
        # Create render task
        task = RenderTask(
            task_id=task_id,
            user_id=request.user_id,
            avatar_id=request.avatar_id,
            lora_path=request.lora_path,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            pose_data_path=request.pose_data_path,
            reference_image_path=request.reference_image_path,
            duration_sec=request.duration_sec,
            quality_preset=request.quality_preset,
            config=config
        )
        
        # Start rendering in background
        background_tasks.add_task(render_video_background, task)
        
        logger.info(f"Created video rendering task {task_id} for user {request.user_id}, avatar {request.avatar_id}")
        
        return RenderTaskResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            output_path=task.output_path,
            metadata=task.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create video rendering task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create video rendering task: {str(e)}")

@app.post("/upscale", response_model=RenderTaskResponse, tags=["Upscaling"])
async def upscale_video(
    request: UpscaleVideoRequest,
    background_tasks: BackgroundTasks
):
    """Upscale existing video."""
    if not video_renderer:
        raise HTTPException(status_code=503, detail="Video renderer not initialized")
    
    try:
        # Generate task ID
        task_id = f"upscale_{uuid.uuid4()}"
        
        # Create upscale task
        task = RenderTask(
            task_id=task_id,
            user_id=request.user_id,
            avatar_id=request.avatar_id,
            input_video_path=request.input_video_path,
            upscale_factor=request.upscale_factor,
            quality_preset=request.quality_preset,
            task_type="upscaling"
        )
        
        # Start upscaling in background
        background_tasks.add_task(upscale_video_background, task)
        
        logger.info(f"Created video upscaling task {task_id} for user {request.user_id}, avatar {request.avatar_id}")
        
        return RenderTaskResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            output_path=task.output_path,
            metadata=task.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create video upscaling task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create video upscaling task: {str(e)}")

@app.post("/render/upload", response_model=RenderTaskResponse, tags=["Rendering"])
async def render_video_with_upload(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    avatar_id: str = Form(...),
    lora_path: str = Form(...),
    prompt: str = Form(...),
    negative_prompt: str = Form(""),
    duration_sec: int = Form(10),
    quality_preset: str = Form(settings.default_quality_preset),
    pose_file: Optional[UploadFile] = File(None),
    reference_image: Optional[UploadFile] = File(None)
):
    """Render video with uploaded pose data and reference image."""
    if not video_renderer:
        raise HTTPException(status_code=503, detail="Video renderer not initialized")
    
    try:
        # Generate task ID
        task_id = f"render_{uuid.uuid4()}"
        
        # Save uploaded pose data if provided
        pose_data_path = None
        if pose_file:
            # Validate file type
            if not any(pose_file.filename.lower().endswith(ext) for ext in settings.supported_pose_formats):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported pose file format: {pose_file.filename}. Supported: {settings.supported_pose_formats}"
                )
            
            # Save file
            filename = f"{task_id}{Path(pose_file.filename).suffix}"
            file_path = settings.input_dir / filename
            
            with open(file_path, "wb") as f:
                content = await pose_file.read()
                f.write(content)
            
            pose_data_path = str(file_path)
        
        # Save uploaded reference image if provided
        reference_image_path = None
        if reference_image:
            # Validate file type
            if not any(reference_image.filename.lower().endswith(ext) for ext in settings.supported_image_formats):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported image format: {reference_image.filename}. Supported: {settings.supported_image_formats}"
                )
            
            # Save file
            filename = f"{task_id}_ref{Path(reference_image.filename).suffix}"
            file_path = settings.input_dir / filename
            
            with open(file_path, "wb") as f:
                content = await reference_image.read()
                f.write(content)
            
            reference_image_path = str(file_path)
        
        # Create render task
        task = RenderTask(
            task_id=task_id,
            user_id=user_id,
            avatar_id=avatar_id,
            lora_path=lora_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            pose_data_path=pose_data_path,
            reference_image_path=reference_image_path,
            duration_sec=duration_sec,
            quality_preset=quality_preset,
            config=RenderConfig()
        )
        
        # Start rendering in background
        background_tasks.add_task(render_video_background, task)
        
        logger.info(f"Created video rendering task {task_id} with uploaded files")
        
        return RenderTaskResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            output_path=task.output_path,
            metadata=task.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create video rendering task with upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create video rendering task: {str(e)}")

@app.get("/task/{task_id}", response_model=RenderTaskResponse, tags=["Tasks"])
async def get_task_status(task_id: str):
    """Get the status of a video rendering task."""
    if not video_renderer:
        raise HTTPException(status_code=503, detail="Video renderer not initialized")
    
    try:
        task = video_renderer.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return RenderTaskResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            output_path=task.output_path,
            metadata=task.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

@app.get("/task/{task_id}/output", tags=["Tasks"])
async def get_task_output(task_id: str):
    """Get the output of a completed video rendering task."""
    if not video_renderer:
        raise HTTPException(status_code=503, detail="Video renderer not initialized")
    
    try:
        task = video_renderer.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if task.status != "completed":
            raise HTTPException(status_code=400, detail=f"Task {task_id} is not completed (status: {task.status})")
        
        if not task.output_path:
            raise HTTPException(status_code=404, detail=f"No output path for task {task_id}")
        
        # Check if output is a file or directory
        output_path = Path(task.output_path)
        if output_path.is_file():
            # Return file
            return FileResponse(
                path=output_path,
                filename=output_path.name,
                media_type="application/octet-stream"
            )
        else:
            # List files in output directory
            files = []
            for file_path in output_path.rglob("*"):
                if file_path.is_file():
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path.relative_to(output_path)),
                        "size_bytes": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            return {
                "task_id": task_id,
                "output_dir": str(output_path),
                "files": files,
                "metadata": task.metadata
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task output {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task output: {str(e)}")

@app.get("/quality-presets", tags=["Rendering"])
async def list_quality_presets():
    """List available quality presets."""
    return {
        "presets": settings.quality_presets,
        "default_preset": settings.default_quality_preset
    }

@app.get("/models", tags=["Models"])
async def list_available_models():
    """List available video generation models."""
    # In production, this would list models from Hugging Face or local storage
    # For MVP, return a static list
    
    models = [
        {
            "id": "wan2.1",
            "name": "Wan Video 2.1",
            "type": "video-diffusion",
            "description": "Open-source video diffusion model for realistic video generation",
            "license": "Apache 2.0",
            "resolution": "512x512",
            "fps": 24
        },
        {
            "id": "stable-diffusion-v1-5",
            "name": "Stable Diffusion 1.5",
            "type": "image-diffusion",
            "description": "Base image model for LoRA training",
            "license": "CreativeML Open RAIL-M",
            "resolution": "512x512"
        },
        {
            "id": "controlnet-openpose",
            "name": "ControlNet OpenPose",
            "type": "controlnet",
            "description": "Pose conditioning for stable diffusion",
            "license": "Apache 2.0"
        },
        {
            "id": "realesrgan",
            "name": "Real-ESRGAN",
            "type": "upscaler",
            "description": "High-quality video upscaling",
            "license": "BSD-3-Clause",
            "upscale_factors": [2, 4]
        }
    ]
    
    return {"models": models}

# Background task functions
async def render_video_background(task: RenderTask):
    """Background task for video rendering."""
    try:
        if not video_renderer:
            logger.error("Video renderer not initialized for background task")
            return
        
        logger.info(f"Starting background video rendering for task {task.task_id}")
        await video_renderer.render_video_async(task)
        
    except Exception as e:
        logger.error(f"Background video rendering failed for task {task.task_id}: {e}")

async def upscale_video_background(task: RenderTask):
    """Background task for video upscaling."""
    try:
        if not video_renderer:
            logger.error("Video renderer not initialized for background task")
            return
        
        logger.info(f"Starting background video upscaling for task {task.task_id}")
        await video_renderer.upscale_video_async(task)
        
    except Exception as e:
        logger.error(f"Background video upscaling failed for task {task.task_id}: {e}")

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
