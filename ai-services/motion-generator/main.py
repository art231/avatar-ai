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
from services.motion_generator import MotionGenerator, MotionConfig, MotionTask

# Initialize logger
logger.add(
    settings.log_file,
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

# Global instances
motion_generator: Optional[MotionGenerator] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Startup
    global motion_generator
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server: {settings.host}:{settings.port}")
    logger.info(f"Data directory: {settings.data_dir}")
    
    # Initialize motion generator
    try:
        motion_generator = MotionGenerator()
        logger.info("Motion generator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize motion generator: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down motion generator service")
    if motion_generator:
        # Cleanup old tasks on shutdown
        motion_generator.cleanup_old_tasks()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Motion Generator service for AvatarAI - Generate realistic avatar animations",
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
class GenerateMotionRequest(BaseModel):
    """Request model for generating motion."""
    user_id: str
    avatar_id: str
    action_prompt: str
    duration_sec: Optional[int] = settings.default_duration_sec
    motion_preset: Optional[str] = "idle_talking"
    config: Optional[MotionConfig] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "avatar_id": "avatar_456",
                "action_prompt": "человек естественно разговаривает",
                "duration_sec": 10,
                "motion_preset": "idle_talking",
                "config": {
                    "fps": 24,
                    "resolution": [512, 512],
                    "smoothing": True,
                    "smoothing_window": 5,
                    "interpolation": "cubic"
                }
            }
        }

class ExtractPoseRequest(BaseModel):
    """Request model for extracting pose from video."""
    user_id: str
    avatar_id: str
    video_path: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "avatar_id": "avatar_456",
                "video_path": "/data/input/video.mp4"
            }
        }

class MotionTaskResponse(BaseModel):
    """Response model for motion task."""
    task_id: str
    status: str
    progress: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    pose_data_path: Optional[str] = None
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
    if not motion_generator:
        raise HTTPException(status_code=503, detail="Motion generator not initialized")
    
    health_details = motion_generator.health_check()
    
    return HealthResponse(
        service=settings.app_name,
        status="healthy" if health_details.get("status") == "healthy" else "unhealthy",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        details=health_details
    )

@app.post("/generate", response_model=MotionTaskResponse, tags=["Motion"])
async def generate_motion(
    request: GenerateMotionRequest,
    background_tasks: BackgroundTasks
):
    """Generate motion from text prompt."""
    if not motion_generator:
        raise HTTPException(status_code=503, detail="Motion generator not initialized")
    
    try:
        # Generate task ID
        task_id = f"motion_{uuid.uuid4()}"
        
        # Use default config if not provided
        config = request.config or MotionConfig()
        
        # Create motion task
        task = MotionTask(
            task_id=task_id,
            user_id=request.user_id,
            avatar_id=request.avatar_id,
            action_prompt=request.action_prompt,
            duration_sec=request.duration_sec,
            motion_preset=request.motion_preset,
            config=config
        )
        
        # Start generation in background
        background_tasks.add_task(generate_motion_background, task)
        
        logger.info(f"Created motion generation task {task_id} for user {request.user_id}, avatar {request.avatar_id}")
        
        return MotionTaskResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            output_path=task.output_path,
            pose_data_path=task.pose_data_path,
            metadata=task.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create motion generation task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create motion generation task: {str(e)}")

@app.post("/extract-pose", response_model=MotionTaskResponse, tags=["Pose"])
async def extract_pose(
    request: ExtractPoseRequest,
    background_tasks: BackgroundTasks
):
    """Extract pose from video."""
    if not motion_generator:
        raise HTTPException(status_code=503, detail="Motion generator not initialized")
    
    try:
        # Generate task ID
        task_id = f"pose_{uuid.uuid4()}"
        
        # Create pose extraction task
        task = MotionTask(
            task_id=task_id,
            user_id=request.user_id,
            avatar_id=request.avatar_id,
            video_path=request.video_path,
            task_type="pose_extraction"
        )
        
        # Start extraction in background
        background_tasks.add_task(extract_pose_background, task)
        
        logger.info(f"Created pose extraction task {task_id} for user {request.user_id}, avatar {request.avatar_id}")
        
        return MotionTaskResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            output_path=task.output_path,
            pose_data_path=task.pose_data_path,
            metadata=task.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create pose extraction task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create pose extraction task: {str(e)}")

