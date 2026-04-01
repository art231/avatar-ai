#!/usr/bin/env python3
"""
Скрипт для исправления проблемы с согласием на условия использования XTTS v2.
Этот скрипт предварительно загружает модель с автоматическим согласием на условия.
"""

import os
import sys
import subprocess
import time

def fix_xtts_tos():
    """Исправить проблему с TOS для XTTS v2."""
    print("=== Исправление проблемы с TOS для XTTS v2 ===")
    
    # Создаем скрипт для загрузки модели с автоматическим согласием
    script_content = '''
import os
import sys
import io

# Устанавливаем переменные окружения
os.environ['COQUI_TOS_AGREED'] = '1'

# Перенаправляем стандартный ввод для автоматического ответа 'y'
class AutoInput:
    def __init__(self):
        self.buffer = io.StringIO()
        
    def write(self, text):
        # Если видим запрос на согласие, автоматически отвечаем 'y'
        if 'I have read, understood and agreed to the Terms and Conditions' in text:
            return 'y'
        return text

# Монkey-patch input для автоматического ответа
original_input = __builtins__.input
def auto_input(prompt=""):
    if 'I have read, understood and agreed to the Terms and Conditions' in prompt:
        print(prompt + " y")
        return 'y'
    return original_input(prompt)

__builtins__.input = auto_input

try:
    from TTS.api import TTS
    print("Импорт TTS успешен")
    
    # Пытаемся загрузить модель
    print("Попытка загрузки модели XTTS v2...")
    tts = TTS(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        progress_bar=False,
        gpu=False,
        tos_agreed=True
    )
    
    print("УСПЕХ: Модель загружена успешно!")
    print(f"Информация о модели: {tts}")
    
    # Сохраняем информацию о успешной загрузке
    with open('/tmp/xtts_model_loaded.txt', 'w') as f:
        f.write('Model loaded successfully at: ' + str(time.time()))
        
except Exception as e:
    print(f"ОШИБКА: Не удалось загрузить модель: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

    # Записываем скрипт во временный файл (используем временную директорию Windows)
    import tempfile
    temp_dir = tempfile.gettempdir()
    script_path = os.path.join(temp_dir, 'load_xtts.py')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"Скрипт создан: {script_path}")
    
    # Запускаем скрипт внутри контейнера xtts-service
    print("\nЗапуск скрипта внутри контейнера xtts-service...")
    
    # Сначала копируем скрипт в контейнер
    copy_cmd = f'docker cp "{script_path}" avatar-ai-xtts-service:/tmp/load_xtts.py'
    print(f"Выполняем: {copy_cmd}")
    result = subprocess.run(copy_cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode != 0:
        print(f"Ошибка копирования скрипта: {result.stderr}")
        return False
    
    # Теперь запускаем скрипт внутри контейнера
    run_cmd = 'docker exec avatar-ai-xtts-service python /tmp/load_xtts.py'
    print(f"Выполняем: {run_cmd}")
    
    # Запускаем с таймаутом
    try:
        result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True, timeout=120)
        print("Вывод скрипта:")
        print(result.stdout)
        
        if result.stderr:
            print("Ошибки:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✓ Модель XTTS v2 успешно загружена с согласием на условия!")
            return True
        else:
            print(f"\n✗ Ошибка загрузки модели: код возврата {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ Таймаут при загрузке модели")
        return False
    except Exception as e:
        print(f"\n✗ Неожиданная ошибка: {e}")
        return False

def restart_xtts_service():
    """Перезапустить xtts-service."""
    print("\n=== Перезапуск xtts-service ===")
    
    # Останавливаем сервис
    stop_cmd = 'docker-compose stop xtts-service'
    print(f"Выполняем: {stop_cmd}")
    result = subprocess.run(stop_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Ошибка остановки сервиса: {result.stderr}")
        return False
    
    # Запускаем сервис
    start_cmd = 'docker-compose up -d xtts-service'
    print(f"Выполняем: {start_cmd}")
    result = subprocess.run(start_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Ошибка запуска сервиса: {result.stderr}")
        return False
    
    # Ждем запуска
    print("Ожидание запуска сервиса...")
    time.sleep(10)
    
    # Проверяем статус
    status_cmd = 'curl -s http://localhost:5003/status | python -c "import json, sys; data = json.load(sys.stdin); print(\"Model loaded:\", data.get(\"model_loaded\", \"unknown\"))"'
    print(f"Проверка статуса: {status_cmd}")
    result = subprocess.run(status_cmd, shell=True, capture_output=True, text=True)
    
    print("Результат проверки статуса:")
    print(result.stdout)
    
    if result.returncode == 0 and 'Model loaded: True' in result.stdout:
        print("\n✓ xtts-service успешно перезапущен с загруженной моделью!")
        return True
    else:
        print("\n✗ Модель все еще не загружена после перезапуска")
        return False

def main():
    """Основная функция."""
    print("=" * 60)
    print("ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С TOS ДЛЯ XTTS v2")
    print("=" * 60)
    
    # Шаг 1: Предварительная загрузка модели с согласием
    if not fix_xtts_tos():
        print("\n✗ Не удалось исправить проблему с TOS")
        return False
    
    # Шаг 2: Перезапуск сервиса
    if not restart_xtts_service():
        print("\n✗ Не удалось перезапустить сервис")
        return False
    
    print("\n" + "=" * 60)
    print("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    print("=" * 60)
    print("XTTS Service теперь должен работать с реальной моделью.")
    print("Проверьте статус: curl http://localhost:5003/status")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)