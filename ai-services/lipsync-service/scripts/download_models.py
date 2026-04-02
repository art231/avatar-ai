#!/usr/bin/env python3
"""
Скрипт для скачивания моделей MuseTalk и Wav2Lip для Дня 13.
"""

import os
import sys
import json
import requests
import zipfile
import tarfile
from pathlib import Path
import subprocess
import shutil
from tqdm import tqdm
import hashlib
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация моделей
MODELS_CONFIG = {
    "muse_talk": {
        "name": "MuseTalk",
        "description": "Real-time talking head generation",
        "checkpoint_url": "https://huggingface.co/TMElyralab/MuseTalk/resolve/main/checkpoints/muse_talk.pt",
        "config_url": "https://huggingface.co/TMElyralab/MuseTalk/raw/main/configs/muse_talk.yaml",
        "output_dir": "muse_talk",
        "files": [
            {"url": "https://huggingface.co/TMElyralab/MuseTalk/resolve/main/checkpoints/muse_talk.pt", "filename": "muse_talk.pt"},
            {"url": "https://huggingface.co/TMElyralab/MuseTalk/raw/main/configs/muse_talk.yaml", "filename": "muse_talk.yaml"},
            {"url": "https://huggingface.co/TMElyralab/MuseTalk/resolve/main/checkpoints/audio2mesh.pt", "filename": "audio2mesh.pt"},
            {"url": "https://huggingface.co/TMElyralab/MuseTalk/resolve/main/checkpoints/renderer.pt", "filename": "renderer.pt"}
        ]
    },
    "wav2lip": {
        "name": "Wav2Lip",
        "description": "Accurate lip sync for talking faces",
        "checkpoint_url": "https://github.com/Rudrabha/Wav2Lip/releases/download/models/wav2lip.pth",
        "checkpoint_url_alt": "https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55cNDuEQ",
        "output_dir": "wav2lip",
        "files": [
            {"url": "https://github.com/Rudrabha/Wav2Lip/releases/download/models/wav2lip.pth", "filename": "wav2lip.pth"},
            {"url": "https://github.com/Rudrabha/Wav2Lip/releases/download/models/wav2lip_gan.pth", "filename": "wav2lip_gan.pth"},
            {"url": "https://github.com/Rudrabha/Wav2Lip/releases/download/models/s3fd.pth", "filename": "s3fd.pth"}
        ]
    }
}

def download_file(url: str, output_path: Path, chunk_size: int = 8192) -> bool:
    """Скачать файл с прогресс-баром."""
    try:
        logger.info(f"Downloading {url} to {output_path}")
        
        # Создаем директорию если нужно
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Загружаем файл
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_path.name) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        logger.info(f"Successfully downloaded {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False

def download_model(model_name: str, models_dir: Path) -> bool:
    """Скачать модель по имени."""
    if model_name not in MODELS_CONFIG:
        logger.error(f"Unknown model: {model_name}")
        return False
    
    config = MODELS_CONFIG[model_name]
    model_dir = models_dir / config["output_dir"]
    
    logger.info(f"Downloading {config['name']} model to {model_dir}")
    
    # Создаем директорию для модели
    model_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    total_files = len(config["files"])
    
    for file_info in config["files"]:
        url = file_info["url"]
        filename = file_info["filename"]
        output_path = model_dir / filename
        
        # Пропускаем если файл уже существует
        if output_path.exists():
            file_size = output_path.stat().st_size
            logger.info(f"File already exists: {output_path} ({file_size} bytes)")
            success_count += 1
            continue
        
        # Скачиваем файл
        if download_file(url, output_path):
            success_count += 1
    
    # Проверяем успешность
    if success_count == total_files:
        logger.info(f"Successfully downloaded all files for {config['name']}")
        
        # Создаем файл с информацией о модели
        info_file = model_dir / "model_info.json"
        with open(info_file, 'w') as f:
            json.dump({
                "model_name": model_name,
                "display_name": config["name"],
                "description": config["description"],
                "files_downloaded": success_count,
                "total_files": total_files,
                "download_date": str(Path(__file__).parent.resolve())
            }, f, indent=2)
        
        return True
    else:
        logger.warning(f"Downloaded {success_count}/{total_files} files for {config['name']}")
        return success_count > 0

def check_gpu_availability() -> bool:
    """Проверить доступность GPU."""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"GPU available: {gpu_name} (Count: {gpu_count})")
            
            # Проверяем память GPU
            for i in range(gpu_count):
                total_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                logger.info(f"GPU {i}: {torch.cuda.get_device_name(i)} - {total_memory:.2f} GB")
        else:
            logger.warning("GPU not available. Models will run on CPU (slow)")
        
        return cuda_available
        
    except ImportError:
        logger.error("PyTorch not installed")
        return False
    except Exception as e:
        logger.error(f"Error checking GPU: {e}")
        return False

