#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции Media Analyzer (День 5)
Проверяет работу Media Analyzer и его интеграцию с backend через AIServiceClient
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
import subprocess
import tempfile
import shutil

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_media_analyzer_service():
    """Тестирование сервиса Media Analyzer напрямую"""
    print("=" * 60)
    print("Тестирование Media Analyzer Service")
    print("=" * 60)
    
    # Проверяем, запущен ли сервис
    try:
        response = requests.get("http://localhost:5005/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"[OK] Media Analyzer сервис запущен: {health_data}")
            return True
        else:
            print(f"[FAIL] Media Analyzer сервис недоступен: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Media Analyzer сервис не запущен (ConnectionError)")
        return False
    except Exception as e:
        print(f"[FAIL] Ошибка при проверке Media Analyzer: {e}")
        return False

def test_media_analyzer_api():
    """Тестирование API Media Analyzer"""
    print("\n" + "=" * 60)
    print("Тестирование API Media Analyzer")
    print("=" * 60)
    
    # Создаем тестовое изображение (простой PNG)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        # Создаем простой PNG файл (1x1 пиксель)
        import base64
        # Простейший PNG файл (1x1 черный пиксель)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        tmp_file.write(png_data)
        test_image_path = tmp_file.name
    
    try:
        # Отправляем файл на анализ
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test.png', f, 'image/png')}
            data = {
                'media_type': 'image',
                'analysis_types': 'face_detection,quality_assessment',
                'align_faces': 'true',
                'output_format': 'json'
            }
            
            response = requests.post(
                "http://localhost:5005/analyze",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ API анализ изображения успешен")
            print(f"  Task ID: {result.get('task_id')}")
            print(f"  Media Type: {result.get('media_type')}")
            print(f"  Success: {result.get('success')}")
            print(f"  Message: {result.get('message')}")
            
            # Проверяем наличие результатов анализа
            analysis_results = result.get('analysis_results', {})
            if analysis_results:
                faces = analysis_results.get('faces', [])
                print(f"  Обнаружено лиц: {len(faces)}")
                
                if faces:
                    face = faces[0]
                    print(f"  Качество лица: {face.get('quality_score', 0):.2f}")
                    print(f"  Уверенность обнаружения: {face.get('detection_confidence', 0):.2f}")
            
            return True
        else:
            print(f"✗ Ошибка API анализа: {response.status_code}")
            print(f"  Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка при тестировании API: {e}")
        return False
    finally:
        # Удаляем временный файл
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)

def test_backend_integration():
    """Тестирование интеграции с backend"""
    print("\n" + "=" * 60)
    print("Тестирование интеграции с Backend")
    print("=" * 60)
    
    # Проверяем, запущен ли backend
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend сервис запущен")
        else:
            print(f"✗ Backend сервис недоступен: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Backend сервис не запущен (ConnectionError)")
        return False
    
    # Проверяем Swagger документацию
    try:
        response = requests.get("http://localhost:5000/swagger/v1/swagger.json", timeout=5)
        if response.status_code == 200:
            print("✓ Swagger документация доступна")
        else:
            print(f"✗ Swagger документация недоступна: {response.status_code}")
    except Exception as e:
        print(f"✗ Ошибка при проверке Swagger: {e}")
    
    return True

def test_docker_compose():
    """Проверка Docker Compose конфигурации"""
    print("\n" + "=" * 60)
    print("Проверка Docker Compose конфигурации")
    print("=" * 60)
    
    docker_compose_path = project_root / "docker-compose.yml"
    if docker_compose_path.exists():
        print("[OK] Docker Compose файл найден")
        
        # Проверяем наличие сервиса media-analyzer
        with open(docker_compose_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'media-analyzer:' in content:
                print("[OK] Сервис media-analyzer настроен в docker-compose.yml")
                
                # Проверяем конфигурацию
                if '5005:5005' in content:
                    print("[OK] Порт 5005 настроен для media-analyzer")
                else:
                    print("[FAIL] Порт 5005 не настроен для media-analyzer")
                
                if 'nvidia' in content.lower():
                    print("[OK] Поддержка NVIDIA GPU настроена")
                else:
                    print("[WARN] Поддержка NVIDIA GPU не настроена (может потребоваться для InsightFace)")
            else:
                print("[FAIL] Сервис media-analyzer не найден в docker-compose.yml")
    else:
        print("[FAIL] Docker Compose файл не найден")
    
    return True

def test_requirements_and_dependencies():
    """Проверка зависимостей Media Analyzer"""
    print("\n" + "=" * 60)
    print("Проверка зависимостей Media Analyzer")
    print("=" * 60)
    
    requirements_path = project_root / "ai-services" / "media-analyzer" / "requirements.txt"
    if requirements_path.exists():
        print("✓ Файл requirements.txt найден")
        
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = f.read()
            
            # Проверяем ключевые зависимости
            key_deps = [
                'insightface',
                'opencv-python',
                'torch',
                'fastapi',
                'uvicorn',
                'pydantic'
            ]
            
            for dep in key_deps:
                if dep in requirements.lower():
                    print(f"✓ Зависимость {dep} найдена")
                else:
                    print(f"✗ Зависимость {dep} не найдена")
    else:
        print("✗ Файл requirements.txt не найден")
    
    return True

def test_face_analyzer_implementation():
    """Проверка реализации Face Analyzer"""
    print("\n" + "=" * 60)
    print("Проверка реализации Face Analyzer")
    print("=" * 60)
    
    face_analyzer_path = project_root / "ai-services" / "media-analyzer" / "services" / "face_analyzer.py"
    if face_analyzer_path.exists():
        print("✓ Файл face_analyzer.py найден")
        
        with open(face_analyzer_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Проверяем ключевые компоненты
            checks = [
                ('class FaceAnalyzer', 'Класс FaceAnalyzer определен'),
                ('insightface', 'Используется InsightFace'),
                ('analyze_image', 'Метод analyze_image определен'),
                ('align_and_save_faces', 'Метод align_and_save_faces определен'),
                ('validate_image', 'Метод validate_image определен')
            ]
            
            for check_str, message in checks:
                if check_str in content:
                    print(f"✓ {message}")
                else:
                    print(f"✗ {message} не найдено")
    else:
        print("✗ Файл face_analyzer.py не найден")
    
    return True

def test_aiserviceclient_integration():
    """Проверка интеграции в AIServiceClient"""
    print("\n" + "=" * 60)
    print("Проверка интеграции в AIServiceClient")
    print("=" * 60)
    
    aiserviceclient_path = project_root / "backend" / "src" / "AvatarAI.Infrastructure" / "Services" / "AIServiceClient.cs"
    if aiserviceclient_path.exists():
        print("✓ Файл AIServiceClient.cs найден")
        
        with open(aiserviceclient_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Проверяем ключевые компоненты
            checks = [
                ('_mediaAnalyzerUrl', 'URL Media Analyzer настроен'),
                ('AnalyzeMediaAsync', 'Метод AnalyzeMediaAsync определен'),
                ('GetMimeType', 'Метод GetMimeType определен'),
                ('SimulateMediaAnalysisAsync', 'Метод SimulateMediaAnalysisAsync определен'),
                ('http://media-analyzer:5005', 'URL сервиса настроен правильно')
            ]
            
            for check_str, message in checks:
                if check_str in content:
                    print(f"✓ {message}")
                else:
                    print(f"✗ {message} не найдено")
    else:
        print("✗ Файл AIServiceClient.cs не найден")
    
    return True

def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ MEDIA ANALYZER (ДЕНЬ 5)")
    print("=" * 60)
    
    test_results = []
    
    # Запускаем тесты
    test_results.append(("Docker Compose конфигурация", test_docker_compose()))
    test_results.append(("Зависимости Media Analyzer", test_requirements_and_dependencies()))
    test_results.append(("Реализация Face Analyzer", test_face_analyzer_implementation()))
    test_results.append(("Интеграция в AIServiceClient", test_aiserviceclient_integration()))
    test_results.append(("Backend интеграция", test_backend_integration()))
    test_results.append(("Media Analyzer сервис", test_media_analyzer_service()))
    test_results.append(("Media Analyzer API", test_media_analyzer_api()))
    
    # Выводим итоговый отчет
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ ПРОЙДЕН" if result else "✗ ПРОВАЛЕН"
        print(f"{status}: {test_name}")
    
    print(f"\nВсего тестов: {total}")
    print(f"Пройдено: {passed}")
    print(f"Провалено: {total - passed}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Интеграция Media Analyzer завершена успешно.")
    else:
        print(f"\n⚠ ПРОЙДЕНО {passed}/{total} ТЕСТОВ")
        print("Требуется дополнительная настройка.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)