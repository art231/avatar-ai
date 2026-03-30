"""
Advanced LoRA Trainer with Kohya_ss integration for production use.
This module provides real LoRA training capabilities for avatar generation.
"""

import os
import sys
import json
import shutil
import asyncio
import subprocess
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
import yaml

from config import settings

# Try to import Kohya_ss modules
try:
    from library.train_util import (
        DreamBoothDataset,
        FineTuningDataset,
        train_one_epoch,
        save_model,
        setup_optimizer,
        setup_scheduler
    )
    from library.model_util import (
        load_models_from_stable_diffusion_checkpoint,
        load_lora_weights,
        save_lora_weights
    )
    from library.utils import (
        setup_logging,
        get_preferred_device,
        setup_seed
    )
    KOHYA_SS_AVAILABLE = True
except ImportError:
    logger.warning("Kohya_ss not available, using simplified training")
    KOHYA_SS_AVAILABLE = False


class AdvancedTrainingConfig(BaseModel):
    """Advanced configuration for LoRA training with Kohya_ss."""
    base_model: str = Field(default=settings.base_model, description="Base model for training")
    model_type: str = Field(default="sd15", description="Model type: sd15, sd21, sdxl")
    lora_rank: int = Field(default=settings.lora_rank, description="LoRA rank")
    lora_alpha: int = Field(default=settings.lora_alpha, description="LoRA alpha")
    learning_rate: float = Field(default=settings.learning_rate, description="Learning rate")
    num_train_epochs: int = Field(default=settings.num_train_epochs, description="Number of training epochs")
    train_batch_size: int = Field(default=settings.train_batch_size, description="Training batch size")
    gradient_accumulation_steps: int = Field(default=settings.gradient_accumulation_steps, description="Gradient accumulation steps")
    mixed_precision: str = Field(default=settings.mixed_precision, description="Mixed precision (fp16, bf16, fp32)")
    resolution: int = Field(default=settings.resolution, description="Training resolution")
    output_dir: Path = Field(default=settings.output_dir, description="Output directory for trained LoRA")
    
    # Advanced settings
    network_module: str = Field(default="networks.lora", description="Network module")
    network_train_unet_only: bool = Field(default=True, description="Train UNet only")
    network_train_text_encoder_only: bool = Field(default=False, description="Train text encoder only")
    network_weights: Optional[str] = Field(default=None, description="Pretrained network weights")
    network_dim: int = Field(default=32, description="Network dimension")
    network_alpha: int = Field(default=16, description="Network alpha")
    clip_skip: int = Field(default=2, description="CLIP skip")
    enable_bucket: bool = Field(default=True, description="Enable bucket")
    min_bucket_reso: int = Field(default=256, description="Minimum bucket resolution")
    max_bucket_reso: int = Field(default=1024, description="Maximum bucket resolution")
    seed: int = Field(default=42, description="Random seed")
    caption_extension: str = Field(default=".txt", description="Caption extension")
    cache_latents: bool = Field(default=True, description="Cache latents")
    cache_latents_to_disk: bool = Field(default=True, description="Cache latents to disk")
    optimizer_type: str = Field(default="AdamW8bit", description="Optimizer type")
    lr_scheduler: str = Field(default="cosine", description="Learning rate scheduler")
    max_token_length: int = Field(default=225, description="Maximum token length")
    save_every_n_epochs: int = Field(default=1, description="Save every N epochs")
    save_last_n_epochs: int = Field(default=3, description="Save last N epochs")
    save_model_as: str = Field(default="safetensors", description="Save model as (safetensors, ckpt, diffusers)")
    keep_tokens: int = Field(default=0, description="Keep tokens")
    caption_dropout_rate: float = Field(default=0.0, description="Caption dropout rate")
    caption_dropout_every_n_epochs: int = Field(default=0, description="Caption dropout every N epochs")
    caption_tag_dropout_rate: float = Field(default=0.0, description="Caption tag dropout rate")
    noise_offset: float = Field(default=0.0, description="Noise offset")
    adaptive_noise_scale: float = Field(default=0.0, description="Adaptive noise scale")
    multires_noise_iterations: int = Field(default=0, description="Multires noise iterations")
    multires_noise_discount: float = Field(default=0.0, description="Multires noise discount")


