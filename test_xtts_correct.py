#!/usr/bin/env python3
"""
Правильный тест XTTS Service.
Используем правильный формат запроса для FastAPI.
"""

import requests
import json
import os
from pathlib import Path

def test_xtts_correct():
    """Тестирование XTTS Service с правильным форматом запроса."""
    print("=== Тестирование XTTS Service (правильный формат) ===")
    
    # URL XTTS Service
    xtts_url = "http://localhost:5003"
    
    # 1. Проверка здоровья
    print("\n1. Проверка здоровья сервиса...")
    try:
        response = requests.get(f"{xtts_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Сервис здоров: {data.get('status')}")
            print(f"   [OK] Модель загружена: {data.get('details', {}).get('model_loaded')}")
        else:
            print(f"   [ERROR] Ошибка здоровья: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Не удалось подключиться: {e}")
        return False
    
    # 2. Создаем тестовый аудио файл
    print("\n2. Создание тестового аудио файла...")
    test_audio_path = Path("test_voice_correct.wav")
    
    try:
        import numpy as np
        import soundfile as sf
        
        sample_rate = 24000
        duration = 2.0
        frequency = 440
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        sf.write(str(test_audio_path), audio, sample_rate)
        print(f"   [OK] Создан файл: {test_audio_path}")
    except Exception as e:
        print(f"   [ERROR] Не удалось создать аудио файл: {e}")
        return False
    
    # 3. Тестирование синтеза речи с правильным форматом
    print("\n3. Тестирование синтеза речи (правильный формат)...")
    
    try:
        # Открываем файл
        with open(test_audio_path, 'rb') as f:
            # Создаем правильный формат запроса
            # FastAPI ожидает отдельные поля для каждого параметра в форме
            # Но также ожидает поле 'request' как JSON строку
            
            # Попробуем отправить как отдельные поля
            files = {
                'voice_file': ('test_voice.wav', f, 'audio/wav')
            }
            
            # Пробуем разные форматы
            
            # Формат 1: Все параметры как отдельные поля
            print("\n   Попытка 1: Все параметры как отдельные поля...")
            form_data = {
                'text': 'Hello, this is a test. Day 4 completed successfully.',
                'language': 'en',  # Используем английский для простоты
                'speed': '1.0',
                'temperature': '0.75',
                'use_cache': 'true'
            }
            
            response = requests.post(
                f"{xtts_url}/synthesize",
                files=files,
                data=form_data,
                timeout=60
            )
            
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   [OK] Успешно! Результат: {result}")
                return True
            else:
                print(f"   Ошибка: {response.text}")
                
                # Формат 2: Пробуем с эндпоинтом /clone-and-synthesize
                print("\n   Попытка 2: Эндпоинт /clone-and-synthesize...")
                f.seek(0)  # Возвращаемся к началу файла
                
                response2 = requests.post(
                    f"{xtts_url}/clone-and-synthesize",
                    files=files,
                    data=form_data,
                    timeout=60
                )
                
                print(f"   Статус: {response2.status_code}")
                if response2.status_code == 200:
                    result = response2.json()
                    print(f"   [OK] Успешно! Результат: {result}")
                    return True
                else:
                    print(f"   Ошибка: {response2.text}")
                    
                    # Формат 3: Пробуем отправить минимальные данные
                    print("\n   Попытка 3: Только обязательные поля...")
                    f.seek(0)  # Возвращаемся к началу файла
                    
                    minimal_data = {
                        'text': 'Hello test'
                    }
                    
                    response3 = requests.post(
                        f"{xtts_url}/synthesize",
                        files=files,
                        data=minimal_data,
                        timeout=60
                    )
                    
                    print(f"   Статус: {response3.status_code}")
                    if response3.status_code == 200:
                        result = response3.json()
                        print(f"   [OK] Успешно! Результат: {result}")
                        return True
                    else:
                        print(f"   Ошибка: {response3.text}")
                        return False
                
    except Exception as e:
        print(f"   [ERROR] Ошибка при запросе: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Удаляем временный файл
        if test_audio_path.exists():
            test_audio_path.unlink()
            print(f"   [OK] Удален временный файл: {test_audio_path}")

def main():
    """Основная функция тестирования."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ XTTS SERVICE (ПРАВИЛЬНЫЙ ФОРМАТ)")
    print("=" * 60)
    
    # Тестируем XTTS Service
    success = test_xtts_correct()
    
    # Итог
    print("\n" + "=" * 60)
    print("ИТОГ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    if success:
        print("[SUCCESS] XTTS Service работает корректно!")
        print("   - API принимает данные")
        print("   - Синтез речи работает")
        return True
    else:
        print("[FAILURE] XTTS Service не работает с текущим форматом запроса")
        print("   - Нужно проверить формат данных в FastAPI")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        if success:
            print("\n" + "=" * 60)
            print("[SUCCESS] Тестирование завершено успешно!")
            print("=" * 60)
            exit(0)
        else:
            print("\n" + "=" * 60)
            print("[FAILURE] Тестирование не удалось")
            print("=" * 60)
            exit(1)
            
    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1)