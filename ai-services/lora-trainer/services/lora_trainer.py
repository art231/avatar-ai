import os
import uuid
import json
import shutil
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from loguru import logger
import torch
import torch.nn as nn
from PIL import Image
import numpy as np
import redis
from pydantic import BaseModel, Field

from config import settings

class TrainingConfig(BaseModel):
    """Configuration for LoRA training."""
    base_model: str = Field(default=settings.base_model, description="Base model for training")
    lora_rank: int = Field(default=settings.lora_rank, description="LoRA rank")
    lora_alpha: int = Field(default=settings.lora_alpha, description="LoRA alpha")
    learning_rate: float = Field(default=settings.learning_rate, description="Learning rate")
    num_train_epochs: int = Field(default=settings.num_train_epochs, description="Number of training epochs")
    train_batch_size: int = Field(default=settings.train_batch_size, description="Training batch size")
    gradient_accumulation_steps: int = Field(default=settings.gradient_accumulation_steps, description="Gradient accumulation steps")
    mixed_precision: str = Field(default=settings.mixed_precision, description="Mixed precision (fp16, bf16, fp32)")
    resolution: int = Field(default=settings.resolution, description="Training resolution")
    output_dir: Path = Field(default=settings.output_dir, description="Output directory for trained LoRA")

class TrainingTask(BaseModel):
    """LoRA training task."""
    task_id: str
    user_id: str
    avatar_id: str
    image_paths: List[str]
    config: TrainingConfig
    status: str = "pending"  # pending, processing, completed, failed
    progress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = {}

