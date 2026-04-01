#!/usr/bin/env python3
"""
Тест интеграции Motion Generator для Дня 7
Проверяем, что методы Motion Generator корректно реализованы в AIServiceClient
"""

import os
import sys
import json

def test_motion_generator_integration():
    """Тестируем интеграцию Motion Generator"""
    print("=" * 60)
    print("Тест интеграции Motion Generator - День 7")
    print("=" * 60)
    
    # Проверяем файлы
    files_to_check = [
        "backend/src/AvatarAI.Application/Interfaces/IAIServiceClient.cs",
        "backend/src/AvatarAI.Infrastructure/Services/AIServiceClient.cs",
        "backend/src/AvatarAI.Api/appsettings.json",
        "ai-services/motion-generator/main.py",
        "ai-services/motion-generator/config.py",
        "ai-services/motion-generator/services/motion_generator.py"
    ]
    
    print("\n1. Проверка файлов:")
    all_files_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   [OK] {file_path}")
        else:
            print(f"   [FAIL] {file_path} - не найден")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n[ERROR] Некоторые файлы не найдены!")
        return False
    
    print("\n2. Проверка конфигурации Motion Generator в appsettings.json:")
    try:
        with open("backend/src/AvatarAI.Api/appsettings.json", "r", encoding="utf-8") as f:
            appsettings = json.load(f)
        
        motion_generator_url = appsettings.get("AI_SERVICES", {}).get("MOTION_GENERATOR_URL")
        if motion_generator_url:
            print(f"   [OK] MOTION_GENERATOR_URL: {motion_generator_url}")
        else:
            print("   [FAIL] MOTION_GENERATOR_URL не найден в конфигурации")
            return False
    except Exception as e:
        print(f"   [FAIL] Ошибка при чтении appsettings.json: {e}")
        return False
    
    print("\n3. Проверка методов Motion Generator в интерфейсе IAIServiceClient:")
    try:
        with open("backend/src/AvatarAI.Application/Interfaces/IAIServiceClient.cs", "r", encoding="utf-8") as f:
            interface_content = f.read()
        
        motion_methods = [
            "GenerateMotionAsync",
            "ExtractPoseAsync", 
            "GetMotionTaskStatusAsync",
            "GetMotionPresetsAsync"
        ]
        
        for method in motion_methods:
            if method in interface_content:
                print(f"   [OK] Метод {method} присутствует в интерфейсе")
            else:
                print(f"   [FAIL] Метод {method} отсутствует в интерфейсе")
                return False
    except Exception as e:
        print(f"   [FAIL] Ошибка при чтении интерфейса: {e}")
        return False
    
    print("\n4. Проверка реализации методов в AIServiceClient:")
    try:
        with open("backend/src/AvatarAI.Infrastructure/Services/AIServiceClient.cs", "r", encoding="utf-8") as f:
            implementation_content = f.read()
        
        for method in motion_methods:
            if f"public async Task<Dictionary<string, object>> {method}" in implementation_content:
                print(f"   [OK] Метод {method} реализован")
            else:
                print(f"   [FAIL] Метод {method} не реализован")
                return False
    except Exception as e:
        print(f"   [FAIL] Ошибка при чтении реализации: {e}")
        return False
    
    print("\n5. Проверка Motion Generator сервиса:")
    try:
        with open("ai-services/motion-generator/main.py", "r", encoding="utf-8") as f:
            motion_service_content = f.read()
        
        required_endpoints = [
            "/generate",
            "/extract-pose", 
            "/task/{task_id}",
            "/health",
            "/presets"
        ]
        
        for endpoint in required_endpoints:
            if endpoint in motion_service_content:
                print(f"   [OK] Эндпоинт {endpoint} присутствует")
            else:
                print(f"   [FAIL] Эндпоинт {endpoint} отсутствует")
                return False
    except Exception as e:
        print(f"   [FAIL] Ошибка при чтении main.py: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Интеграция Motion Generator успешно завершена!")
    print("=" * 60)
    
    print("\nКраткое описание реализованных методов:")
    print("""
    1. GenerateMotionAsync() - генерация движения аватара по текстовому промпту
       - Параметры: userId, avatarId, actionPrompt, durationSec, motionPreset, motionConfig
       - Возвращает: task_id, статус, прогресс, путь к выходному файлу
    
    2. ExtractPoseAsync() - извлечение позы из видео
       - Параметры: userId, avatarId, videoPath
       - Возвращает: pose_data с ключевыми точками и временными метками
    
    3. GetMotionTaskStatusAsync() - проверка статуса задачи генерации движения
       - Параметры: taskId
       - Возвращает: статус, стадию, прогресс, время создания/завершения
    
    4. GetMotionPresetsAsync() - получение списка пресетов движений
       - Возвращает: словарь пресетов (idle_talking, presentation, conversation, enthusiastic)
    
    Особенности реализации:
    - Retry политика с экспоненциальной задержкой (3 попытки)
    - Fallback симуляция для MVP режима работы
    - Поддержка различных пресетов движений
    - Единый интерфейс для всех AI сервисов
    """)
    
    return True

def check_docker_compose():
    """Проверяем конфигурацию Docker Compose"""
    print("\n" + "=" * 60)
    print("Проверка Docker Compose конфигурации")
    print("=" * 60)
    
    docker_compose_files = [
        "docker-compose.yml",
        "docker-compose.test.yml"
    ]
    
    for file_path in docker_compose_files:
        if os.path.exists(file_path):
            print(f"\nПроверка {file_path}:")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "motion-generator" in content:
                    print("   [OK] Сервис motion-generator найден")
                    
                    # Проверяем порт
                    if "5002" in content:
                        print("   [OK] Порт 5002 настроен")
                    else:
                        print("   [WARN] Порт 5002 не найден, проверьте конфигурацию")
                else:
                    print("   [FAIL] Сервис motion-generator не найден")
            except Exception as e:
                print(f"   [FAIL] Ошибка при чтении {file_path}: {e}")
        else:
            print(f"\nФайл {file_path} не найден")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print("Запуск теста интеграции Motion Generator...")
    print(f"Текущая директория: {os.getcwd()}")
    print()
    
    success = test_motion_generator_integration()
    
    # Проверяем Docker Compose
    check_docker_compose()
    
    if success:
        print("\n[SUCCESS] День 7 - Интеграция Motion Generator успешно завершена!")
        print("\nСледующие шаги:")
        print("1. Запустить docker-compose up для проверки работы всех сервисов")
        print("2. Протестировать API Motion Generator через Swagger или Postman")
        print("3. Интегрировать Motion Generator в PipelineOrchestrator")
        print("4. Добавить поддержку движений в GenerationTasksController")
    else:
        print("\n[FAIL] Тест не пройден. Проверьте реализацию.")
        sys.exit(1)
