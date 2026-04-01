import requests
import time
import json

def quick_test_xtts():
    """Быстрый тест XTTS Service после запуска."""
    
    print("=== Быстрый тест XTTS Service ===")
    
    base_url = "http://localhost:5003"
    
    # Ждем запуска сервиса (максимум 2 минуты)
    print("Ожидание запуска сервиса...")
    max_wait = 120
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
        print("[ERROR] Сервис не запустился за 2 минуты")
        return False
    
    # Проверяем основные эндпоинты
    print("\nПроверка эндпоинтов:")
    
    endpoints = [
        ("/health", "GET"),
        ("/languages", "GET"),
        ("/status", "GET"),
        ("/voices", "GET"),
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"  [OK] {endpoint} - OK")
                if endpoint == "/status":
                    data = response.json()
                    print(f"     Модель загружена: {data.get('model_loaded', False)}")
                    print(f"     Redis подключен: {data.get('redis_connected', False)}")
                    print(f"     GPU доступен: {data.get('gpu_available', False)}")
            else:
                print(f"  [ERROR] {endpoint} - Ошибка {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"  [ERROR] {endpoint} - Исключение: {e}")
    
    print("\n=== Тест завершен ===")
    print("\nДля полного тестирования используйте:")
    print("python test_xtts_api.py")
    
    return True

if __name__ == "__main__":
    quick_test_xtts()