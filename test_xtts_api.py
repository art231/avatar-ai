import requests
import json
import time
import os

def test_xtts_service():
    """Тестирование XTTS Service API после запуска."""
    
    print("=== Тестирование XTTS Service API ===")
    
    base_url = "http://localhost:5003"
    
    # 1. Проверка health endpoint
    print("\n1. Проверка health endpoint:")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Данные: {json.dumps(health_data, indent=2, ensure_ascii=False)}")
            
            if health_data.get('status') == 'healthy':
                print("   ✅ Сервис здоров")
            elif health_data.get('status') == 'degraded':
                print("   ⚠️  Сервис работает в деградированном режиме")
            else:
                print("   ❌ Сервис не здоров")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        return False
    
    # 2. Проверка languages endpoint
    print("\n2. Проверка languages endpoint:")
    try:
        response = requests.get(f"{base_url}/languages", timeout=10)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            languages_data = response.json()
            print(f"   Поддерживаемых языков: {languages_data.get('total', 0)}")
            print(f"   Языки: {', '.join([lang['code'] for lang in languages_data.get('languages', [])[:5]])}...")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 3. Проверка voices endpoint
    print("\n3. Проверка voices endpoint:")
    try:
        response = requests.get(f"{base_url}/voices", timeout=10)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            voices_data = response.json()
            print(f"   Доступных голосов: {voices_data.get('total', 0)}")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 4. Проверка status endpoint
    print("\n4. Проверка status endpoint:")
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            status_data = response.json()
            print(f"   Модель загружена: {'✅' if status_data.get('model_loaded') else '❌'}")
            print(f"   Redis подключен: {'✅' if status_data.get('redis_connected') else '❌'}")
            print(f"   GPU доступен: {'✅' if status_data.get('gpu_available') else '❌'}")
            print(f"   Устройство: {status_data.get('device', 'N/A')}")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 5. Проверка files endpoint
    print("\n5. Проверка files endpoint:")
    try:
        response = requests.get(f"{base_url}/files", timeout=10)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            files_data = response.json()
            print(f"   Сгенерированных файлов: {len(files_data.get('files', []))}")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n=== Тестирование завершено ===")
    print("\nДля тестирования синтеза речи используйте команду:")
    print("curl -X POST http://localhost:5003/synthesize \\")
    print("  -F 'voice_file=@path/to/voice.wav' \\")
    print("  -F 'text=Hello, this is a test' \\")
    print("  -F 'language=en'")
    
    return True

if __name__ == "__main__":
    print("Ожидание запуска XTTS Service...")
    
    # Ждем до 5 минут пока сервис запустится
    max_wait_time = 300  # 5 минут
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get("http://localhost:5003/health", timeout=5)
            if response.status_code == 200:
                print("Сервис обнаружен, начинаем тестирование...")
                test_xtts_service()
                break
        except:
            elapsed = time.time() - start_time
            print(f"Ожидание сервиса... ({int(elapsed)} сек)")
            time.sleep(5)
    else:
        print(f"❌ Сервис не запустился за {max_wait_time} секунд")
        print("Проверьте логи: docker-compose logs xtts-service")