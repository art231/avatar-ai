import requests
import time
import sys

def check_xtts_service():
    """Проверка статуса XTTS Service."""
    
    print("=== Проверка статуса XTTS Service ===")
    
    base_url = "http://localhost:5003"
    
    # Проверяем, запущен ли сервис
    print("Проверка доступности сервиса...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Сервис запущен! Попытка {attempt + 1}/{max_attempts}")
                health_data = response.json()
                print(f"Статус: {health_data.get('status', 'unknown')}")
                print(f"Детали: {health_data.get('details', {})}")
                return True
            else:
                print(f"  Сервис отвечает с кодом {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"  Попытка {attempt + 1}/{max_attempts}: Сервис недоступен, ждем 5 секунд...")
            time.sleep(5)
        except Exception as e:
            print(f"  Ошибка: {e}")
            time.sleep(5)
    
    print(f"❌ Сервис не запустился за {max_attempts * 5} секунд")
    
    # Проверяем, есть ли контейнер
    print("\nПроверка Docker контейнеров...")
    import subprocess
    try:
        result = subprocess.run(['docker', 'ps', '-a'], capture_output=True, text=True)
        if 'xtts' in result.stdout.lower():
            print("Контейнер xtts-service найден в списке контейнеров")
            # Проверяем логи
            print("\nПроверка логов контейнера...")
            log_result = subprocess.run(['docker-compose', 'logs', '--tail=10', 'xtts-service'], 
                                       capture_output=True, text=True)
            print("Последние 10 строк логов:")
            print(log_result.stdout)
        else:
            print("Контейнер xtts-service не найден")
    except Exception as e:
        print(f"Ошибка при проверке Docker: {e}")
    
    return False

if __name__ == "__main__":
    success = check_xtts_service()
    sys.exit(0 if success else 1)