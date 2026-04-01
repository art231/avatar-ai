#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Lipsync Processor.
"""

import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Используем относительный импорт
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "lipsync_processor", 
        "ai-services/lipsync-service/services/lipsync_processor.py"
    )
    lipsync_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lipsync_module)
    LipSyncProcessor = lipsync_module.LipSyncProcessor
    
    print("✓ Успешно импортирован LipSyncProcessor")
    
    # Создаем процессор
    processor = LipSyncProcessor(processor_type="wav2lip")
    print(f"✓ Процессор создан: {processor}")
    
    # Проверяем health check
    health = processor.health_check()
    print(f"✓ Health check: {health}")
    
    if health.get("processor_available", False):
        print("✓ Процессор доступен и работает!")
    else:
        print(f"✗ Процессор не доступен: {health.get('error', 'Неизвестная ошибка')}")
        
except ImportError as e:
    print(f"✗ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ Ошибка при тестировании: {e}")
    import traceback
    traceback.print_exc()