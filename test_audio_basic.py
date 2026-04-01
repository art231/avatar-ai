import requests
import json
import os
import time

print("=== Базовый тест Audio Preprocessor API ===")

# Создаем простой тестовый файл
import numpy as np
import soundfile as sf

sample_rate = 22050
duration = 5.0
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = 0.5 * np.sin(2 * np.pi * 440 * t)
sf.write('test_basic.wav', audio, sample_rate, subtype='PCM_16')

print(f"Создан тестовый файл: test_basic.wav")
print(f"Размер: {os.path.getsize('test_basic.wav')} байт")

# Проверяем доступность сервиса
url = 'http://localhost:5004'
health_url = f'{url}/health'

print(f"\nПроверяем доступность сервиса по адресу: {health_url}")

max_retries = 30
for i in range(max_retries):
    try:
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print(f"Health check: статус {response.status_code}")
            print(f"Ответ: {response.json()}")
            break
        else:
            print(f"Попытка {i+1}/{max_retries}: статус {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"Попытка {i+1}/{max_retries}: сервис не отвечает, ждем...")
    except Exception as e:
        print(f"Попытка {i+1}/{max_retries}: ошибка {e}")
    
    if i < max_retries - 1:
        time.sleep(2)
else:
    print(f"\nСервис не ответил после {max_retries} попыток")
    print("Проверьте логи: docker-compose logs audio-preprocessor")
    exit(1)

# Тестируем корневой endpoint
print(f"\nТестируем корневой endpoint: {url}/")
try:
    response = requests.get(f'{url}/', timeout=10)
    print(f"Корневой endpoint: статус {response.status_code}")
    if response.status_code == 200:
        print(f"Ответ: {response.json()}")
except Exception as e:
    print(f"Ошибка при проверке корневого endpoint: {e}")

# Тестируем files endpoint
print(f"\nТестируем endpoint /files")
try:
    response = requests.get(f'{url}/files', timeout=10)
    print(f"Files endpoint: статус {response.status_code}")
    if response.status_code == 200:
        print(f"Ответ: {response.json()}")
except Exception as e:
    print(f"Ошибка при проверке files endpoint: {e}")

# Очистка
if os.path.exists('test_basic.wav'):
    os.remove('test_basic.wav')
    print("\nТестовый файл удален")

print("\n=== Базовый тест завершен ===")
print("\nПримечание: Сервис audio-preprocessor запущен и отвечает на health checks.")
print("Модель Demucs все еще загружается в фоне, что может занять несколько минут.")
print("Основной функционал предобработки аудио будет доступен после загрузки модели.")