#!/usr/bin/env python3
"""
Скрипт для скачивания и проверки моделей XTTS v2 для Дня 13.
"""

import os
import sys
import json
import requests
from pathlib import Path
import subprocess
import shutil
import logging
from TTS.api import TTS

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_xtts_model() -> dict:
    """Проверить наличие и состояние модели XTTS v2."""
    try:
        logger.info("Checking XTTS v2 model...")
        
        # Пробуем загрузить модель
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
        
        # Получаем информацию о модели
        model_info = {
            "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
            "status": "loaded",
            "device": tts.device,
            "speakers": tts.speakers,
            "languages": tts.languages,
            "is_multi_lingual": tts.is_multi_lingual,
            "is_multi_speaker": tts.is_multi_speaker,
            "model_path": tts.model_path
        }
        
        logger.info(f"XTTS v2 model loaded successfully on {tts.device}")
        logger.info(f"Supported languages: {tts.languages}")
        logger.info(f"Model path: {tts.model_path}")
        
        return model_info
        
    except Exception as e:
        logger.error(f"Failed to load XTTS v2 model: {e}")
        return {
            "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
            "status": "error",
            "error": str(e)
        }

def download_xtts_model() -> bool:
    """Скачать модель XTTS v2 если она не загружена."""
    try:
        logger.info("Downloading XTTS v2 model...")
        
        # Используем TTS API для скачивания модели
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True)
        
        # Проверяем что модель загружена
        if hasattr(tts, 'model_path') and tts.model_path:
            logger.info(f"Model downloaded to: {tts.model_path}")
            
            # Проверяем размер модели
            model_dir = Path(tts.model_path).parent
            total_size = 0
            for file in model_dir.rglob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
            
            logger.info(f"Model size: {total_size / 1024**3:.2f} GB")
            return True
        else:
            logger.error("Model download failed - no model path")
            return False
            
    except Exception as e:
        logger.error(f"Failed to download XTTS v2 model: {e}")
        return False

def test_xtts_quality() -> dict:
    """Протестировать качество синтеза речи."""
    try:
        logger.info("Testing XTTS v2 quality...")
        
        # Создаем тестовый текст
        test_text = "Hello, this is a test of the XTTS v2 model quality."
        
        # Загружаем модель
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
        
        # Создаем тестовый аудио файл
        test_dir = Path("test_output")
        test_dir.mkdir(exist_ok=True)
        output_file = test_dir / "test_xtts_quality.wav"
        
        # Генерируем речь
        tts.tts_to_file(
            text=test_text,
            file_path=str(output_file),
            speaker=tts.speakers[0] if tts.speakers else None,
            language="en"
        )
        
        # Проверяем результат
        if output_file.exists():
            file_size = output_file.stat().st_size
            logger.info(f"Test audio generated: {output_file} ({file_size} bytes)")
            
            return {
                "success": True,
                "output_file": str(output_file),
                "file_size": file_size,
                "text": test_text,
                "language": "en"
            }
        else:
            logger.error("Test audio generation failed")
            return {"success": False, "error": "Output file not created"}
            
    except Exception as e:
        logger.error(f"XTTS quality test failed: {e}")
        return {"success": False, "error": str(e)}

def optimize_xtts_performance() -> dict:
    """Оптимизировать производительность XTTS v2."""
    try:
        logger.info("Optimizing XTTS v2 performance...")
        
        optimizations = {
            "gpu_available": False,
            "half_precision": False,
            "batch_size": 1,
            "cache_voice_embeddings": True,
            "optimization_suggestions": []
        }
        
        # Проверяем доступность GPU
        import torch
        if torch.cuda.is_available():
            optimizations["gpu_available"] = True
            optimizations["device"] = "cuda"
            
            # Проверяем поддержку half precision
            if torch.cuda.get_device_capability()[0] >= 7:  # Volta и новее
                optimizations["half_precision"] = True
                optimizations["optimization_suggestions"].append("Use half precision (FP16) for faster inference")
            
            # Проверяем память GPU
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            optimizations["gpu_memory_gb"] = gpu_memory
            
            if gpu_memory >= 8:
                optimizations["batch_size"] = 2
                optimizations["optimization_suggestions"].append("Increase batch size to 2 for better throughput")
            elif gpu_memory >= 4:
                optimizations["batch_size"] = 1
                optimizations["optimization_suggestions"].append("Keep batch size at 1 for stable performance")
            else:
                optimizations["optimization_suggestions"].append("Consider using CPU or upgrading GPU")
        
        else:
            optimizations["device"] = "cpu"
            optimizations["optimization_suggestions"].append("GPU not available - consider enabling CUDA")
        
        # Проверяем кэширование
        optimizations["optimization_suggestions"].append("Enable voice embedding cache for repeated voices")
        
        logger.info(f"Performance optimizations: {optimizations}")
        return optimizations
        
    except Exception as e:
        logger.error(f"Performance optimization failed: {e}")
        return {"error": str(e)}

def main():
    """Основная функция."""
    logger.info("=" * 50)
    logger.info("XTTS v2 Model Setup - Day 13")
    logger.info("=" * 50)
    
    # Проверяем текущее состояние модели
    model_info = check_xtts_model()
    
    if model_info["status"] == "loaded":
        logger.info("✅ XTTS v2 model is already loaded")
        
        # Тестируем качество
        test_result = test_xtts_quality()
        if test_result["success"]:
            logger.info("✅ XTTS quality test passed")
        else:
            logger.warning(f"⚠️ XTTS quality test failed: {test_result.get('error', 'Unknown error')}")
        
        # Оптимизируем производительность
        optimizations = optimize_xtts_performance()
        
    else:
        logger.warning("⚠️ XTTS v2 model not loaded or has errors")
        
        # Пробуем скачать модель
        logger.info("Attempting to download XTTS v2 model...")
        if download_xtts_model():
            logger.info("✅ XTTS v2 model downloaded successfully")
            
            # Проверяем снова
            model_info = check_xtts_model()
            if model_info["status"] == "loaded":
                # Тестируем качество
                test_result = test_xtts_quality()
                
                # Оптимизируем производительность
                optimizations = optimize_xtts_performance()
            else:
                logger.error("❌ Failed to load model after download")
        else:
            logger.error("❌ Failed to download XTTS v2 model")
    
    # Создаем отчет
    report_file = Path("xtts_setup_report.json")
    report = {
        "model_info": model_info,
        "optimizations": optimizations if 'optimizations' in locals() else {},
        "test_result": test_result if 'test_result' in locals() else {}
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Report saved to: {report_file}")
    logger.info("=" * 50)
    logger.info("XTTS v2 setup complete!")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()