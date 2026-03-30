"""
Complete Training Pipeline for AvatarAI.
This orchestrates the entire training process from data preparation to model deployment.
"""

import asyncio
import json
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
import httpx
from pydantic import BaseModel, Field

from config import settings


class PipelineStage(BaseModel):
    """Pipeline stage configuration."""
    name: str
    service: str
    endpoint: str
    timeout: int = 300
    retry_count: int = 3
    depends_on: List[str] = []
    config: Dict[str, Any] = {}


class TrainingPipeline(BaseModel):
    """Complete training pipeline configuration."""
    pipeline_id: str
    user_id: str
    avatar_id: str
    image_paths: List[str]
    voice_sample_path: Optional[str] = None
    stages: List[PipelineStage] = []
    current_stage: str = "initializing"
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    results: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class CompletePipelineService:
    """Complete training pipeline orchestrator."""
    
    def __init__(self):
        self.logger = logger
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Define pipeline stages
        self.default_stages = [
            PipelineStage(
                name="data_validation",
                service="media-analyzer",
                endpoint="/api/v1/validate-images",
                config={"min_images": 10, "max_images": 50}
            ),
            PipelineStage(
                name="face_analysis",
                service="media-analyzer",
                endpoint="/api/v1/analyze-faces",
                depends_on=["data_validation"]
            ),
            PipelineStage(
                name="audio_preprocessing",
                service="audio-preprocessor",
                endpoint="/api/v1/preprocess-audio",
                depends_on=["data_validation"],
                config={"target_sr": 16000, "normalize": True}
            ),
            PipelineStage(
                name="lora_training",
                service="lora-trainer",
                endpoint="/api/v1/train-lora",
                depends_on=["face_analysis"],
                timeout=3600,  # 1 hour
                config={
                    "base_model": "runwayml/stable-diffusion-v1-5",
                    "resolution": 512,
                    "epochs": 10,
                    "batch_size": 2
                }
            ),
            PipelineStage(
                name="voice_training",
                service="xtts-service",
                endpoint="/api/v1/train-voice",
                depends_on=["audio_preprocessing"],
                timeout=1800,  # 30 minutes
                config={"language": "en", "speaker_wav": None}
            ),
            PipelineStage(
                name="model_integration",
                service="training-pipeline",
                endpoint="/api/v1/integrate-models",
                depends_on=["lora_training", "voice_training"],
                config={"merge_models": True}
            ),
            PipelineStage(
                name="quality_check",
                service="media-analyzer",
                endpoint="/api/v1/quality-check",
                depends_on=["model_integration"],
                config={"threshold": 0.8}
            ),
            PipelineStage(
                name="deployment",
                service="backend",
                endpoint="/api/v1/avatars/{avatar_id}/deploy",
                depends_on=["quality_check"],
                config={"make_active": True}
            )
        ]
    
    async def create_pipeline(self, user_id: str, avatar_id: str, 
                            image_paths: List[str], voice_sample_path: Optional[str] = None) -> TrainingPipeline:
        """Create a new training pipeline."""
        pipeline_id = str(uuid.uuid4())
        
        pipeline = TrainingPipeline(
            pipeline_id=pipeline_id,
            user_id=user_id,
            avatar_id=avatar_id,
            image_paths=image_paths,
            voice_sample_path=voice_sample_path,
            stages=self.default_stages,
            metadata={
                "total_stages": len(self.default_stages),
                "image_count": len(image_paths),
                "has_voice": voice_sample_path is not None
            }
        )
        
        self.logger.info(f"Created pipeline {pipeline_id} for avatar {avatar_id}")
        return pipeline
    
    async def execute_stage(self, pipeline: TrainingPipeline, stage: PipelineStage) -> bool:
        """Execute a single pipeline stage."""
        try:
            self.logger.info(f"Executing stage {stage.name} for pipeline {pipeline.pipeline_id}")
            
            # Update pipeline status
            pipeline.current_stage = stage.name
            await self._update_pipeline_status(pipeline)
            
            # Prepare request data
            request_data = {
                "pipeline_id": pipeline.pipeline_id,
                "avatar_id": pipeline.avatar_id,
                "user_id": pipeline.user_id,
                "config": stage.config
            }
            
            # Add stage-specific data
            if stage.name == "data_validation":
                request_data["image_paths"] = pipeline.image_paths
            elif stage.name == "face_analysis":
                request_data["image_paths"] = pipeline.image_paths
            elif stage.name == "audio_preprocessing" and pipeline.voice_sample_path:
                request_data["audio_path"] = pipeline.voice_sample_path
            elif stage.name == "lora_training":
                request_data["image_paths"] = pipeline.image_paths
                if "face_analysis" in pipeline.results:
                    request_data["face_data"] = pipeline.results["face_analysis"]
            elif stage.name == "voice_training" and pipeline.voice_sample_path:
                request_data["audio_path"] = pipeline.voice_sample_path
            elif stage.name == "deployment":
                request_data["lora_model"] = pipeline.results.get("lora_training", {}).get("model_path")
                request_data["voice_model"] = pipeline.results.get("voice_training", {}).get("model_path")
            
            # Make HTTP request to the service
            service_url = f"http://{stage.service}:{settings.service_port}{stage.endpoint}"
            
            # Replace placeholders in endpoint
            service_url = service_url.replace("{avatar_id}", pipeline.avatar_id)
            
            self.logger.info(f"Calling {service_url} for stage {stage.name}")
            
            response = await self.http_client.post(
                service_url,
                json=request_data,
                timeout=stage.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                pipeline.results[stage.name] = result
                
                # Update progress
                stage_index = next(i for i, s in enumerate(pipeline.stages) if s.name == stage.name)
                pipeline.progress = (stage_index + 1) / len(pipeline.stages)
                
                self.logger.info(f"Stage {stage.name} completed successfully")
                return True
            else:
                error_msg = f"Stage {stage.name} failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                pipeline.error_message = error_msg
                return False
                
        except Exception as e:
            error_msg = f"Stage {stage.name} failed with exception: {str(e)}"
            self.logger.error(error_msg)
            pipeline.error_message = error_msg
            return False
    
    async def execute_pipeline(self, pipeline: TrainingPipeline) -> TrainingPipeline:
        """Execute the complete training pipeline."""
        try:
            pipeline.status = "running"
            pipeline.started_at = datetime.utcnow()
            await self._update_pipeline_status(pipeline)
            
            # Track completed stages
            completed_stages = set()
            
            # Execute stages in dependency order
            while len(completed_stages) < len(pipeline.stages):
                # Find stages whose dependencies are satisfied
                for stage in pipeline.stages:
                    if stage.name in completed_stages:
                        continue
                    
                    # Check if all dependencies are satisfied
                    dependencies_satisfied = all(
                        dep in completed_stages for dep in stage.depends_on
                    )
                    
                    if dependencies_satisfied:
                        # Execute stage
                        success = await self.execute_stage(pipeline, stage)
                        
                        if success:
                            completed_stages.add(stage.name)
                            
                            # Update pipeline status
                            await self._update_pipeline_status(pipeline)
                        else:
                            # Stage failed, abort pipeline
                            pipeline.status = "failed"
                            pipeline.completed_at = datetime.utcnow()
                            await self._update_pipeline_status(pipeline)
                            return pipeline
                        
                        # Break to re-evaluate dependencies
                        break
                else:
                    # No stage ready to execute (should not happen in valid DAG)
                    self.logger.warning("No stage ready to execute, checking for circular dependencies")
                    await asyncio.sleep(1)
            
            # All stages completed successfully
            pipeline.status = "completed"
            pipeline.progress = 1.0
            pipeline.completed_at = datetime.utcnow()
            
            # Generate final results
            pipeline.metadata.update({
                "total_time_seconds": (pipeline.completed_at - pipeline.started_at).total_seconds(),
                "completed_stages": list(completed_stages),
                "final_model_ready": True
            })
            
            await self._update_pipeline_status(pipeline)
            self.logger.info(f"Pipeline {pipeline.pipeline_id} completed successfully")
            
            return pipeline
            
        except Exception as e:
            error_msg = f"Pipeline execution failed: {str(e)}"
            self.logger.error(error_msg)
            pipeline.status = "failed"
            pipeline.error_message = error_msg
            pipeline.completed_at = datetime.utcnow()
            await self._update_pipeline_status(pipeline)
            return pipeline
    
    async def _update_pipeline_status(self, pipeline: TrainingPipeline):
        """Update pipeline status in database/Redis."""
        # In production, this would update a database or Redis
        # For now, just log the status
        self.logger.info(
            f"Pipeline {pipeline.pipeline_id} - "
            f"Status: {pipeline.status}, "
            f"Stage: {pipeline.current_stage}, "
            f"Progress: {pipeline.progress:.1%}"
        )
        
        # Here you would add Redis/database update logic
        # Example:
        # if self.redis_client:
        #     pipeline_key = f"pipeline:{pipeline.pipeline_id}"
        #     self.redis_client.setex(
        #         pipeline_key,
        #         86400,  # 24 hours
        #         pipeline.json()
        #     )
    
    async def get_pipeline_status(self, pipeline_id: str) -> Optional[TrainingPipeline]:
        """Get pipeline status by ID."""
        # In production, this would query database/Redis
        # For now, return None (implement as needed)
        return None
    
    async def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Cancel a running pipeline."""
        # In production, this would send cancellation signals to all services
        # For now, just log
        self.logger.info(f"Cancelling pipeline {pipeline_id}")
        return True
    
    async def cleanup_pipeline(self, pipeline_id: str):
        """Clean up pipeline resources."""
        # In production, this would clean up temporary files, models, etc.
        self.logger.info(f"Cleaning up pipeline {pipeline_id}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of pipeline service."""
        return {
            "service": "training-pipeline",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "stages_configured": len(self.default_stages),
            "services": list(set(stage.service for stage in self.default_stages))
        }
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()


# Example usage
async def main():
    """Example of using the complete pipeline."""
    pipeline_service = CompletePipelineService()
    
    # Create a pipeline
    image_paths = ["/data/images/photo1.jpg", "/data/images/photo2.jpg"]
    voice_sample = "/data/audio/voice.wav"
    
    pipeline = await pipeline_service.create_pipeline(
        user_id="user123",
        avatar_id="avatar456",
        image_paths=image_paths,
        voice_sample_path=voice_sample
    )
    
    # Execute the pipeline
    result = await pipeline_service.execute_pipeline(pipeline)
    
    # Check result
    if result.status == "completed":
        print(f"Pipeline completed successfully in {result.metadata['total_time_seconds']} seconds")
        print(f"Results: {json.dumps(result.results, indent=2)}")
    else:
        print(f"Pipeline failed: {result.error_message}")
    
    # Clean up
    await pipeline_service.close()


if __name__ == "__main__":
    asyncio.run(main())