@app.post("/generate/upload", response_model=MotionTaskResponse, tags=["Motion"])
async def generate_motion_with_upload(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    avatar_id: str = Form(...),
    action_prompt: str = Form(...),
    duration_sec: int = Form(settings.default_duration_sec),
    video_file: Optional[UploadFile] = File(None)
):
    """Generate motion with optional video upload for pose extraction."""
    if not motion_generator:
        raise HTTPException(status_code=503, detail="Motion generator not initialized")
    
    try:
        # Generate task ID
        task_id = f"motion_{uuid.uuid4()}"
        
        # Save uploaded video if provided
        video_path = None
        if video_file:
            # Validate file type
            if not any(video_file.filename.lower().endswith(ext) for ext in settings.supported_video_formats):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file format: {video_file.filename}. Supported: {settings.supported_video_formats}"
                )
            
            # Save file
            filename = f"{task_id}{Path(video_file.filename).suffix}"
            file_path = settings.input_dir / filename
            
            with open(file_path, "wb") as f:
                content = await video_file.read()
                f.write(content)
            
            video_path = str(file_path)
        
        # Create motion task
        task = MotionTask(
            task_id=task_id,
            user_id=user_id,
            avatar_id=avatar_id,
            action_prompt=action_prompt,
            duration_sec=duration_sec,
            video_path=video_path,
            config=MotionConfig()
        )
        
        # Start generation in background
        background_tasks.add_task(generate_motion_background, task)
        
        logger.info(f"Created motion generation task {task_id} with uploaded video")
        
        return MotionTaskResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            output_path=task.output_path,
            pose_data_path=task.pose_data_path,
            metadata=task.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create motion generation task with upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create motion generation task: {str(e)}")

@app.get("/task/{task_id}", response_model=MotionTaskResponse, tags=["Tasks"])
async def get_task_status(task_id: str):
    """Get the status of a motion generation task."""
    if not motion_generator:
        raise HTTPException(status_code=503, detail="Motion generator not initialized")
    
    try:
        task = motion_generator.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return MotionTaskResponse(
            task_id=task.task_id,
            status=task.status,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            error_message=task.error_message,
            output_path=task.output_path,
            pose_data_path=task.pose_data_path,
            metadata=task.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

@app.get("/task/{task_id}/output", tags=["Tasks"])
async def get_task_output(task_id: str):
    """Get the output of a completed motion generation task."""
    if not motion_generator:
        raise HTTPException(status_code=503, detail="Motion generator not initialized")
    
    try:
        task = motion_generator.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if task.status != "completed":
            raise HTTPException(status_code=400, detail=f"Task {task_id} is not completed (status: {task.status})")
        
        if not task.output_path:
            raise HTTPException(status_code=404, detail=f"No output path for task {task_id}")
        
        # Return pose data if available
        pose_data = None
        if task.pose_data_path and Path(task.pose_data_path).exists():
            with open(task.pose_data_path, 'r') as f:
                pose_data = json.load(f)
        
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
                "pose_data": pose_data,
                "metadata": task.metadata
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task output {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task output: {str(e)}")

@app.get("/presets", tags=["Motion"])
async def list_motion_presets():
    """List available motion presets."""
    return {
        "presets": settings.default_motion_presets,
        "default_preset": "idle_talking"
    }

@app.get("/models", tags=["Models"])
async def list_available_models():
    """List available motion generation models."""
    # In production, this would list models from Hugging Face or local storage
    # For MVP, return a static list
    
    models = [
        {
            "id": "unimotion",
            "name": "UniMotion",
            "type": "text-to-motion",
            "description": "Text-to-motion generation using SMPL parameters",
            "license": "MIT",
            "supported_actions": ["talking", "walking", "gesturing", "idle"]
        },
        {
            "id": "mdm",
            "name": "Motion Diffusion Model",
            "type": "diffusion",
            "description": "High-quality motion generation using diffusion",
            "license": "MIT",
            "supported_actions": ["complex movements", "dancing", "sports"]
        },
        {
            "id": "dwpose",
            "name": "DWPose",
            "type": "pose_estimation",
            "description": "Accurate 2D pose estimation",
            "license": "Apache 2.0",
            "supported_actions": ["pose_extraction"]
        }
    ]
    
    return {"models": models}

# Background task functions
async def generate_motion_background(task: MotionTask):
    """Background task for motion generation."""
    try:
        if not motion_generator:
            logger.error("Motion generator not initialized for background task")
            return
        
        logger.info(f"Starting background motion generation for task {task.task_id}")
        await motion_generator.generate_motion_async(task)
        
    except Exception as e:
        logger.error(f"Background motion generation failed for task {task.task_id}: {e}")

async def extract_pose_background(task: MotionTask):
    """Background task for pose extraction."""
    try:
        if not motion_generator:
            logger.error("Motion generator not initialized for background task")
            return
        
        logger.info(f"Starting background pose extraction for task {task.task_id}")
        await motion_generator.extract_pose_async(task)
        
    except Exception as e:
        logger.error(f"Background pose extraction failed for task {task.task_id}: {e}")

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