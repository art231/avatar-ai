#!/usr/bin/env python3
"""
Упрощенный скрипт для скачивания моделей MuseTalk и Wav2Lip (неинтерактивный).
"""

import os
import sys
import json
import requests
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация моделей (только основные файлы)
MODELS_CONFIG = {
    "wav2lip": {
        "name": "Wav2Lip",
        "output_dir": "wav2lip",
        "files": [
            {"url": "https://github.com/Rudrabha/Wav2Lip/releases/download/models/wav2lip.pth", "filename": "wav2lip.pth"},
        ]
    }
}

def download_file_simple(url: str, output_path: Path) -> bool:
    """Скачать файл без прогресс-бара."""
    try:
        logger.info(f"Downloading {url}")
        
        # Создаем директорию если нужно
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Загружаем файл
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = output_path.stat().st_size
        logger.info(f"Downloaded {output_path.name} ({file_size} bytes)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False

def download_model_simple(model_name: str, models_dir: Path) -> bool:
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
        if download_file_simple(url, output_path):
            success_count += 1
    
    # Проверяем успешность
    if success_count > 0:
        logger.info(f"Downloaded {success_count}/{total_files} files for {config['name']}")
        
        # Создаем файл с информацией о модели
        info_file = model_dir / "model_info.json"
        with open(info_file, 'w') as f:
            json.dump({
                "model_name": model_name,
                "display_name": config["name"],
                "files_downloaded": success_count,
                "total_files": total_files,
                "download_date": str(Path(__file__).parent.resolve())
            }, f, indent=2)
        
        return True
    else:
        logger.error(f"Failed to download any files for {config['name']}")
        return False

def main():
    """Основная функция."""
    # Определяем директорию для моделей
    script_dir = Path(__file__).parent.parent
    models_dir = script_dir / "models"
    
    logger.info(f"Models directory: {models_dir}")
    
    # Проверяем доступность GPU
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
        else:
            logger.warning("GPU not available - models will use CPU")
    except ImportError:
        logger.warning("PyTorch not installed - assuming CPU mode")
        gpu_available = False
    
    # Скачиваем модели
    success_models = []
    
    for model_name in ["wav2lip"]:  # Начнем с Wav2Lip как самой важной
        logger.info(f"\n{'='*50}")
        logger.info(f"Downloading {model_name.upper()} model")
        logger.info(f"{'='*50}")
        
        if download_model_simple(model_name, models_dir):
            success_models.append(model_name)
    
    # Итоговый отчет
    logger.info(f"\n{'='*50}")
    logger.info("DOWNLOAD SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"GPU available: {'Yes' if gpu_available else 'No'}")
    logger.info(f"Models downloaded: {len(success_models)}/{len(MODELS_CONFIG)}")
    
    for model_name in MODELS_CONFIG.keys():
        status = "✓" if model_name in success_models else "✗"
        logger.info(f"  {status} {MODELS_CONFIG[model_name]['name']}")
    
    if success_models:
        logger.info(f"\nModels are ready in: {models_dir}")
        logger.info("\nTo use the models in Docker:")
        logger.info("1. Copy models to container: docker cp models/. avatar-ai-lipsync-service:/app/models/")
        logger.info("2. Or rebuild container: docker-compose build lipsync-service")
    else:
        logger.error("\nNo models were downloaded successfully")
    
    logger.info(f"\n{'='*50}")

if __name__ == "__main__":
    main()