import os
import uuid
import json
import asyncio
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from loguru import logger

from config import settings
from services.lora_trainer import LoraTrainer, TrainingConfig, TrainingTask

# Initialize logger
logger.add(
    settings.log_file,
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

# Global instances
lora_trainer: Optional[LoraTrainer] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Startup
    global lora_trainer
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server: {settings.host}:{settings.port}")
    logger.info(f"Data directory: {settings.data_dir}")
    
    # Initialize LoRA trainer
    try:
        lora_trainer = LoraTrainer()
        logger.info("LoRA trainer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LoRA trainer: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down LoRA trainer service")
    if lora_trainer:
        # Cleanup old tasks on shutdown
        lora_trainer.cleanup_old_tasks()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="LoRA Trainer service for AvatarAI - Train personalized avatar models",
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
class CreateTrainingRequest(BaseModel):
    """Request model for creating a training task."""
    user_id: str
    avatar_id: str
    image_urls: Optional[List[str]] = None
    config: Optional[TrainingConfig] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "avatar_id": "avatar_456",
                "image_urls": [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ],
                "config": {
                    "base_model": "runwayml/stable-diffusion-v1-5",
                    "lora_rank": 32,
                    "lora_alpha": 16,
                    "learning_rate": 1e-4,
                    "num_train_epochs": 10,
                    "train_batch_size": 1,
                    "gradient_accumulation_steps": 4,
                    "mixed_precision": "fp16",
                    "resolution": 512
                }
            }
        }

class TrainingTaskResponse(BaseModel):
    """Response model for training task."""
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
    if not lora_trainer:
        raise HTTPException(status_code=503, detail="LoRA trainer not initialized")
    
    health_details = lora_trainer.health_check()
    
    return HealthResponse(
        service=settings.app_name,
        status="healthy" if health_details.get("status") == "healthy" else "unhealthy",
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        details=health_details
    )