class AdvancedTrainingTask(BaseModel):
    """Advanced LoRA training task."""
    task_id: str
    user_id: str
    avatar_id: str
    image_paths: List[str]
    captions: Optional[Dict[str, str]] = None  # image_path -> caption
    config: AdvancedTrainingConfig
    status: str = "pending"  # pending, preprocessing, training, completed, failed
    progress: float = 0.0
    current_stage: str = "initializing"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = {}
    logs: List[str] = []


class AdvancedLoraTrainer:
    """Advanced LoRA trainer with Kohya_ss integration."""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"
        self.redis_client = None
        self.logger = logger
        
        # Initialize Redis client for task queue
        self._init_redis()
        
        # Initialize Kohya_ss components if available
        self._init_kohya_ss()
        
        # Training state
        self.active_tasks: Dict[str, AdvancedTrainingTask] = {}
    
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
    
    def _init_kohya_ss(self):
        """Initialize Kohya_ss components."""
        if not KOHYA_SS_AVAILABLE:
            self.logger.warning("Kohya_ss not available. Using simplified training mode.")
            return
        
        try:
            self.logger.info(f"Initializing Kohya_ss on device: {self.device}")
            
            # Setup logging for Kohya_ss
            setup_logging()
            
            # Setup seed for reproducibility
            setup_seed(42)
            
            # Get preferred device
            device = get_preferred_device()
            self.logger.info(f"Kohya_ss using device: {device}")
            
            self.logger.info("Kohya_ss initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Kohya_ss: {e}")
            raise
    
    def validate_and_preprocess_images(self, image_paths: List[str]) -> Tuple[bool, str, List[str], Dict[str, str]]:
        """Validate and preprocess images for training."""
        valid_paths = []
        captions = {}
        
        if not image_paths:
            return False, "No images provided", [], {}
        
        if len(image_paths) < settings.min_images:
            return False, f"Too few images: {len(image_paths)} < {settings.min_images}", [], {}
        
        if len(image_paths) > settings.max_images:
            return False, f"Too many images: {len(image_paths)} > {settings.max_images}", [], {}
        
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
            
            # Try to open and preprocess image
            try:
                with Image.open(path) as img:
                    img.verify()  # Verify it's a valid image
                
                # Check resolution
                with Image.open(path) as img:
                    width, height = img.size
                    
                    # Resize if needed
                    if width < settings.resolution or height < settings.resolution:
                        self.logger.warning(f"Image too small: {width}x{height} < {settings.resolution}")
                        continue
                    
                    # Create square image for training
                    min_dim = min(width, height)
                    left = (width - min_dim) // 2
                    top = (height - min_dim) // 2
                    right = left + min_dim
                    bottom = top + min_dim
                    
                    cropped_img = img.crop((left, top, right, bottom))
                    resized_img = cropped_img.resize((settings.resolution, settings.resolution), Image.Resampling.LANCZOS)
                    
                    # Save preprocessed image
                    preprocessed_path = path.parent / f"preprocessed_{path.name}"
                    resized_img.save(preprocessed_path, quality=95)
                    
                    valid_paths.append(str(preprocessed_path))
                    
                    # Generate caption (in production, this would use BLIP or similar)
                    caption = f"photo of person, high quality, detailed"
                    captions[str(preprocessed_path)] = caption
                
            except Exception as e:
                self.logger.warning(f"Invalid image file {image_path}: {e}")
                continue
        
        if len(valid_paths) < settings.min_images:
            return False, f"Only {len(valid_paths)} valid images found, need at least {settings.min_images}", [], {}
        
        return True, f"Found {len(valid_paths)} valid images", valid_paths, captions
    
    def create_training_config_file(self, task: AdvancedTrainingTask, training_dir: Path) -> Path:
        """Create Kohya_ss training configuration file."""
        config_path = training_dir / "training_config.yaml"
        
        config = {
            "model_name_or_path": task.config.base_model,
            "output_dir": str(training_dir / "output"),
            "output_name": f"lora_{task.task_id}",
            "save_model_as": task.config.save_model_as,
            "mixed_precision": task.config.mixed_precision,
            "save_precision": task.config.mixed_precision,
            "seed": task.config.seed,
            "num_processes": 1,
            "num_machines": 1,
            "machine_rank": 0,
            "dataset_config": str(training_dir / "dataset_config.toml"),
            "training_comment": f"AvatarAI training for task {task.task_id}",
            "max_train_steps": task.config.num_train_epochs * 100,  # Approximate
            "learning_rate": task.config.learning_rate,
            "lr_scheduler": task.config.lr_scheduler,
            "lr_warmup_steps": 0,
            "train_batch_size": task.config.train_batch_size,
            "gradient_accumulation_steps": task.config.gradient_accumulation_steps,
            "max_token_length": task.config.max_token_length,
            "caption_extension": task.config.caption_extension,
            "cache_latents": task.config.cache_latents,
            "cache_latents_to_disk": task.config.cache_latents_to_disk,
            "enable_bucket": task.config.enable_bucket,
            "min_bucket_reso": task.config.min_bucket_reso,
            "max_bucket_reso": task.config.max_bucket_reso,
            "resolution": f"{task.config.resolution},{task.config.resolution}",
            "network_module": task.config.network_module,
            "network_dim": task.config.network_dim,
            "network_alpha": task.config.network_alpha,
            "network_train_unet_only": task.config.network_train_unet_only,
            "network_train_text_encoder_only": task.config.network_train_text_encoder_only,
            "text_encoder_lr": task.config.learning_rate,
            "unet_lr": task.config.learning_rate,
            "network_weights": task.config.network_weights,
            "network_dropout": 0,
            "dim_from_weights": False,
            "scale_weight_norms": 1.0,
            "noise_offset": task.config.noise_offset,
            "multires_noise_iterations": task.config.multires_noise_iterations,
            "multires_noise_discount": task.config.multires_noise_discount,
            "adaptive_noise_scale": task.config.adaptive_noise_scale,
            "clip_skip": task.config.clip_skip,
            "max_data_loader_n_workers": 0,
            "persistent_data_loader_workers": False,
            "max_train_epochs": task.config.num_train_epochs,
            "max_data_loader_n_workers": 0,
            "mem_eff_attn": False,
            "xformers": True,
            "vae": None,
            "v2": task.config.model_type == "sd21",
            "v_parameterization": False,
            "sdxl": task.config.model_type == "sdxl",
            "full_fp16": task.config.mixed_precision == "fp16",
            "full_bf16": task.config.mixed_precision == "bf16",
            "gradient_checkpointing": True,
            "logging_dir": str(training_dir / "logs"),
            "log_prefix": task.task_id,
            "log_with": "tensorboard",
            "log_tracker_name": None,
            "log_tracker_config": None,
            "sample_every_n_steps": 0,
            "sample_every_n_epochs": 1,
            "sample_sampler": "euler_a",
            "sample_prompts": ["photo of person, high quality, detailed"],
            "save_every_n_epochs": task.config.save_every_n_epochs,
            "save_last_n_epochs": task.config.save_last_n_epochs,
            "save_state": False,
            "resume": None,
            "train_text_encoder": not task.config.network_train_unet_only,
            "color_aug": False,
            "flip_aug": False,
            "face_crop_aug_range": None,
            "random_crop": False,
            "shuffle_caption": False,
            "keep_tokens": task.config.keep_tokens,
            "caption_dropout_rate": task.config.caption_dropout_rate,
            "caption_dropout_every_n_epochs": task.config.caption_dropout_every_n_epochs,
            "caption_tag_dropout_rate": task.config.caption_tag_dropout_rate,
            "reg_data_dir": None,
            "in_json": None,
            "data_backend": "local",
            "vae_batch_size": 0,
            "min_snr_gamma": 0,
            "down_lr_weight": None,
            "mid_lr_weight": None,
            "up_lr_weight": None,
            "block_lr_zero_threshold": 0,
            "block_dims": None,
            "block_alphas": None,
            "conv_block_dims": None,
            "conv_block_alphas": None,
            "weighted_captions": False,
            "unit": 1,
            "save_every_n_steps": 0,
            "save_last_n_steps": -1,
            "save_state_every_n_steps": 0,
            "save_state_last_n_steps": -1,
            "use_wandb": False,
            "wandb_api_key": None,
            "wandb_run_name": None,
            "wandb_log_model": False,
            "scale_v_pred_loss_like_noise_pred": False,
            "min_timestep": 0,
            "max_timestep": 1000,
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return config_path
    
    def create_dataset_config(self, training_dir: Path, image_paths: List[str], captions: Dict[str, str]) -> Path:
        """Create dataset configuration for Kohya_ss."""
        dataset_config_path = training_dir / "dataset_config.toml"
        
        # Create image directory
        image_dir = training_dir / "images"
        image_dir.mkdir(parents=True, exist