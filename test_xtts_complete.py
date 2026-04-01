import requests
import json
import time
import os

def test_xtts_service_complete():
    """Полный тест XTTS Service после запуска."""
    
    print("=== Полный тест XTTS Service ===")
    
    base_url = "http://localhost:5003"
    
    # Ждем запуска сервиса
    print("Ожидание запуска сервиса...")
    max_wait = 300  # 5 минут
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get('status') == 'healthy':
                    print("[OK] Сервис запущен и здоров!")
                    break
                else:
                    print(f"  Сервис запущен, но статус: {health_data.get('status')}")
                    break
        except:
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0:  # Сообщаем каждые 30 секунд
                print(f"  ... ({elapsed} сек)")
            time.sleep(5)
    else:
        print("[ERROR] Сервис не запустился за 5 минут")
        return False
    
    print("\n=== Тестирование эндпоинтов ===")
    
    # 1. Проверка корневого эндпоинта
    print("\n1. Корневой эндпоинт (/):")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("   [OK] OK")
            data = response.json()
            print(f"   Версия: {data.get('version')}")
            print(f"   Сообщение: {data.get('message')}")
        else:
            print(f"   [ERROR] Ошибка {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Исключение: {e}")
    
    # 2. Проверка health
    print("\n2. Health check (/health):")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("   [OK] OK")
            data = response.json()
            print(f"   Статус: {data.get('status')}")
            details = data.get('details', {})
            print(f"   Модель загружена: {details.get('model_loaded', False)}")
            print(f"   Redis подключен: {details.get('redis_connected', False)}")
            print(f"   GPU доступен: {details.get('cuda_available', False)}")
        else:
            print(f"   [ERROR] Ошибка {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Исключение: {e}")
    
    # 3. Проверка languages
    print("\n3. Поддерживаемые языки (/languages):")
    try:
        response = requests.get(f"{base_url}/languages", timeout=10)
        if response.status_code == 200:
            print("   [OK] OK")
            data = response.json()
            languages = data.get('languages', [])
            print(f"   Всего языков: {len(languages)}")
            for lang in languages[:5]:  # Показываем первые 5
                print(f"   - {lang.get('name')} ({lang.get('code')})")
            if len(languages) > 5:
                print(f"   ... и еще {len(languages) - 5} языков")
        else:
            print(f"   [ERROR] Ошибка {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Исключение: {e}")
    
    # 4. Проверка voices
    print("\n4. Доступные голоса (/voices):")
    try:
        response = requests.get(f"{base_url}/voices", timeout=10)
        if response.status_code == 200:
            print("   [OK] OK")
            data = response.json()
            voices = data.get('voices', [])
            print(f"   Всего голосов: {len(voices)}")
        else:
            print(f"   [ERROR] Ошибка {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Исключение: {e}")
    
    # 5. Проверка status
    print("\n5. Детальный статус (/status):")
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            print("   [OK] OK")
            data = response.json()
            print(f"   Версия: {data.get('version')}")
            print(f"   Модель загружена: {data.get('model_loaded', False)}")
            print(f"   Redis подключен: {data.get('redis_connected', False)}")
            print(f"   GPU доступен: {data.get('gpu_available', False)}")
            print(f"   Поддерживаемых языков: {data.get('supported_languages', 0)}")
        else:
            print(f"   [ERROR] Ошибка {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Исключение: {e}")
    
    # 6. Проверка files
    print("\n6. Сгенерированные файлы (/files):")
    try:
        response = requests.get(f"{base_url}/files", timeout=10)
        if response.status_code == 200:
            print("   [OK] OK")
            data = response.json()
            files = data.get('files', [])
            print(f"   Всего файлов: {len(files)}")
        else:
            print(f"   [ERROR] Ошибка {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Исключение: {e}")
    
    # 7. Тест синтеза речи (если есть тестовый аудиофайл)
    print("\n7. Тест синтеза речи (/synthesize):")
    test_audio_file = "test_voice.wav"
    if os.path.exists(test_audio_file):
        try:
            print(f"   Используем тестовый файл: {test_audio_file}")
            files = {'voice_file': open(test_audio_file, 'rb')}
            data = {
                'text': 'Hello, this is a test of the XTTS service.',
                'language': 'en',
                'speed': 1.0,
                'temperature': 0.75,
                'use_cache': True
            }
            
            # Сначала отправляем POST запрос с JSON данными
            response = requests.post(
                f"{base_url}/synthesize",
                data=data,
                files=files,
                timeout=30
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
            else:
                print(f"   [ERROR] Ошибка синтеза: {response.status_code}")
                print(f"   Ответ: {response.text[:200]}")
                
        except Exception as e:
            print(f"   [ERROR] Исключение при синтезе: {e}")
        finally:
            if 'files' in locals():
                files['voice_file'].close()
    else:
        print("   [WARNING] Тестовый аудиофайл не найден, пропускаем тест синтеза")
        print("   Создайте тестовый файл: python create_test_voice.py")
    
    print("\n=== Тест завершен ===")
    print("\nДля быстрого теста используйте: python test_xtts_quick.py")
    
    return True

if __name__ == "__main__":
    success = test_xtts_service_complete()
    exit(0 if success else 1)