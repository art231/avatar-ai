import requests
import json
import time

def test_xtts_simple():
    """Простой тест синтеза речи XTTS Service."""
    
    print("=== Простой тест синтеза речи XTTS Service ===")
    
    base_url = "http://localhost:5003"
    
    # Ждем запуска сервиса
    print("Ожидание запуска сервиса...")
    max_wait = 60
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("[OK] Сервис запущен!")
                break
        except:
            elapsed = int(time.time() - start_time)
            print(f"  ... ({elapsed} сек)")
            time.sleep(5)
    else:
        print("[ERROR] Сервис не запустился за 1 минуту")
        return False
    
    # Проверяем корневой эндпоинт
    print("\n1. Проверка корневого эндпоинта (/):")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("   [OK] OK")
            data = response.json()
            print(f"   Версия: {data.get('version')}")
            print(f"   Сообщение: {data.get('message')}")
        else:
            print(f"   [ERROR] Ошибка {response.status_code}: {response.text[:100]}")
    except Exception as e:
        print(f"   [ERROR] Исключение: {e}")
    
    # Проверяем статус
    print("\n2. Проверка статуса (/status):")
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            print("   [OK] OK")
            data = response.json()
            print(f"   Модель загружена: {data.get('model_loaded', False)}")
            print(f"   Redis подключен: {data.get('redis_connected', False)}")
            print(f"   GPU доступен: {data.get('gpu_available', False)}")
        else:
            print(f"   [ERROR] Ошибка {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Исключение: {e}")
    
    # Тест синтеза речи (если есть тестовый аудиофайл)
    print("\n3. Тест синтеза речи (/synthesize):")
    test_audio_file = "test_voice.wav"
    
    import os
    if os.path.exists(test_audio_file):
        try:
            print(f"   Используем тестовый файл: {test_audio_file}")
            
            # Правильный формат запроса для FastAPI
            # 1. Параметры как multipart/form-data
            files = {
                'voice_file': ('test_voice.wav', open(test_audio_file, 'rb'), 'audio/wav')
            }
            
            # 2. Данные как multipart/form-data
            data = {
                'text': 'Hello, this is a test of the XTTS service.',
                'language': 'en',
                'speed': '1.0',
                'temperature': '0.75',
                'use_cache': 'true'
            }
            
            # Отправляем POST запрос
            response = requests.post(
                f"{base_url}/synthesize",
                data=data,
                files=files,
                timeout=60  # Увеличиваем таймаут для загрузки модели
            )
            
            if response.status_code == 200:
                print("   [OK] Синтез речи успешен!")
                result = response.json()
                print(f"   Время обработки: {result.get('processing_time', 0):.2f} сек")
                print(f"   Длина текста: {result.get('text_length', 0)} символов")
                print(f"   Использован кэш: {result.get('cached', False)}")
                
                # Проверяем, есть ли путь к аудиофайлу
                audio_path = result.get('audio_path')
                if audio_path:
                    print(f"   Аудиофайл: {audio_path}")
                    
                    # Пробуем скачать файл
                    filename = os.path.basename(audio_path)
                    download_url = f"{base_url}/download/{filename}"
                    print(f"   Ссылка для скачивания: {download_url}")
                    
                    # Проверяем скачивание
                    try:
                        download_response = requests.get(download_url, timeout=10)
                        if download_response.status_code == 200:
                            print("   [OK] Файл доступен для скачивания")
                        else:
                            print(f"   [WARNING] Ошибка скачивания: {download_response.status_code}")
                    except Exception as e:
                        print(f"   [WARNING] Ошибка при скачивании: {e}")
            else:
                print(f"   [ERROR] Ошибка синтеза: {response.status_code}")
                print(f"   Ответ: {response.text[:200]}")
                
        except Exception as e:
            print(f"   [ERROR] Исключение при синтезе: {e}")
        finally:
            if 'files' in locals():
                files['voice_file'][1].close()
    else:
        print("   [WARNING] Тестовый аудиофайл не найден, пропускаем тест синтеза")
        print("   Создайте тестовый файл: python create_test_voice.py")
    
    print("\n=== Тест завершен ===")
    return True

if __name__ == "__main__":
    test_xtts_simple()