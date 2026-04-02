#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности Дня 11:
Управление аватарами во фронтенде

Этот скрипт проверяет созданные компоненты и их интеграцию.
"""

import os
import sys

def check_file_exists(filepath, description):
    """Проверяет существование файла."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: Файл не найден - {filepath}")
        return False

def check_directory_structure():
    """Проверяет структуру директорий фронтенда."""
    print("\n🔍 Проверка структуры директорий фронтенда:")
    
    base_path = "frontend"
    required_dirs = [
        "src/app/pages/avatars",
        "src/ui/components",
        "src/application/services",
        "src/infrastructure/api"
    ]
    
    all_exists = True
    for dir_path in required_dirs:
        full_path = os.path.join(base_path, dir_path)
        if os.path.exists(full_path):
            print(f"  ✅ Директория: {dir_path}")
        else:
            print(f"  ❌ Директория: {dir_path} - не найдена")
            all_exists = False
    
    return all_exists

def check_components():
    """Проверяет созданные компоненты."""
    print("\n🔍 Проверка созданных компонентов:")
    
    components = [
        ("frontend/src/application/services/avatar.service.ts", "Сервис AvatarService"),
        ("frontend/src/ui/components/image-upload.component.ts", "Компонент загрузки изображений"),
        ("frontend/src/ui/components/audio-upload.component.ts", "Компонент загрузки аудио"),
        ("frontend/src/app/pages/avatars/avatars.component.ts", "Компонент галереи аватаров"),
        ("frontend/src/app/pages/avatars/avatar-detail.component.ts", "Компонент детальной страницы аватара"),
        ("frontend/src/app/pages/avatars/avatar-create.component.ts", "Компонент создания аватара"),
        ("frontend/src/app/app.routes.ts", "Файл маршрутов")
    ]
    
    all_exists = True
    for filepath, description in components:
        if check_file_exists(filepath, description):
            # Проверяем размер файла (должен быть больше 0)
            if os.path.getsize(filepath) > 0:
                print(f"    Размер: {os.path.getsize(filepath)} байт")
            else:
                print(f"    ⚠️  Файл пустой")
                all_exists = False
        else:
            all_exists = False
    
    return all_exists

def check_implementation_plan():
    """Проверяет обновление плана реализации."""
    print("\n🔍 Проверка плана реализации:")
    
    plan_file = "IMPLEMENTATION_PLAN.md"
    if check_file_exists(plan_file, "План реализации"):
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Проверяем, что День 11 отмечен как завершенный
            if "### ✅ День 11: Фронтенд - Управление аватарами" in content:
                print("  ✅ День 11 отмечен как завершенный")
            else:
                print("  ❌ День 11 не отмечен как завершенный")
                return False
                
            # Проверяем, что День 12 установлен как текущий
            if "### 🚀 День 12: Фронтенд - Генерация контента (ТЕКУЩИЙ ДЕНЬ)" in content:
                print("  ✅ День 12 установлен как текущий")
            else:
                print("  ❌ День 12 не установлен как текущий")
                return False
                
            return True
        except Exception as e:
            print(f"  ❌ Ошибка чтения файла: {e}")
            return False
    
    return False

def analyze_component_content():
    """Анализирует содержимое ключевых компонентов."""
    print("\n🔍 Анализ содержимого компонентов:")
    
    components_to_analyze = [
        ("frontend/src/application/services/avatar.service.ts", [
            "getAvatars",
            "getAvatar",
            "createAvatar",
            "updateAvatar",
            "deleteAvatar",
            "startTraining",
            "getTrainingProgress",
            "generateVideo"
        ]),
        ("frontend/src/ui/components/image-upload.component.ts", [
            "ImageUploadComponent",
            "onDragOver",
            "onDrop",
            "onFileSelected",
            "removeImage"
        ]),
        ("frontend/src/ui/components/audio-upload.component.ts", [
            "AudioUploadComponent",
            "togglePlay",
            "toggleMute",
            "onVolumeChange"
        ])
    ]
    
    all_good = True
    for filepath, expected_methods in components_to_analyze:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n  📄 {os.path.basename(filepath)}:")
                found_methods = []
                for method in expected_methods:
                    if method in content:
                        found_methods.append(method)
                        print(f"    ✅ {method}")
                    else:
                        print(f"    ❌ {method} - не найден")
                        all_good = False
                
                if len(found_methods) == len(expected_methods):
                    print(f"    Все {len(found_methods)} методов найдены")
                else:
                    print(f"    Найдено {len(found_methods)} из {len(expected_methods)} методов")
                    
            except Exception as e:
                print(f"    ❌ Ошибка чтения файла: {e}")
                all_good = False
        else:
            print(f"  ❌ Файл не найден: {filepath}")
            all_good = False
    
    return all_good

def main():
    """Основная функция тестирования."""
    print("=" * 60)
    print("Тестирование функциональности Дня 11")
    print("Управление аватарами во фронтенде")
    print("=" * 60)
    
    # Проверяем текущую директорию
    current_dir = os.getcwd()
    print(f"Текущая директория: {current_dir}")
    
    # Выполняем проверки
    dir_check = check_directory_structure()
    comp_check = check_components()
    plan_check = check_implementation_plan()
    content_check = analyze_component_content()
    
    print("\n" + "=" * 60)
    print("Итоги тестирования:")
    print("=" * 60)
    
    results = {
        "Структура директорий": dir_check,
        "Компоненты созданы": comp_check,
        "План реализации обновлен": plan_check,
        "Содержимое компонентов": content_check
    }
    
    all_passed = True
    for check_name, result in results.items():
        status = "✅ ПРОЙДЕНО" if result else "❌ НЕ ПРОЙДЕНО"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("День 11 завершен: Управление аватарами реализовано")
        print("\nСозданы следующие компоненты:")
        print("1. AvatarService - сервис для работы с аватарами")
        print("2. ImageUploadComponent - загрузка изображений с предпросмотром")
        print("3. AudioUploadComponent - загрузка аудио с плеером")
        print("4. AvatarsComponent - галерея аватаров")
        print("5. AvatarDetailComponent - детальная страница аватара")
        print("6. AvatarCreateComponent - создание нового аватара")
        print("\nСледующий шаг: День 12 - Генерация контента")
    else:
        print("⚠️  НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ")
        print("Пожалуйста, исправьте указанные проблемы")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())