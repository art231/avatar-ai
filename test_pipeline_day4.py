#!/usr/bin/env python3
"""
Тестовый пайплайн для Дня 4: проверка интеграции XTTS Service и Lipsync Service.
Этот скрипт тестирует полный пайплайн от текста до видео с липсинком.
"""

import os
import sys
import time
import requests
import json
import tempfile
from pathlib import Path
import subprocess
import shutil

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_xtts_service():
    """Тестирование XTTS Service."""
    print("=== Тестирование XTTS Service ===")
    
    # URL XTTS Service
    xtts_url = "http://localhost:5003"
    
    # Проверка здоровья
    try:
        health_response = requests.get(f"{xtts_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✓ XTTS Service здоров: {health_data}")
            
            # Проверка, что модель загружена
            if health_data.get("model_loaded"):
                print("✓ Модель XTTS v2 успешно загружена")
            else:
                print("✗ Модель XTTS v2 не загружена")
                print(f"  Ошибка: {health_data.get('model_error', 'Неизвестная ошибка')}")
                return False
        else:
            print(f"✗ XTTS Service не здоров: {health_response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Не удалось подключиться к XTTS Service: {e}")
        return False
    
    # Создание тестового аудио файла
    print("\nСоздание тестового аудио файла...")
    test_audio_path = Path("test_voice_sample.wav")
    
    # Используем существующий скрипт для создания тестового аудио
    if not test_audio_path.exists():
        try:
            # Создаем простой синусоидальный аудио файл
            import numpy as np
            import soundfile as sf
            
            sample_rate = 24000
            duration = 3.0  # секунды
            frequency = 440  # Гц
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio = 0.5 * np.sin(2 * np.pi * frequency * t)
            
            sf.write(str(test_audio_path), audio, sample_rate)
            print(f"✓ Создан тестовый аудио файл: {test_audio_path}")
        except Exception as e:
            print(f"✗ Не удалось создать тестовый аудио файл: {e}")
            return False
    else:
        print(f"✓ Используем существующий тестовый аудио файл: {test_audio_path}")
    
    # Тестирование синтеза речи
    print("\nТестирование синтеза речи...")
    try:
        # Подготовка данных для запроса
        test_text = "Привет, это тест синтеза речи от XTTS Service. День 4 успешно выполнен."
        
        # Создаем multipart/form-data запрос
        files = {
            'voice_sample': open(test_audio_path, 'rb'),
        }
        
        data = {
            'text': test_text,
            'language': 'ru',
            'speed': 1.0,
            'temperature': 0.75
        }
        
        # Отправляем запрос
        response = requests.post(
            f"{xtts_url}/api/v1/tts/clone-and-synthesize",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✓ Синтез речи успешен!")
                print(f"  Аудио файл: {result.get('audio_path')}")
                print(f"  Время обработки: {result.get('processing_time', 0):.2f} сек")
                print(f"  Длительность аудио: {result.get('audio_info', {}).get('duration_seconds', 0):.2f} сек")
                
                # Сохраняем путь к сгенерированному аудио
                audio_result_path = result.get("audio_path")
                if audio_result_path and os.path.exists(audio_result_path):
                    print(f"✓ Аудио файл сохранен: {audio_result_path}")
                    return True, audio_result_path
                else:
                    print("✗ Аудио файл не найден после генерации")
                    return False, None
            else:
                print(f"✗ Ошибка синтеза речи: {result.get('error', 'Неизвестная ошибка')}")
                return False, None
        else:
            print(f"✗ Ошибка HTTP: {response.status_code}")
            print(f"  Ответ: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка запроса: {e}")
        return False, None
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        return False, None
    finally:
        # Закрываем файл
        if 'files' in locals():
            files['voice_sample'].close()

def test_lipsync_service(audio_path):
    """Тестирование Lipsync Service."""
    print("\n=== Тестирование Lipsync Service ===")
    
    # URL Lipsync Service
    lipsync_url = "http://localhost:5006"
    
    # Проверка здоровья
    try:
        health_response = requests.get(f"{lipsync_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✓ Lipsync Service здоров: {health_data}")
        else:
            print(f"✗ Lipsync Service не здоров: {health_response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Не удалось подключиться к Lipsync Service: {e}")
        return False
    
    # Создание тестового видео файла (статическое изображение как видео)
    print("\nСоздание тестового видео файла...")
    test_video_path = Path("test_video_sample.mp4")
    
    if not test_video_path.exists():
        try:
            # Используем ffmpeg для создания тестового видео из статического изображения
            # Сначала создаем тестовое изображение
            test_image_path = Path("test_face_image.png")
            
            if not test_image_path.exists():
                import cv2
                import numpy as np
                
                # Создаем простое изображение с лицом
                img = np.ones((512, 512, 3), dtype=np.uint8) * 255
                
                # Рисуем лицо
                cv2.circle(img, (256, 200), 100, (200, 200, 200), -1)  # голова
                cv2.circle(img, (220, 180), 20, (255, 255, 255), -1)   # левый глаз
                cv2.circle(img, (292, 180), 20, (255, 255, 255), -1)   # правый глаз
                cv2.circle(img, (220, 180), 10, (0, 0, 0), -1)         # левый зрачок
                cv2.circle(img, (292, 180), 10, (0, 0, 0), -1)         # правый зрачок
                cv2.ellipse(img, (256, 250), (60, 30), 0, 0, 180, (0, 0, 0), 5)  # рот
                
                cv2.imwrite(str(test_image_path), img)
                print(f"✓ Создано тестовое изображение: {test_image_path}")
            
            # Конвертируем изображение в видео с помощью ffmpeg
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(test_image_path),
                "-c:v", "libx264",
                "-t", "5",  # 5 секунд
                "-pix_fmt", "yuv420p",
                str(test_video_path)
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Создано тестовое видео: {test_video_path}")
            else:
                print(f"✗ Ошибка создания видео: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Не удалось создать тестовое видео: {e}")
            return False
    else:
        print(f"✓ Используем существующее тестовое видео: {test_video_path}")
    
    # Тестирование липсинка
    print("\nТестирование липсинка...")
    try:
        # Подготовка файлов
        files = {
            'video': open(test_video_path, 'rb'),
            'audio': open(audio_path, 'rb'),
        }
        
        data = {
            'quality': 'medium',
            'sync_accuracy': '0.9',
            'processor_type': 'wav2lip'
        }
        
        # Отправляем запрос
        response = requests.post(
            f"{lipsync_url}/api/v1/lipsync/process",
            files=files,
            data=data,
            timeout=60  # Долгая операция
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✓ Липсинк успешен!")
                print(f"  Видео файл: {result.get('output_path')}")
                print(f"  Время обработки: {result.get('processing_time', 0):.2f} сек")
                print(f"  Качество: {result.get('quality', 'unknown')}")
                
                output_path = result.get("output_path")
                if output_path and os.path.exists(output_path):
                    print(f"✓ Видео файл сохранен: {output_path}")
                    return True, output_path
                else:
                    print("✗ Видео файл не найден после обработки")
                    return False, None
            else:
                print(f"✗ Ошибка липсинка: {result.get('error', 'Неизвестная ошибка')}")
                return False, None
        else:
            print(f"✗ Ошибка HTTP: {response.status_code}")
            print(f"  Ответ: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка запроса: {e}")
        return False, None
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        return False, None
    finally:
        # Закрываем файлы
        if 'files' in locals():
            files['video'].close()
            files['audio'].close()

def test_full_pipeline():
    """Тестирование полного пайплайна."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ПОЛНОГО ПАЙПЛАЙНА - ДЕНЬ 4")
    print("=" * 60)
    
    start_time = time.time()
    
    # Шаг 1: Тестирование XTTS Service
    xtts_success, audio_path = test_xtts_service()
    if not xtts_success:
        print("\n✗ Пайплайн прерван: XTTS Service не работает")
        return False
    
    # Шаг 2: Тестирование Lipsync Service
    lipsync_success, video_path = test_lipsync_service(audio_path)
    if not lipsync_success:
        print("\n✗ Пайплайн прерван: Lipsync Service не работает")
        return False
    
    # Итог
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("ИТОГ ТЕСТИРОВАНИЯ ПАЙПЛАЙНА")
    print("=" * 60)
    print(f"✓ XTTS Service: {'РАБОТАЕТ' if xtts_success else 'НЕ РАБОТАЕТ'}")
    print(f"✓ Lipsync Service: {'РАБОТАЕТ' if lipsync_success else 'НЕ РАБОТАЕТ'}")
    print(f"✓ Сгенерированное аудио: {audio_path}")
    print(f"✓ Сгенерированное видео: {video_path}")
    print(f"✓ Общее время выполнения: {total_time:.2f} секунд")
    print("\n✓ ПАЙПЛАЙН ДНЯ 4 УСПЕШНО ПРОТЕСТИРОВАН!")
    print("=" * 60)
    
    return True

def cleanup():
    """Очистка временных файлов."""
    print("\nОчистка временных файлов...")
    
    files_to_remove = [
        "test_voice_sample.wav",
        "test_face_image.png",
        "test_video_sample.mp4",
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✓ Удален: {file}")
            except Exception as e:
                print(f"✗ Не удалось удалить {file}: {e}")

if __name__ == "__main__":
    try:
        success = test_full_pipeline()
        
        if success:
            print("\n✓ День 4 завершен успешно!")
            print("  - XTTS Service интегрирован с реальной моделью")
            print("  - Lipsync Service готов к работе")
            print("  - Полный пайплайн от текста до видео работает")
        else:
            print("\n✗ День 4 не завершен: есть проблемы с пайплайном")
        
        # Очистка
        cleanup()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        cleanup()
        sys.exit(1)