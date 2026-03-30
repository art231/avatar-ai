import os
import uuid
import json
import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import redis
from loguru import logger


class TrainingStage(str, Enum):
    """Training pipeline stages."""
    PENDING = "pending"
    DATA_PREPARATION = "data_preparation"
    FACE_ANALYSIS = "face_analysis"
    VOICE_ANALYSIS = "voice_analysis"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    COMPLETED = "completed"
    FAILED = "failed"


class TrainingStatus(str, Enum):
    """Training task status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TrainingConfig:
    """Training configuration."""
    base_model: str = "stable-diffusion-xl-base-1.0"
    lora_rank: int = 32
    lora_alpha: int = 16
    learning_rate: float = 1e-4
    num_train_epochs: int = 10
    train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    mixed_precision: str = "fp16"
    resolution: int = 512
    voice_model: str = "xtts-v2"
    lipsync_model: str = "muse_talk"
    quality_preset: str = "high"


@dataclass
class TrainingTask:
    """Training task data."""
    task_id: str
    user_id: str
    avatar_id: str
    image_paths: List[str]
    voice_sample_path: str
    config: TrainingConfig
    status: TrainingStatus = TrainingStatus.PENDING
    stage: TrainingStage = TrainingStage.PENDING
    progress: float = 0.0
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class TrainingPipeline:
    """Training pipeline orchestrator."""
    
    def __init__(self):
        self.logger = logger
        self.redis_client = None
        self.ai_services = {
            "audio_preprocessor": "http://audio-preprocessor:5001",
            "media_analyzer": "http://media-analyzer:5002",
            "xtts_service": "http://xtts-service:5003",
            "lora_trainer": "http://lora-trainer:5004",
            "lipsync_service": "http://lipsync-service:5006"
        }
        
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis client."""
        try:
            redis_host = os.getenv("REDIS_HOST", "redis")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            self.logger.info(f"Redis connected to {redis_host}:{redis_port}")
        except Exception as e:
            self.logger.warning(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def start_training(self, task: TrainingTask) -> TrainingTask:
        """Start training pipeline."""
        try:
            task.status = TrainingStatus.PROCESSING
            task.started_at = datetime.utcnow()
            await self._update_task(task)
            
            self.logger.info(f"Starting training pipeline for task {task.task_id}")
            
            # Stage 1: Data Preparation
            task.stage = TrainingStage.DATA_PREPARATION
            task.progress = 0.1
            await self._update_task(task)
            
            prepared_data = await self._prepare_data(task)
            task.metadata["prepared_data"] = prepared_data
            task.progress = 0.2
            await self._update_task(task)
            
            # Stage 2: Face Analysis
            task.stage = TrainingStage.FACE_ANALYSIS
            await self._update_task(task)
            
            face_analysis = await self._analyze_faces(task, prepared_data)
            task.metadata["face_analysis"] = face_analysis
            task.progress = 0.4
            await self._update_task(task)
            
            # Stage 3: Voice Analysis
            task.stage = TrainingStage.VOICE_ANALYSIS
            await self._update_task(task)
            
            voice_analysis = await self._analyze_voice(task, prepared_data)
            task.metadata["voice_analysis"] = voice_analysis
            task.progress = 0.6
            await self._update_task(task)
            
            # Stage 4: Model Training
            task.stage = TrainingStage.MODEL_TRAINING
            await self._update_task(task)
            
            trained_model = await self._train_model(task, prepared_data, face_analysis, voice_analysis)
            task.metadata["trained_model"] = trained_model
            task.progress = 0.8
            await self._update_task(task)
            
            # Stage 5: Model Validation
            task.stage = TrainingStage.MODEL_VALIDATION
            await self._update_task(task)
            
            validation_result = await self._validate_model(task, trained_model)
            task.metadata["validation_result"] = validation_result
            task.progress = 0.9
            await self._update_task(task)
            
            # Complete
            task.stage = TrainingStage.COMPLETED
            task.status = TrainingStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.progress = 1.0
            task.output_path = trained_model.get("model_path", "")
            await self._update_task(task)
            
            self.logger.info(f"Training pipeline completed for task {task.task_id}")
            return task
            
        except Exception as e:
            self.logger.error(f"Training pipeline failed for task {task.task_id}: {e}")
            task.stage = TrainingStage.FAILED
            task.status = TrainingStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            await self._update_task(task)
            return task
    
    async def _prepare_data(self, task: TrainingTask) -> Dict[str, Any]:
        """Prepare training data."""
        self.logger.info(f"Preparing data for task {task.task_id}")
        
        # Preprocess audio
        audio_result = await self._call_ai_service(
            "audio_preprocessor",
            "POST",
            "/preprocess",
            data={"audio_path": task.voice_sample_path}
        )
        
        # Analyze images
        image_analyses = []
        for image_path in task.image_paths:
            analysis = await self._call_ai_service(
                "media_analyzer",
                "POST",
                "/analyze/image",
                data={"image_path": image_path}
            )
            image_analyses.append(analysis)
        
        return {
            "audio_preprocessed": audio_result,
            "image_analyses": image_analyses,
            "total_images": len(task.image_paths),
            "prepared_at": datetime.utcnow().isoformat()
        }
    
    async def _analyze_faces(self, task: TrainingTask, prepared_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze faces in images."""
        self.logger.info(f"Analyzing faces for task {task.task_id}")
        
        image_analyses = prepared_data["image_analyses"]
        face_analyses = []
        
        for image_analysis in image_analyses:
            face_analysis = await self._call_ai_service(
                "media_analyzer",
                "POST",
                "/analyze/face",
                data={"image_path": image_analysis.get("image_path", "")}
            )
            face_analyses.append(face_analysis)
        
        # Aggregate results
        return {
            "face_analyses": face_analyses,
            "average_confidence": sum(f.get("confidence", 0) for f in face_analyses) / len(face_analyses) if face_analyses else 0,
            "total_faces": len(face_analyses),
            "analysis_completed_at": datetime.utcnow().isoformat()
        }
    
    async def _analyze_voice(self, task: TrainingTask, prepared_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze voice sample."""
        self.logger.info(f"Analyzing voice for task {task.task_id}")
        
        audio_preprocessed = prepared_data["audio_preprocessed"]
        
        voice_analysis = await self._call_ai_service(
            "xtts_service",
            "POST",
            "/analyze",
            data={"audio_path": audio_preprocessed.get("processed_path", "")}
        )
        
        return {
            "voice_analysis": voice_analysis,
            "voice_characteristics": voice_analysis.get("characteristics", {}),
            "voice_embedding": voice_analysis.get("embedding", []),
            "analysis_completed_at": datetime.utcnow().isoformat()
        }
    
    async def _train_model(self, task: TrainingTask, prepared_data: Dict[str, Any],
                          face_analysis: Dict[str, Any], voice_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Train AI model."""
        self.logger.info(f"Training model for task {task.task_id}")
        
        training_config = {
            "task_id": task.task_id,
            "image_paths": task.image_paths,
            "voice_sample_path": task.voice_sample_path,
            "face_analysis": face_analysis,
            "voice_analysis": voice_analysis,
            "config": asdict(task.config)
        }
        
        training_result = await self._call_ai_service(
            "lora_trainer",
            "POST",
            "/train",
            data=training_config
        )
        
        return {
            "training_result": training_result,
            "model_path": training_result.get("model_path", ""),
            "training_metrics": training_result.get("metrics", {}),
            "training_completed_at": datetime.utcnow().isoformat()
        }
    
    async def _validate_model(self, task: TrainingTask, trained_model: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trained model."""
        self.logger.info(f"Validating model for task {task.task_id}")
        
        # Generate test samples
        test_samples = await self._generate_test_samples(task, trained_model)
        
        # Validate samples
        validation_results = await self._validate_samples(test_samples)
        
        return {
            "test_samples": test_samples,
            "validation_results": validation_results,
            "overall_quality": validation_results.get("quality_score", 0.0),
            "validation_passed": validation_results.get("passed", False),
            "validation_completed_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_test_samples(self, task: TrainingTask, trained_model: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test samples using trained model."""
        test_samples = []
        
        # Generate test audio
        test_texts = [
            "Hello, this is a test of the trained voice model.",
            "How are you doing today?",
            "The weather is nice today, isn't it?"
        ]
        
        for text in test_texts:
            audio_result = await self._call_ai_service(
                "xtts_service",
                "POST",
                "/generate",
                data={
                    "text": text,
                    "voice_model": trained_model.get("model_path", ""),
                    "output_format": "wav"
                }
            )
            
            test_samples.append({
                "text": text,
                "audio_result": audio_result,
                "generated_at": datetime.utcnow().isoformat()
            })
        
        return test_samples
    
    async def _validate_samples(self, test_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate generated samples."""
        # Simple validation - check if audio was generated
        valid_samples = []
        for sample in test_samples:
            audio_result = sample.get("audio_result", {})
            if audio_result.get("success", False):
                valid_samples.append(sample)
        
        quality_score = len(valid_samples) / len(test_samples) if test_samples else 0.0
        
        return {
            "total_samples": len(test_samples),
            "valid_samples": len(valid_samples),
            "quality_score": quality_score,
            "passed": quality_score >= 0.7,  # 70% threshold
            "validation_details": {
                "audio_generated": len(valid_samples),
                "audio_failed": len(test_samples) - len(valid_samples)
            }
        }
    
    async def _call_ai_service(self, service_name: str, method: str, endpoint: str,
                              data: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI service."""
        url = f"{self.ai_services[service_name]}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "POST":
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise Exception(f"Service {service_name} returned {response.status}: {error_text}")
                else:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise Exception(f"Service {service_name} returned {response.status}: {error_text}")
        except Exception as e:
            self.logger.error(f"Failed to call {service_name}: {e}")
            raise
    
    async def _update_task(self, task: TrainingTask):
        """Update task in Redis."""
        if self.redis_client is None:
            return
        
        try:
            task_key = f"training_task:{task.task_id}"
            task_data = asdict(task)
            
            # Convert datetime to string
            for field in ["created_at", "started_at", "completed_at"]:
                if task_data.get(field):
                    task_data[field] = task_data[field].isoformat()
            
            # Convert enums to strings
            task_data["status"] = task_data["status"].value
            task_data["stage"] = task_data["stage"].value
            
            self.redis_client.setex(
                task_key,
                86400,  # 24 hours
                json.dumps(task_data)
            )
            
            # Publish update
            self.redis_client.publish(
                f"training_updates:{task.task_id}",
                json.dumps({
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "stage": task.stage.value,
                    "progress": task.progress
                })
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to update task in Redis: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[TrainingTask]:
        """Get task status from Redis."""
        if self.redis_client is None:
            return None
        
        try:
            task_key = f"training_task:{task_id}"
            task_data = self.redis_client.get(task_key)
            
            if task_data:
                data = json.loads(task_data)
                
                # Convert string dates back to datetime
                for field in ["created_at", "started_at", "completed_at"]:
                    if data.get(field):
                        data[field] = datetime.fromisoformat(data[field])
                
                # Convert string enums back
                data["status"] = TrainingStatus(data["status"])
                data["stage"] = TrainingStage(data["stage"])
                
                # Recreate config
                if "config" in data:
                    data["config"] = TrainingConfig(**data["config"])
                
                return TrainingTask(**data)
            
        except Exception as e:
            self.logger.error(f"Failed to get task status: {e}")
        
        return None


# FastAPI application
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="AvatarAI Training Pipeline", version="1.0.0")

pipeline = TrainingPipeline()


class StartTrainingRequest(BaseModel):
    user_id: str
    avatar_id: str
    image_paths: List[str]
    voice_sample_path: str
    config: Optional[Dict[str, Any]] = None


class TrainingResponse(BaseModel):
    task_id: str
    status: str
    stage: str
    progress: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None


@app.post("/start", response_model=TrainingResponse)
async def start_training(request: StartTrainingRequest, background_tasks: BackgroundTasks):
    """Start training pipeline."""
    try:
        # Create task
        config_dict = request.config or {}
        config = TrainingConfig(**config_dict)
        
        task = TrainingTask(
            task_id=f"train_{uuid.uuid4()}",
            user_id=request.user_id,
            avatar_id=request.avatar_id,
            image_paths=request.image_paths,
            voice_sample_path=request.voice_sample_path,
            config=config
        )
        
        # Start training in background
        background_tasks.add_task(pipeline.start_training, task)
        
        return TrainingResponse(
            task_id=task.task_id,
            status=task.status.value,
            stage=task.stage.value,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            output_path=task.output_path,
            error_message=task.error_message
        )
        
    except Exception as e:
        logger.error(f"Failed to start training: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")


@app.get("/status/{task_id}", response_model=TrainingResponse)
async def get_training_status(task_id: str):
    """Get training task status."""
    task = pipeline.get_task_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return TrainingResponse(
        task_id=task.task_id,
        status=task.status.value,
        stage=task.stage.value,
        progress=task.progress,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        output_path=task.output_path,
        error_message=task.error_message
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "service": "training-pipeline",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "redis_connected": pipeline.redis_client is not None and pipeline.redis_client.ping()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5007,
        reload=True,
        log_level="info"
    )
