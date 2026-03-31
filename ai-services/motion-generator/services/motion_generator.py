import os
import json
import asyncio
import uuid
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import traceback

import numpy as np
from loguru import logger

from config import settings


@dataclass
class MotionConfig:
    """Configuration for motion generation."""
    fps: int = 24
    resolution: List[int] = field(default_factory=lambda: [512, 512])
    smoothing: bool = True
    smoothing_window: int = 5
    interpolation: str = "cubic"
    use_gpu: bool = True
    motion_intensity: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fps": self.fps,
            "resolution": self.resolution,
            "smoothing": self.smoothing,
            "smoothing_window": self.smoothing_window,
            "interpolation": self.interpolation,
            "use_gpu": self.use_gpu,
            "motion_intensity": self.motion_intensity
        }


@dataclass
class MotionTask:
    """Represents a motion generation task."""
    task_id: str
    user_id: str
    avatar_id: str
    action_prompt: str
    duration_sec: int = 10
    motion_preset: str = "idle_talking"
    video_path: Optional[str] = None
    task_type: str = "motion_generation"
    config: Optional[MotionConfig] = None
    
    # Task status fields
    status: str = "pending"  # pending, processing, completed, failed
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    pose_data_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.config is None:
            self.config = MotionConfig()


class MotionGenerator:
    """Main motion generation service."""
    
    def __init__(self):
        """Initialize the motion generator."""
        self.tasks: Dict[str, MotionTask] = {}
        self.initialized = False
        self.models_loaded = False
        
        try:
            self._initialize()
            self.initialized = True
            logger.info("Motion generator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize motion generator: {e}")
            raise
    
    def _initialize(self):
        """Initialize models and components."""
        # Create necessary directories
        directories = [
            settings.output_dir,
            settings.input_dir,
            settings.models_dir,
            settings.log_file.parent,
            settings.smpl_model_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # In production, this would load actual models
        # For MVP, we'll simulate model loading
        logger.info(f"Initializing motion generator with model: {settings.motion_model}")
        logger.info(f"Pose estimation model: {settings.pose_estimation_model}")
        logger.info(f"Using GPU: {settings.use_gpu}")
        
        # Simulate model loading
        time.sleep(1)  # Simulate loading time
        self.models_loaded = True
        
        # Cleanup old tasks
        self.cleanup_old_tasks()
    
    async def generate_motion_async(self, task: MotionTask):
        """Generate motion asynchronously."""
        try:
            task.status = "processing"
            task.started_at = datetime.utcnow()
            task.progress = 0.1
            
            logger.info(f"Starting motion generation for task {task.task_id}")
            logger.info(f"Action prompt: {task.action_prompt}")
            logger.info(f"Duration: {task.duration_sec} seconds")
            
            # Simulate motion generation process
            steps = 10
            for i in range(steps):
                await asyncio.sleep(0.5)  # Simulate processing
                task.progress = 0.1 + (i * 0.8 / steps)
                
                # Update task status
                self.tasks[task.task_id] = task
            
            # Generate mock output
            output_dir = settings.output_dir / f"motion_{task.task_id}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create mock pose data
            pose_data = self._generate_mock_pose_data(task)
            pose_file = output_dir / "pose_data.json"
            with open(pose_file, 'w') as f:
                json.dump(pose_data, f, indent=2)
            
            # Create mock output files
            output_files = [
                "motion_params.npy",
                "keypoints.json",
                "timeline.csv"
            ]
            
            for filename in output_files:
                file_path = output_dir / filename
                with open(file_path, 'w') as f:
                    f.write(f"Mock data for {filename}")
            
            task.output_path = str(output_dir)
            task.pose_data_path = str(pose_file)
            task.progress = 1.0
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            
            logger.info(f"Motion generation completed for task {task.task_id}")
            logger.info(f"Output saved to: {task.output_path}")
            
        except Exception as e:
            logger.error(f"Motion generation failed for task {task.task_id}: {e}")
            logger.error(traceback.format_exc())
            
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
        
        # Update task in storage
        self.tasks[task.task_id] = task
    
    async def extract_pose_async(self, task: MotionTask):
        """Extract pose from video asynchronously."""
        try:
            task.status = "processing"
            task.started_at = datetime.utcnow()
            task.progress = 0.1
            
            logger.info(f"Starting pose extraction for task {task.task_id}")
            
            if not task.video_path:
                raise ValueError("Video path is required for pose extraction")
            
            # Check if video file exists
            video_path = Path(task.video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"Video file not found: {task.video_path}")
            
            # Simulate pose extraction process
            steps = 8
            for i in range(steps):
                await asyncio.sleep(0.5)  # Simulate processing
                task.progress = 0.1 + (i * 0.8 / steps)
                self.tasks[task.task_id] = task
            
            # Generate mock pose data
            pose_data = self._generate_mock_pose_data(task)
            
            output_dir = settings.output_dir / f"pose_{task.task_id}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            pose_file = output_dir / "extracted_pose.json"
            with open(pose_file, 'w') as f:
                json.dump(pose_data, f, indent=2)
            
            # Create summary file
            summary_file = output_dir / "extraction_summary.txt"
            with open(summary_file, 'w') as f:
                f.write(f"Pose extraction completed for task {task.task_id}\n")
                f.write(f"Video: {task.video_path}\n")
                f.write(f"Frames processed: 240\n")
                f.write(f"Keypoints detected: 17 per frame\n")
                f.write(f"Processing time: 5.2 seconds\n")
            
            task.output_path = str(output_dir)
            task.pose_data_path = str(pose_file)
            task.progress = 1.0
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            
            logger.info(f"Pose extraction completed for task {task.task_id}")
            
        except Exception as e:
            logger.error(f"Pose extraction failed for task {task.task_id}: {e}")
            logger.error(traceback.format_exc())
            
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
        
        self.tasks[task.task_id] = task
    
    def _generate_mock_pose_data(self, task: MotionTask) -> Dict[str, Any]:
        """Generate mock pose data for testing."""
        frames = task.duration_sec * settings.fps
        keypoints = 17
        
        pose_data = {
            "task_id": task.task_id,
            "user_id": task.user_id,
            "avatar_id": task.avatar_id,
            "action_prompt": task.action_prompt,
            "duration_sec": task.duration_sec,
            "fps": settings.fps,
            "total_frames": frames,
            "keypoints_per_frame": keypoints,
            "motion_preset": task.motion_preset,
            "timestamp": datetime.utcnow().isoformat(),
            "pose_sequence": []
        }
        
        # Generate mock pose sequence
        for frame in range(min(10, frames)):  # Limit to first 10 frames for demo
            frame_data = {
                "frame": frame,
                "time": frame / settings.fps,
                "keypoints": []
            }
            
            for kp in range(keypoints):
                # Generate realistic mock keypoint positions
                x = np.sin(frame * 0.1 + kp * 0.5) * 0.5 + 0.5
                y = np.cos(frame * 0.1 + kp * 0.3) * 0.5 + 0.5
                confidence = 0.8 + np.random.random() * 0.2
                
                frame_data["keypoints"].append({
                    "id": kp,
                    "x": float(x),
                    "y": float(y),
                    "confidence": float(confidence)
                })
            
            pose_data["pose_sequence"].append(frame_data)
        
        return pose_data
    
    def get_task_status(self, task_id: str) -> Optional[MotionTask]:
        """Get the status of a task."""
        return self.tasks.get(task_id)
    
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
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the motion generator."""
        health_status = {
            "status": "healthy",
            "initialized": self.initialized,
            "models_loaded": self.models_loaded,
            "active_tasks": len([t for t in self.tasks.values() if t.status in ["pending", "processing"]]),
            "total_tasks": len(self.tasks),
            "disk_space": self._check_disk_space(),
            "memory_usage": self._get_memory_usage(),
            "gpu_available": settings.use_gpu
        }
        
        # Check if critical components are working
        if not self.initialized:
            health_status["status"] = "unhealthy"
            health_status["error"] = "Motion generator not initialized"
        
        return health_status
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        # For MVP, return mock data
        return {
            "data_dir": str(settings.data_dir),
            "available_gb": 50.2,
            "total_gb": 100.0,
            "used_percent": 49.8
        }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information."""
        # For MVP, return mock data
        return {
            "used_mb": 512,
            "total_mb": 8192,
            "used_percent": 6.25
        }


# Create __init__.py for services module
__all__ = ["MotionGenerator", "MotionConfig", "MotionTask"]