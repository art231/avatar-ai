import requests
import json
import os
import time
import numpy as np
import soundfile as sf

print("=== Базовый тест XTTS Service API ===")

# Создаем тестовый аудиофайл для клонирования голоса
sample_rate = 22050
duration = 3.0
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # Синусоида 440 Гц
sf.write('test_voice.wav', audio, sample_rate, subtype='PCM_16')

print(f"Создан тестовый голосовой файл: test_voice.wav")
print(f"Размер: {os.path.getsize('test_voice.wav')} байт")

# Проверяем доступность сервиса
url = 'http://localhost:5003'
health_url = f'{url}/health'

print(f"\nПроверяем доступность сервиса по адресу: {health_url}")

max_retries = 60  # Модель может загружаться долго
for i in range(max_retries):
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"Health check: статус {response.status_code}")
            print(f"Ответ: {json.dumps(health_data, indent=2)}")
            
            # Проверяем статус модели
            if health_data.get('status') == 'healthy':
                print("✅ Сервис здоров и готов к работе")
                break
            elif health_data.get('status') == 'degraded':
                print("⚠️  Сервис работает в деградированном режиме (модель не загружена)")
                break
            else:
                print(f"❌ Сервис не здоров: {health_data.get('status')}")
        else:
            print(f"Попытка {i+1}/{max_retries}: статус {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"Попытка {i+1}/{max_retries}: сервис не отвечает, ждем...")
    except Exception as e:
        print(f"Попытка {i+1}/{max_retries}: ошибка {e}")
    
    if i < max_retries - 1:
        time.sleep(5)  # Ждем 5 секунд между попытками
else:
    print(f"\n❌ Сервис не ответил после {max_retries} попыток")
    print("Проверьте логи: docker-compose logs xtts-service")
    exit(1)

# Тестируем корневой endpoint
print(f"\nТестируем корневой endpoint: {url}/")
try:
    response = requests.get(f'{url}/', timeout=10)
    print(f"Корневой endpoint: статус {response.status_code}")
    if response.status_code == 200:
        print(f"Ответ: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Ошибка при проверке корневого endpoint: {e}")

# Тестируем languages endpoint
print(f"\nТестируем endpoint /languages")
try:
    response = requests.get(f'{url}/languages', timeout=10)
    print(f"Languages endpoint: статус {response.status_code}")
    if response.status_code == 200:
        languages_data = response.json()
        print(f"Поддерживаемые языки: {languages_data.get('total', 0)}")
        for lang in languages_data.get('languages', [])[:5]:  # Показываем первые 5
            print(f"  - {lang.get('code')}: {lang.get('name')}")
except Exception as e:
    print(f"Ошибка при проверке languages endpoint: {e}")

# Тестируем voices endpoint
print(f"\nТестируем endpoint /voices")
try:
    response = requests.get(f'{url}/voices', timeout=10)
    print(f"Voices endpoint: статус {response.status_code}")
    if response.status_code == 200:
        voices_data = response.json()
        print(f"Доступные голоса: {voices_data.get('total', 0)}")
        for voice in voices_data.get('voices', [])[:3]:  # Показываем первые 3
            print(f"  - {voice.get('name')} ({voice.get('language')})")
except Exception as e:
    print(f"Ошибка при проверке voices endpoint: {e}")

# Тестируем files endpoint
print(f"\nТестируем endpoint /files")
try:
    response = requests.get(f'{url}/files', timeout=10)
    print(f"Files endpoint: статус {response.status_code}")
    if response.status_code == 200:
        files_data = response.json()
        print(f"Сгенерированные файлы: {len(files_data.get('files', []))}")
except Exception as e:
    print(f"Ошибка при проверке files endpoint: {e}")

# Тестируем status endpoint
print(f"\nТестируем endpoint /status")
try:
    response = requests.get(f'{url}/status', timeout=10)
    print(f"Status endpoint: статус {response.status_code}")
    if response.status_code == 200:
        status_data = response.json()
        print("Статус сервиса:")
        print(f"  Модель загружена: {'✅' if status_data.get('model_loaded') else '❌'}")
        print(f"  Redis подключен: {'✅' if status_data.get('redis_connected') else '❌'}")
        print(f"  GPU доступен: {'✅' if status_data.get('gpu_available') else '❌'}")
        print(f"  Устройство: {status_data.get('device', 'N/A')}")
        print(f"  Поддерживаемых языков: {status_data.get('supported_languages', 0)}")
except Exception as e:
    print(f"Ошибка при проверке status endpoint: {e}")

# Очистка
if os.path.exists('test_voice.wav'):
    os.remove('test_voice.wav')
    print("\nТестовый файл удален")

print("\n=== Базовый тест завершен ===")
print("\nСледующие шаги:")
print("1. Дождитесь завершения сборки xtts-service")
print("2. Проверьте, что модель XTTS v2 загружена (health endpoint)")
print("3. Протестируйте синтез речи через /synthesize endpoint")
print("4. Убедитесь, что Redis работает для кэширования голосовых эмбеддингов")