class LoraTrainer:
    """LoRA trainer service for creating personalized avatar models."""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"
        self.redis_client = None
        self.logger = logger
        
        # Initialize Redis client for task queue
        self._init_redis()
        
        # Initialize model components
        self._init_components()
    
    def _init_redis(self):
        """Initialize Redis client for task queue."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            self.logger.info(f"Redis connected successfully to {settings.redis_host}:{settings.redis_port}")
        except Exception as e:
            self.logger.warning(f"Failed to connect to Redis: {e}. Task queue will be in-memory only.")
            self.redis_client = None
    
    def _init_components(self):
        """Initialize model components."""
        try:
            self.logger.info(f"Initializing LoRA trainer on device: {self.device}")
            
            # Check CUDA availability
            if self.device == "cuda":
                self.logger.info(f"CUDA available: {torch.cuda.is_available()}")
                self.logger.info(f"CUDA device: {torch.cuda.get_device_name(0)}")
                self.logger.info(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
            
            # Note: In production, we would load Kohya_ss or similar library here
            # For MVP, we'll create a simplified implementation
            
            self.logger.info("LoRA trainer initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LoRA trainer: {e}")
            raise
    
    def validate_images(self, image_paths: List[str]) -> Tuple[bool, str, List[str]]:
        """Validate images for training."""
        valid_paths = []
        
        if not image_paths:
            return False, "No images provided", []
        
        if len(image_paths) < settings.min_images:
            return False, f"Too few images: {len(image_paths)} < {settings.min_images}", []
        
        if len(image_paths) > settings.max_images:
            return False, f"Too many images: {len(image_paths)} > {settings.max_images}", []
        
        for image_path in image_paths:
            path = Path(image_path)
            
            # Check file exists
            if not path.exists():
                self.logger.warning(f"Image not found: {image_path}")
                continue
            
            # Check file extension
            if path.suffix.lower() not in settings.supported_image_formats:
                self.logger.warning(f"Unsupported image format: {path.suffix}")
                continue
            
            # Check file size
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > settings.max_image_size_mb:
                self.logger.warning(f"Image too large: {file_size_mb:.1f}MB > {settings.max_image_size_mb}MB")
                continue
            
            # Try to open image
            try:
                with Image.open(path) as img:
                    img.verify()  # Verify it's a valid image
                
                # Check resolution
                with Image.open(path) as img:
                    width, height = img.size
                    if width < settings.resolution or height < settings.resolution:
                        self.logger.warning(f"Image too small: {width}x{height} < {settings.resolution}")
                        continue
                
                valid_paths.append(str(path))
                
            except Exception as e:
                self.logger.warning(f"Invalid image file {image_path}: {e}")
                continue
        
        if len(valid_paths) < settings.min_images:
            return False, f"Only {len(valid_paths)} valid images found, need at least {settings.min_images}", []
        
        return True, f"Found {len(valid_paths)} valid images", valid_paths
    
    def prepare_training_data(self, image_paths: List[str], output_dir: Path) -> Tuple[bool, str, Optional[Path]]:
        """Prepare training data from images."""
        try:
            # Create training directory
            training_dir = output_dir / "training_data"
            training_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy and preprocess images
            for i, image_path in enumerate(image_paths):
                src_path = Path(image_path)
                dst_path = training_dir / f"image_{i:04d}{src_path.suffix}"
                
                # Copy image
                shutil.copy2(src_path, dst_path)
                
                # Optional: Resize and normalize
                # In production, we would use more sophisticated preprocessing
                
            # Create metadata file
            metadata = {
                "total_images": len(image_paths),
                "image_paths": [str(p) for p in image_paths],
                "prepared_at": datetime.utcnow().isoformat(),
                "resolution": settings.resolution
            }
            
            metadata_path = training_dir / "metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            return True, "Training data prepared successfully", training_dir
            
        except Exception as e:
            self.logger.error(f"Failed to prepare training data: {e}")
            return False, f"Failed to prepare training data: {str(e)}", None
    
    def train_lora_simplified(self, training_dir: Path, config: TrainingConfig) -> Tuple[bool, str, Optional[Path]]:
        """
        Simplified LoRA training implementation.
        
        Note: In production, this would integrate with Kohya_ss or similar library.
        For MVP, we create a mock implementation that simulates training.
        """
        try:
            self.logger.info(f"Starting LoRA training with config: {config.dict()}")
            
            # Create output directory
            lora_output_dir = config.output_dir / f"lora_{uuid.uuid4()}"
            lora_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Simulate training process
            total_steps = config.num_train_epochs * 10  # Simulate 10 steps per epoch
            for step in range(total_steps):
                # Simulate training progress
                progress = (step + 1) / total_steps
                
                # Simulate GPU memory usage
                if self.device == "cuda":
                    memory_allocated = torch.cuda.memory_allocated() / 1e9
                    memory_reserved = torch.cuda.memory_reserved() / 1e9
                    
                    if step % 10 == 0:
                        self.logger.info(f"Training step {step+1}/{total_steps}, "
                                       f"progress: {progress:.1%}, "
                                       f"GPU memory: {memory_allocated:.2f}/{memory_reserved:.2f} GB")
                
                # Simulate training time
                asyncio.sleep(0.1)  # In real implementation, this would be actual training
            
            # Create mock LoRA file
            lora_path = lora_output_dir / "lora_model.safetensors"
            
            # In production, this would be the actual trained LoRA weights
            # For MVP, we create a placeholder file
            mock_lora_data = {
                "metadata": {
                    "base_model": config.base_model,
                    "lora_rank": config.lora_rank,
                    "lora_alpha": config.lora_alpha,
                    "learning_rate": config.learning_rate,
                    "trained_at": datetime.utcnow().isoformat(),
                    "training_steps": total_steps,
                    "resolution": config.resolution
                },
                "weights": {}  # Empty for mock
            }
            
            # Save as JSON (in production would be safetensors)
            with open(lora_path, "w") as f:
                json.dump(mock_lora_data, f, indent=2)
            
            # Also create a proper safetensors placeholder
            safetensors_path = lora_output_dir / "lora_model_real.safetensors"
            with open(safetensors_path, "wb") as f:
                f.write(b"SAFETENSORS placeholder - real implementation would have actual weights")
            
            self.logger.info(f"LoRA training completed: {lora_path}")
            
            return True, "LoRA training completed successfully", lora_output_dir
            
        except Exception as e:
            self.logger.error(f"LoRA training failed: {e}")
            return False, f"LoRA training failed: {str(e)}", None
    
    async def train_lora_async(self, task: TrainingTask) -> TrainingTask:
        """Asynchronous LoRA training."""
        try:
            task.status = "processing"
            task.started_at = datetime.utcnow()
            
            # Update task in Redis if available
            await self._update_task_status(task)
            
            # Step 1: Validate images
            self.logger.info(f"Validating {len(task.image_paths)} images for task {task.task_id}")
            is_valid, message, valid_paths = self.validate_images(task.image_paths)
            
            if not is_valid:
                task.status = "failed"
                task.error_message = message
                task.completed_at = datetime.utcnow()
                await self._update_task_status(task)
                return task
            
            # Step 2: Prepare training data
            self.logger.info(f"Preparing training data for task {task.task_id}")
            success, message, training_dir = self.prepare_training_data(
                valid_paths, 
                Path(settings.data_dir) / "training" / task.task_id
            )
            
            if not success:
                task.status = "failed"
                task.error_message = message
                task.completed_at = datetime.utcnow()
                await self._update_task_status(task)
                return task
            
            # Step 3: Train LoRA
            self.logger.info(f"Starting LoRA training for task {task.task_id}")
            success, message, output_dir = self.train_lora_simplified(training_dir, task.config)
            
            if not success:
                task.status = "failed"
                task.error_message = message
                task.completed_at = datetime.utcnow()
                await self._update_task_status(task)
                return task
            
            # Step 4: Update task with results
            task.status = "completed"
            task.progress = 1.0
            task.completed_at = datetime.utcnow()
            task.output_path = str(output_dir)
            task.metadata.update({
                "training_dir": str(training_dir),
                "output_dir": str(output_dir),
                "valid_images": len(valid_paths),
                "training_time_seconds": (task.completed_at - task.started_at).total_seconds()
            })
            
            await self._update_task_status(task)
            self.logger.info(f"Task {task.task_id} completed successfully")
            
            return task
            
        except Exception as e:
            self.logger.error(f"Error in train_lora_async for task {task.task_id}: {e}")
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await self._update_task_status(task)
            return task
    
    async def _update_task_status(self, task: TrainingTask):
        """Update task status in Redis."""
        if self.redis_client is None:
            return
        
        try:
            task_key = f"lora_task:{task.task_id}"
            task_data = task.dict()
            task_data["created_at"] = task_data["created_at"].isoformat()
            if task_data["started_at"]:
                task_data["started_at"] = task_data["started_at"].isoformat()
            if task_data["completed_at"]:
                task_data["completed_at"] = task_data["completed_at"].isoformat()
            
            self.redis_client.setex(
                task_key,
                settings.task_timeout_seconds,
                json.dumps(task_data)
            )
            
            # Also publish to task queue for real-time updates
            self.redis_client.publish(
                f"lora_task_updates:{task.task_id}",
                json.dumps({"status": task.status, "progress": task.progress})
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to update task status in Redis: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[TrainingTask]:
        """Get task status from Redis."""
        if self.redis_client is None:
            return None
        
        try:
            task_key = f"lora_task:{task_id}"
            task_data = self.redis_client.get(task_key)
            
            if task_data:
                data = json.loads(task_data)
                # Convert string dates back to datetime
                for date_field in ["created_at", "started_at", "completed_at"]:
                    if data.get(date_field):
                        data[date_field] = datetime.fromisoformat(data[date_field])
                
                return TrainingTask(**data)
            
        except Exception as e:
            self.logger.error(f"Failed to get task status: {e}")
        
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of LoRA trainer."""
        health_status = {
            "service": "lora-trainer",
            "status": "healthy",
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "redis_connected": self.redis_client is not None and self.redis_client.ping(),
            "models_loaded": True,  # Simplified for MVP
            "gpu_memory_available": None
        }
        
        if self.device == "cuda" and torch.cuda.is_available():
            health_status["gpu_memory_available"] = {
                "allocated_gb": torch.cuda.memory_allocated() / 1e9,
                "reserved_gb": torch.cuda.memory_reserved() / 1e9,
                "total_gb": torch.cuda.get_device_properties(0).total_memory / 1e9
            }
        
        return health_status
    
    def cleanup_old_tasks(self, older_than_hours: int = 24):
        """Clean up old training tasks and data."""
        try:
            if self.redis_client is None:
                return
            
            # Find old task keys
            task_keys = self.redis_client.keys("lora_task:*")
            deleted_count = 0
            
            for task_key in task_keys:
                task_data = self.redis_client.get(task_key)
                if task_data:
                    data = json.loads(task_data)
                    created_at = datetime.fromisoformat(data["created_at"])
                    
                    age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
                    
                    if age_hours > older_than_hours:
                        self.redis_client.delete(task_key)
                        deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} old tasks")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old tasks: {e}")