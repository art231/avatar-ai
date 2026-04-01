#!/usr/bin/env python3
"""
Простой скрипт для исправления проблемы с TOS для XTTS v2.
"""

import os
import sys
import subprocess
import tempfile

def create_tts_script():
    """Создать скрипт для загрузки TTS модели."""
    script = '''
import os
import sys

# Устанавливаем переменные окружения
os.environ['COQUI_TOS_AGREED'] = '1'

# Monkey-patch input для автоматического ответа 'y'
import builtins
original_input = builtins.input

def auto_input(prompt=""):
    if 'I have read, understood and agreed to the Terms and Conditions' in prompt:
        print(prompt + " y")
        return 'y'
    return original_input(prompt)

builtins.input = auto_input

try:
    from TTS.api import TTS
    print("TTS imported successfully")
    
    print("Loading XTTS v2 model...")
    # Пробуем без параметра tos_agreed, так как он может не поддерживаться
    try:
        tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=False,
            gpu=False
        )
    except TypeError:
        # Если не поддерживается параметр gpu, пробуем без него
        tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            progress_bar=False
        )
    
    print("SUCCESS: Model loaded successfully!")
    print(f"Model: {tts}")
    
    # Проверяем основные методы
    if hasattr(tts, 'speakers'):
        print(f"Speakers: {tts.speakers}")
    if hasattr(tts, 'languages'):
        print(f"Languages: {tts.languages}")
    
    # Сохраняем маркер успешной загрузки
    with open('/tmp/xtts_loaded.txt', 'w') as f:
        f.write('OK')
    
    sys.exit(0)
    
except Exception as e:
    print(f"ERROR: Failed to load model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    return script

def main():
    """Основная функция."""
    print("=" * 60)
    print("FIXING XTTS TOS ISSUE")
    print("=" * 60)
    
    # Создаем временный файл со скриптом
    script_content = create_tts_script()
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
    temp_file.write(script_content)
    temp_file.close()
    
    script_path = temp_file.name
    print(f"Script created: {script_path}")
    
    # Копируем скрипт в контейнер
    print("\nCopying script to container...")
    copy_cmd = f'docker cp "{script_path}" avatar-ai-xtts-service:/tmp/load_model.py'
    print(f"Running: {copy_cmd}")
    
    result = subprocess.run(copy_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Copy failed: {result.stderr}")
        os.unlink(script_path)
        return False
    
    # Запускаем скрипт в контейнере
    print("\nRunning script in container...")
    run_cmd = 'docker exec avatar-ai-xtts-service python /tmp/load_model.py'
    print(f"Running: {run_cmd}")
    
    try:
        result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True, timeout=180)
        print("\nScript output:")
        print(result.stdout)
        
        if result.stderr:
            print("Script errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\nSUCCESS: Model loaded successfully!")
            
            # Перезапускаем сервис
            print("\nRestarting xtts-service...")
            subprocess.run('docker-compose restart xtts-service', shell=True, capture_output=True, text=True)
            
            # Ждем и проверяем статус
            import time
            time.sleep(10)
            
            print("\nChecking service status...")
            status_cmd = 'curl -s http://localhost:5003/status'
            result = subprocess.run(status_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Status response:")
                print(result.stdout)
                
                # Проверяем, загружена ли модель
                import json
                try:
                    status_data = json.loads(result.stdout)
                    if status_data.get('model_loaded'):
                        print("\nSUCCESS: XTTS Service is now running with loaded model!")
                        return True
                    else:
                        print("\nWARNING: Service running but model not loaded")
                        return False
                except:
                    print("\nCould not parse status response")
                    return False
            else:
                print("\nFailed to check status")
                return False
        else:
            print(f"\nFAILED: Script returned {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\nTIMEOUT: Script took too long")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        return False
    finally:
        # Удаляем временный файл
        os.unlink(script_path)

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n" + "=" * 60)
            print("FIX COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("FIX FAILED")
            print("=" * 60)
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)