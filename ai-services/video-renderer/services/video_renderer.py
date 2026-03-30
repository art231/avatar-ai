import os
import json
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
import redis

from config import settings

class TaskStatus(str, Enum):
    """Status of a render task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class RenderConfig:
    """Configuration for video rendering."""
    resolution: List[int] = field(default_factory=lambda: [512, 512])
    fps: int = 24
    num_inference_steps: int = 35
    guidance_scale: float = 7.5
    upscale: bool = False
    upscale_factor: int = 2
    enable_color_correction: bool = True
    enable_stabilization: bool = False
    enable_background_removal: bool = False

@dataclass
class RenderTask:
    """Video rendering task."""
    task_id: str
    user_id: str
    avatar_id: str
    lora_path: str
    prompt: str
    negative_prompt: str = ""
    pose_data_path: Optional[str] = None
    reference_image_path: Optional[str] = None
    input_video_path: Optional[str] = None
    duration_sec: int = 10
    quality_preset: str = "medium"
    upscale_factor: int = 2
    config: RenderConfig = field(default_factory=RenderConfig)
    task_type: str = "rendering"
    
    # Task status fields
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class VideoRenderer:
    """Video renderer service for generating avatar videos."""
    
    def __init__(self):
        """Initialize video renderer."""
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
        
        # Task storage
        self.tasks: Dict[str, RenderTask] = {}
        
        # Initialize models (in production, this would load actual models)
        self._initialize_models()
        
        logger.info("Video renderer initialized")
    
    def _initialize_models(self):
        """Initialize video generation models."""
        # In production, this would load actual models
        # For MVP, just log initialization
        logger.info("Initializing video generation models")
        
        # Check if models directory exists
        if not settings.models_dir.exists():
            logger.warning(f"Models directory does not exist: {settings.models_dir}")
        
        # Check if workflows directory exists
        if not settings.comfyui_workflow_path.parent.exists():
            logger.warning(f"Workflows directory does not exist: {settings.comfyui_workflow_path.parent}")
    
    async def render_video_async(self, task: RenderTask):
        """Render video asynchronously."""
        try:
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.utcnow()
            task.progress = 0.1
            
            # Update task in storage
            self.tasks[task.task_id] = task
            
            logger.info(f"Starting video rendering for task {task.task_id}")
            
            # Simulate video rendering process
            # In production, this would call actual video generation models
            
            # Step 1: Prepare inputs
            task.progress = 0.2
            await self._prepare_inputs(task)
            
            # Step 2: Generate video frames
            task.progress = 0.4
            await self._generate_frames(task)
            
            # Step 3: Apply pose conditioning if available
            task.progress = 0.6
            if task.pose_data_path:
                await self._apply_pose_conditioning(task)
            
            # Step 4: Upscale if requested
            task.progress = 0.8
            if task.config.upscale:
                await self._upscale_video(task)
            
            # Step 5: Post-processing
            task.progress = 0.9
            await self._post_process_video(task)
            
            # Step 6: Finalize
            task.progress = 1.0
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            # Set output path
            output_filename = f"avatar_{task.avatar_id}_{task.task_id}.mp4"
            task.output_path = str(settings.output_dir / output_filename)
            
            # Add metadata
            task.metadata.update({
                "duration_sec": task.duration_sec,
                "quality_preset": task.quality_preset,
                "resolution": task.config.resolution,
                "fps": task.config.fps,
                "generated_at": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Video rendering completed for task {task.task_id}")
            
        except Exception as e:
            logger.error(f"Video rendering failed for task {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
    
    async def upscale_video_async(self, task: RenderTask):
        """Upscale video asynchronously."""
        try:
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.utcnow()
            task.progress = 0.1
            
            # Update task in storage
            self.tasks[task.task_id] = task
            
            logger.info(f"Starting video upscaling for task {task.task_id}")
            
            # Check if input video exists
            if not task.input_video_path or not Path(task.input_video_path).exists():
                raise FileNotFoundError(f"Input video not found: {task.input_video_path}")
            
            # Simulate upscaling process
            # In production, this would call actual upscaling models
            
            # Step 1: Load video
            task.progress = 0.3
            await self._load_video_for_upscaling(task)
            
            # Step 2: Apply upscaling
            task.progress = 0.7
            await self._apply_upscaling(task)
            
            # Step 3: Save upscaled video
            task.progress = 0.9
            await self._save_upscaled_video(task)
            
            # Step 4: Finalize
            task.progress = 1.0
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            # Set output path
            input_path = Path(task.input_video_path)
            output_filename = f"{input_path.stem}_upscaled_x{task.upscale_factor}{input_path.suffix}"
            task.output_path = str(settings.output_dir / output_filename)
            
            # Add metadata
            task.metadata.update({
                "upscale_factor": task.upscale_factor,
                "quality_preset": task.quality_preset,
                "original_path": task.input_video_path,
                "upscaled_at": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Video upscaling completed for task {task.task_id}")
            
        except Exception as e:
            logger.error(f"Video upscaling failed for task {task.task_id}: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
    
    async def _prepare_inputs(self, task: RenderTask):
        """Prepare inputs for video rendering."""
        logger.info(f"Preparing inputs for task {task.task_id}")
        
        # Check if LoRA model exists
        if not Path(task.lora_path).exists():
            raise FileNotFoundError(f"LoRA model not found: {task.lora_path}")
        
        # Check if pose data exists (if provided)
        if task.pose_data_path and not Path(task.pose_data_path).exists():
            raise FileNotFoundError(f"Pose data not found: {task.pose_data_path}")
        
        # Check if reference image exists (if provided)
        if task.reference_image_path and not Path(task.reference_image_path).exists():
            raise FileNotFoundError(f"Reference image not found: {task.reference_image_path}")
        
        # Create output directory
        output_dir = settings.output_dir / task.task_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        await asyncio.sleep(0.5)  # Simulate work
    
    async def _generate_frames(self, task: RenderTask):
        """Generate video frames."""
        logger.info(f"Generating frames for task {task.task_id}")
        
        # In production, this would use video diffusion models
        # For MVP, simulate frame generation
        
        num_frames = task.duration_sec * task.config.fps
        
        # Simulate frame generation progress
        for i in range(int(num_frames)):
            # Simulate work
            await asyncio.sleep(0.01)
        
        logger.info(f"Generated {num_frames} frames for task {task.task_id}")
    
    async def _apply_pose_conditioning(self, task: RenderTask):
        """Apply pose conditioning to video frames."""
        logger.info(f"Applying pose conditioning for task {task.task_id}")
        
        # In production, this would use ControlNet or similar
        # For MVP, simulate pose conditioning
        
        await asyncio.sleep(0.5)  # Simulate work
        
        logger.info(f"Applied pose conditioning for task {task.task_id}")
    
    async def _upscale_video(self, task: RenderTask):
        """Upscale video."""
        logger.info(f"Upscaling video for task {task.task_id}")
        
        # In production, this would use Real-ESRGAN or similar
        # For MVP, simulate upscaling
        
        await asyncio.sleep(1.0)  # Simulate work
        
        logger.info(f"Upscaled video for task {task.task_id}")
    
    async def _post_process_video(self, task: RenderTask):
        """Apply post-processing to video."""
        logger.info(f"Applying post-processing for task {task.task_id}")
        
        # Apply color correction if enabled
        if task.config.enable_color_correction:
            await self._apply_color_correction(task)
        
        # Apply stabilization if enabled
        if task.config.enable_stabilization:
            await self._apply_stabilization(task)
        
        # Apply background removal if enabled
        if task.config.enable_background_removal:
            await self._apply_background_removal(task)
        
        logger.info(f"Applied post-processing for task {task.task_id}")
    
    async def _apply_color_correction(self, task: RenderTask):
        """Apply color correction to video."""
        await asyncio.sleep(0.2)  # Simulate work
    
    async def _apply_stabilization(self, task: RenderTask):
        """Apply video stabilization."""
        await asyncio.sleep(0.3)  # Simulate work
    
    async def _apply_background_removal(self, task: RenderTask):
        """Apply background removal."""
        await asyncio.sleep(0.4)  # Simulate work
    
    async def _load_video_for_upscaling(self, task: RenderTask):
        """Load video for upscaling."""
        logger.info(f"Loading video for upscaling: {task.input_video_path}")
        await asyncio.sleep(0.5)  # Simulate work
    
    async def _apply_upscaling(self, task: RenderTask):
        """Apply upscaling to video."""
        logger.info(f"Applying upscaling with factor {task.upscale_factor}")
        await asyncio.sleep(1.0)  # Simulate work
    
    async def _save_upscaled_video(self, task: RenderTask):
        """Save upscaled video."""
        logger.info(f"Saving upscaled video")
        await asyncio.sleep(0.5)  # Simulate work
    
    def get_task_status(self, task_id: str) -> Optional[RenderTask]:
        """Get the status of a render task."""
        return self.tasks.get(task_id)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Check Redis connection
            self.redis_client.ping()
            redis_status = "healthy"
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            redis_status = "unhealthy"
        
        # Check models directory
        models_status = "healthy" if settings.models_dir.exists() else "unhealthy"
        
        # Check output directory
        output_status = "healthy" if settings.output_dir.exists() else "unhealthy"
        
        return {
            "status": "healthy" if all([
                redis_status == "healthy",
                models_status == "healthy",
                output_status == "healthy"
            ]) else "unhealthy",
            "redis": redis_status,
            "models": models_status,
            "output": output_status,
            "active_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PROCESSING]),
            "total_tasks": len(self.tasks)
        }
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks."""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if task.completed_at and task.completed_at.timestamp() < cutoff_time:
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        if tasks_to_remove:
            logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")