@app.post("/train", response_model=TrainingTaskResponse, tags=["Training"])
async def create_training_task(
    request: CreateTrainingRequest,
    background_tasks: BackgroundTasks
):
    """Create a new LoRA training task."""
    if not lora_trainer:
        raise HTTPException(status_code=503, detail="LoRA trainer not initialized")
    
    try:
        # Generate task ID
        task_id = f"lora_{uuid.uuid4()}"
        
        # Use default config if not provided
        config = request.config or TrainingConfig()
        
        # Create training task
        task = TrainingTask(
            task_id=task_id,
            user_id=request.user_id,
            avatar_id=request.avatar_id,
            image_paths=request.image_urls or [],
            config=config
        )
        
        # Validate that we have image paths
        if not task.image_paths:
            raise HTTPException(status_code=400, detail="No image URLs provided")
        
        # Start training in background
        background_tasks.add_task(train_lora_background, task)
        
        logger.info(f"Created training task {task_id} for user {request.user_id}, avatar {request.avatar_id}")
        
        return TrainingTaskResponse(
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
        logger.error(f"Failed to create training task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create training task: {str(e)}")

@app.post("/train/upload", response_model=TrainingTaskResponse, tags=["Training"])
async def create_training_task_with_upload(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    avatar_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """Create a training task with uploaded images."""
    if not lora_trainer:
        raise HTTPException(status_code=503, detail="LoRA trainer not initialized")
    
    try:
        # Generate task ID
        task_id = f"lora_{uuid.uuid4()}"
        
        # Save uploaded files
        image_paths = []
        for i, file in enumerate(files):
            # Validate file type
            if not any(file.filename.lower().endswith(ext) for ext in settings.supported_image_formats):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file format: {file.filename}. Supported: {settings.supported_image_formats}"
                )
            
            # Save file
            filename = f"{task_id}_{i:04d}{Path(file.filename).suffix}"
            file_path = settings.input_dir / filename
            
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            image_paths.append(str(file_path))
        
        # Create training task
        task = TrainingTask(
            task_id=task_id,
            user_id=user_id,
            avatar_id=avatar_id,
            image_paths=image_paths,
            config=TrainingConfig()
        )
        
        # Start training in background
        background_tasks.add_task(train_lora_background, task)
        
        logger.info(f"Created training task {task_id} with {len(files)} uploaded images")
        
        return TrainingTaskResponse(
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
        logger.error(f"Failed to create training task with upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create training task: {str(e)}")

@app.get("/train/{task_id}", response_model=TrainingTaskResponse, tags=["Training"])
async def get_training_task(task_id: str):
    """Get the status of a training task."""
    if not lora_trainer:
        raise HTTPException(status_code=503, detail="LoRA trainer not initialized")
    
    try:
        task = lora_trainer.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return TrainingTaskResponse(
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

@app.get("/train/{task_id}/output", tags=["Training"])
async def get_training_output(task_id: str):
    """Get the output of a completed training task."""
    if not lora_trainer:
        raise HTTPException(status_code=503, detail="LoRA trainer not initialized")
    
    try:
        task = lora_trainer.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if task.status != "completed":
            raise HTTPException(status_code=400, detail=f"Task {task_id} is not completed (status: {task.status})")
        
        if not task.output_path:
            raise HTTPException(status_code=404, detail=f"No output path for task {task_id}")
        
        # List files in output directory
        output_dir = Path(task.output_path)
        if not output_dir.exists():
            raise HTTPException(status_code=404, detail=f"Output directory not found: {task.output_path}")
        
        files = []
        for file_path in output_dir.rglob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "path": str(file_path.relative_to(output_dir)),
                    "size_bytes": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        return {
            "task_id": task_id,
            "output_dir": str(output_dir),
            "files": files,
            "metadata": task.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task output {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task output: {str(e)}")

@app.delete("/train/{task_id}", tags=["Training"])
async def cancel_training_task(task_id: str):
    """Cancel a training task (if possible)."""
    if not lora_trainer:
        raise HTTPException(status_code=503, detail="LoRA trainer not initialized")
    
    # Note: In production, we would implement actual cancellation logic
    # For MVP, we just mark it as cancelled if it's still pending
    
    try:
        task = lora_trainer.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if task.status in ["completed", "failed"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel task in {task.status} state"
            )
        
        # In production, we would stop the training process
        # For MVP, we just update the status
        task.status = "cancelled"
        task.completed_at = datetime.utcnow()
        task.error_message = "Cancelled by user"
        
        # Update in Redis
        if lora_trainer.redis_client:
            task_key = f"lora_task:{task_id}"
            task_data = task.dict()
            task_data["created_at"] = task_data["created_at"].isoformat()
            if task_data["started_at"]:
                task_data["started_at"] = task_data["started_at"].isoformat()
            if task_data["completed_at"]:
                task_data["completed_at"] = task_data["completed_at"].isoformat()
            
            lora_trainer.redis_client.setex(
                task_key,
                settings.task_timeout_seconds,
                json.dumps(task_data)
            )
        
        logger.info(f"Cancelled training task {task_id}")
        
        return {"message": f"Task {task_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")

@app.get("/models", tags=["Models"])
async def list_available_models():
    """List available base models for training."""
    # In production, this would list models from Hugging Face or local storage
    # For MVP, return a static list
    
    models = [
        {
            "id": "runwayml/stable-diffusion-v1-5",
            "name": "Stable Diffusion 1.5",
            "type": "diffusion",
            "resolution": "512x512",
            "license": "CreativeML Open RAIL-M",
            "description": "General purpose text-to-image model"
        },
        {
            "id": "stabilityai/stable-diffusion-2-1",
            "name": "Stable Diffusion 2.1",
            "type": "diffusion",
            "resolution": "768x768",
            "license": "CreativeML Open RAIL-M",
            "description": "Improved version with better text understanding"
        },
        {
            "id": "SG161222/Realistic_Vision_V5.1",
            "name": "Realistic Vision V5.1",
            "type": "diffusion",
            "resolution": "512x512",
            "license": "CreativeML Open RAIL-M",
            "description": "Specialized for realistic human faces"
        }
    ]
    
    return {"models": models}

# Background task function
async def train_lora_background(task: TrainingTask):
    """Background task for LoRA training."""
    try:
        if not lora_trainer:
            logger.error("LoRA trainer not initialized for background task")
            return
        
        logger.info(f"Starting background training for task {task.task_id}")
        await lora_trainer.train_lora_async(task)
        
    except Exception as e:
        logger.error(f"Background training failed for task {task.task_id}: {e}")

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