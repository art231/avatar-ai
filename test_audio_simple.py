import requests
import json
import os
import time

print("=== Простой тест Audio Preprocessor API ===")

# Сначала создаем тестовый файл
import numpy as np
import soundfile as sf

sample_rate = 22050
duration = 5.0
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = 0.5 * np.sin(2 * np.pi * 440 * t)
sf.write('test_simple.wav', audio, sample_rate, subtype='PCM_16')

print(f"Создан тестовый файл: test_simple.wav")
print(f"Размер: {os.path.getsize('test_simple.wav')} байт")

# Проверяем доступность сервиса
url = 'http://localhost:5004'
health_url = f'{url}/health'

print(f"\nПроверяем доступность сервиса по адресу: {health_url}")

try:
    # Проверяем health endpoint
    response = requests.get(health_url, timeout=10)
    print(f"Health check: статус {response.status_code}")
    if response.status_code == 200:
        print(f"Ответ: {response.json()}")
    else:
        print(f"Ошибка: {response.text}")
        exit(1)
        
except requests.exceptions.ConnectionError:
    print("Не удалось подключиться к сервису. Убедитесь, что audio-preprocessor запущен.")
    print("Проверьте: docker-compose ps | findstr audio-preprocessor")
    exit(1)
except Exception as e:
    print(f"Ошибка при проверке health: {e}")
    exit(1)

# Тестируем основной endpoint
preprocess_url = f'{url}/preprocess'
print(f"\nТестируем endpoint: {preprocess_url}")

try:
    with open('test_simple.wav', 'rb') as f:
        files = {'file': ('test_simple.wav', f, 'audio/wav')}
        data = {
            'sample_rate': '22050',
            'remove_silence': 'true',
            'normalize_loudness': 'true',
            'target_lufs': '-23.0'
        }
        
        print("Отправляем запрос на предобработку аудио...")
        start_time = time.time()
        response = requests.post(preprocess_url, files=files, data=data, timeout=120)
        elapsed = time.time() - start_time
        
        print(f"Время выполнения: {elapsed:.2f} секунд")
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n=== УСПЕХ ===")
            print(f"Успех: {result.get('success', 'N/A')}")
            print(f"Выходной путь: {result.get('output_path', 'N/A')}")
            print(f"Время обработки: {result.get('processing_time', 'N/A')} секунд")
            
            audio_info = result.get('audio_info', {})
            if audio_info:
                print(f"\nИнформация об аудио:")
                print(f"  Частота дискретизации: {audio_info.get('sample_rate', 'N/A')} Гц")
                print(f"  Длительность: {audio_info.get('duration_seconds', 'N/A')} секунд")
                print(f"  Формат: {audio_info.get('format', 'N/A')}")
                
                quality_metrics = audio_info.get('quality_metrics', {})
                if quality_metrics:
                    print(f"  SNR: {quality_metrics.get('snr_db', 'N/A')} дБ")
                    print(f"  Пиковый уровень: {quality_metrics.get('peak_level_db', 'N/A')} дБFS")
                    print(f"  Громкость (LUFS): {quality_metrics.get('integrated_loudness', 'N/A')} LUFS")
                    print(f"  Процент клиппинга: {quality_metrics.get('clipping_percentage', 'N/A')}%")
                    print(f"  Проверка качества пройдена: {quality_metrics.get('quality_check_passed', 'N/A')}")
            
            print(f"\nСообщение: {result.get('message', 'N/A')}")
            
        else:
            print(f"\n=== ОШИБКА ===")
            print(f"Статус: {response.status_code}")
            print(f"Ответ: {response.text}")
            
except Exception as e:
    print(f"\n=== ИСКЛЮЧЕНИЕ ===")
    print(f"Тип: {type(e).__name__}")
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()

# Очистка
if os.path.exists('test_simple.wav'):
    os.remove('test_simple.wav')
    print("\nТестовый файл удален")

print("\n=== Тест завершен ===")