def setup_model_environment(models_dir: Path) -> bool:
    """Настроить окружение для моделей."""
    try:
        # Создаем симлинки для Docker
        docker_models_dir = Path("/app/models")
        
        if docker_models_dir.exists():
            logger.info(f"Docker models directory exists: {docker_models_dir}")
            
            # Копируем модели если нужно
            for model_dir in models_dir.iterdir():
                if model_dir.is_dir():
                    docker_model_dir = docker_models_dir / model_dir.name
                    docker_model_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Копируем файлы
                    for file in model_dir.iterdir():
                        if file.is_file():
                            docker_file = docker_model_dir / file.name
                            if not docker_file.exists():
                                shutil.copy2(file, docker_file)
                                logger.info(f"Copied {file.name} to Docker directory")
        
        # Создаем файл конфигурации
        config_file = models_dir / "models_config.json"
        config = {
            "models_dir": str(models_dir.resolve()),
            "available_models": list(MODELS_CONFIG.keys()),
            "gpu_available": check_gpu_availability(),
            "setup_complete": True
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Configuration saved to {config_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up model environment: {e}")
        return False

def main():
    """Основная функция."""
    # Определяем директорию для моделей
    script_dir = Path(__file__).parent.parent
    models_dir = script_dir / "models"
    
    logger.info(f"Models directory: {models_dir}")
    
    # Проверяем доступность GPU
    gpu_available = check_gpu_availability()
    
    if not gpu_available:
        logger.warning("""
        ⚠️  GPU не доступен!
        
        Для работы реальных моделей MuseTalk и Wav2Lip требуется NVIDIA GPU с CUDA.
        Без GPU модели будут работать очень медленно или не будут работать вообще.
        
        Вы можете:
        1. Продолжить с симуляцией (fallback mode)
        2. Установить NVIDIA драйверы и CUDA
        3. Использовать облачный GPU сервис
        
        Продолжить скачивание моделей? (они все равно будут работать в симуляции)
        """)
        
        response = input("Продолжить? (y/n): ").strip().lower()
        if response != 'y':
            logger.info("Скачивание отменено")
            return
    
    # Скачиваем модели
    success_models = []
    
    for model_name in ["muse_talk", "wav2lip"]:
        logger.info(f"\n{'='*50}")
        logger.info(f"Downloading {model_name.upper()} model")
        logger.info(f"{'='*50}")
        
        if download_model(model_name, models_dir):
            success_models.append(model_name)
    
    # Настраиваем окружение
    if success_models:
        logger.info(f"\n{'='*50}")
        logger.info("Setting up model environment")
        logger.info(f"{'='*50}")
        
        if setup_model_environment(models_dir):
            logger.info("✅ Model environment setup complete!")
        else:
            logger.warning("⚠️  Model environment setup had issues")
    
    # Итоговый отчет
    logger.info(f"\n{'='*50}")
    logger.info("DOWNLOAD SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"GPU available: {'✅ Yes' if gpu_available else '❌ No'}")
    logger.info(f"Models downloaded: {len(success_models)}/{len(MODELS_CONFIG)}")
    
    for model_name in MODELS_CONFIG.keys():
        status = "✅" if model_name in success_models else "❌"
        logger.info(f"  {status} {MODELS_CONFIG[model_name]['name']}")
    
    if success_models:
        logger.info(f"\n🎉 Models are ready in: {models_dir}")
        logger.info("To use the models in Docker, rebuild the container:")
        logger.info("  docker-compose build lipsync-service")
        logger.info("  docker-compose up -d lipsync-service")
    else:
        logger.error("\n❌ No models were downloaded successfully")
    
    logger.info(f"\n{'='*50}")

if __name__ == "__main__":
    main()