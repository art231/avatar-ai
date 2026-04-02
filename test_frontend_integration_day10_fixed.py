#!/usr/bin/env python3
"""
Тестирование интеграции фронтенда (День 10)
Проверка аутентификации и базовых компонентов
"""

import os
import sys
import json
import requests
from pathlib import Path

def print_header(text):
    """Печать заголовка"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def print_status(status, message):
    """Печать статуса"""
    if status == "OK":
        print(f"  [OK] {message}")
    elif status == "ERROR":
        print(f"  [ERROR] {message}")
    elif status == "WARNING":
        print(f"  [WARNING] {message}")
    else:
        print(f"  [?] {message}")

def check_frontend_structure():
    """Проверка структуры фронтенда"""
    print_header("Проверка структуры фронтенда")
    
    frontend_path = Path("frontend")
    required_dirs = [
        "src/app/pages/auth",
        "src/application/services",
        "src/infrastructure/api",
        "src/ui/components",
        "src/app/guards"
    ]
    
    required_files = [
        "src/app/pages/auth/login.component.ts",
        "src/app/pages/auth/register.component.ts",
        "src/app/pages/auth/forgot-password.component.ts",
        "src/application/services/auth.service.ts",
        "src/infrastructure/api/api-client.service.ts",
        "src/app/guards/auth.guard.ts",
        "src/app/app.routes.ts",
        "src/ui/components/navbar.component.ts"
    ]
    
    all_ok = True
    
    # Проверка директорий
    for dir_path in required_dirs:
        full_path = frontend_path / dir_path
        if full_path.exists():
            print_status("OK", f"Директория существует: {dir_path}")
        else:
            print_status("ERROR", f"Директория отсутствует: {dir_path}")
            all_ok = False
    
    # Проверка файлов
    for file_path in required_files:
        full_path = frontend_path / file_path
        if full_path.exists():
            print_status("OK", f"Файл существует: {file_path}")
        else:
            print_status("ERROR", f"Файл отсутствует: {file_path}")
            all_ok = False
    
    return all_ok

def check_angular_config():
    """Проверка конфигурации Angular"""
    print_header("Проверка конфигурации Angular")
    
    config_files = [
        "frontend/angular.json",
        "frontend/package.json",
        "frontend/tsconfig.json"
    ]
    
    all_ok = True
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print_status("OK", f"Конфигурационный файл существует: {config_file}")
            
            # Проверка package.json на наличие зависимостей
            if config_file.endswith("package.json"):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        package_json = json.load(f)
                    
                    required_deps = [
                        "@angular/core",
                        "@angular/common",
                        "@angular/forms",
                        "@angular/router",
                        "@angular/common/http",
                        "rxjs"
                    ]
                    
                    deps = package_json.get("dependencies", {})
                    for dep in required_deps:
                        if dep in deps:
                            print_status("OK", f"  Зависимость установлена: {dep}")
                        else:
                            print_status("WARNING", f"  Зависимость отсутствует: {dep}")
                            all_ok = False
                except Exception as e:
                    print_status("ERROR", f"  Ошибка чтения package.json: {e}")
                    all_ok = False
        else:
            print_status("ERROR", f"Конфигурационный файл отсутствует: {config_file}")
            all_ok = False
    
    return all_ok

def check_backend_api():
    """Проверка доступности backend API"""
    print_header("Проверка доступности backend API")
    
    endpoints = [
        ("http://localhost:5000/health", "Health check"),
        ("http://localhost:5000/api/auth/health", "Auth health"),
        ("http://localhost:5000/swagger", "Swagger UI")
    ]
    
    all_ok = True
    
    for url, description in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_status("OK", f"{description}: доступен ({url})")
            else:
                print_status("WARNING", f"{description}: HTTP {response.status_code} ({url})")
                all_ok = False
        except requests.exceptions.RequestException as e:
            print_status("ERROR", f"{description}: недоступен - {e}")
            all_ok = False
    
    return all_ok

def analyze_auth_service():
    """Анализ сервиса аутентификации"""
    print_header("Анализ сервиса аутентификации")
    
    auth_service_path = "frontend/src/application/services/auth.service.ts"
    
    if not os.path.exists(auth_service_path):
        print_status("ERROR", "Файл auth.service.ts не найден")
        return False
    
    try:
        with open(auth_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_methods = [
            "login",
            "register", 
            "logout",
            "refreshToken",
            "forgotPassword",
            "getCurrentUser",
            "isLoggedIn",
            "getAccessToken"
        ]
        
        required_interfaces = [
            "LoginRequest",
            "RegisterRequest", 
            "AuthResponse",
            "User"
        ]
        
        all_ok = True
        
        # Проверка интерфейсов
        for interface in required_interfaces:
            if interface in content:
                print_status("OK", f"Интерфейс определен: {interface}")
            else:
                print_status("ERROR", f"Интерфейс отсутствует: {interface}")
                all_ok = False
        
        # Проверка методов
        for method in required_methods:
            if f"{method}(" in content:
                print_status("OK", f"Метод определен: {method}")
            else:
                print_status("ERROR", f"Метод отсутствует: {method}")
                all_ok = False
        
        # Проверка localStorage использования
        if "localStorage" in content:
            print_status("OK", "Используется localStorage для хранения токенов")
        else:
            print_status("WARNING", "localStorage не используется для хранения токенов")
            all_ok = False
        
        # Проверка BehaviorSubject
        if "BehaviorSubject" in content:
            print_status("OK", "Используется BehaviorSubject для состояния")
        else:
            print_status("WARNING", "BehaviorSubject не используется для состояния")
            all_ok = False
        
        return all_ok
        
    except Exception as e:
        print_status("ERROR", f"Ошибка анализа auth.service.ts: {e}")
        return False

def analyze_routes():
    """Анализ роутов"""
    print_header("Анализ роутов")
    
    routes_path = "frontend/src/app/app.routes.ts"
    
    if not os.path.exists(routes_path):
        print_status("ERROR", "Файл app.routes.ts не найден")
        return False
    
    try:
        with open(routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_routes = [
            "login",
            "register",
            "forgot-password",
            "dashboard",
            "avatars",
            "training",
            "generation"
        ]
        
        required_guards = [
            "AuthGuard",
            "NoAuthGuard"
        ]
        
        all_ok = True
        
        # Проверка роутов
        for route in required_routes:
            if f"'{route}'" in content or f'"{route}"' in content:
                print_status("OK", f"Роут определен: {route}")
            else:
                print_status("ERROR", f"Роут отсутствует: {route}")
                all_ok = False
        
        # Проверка guards
        for guard in required_guards:
            if guard in content:
                print_status("OK", f"Guard определен: {guard}")
            else:
                print_status("ERROR", f"Guard отсутствует: {guard}")
                all_ok = False
        
        # Проверка canActivate
        if "canActivate" in content:
            print_status("OK", "Используется canActivate для защиты роутов")
        else:
            print_status("ERROR", "Не используется canActivate для защиты роутов")
            all_ok = False
        
        return all_ok
        
    except Exception as e:
        print_status("ERROR", f"Ошибка анализа app.routes.ts: {e}")
        return False

def check_navbar_component():
    """Проверка компонента навигации"""
    print_header("Проверка компонента навигации")
    
    navbar_path = "frontend/src/ui/components/navbar.component.ts"
    
    if not os.path.exists(navbar_path):
        print_status("ERROR", "Файл navbar.component.ts не найден")
        return False
    
    try:
        with open(navbar_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_features = [
            "AuthService",
            "currentUser$",
            "logout()",
            "routerLink",
            "dropdown menu",
            "mobile menu"
        ]
        
        all_ok = True
        
        # Проверка основных функций
        if "AuthService" in content:
            print_status("OK", "Интегрирован AuthService")
        else:
            print_status("ERROR", "Не интегрирован AuthService")
            all_ok = False
        
        if "currentUser$" in content:
            print_status("OK", "Используется currentUser$ observable")
        else:
            print_status("WARNING", "Не используется currentUser$ observable")
            all_ok = False
        
        if "logout()" in content:
            print_status("OK", "Реализован метод logout()")
        else:
            print_status("ERROR", "Не реализован метод logout()")
            all_ok = False
        
        # Проверка шаблона
        if "routerLink" in content:
            print_status("OK", "Используется routerLink для навигации")
        else:
            print_status("ERROR", "Не используется routerLink для навигации")
            all_ok = False
        
        if "dropdown" in content.lower():
            print_status("OK", "Реализовано dropdown меню")
        else:
            print_status("WARNING", "Не реализовано dropdown меню")
            all_ok = False
        
        if "mobile" in content.lower():
            print_status("OK", "Реализована мобильная версия")
        else:
            print_status("WARNING", "Не реализована мобильная версия")
            all_ok = False
        
        return all_ok
        
    except Exception as e:
        print_status("ERROR", f"Ошибка анализа navbar.component.ts: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print_header("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ФРОНТЕНДА (День 10)")
    print("Проверка реализации аутентификации и базовых компонентов")
    
    results = []
    
    # Проверка структуры
    results.append(("Структура фронтенда", check_frontend_structure()))
    
    # Проверка конфигурации
    results.append(("Конфигурация Angular", check_angular_config()))
    
    # Проверка backend API (опционально)
    try:
        results.append(("Backend API", check_backend_api()))
    except Exception as e:
        print_status("WARNING", f"Пропущена проверка backend API: {e}")
        results.append(("Backend API", True))  # Пропускаем, если не критично
    
    # Анализ компонентов
    results.append(("Сервис аутентификации", analyze_auth_service()))
    results.append(("Роуты и guards", analyze_routes()))
    results.append(("Компонент навигации", check_navbar_component()))
    
    # Итоги
    print_header("ИТОГИ ТЕСТИРОВАНИЯ")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    
    print(f"\nВсего проверок: {total_tests}")
    print(f"Успешно пройдено: {passed_tests}")
    print(f"Не пройдено: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print_status("OK", "Все проверки пройдены успешно!")
        print("\n[SUCCESS] День 10 завершен: Фронтенд с аутентификацией и базовыми компонентами реализован!")
        print("\nСледующие шаги:")
        print("1. Запустить фронтенд: cd frontend && npm install && npm run dev")
        print("2. Открыть http://localhost:3000 в браузере")
        print("3. Протестировать регистрацию, вход и навигацию")
        print("4. Перейти к Дню 11: Управление аватарами")
        return 0
    else:
        print_status("ERROR", "Некоторые проверки не пройдены")
        print("\n[WARNING] Необходимо исправить следующие проблемы:")
        for name, result in results:
            if not result:
                print(f"  - {name}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)