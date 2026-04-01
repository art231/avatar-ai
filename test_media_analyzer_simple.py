#!/usr/bin/env python3
"""
Упрощенный тестовый скрипт для проверки интеграции Media Analyzer (День 5)
"""

import os
import sys
import json
import requests
from pathlib import Path
import tempfile
import base64

def test_docker_compose():
    """Проверка Docker Compose конфигурации"""
    print("\n" + "=" * 60)
    print("Проверка Docker Compose конфигурации")
    print("=" * 60)
    
    docker_compose_path = Path(__file__).parent / "docker-compose.yml"
    if docker_compose_path.exists():
        print("[OK] Docker Compose файл найден")
        
        with open(docker_compose_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'media-analyzer:' in content:
                print("[OK] Сервис media-analyzer настроен")
                if '5005:5005' in content:
                    print("[OK] Порт 5005 настроен")
                if 'nvidia' in content.lower():
                    print("[OK] Поддержка NVIDIA GPU настроена")
                return True
            else:
                print("[FAIL] Сервис media-analyzer не найден")
                return False
    else:
        print("[FAIL] Docker Compose файл не найден")
        return False

def test_requirements():
    """Проверка зависимостей"""
    print("\n" + "=" * 60)
    print("Проверка зависимостей Media Analyzer")
    print("=" * 60)
    
    req_path = Path(__file__).parent / "ai-services" / "media-analyzer" / "requirements.txt"
    if req_path.exists():
        print("[OK] Файл requirements.txt найден")
        with open(req_path, 'r', encoding='utf-8') as f:
            reqs = f.read().lower()
            for dep in ['insightface', 'opencv', 'torch', 'fastapi']:
                if dep in reqs:
                    print(f"[OK] Зависимость {dep} найдена")
                else:
                    print(f"[WARN] Зависимость {dep} не найдена")
        return True
    else:
        print("[FAIL] Файл requirements.txt не найден")
        return False

def test_face_analyzer():
    """Проверка реализации Face Analyzer"""
    print("\n" + "=" * 60)
    print("Проверка реализации Face Analyzer")
    print("=" * 60)
    
    fa_path = Path(__file__).parent / "ai-services" / "media-analyzer" / "services" / "face_analyzer.py"
    if fa_path.exists():
        print("[OK] Файл face_analyzer.py найден")
        with open(fa_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class FaceAnalyzer' in content and 'analyze_image' in content:
                print("[OK] Ключевые компоненты найдены")
                return True
            else:
                print("[FAIL] Ключевые компоненты не найдены")
                return False
    else:
        print("[FAIL] Файл face_analyzer.py не найден")
        return False

def test_aiserviceclient():
    """Проверка интеграции в AIServiceClient"""
    print("\n" + "=" * 60)
    print("Проверка интеграции в AIServiceClient")
    print("=" * 60)
    
    client_path = Path(__file__).parent / "backend" / "src" / "AvatarAI.Infrastructure" / "Services" / "AIServiceClient.cs"
    if client_path.exists():
        print("[OK] Файл AIServiceClient.cs найден")
        with open(client_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'AnalyzeMediaAsync' in content and '_mediaAnalyzerUrl' in content:
                print("[OK] Интеграция Media Analyzer настроена")
                return True
            else:
                print("[FAIL] Интеграция Media Analyzer не настроена")
                return False
    else:
        print("[FAIL] Файл AIServiceClient.cs не найден")
        return False

def test_backend_compilation():
    """Проверка компиляции backend"""
    print("\n" + "=" * 60)
    print("Проверка компиляции Backend")
    print("=" * 60)
    
    try:
        import subprocess
        result = subprocess.run(
            ["dotnet", "build", "backend/AvatarAI.sln"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("[OK] Backend успешно скомпилирован")
            return True
        else:
            print(f"[FAIL] Ошибка компиляции: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"[FAIL] Ошибка при компиляции: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ MEDIA ANALYZER (ДЕНЬ 5)")
    print("=" * 60)
    
    tests = [
        ("Docker Compose конфигурация", test_docker_compose),
        ("Зависимости Media Analyzer", test_requirements),
        ("Реализация Face Analyzer", test_face_analyzer),
        ("Интеграция в AIServiceClient", test_aiserviceclient),
        ("Компиляция Backend", test_backend_compilation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            status = "[OK]" if result else "[FAIL]"
            print(f"{status} {name}")
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "ПРОЙДЕН" if result else "ПРОВАЛЕН"
        print(f"{status}: {name}")
    
    print(f"\nВсего тестов: {total}")
    print(f"Пройдено: {passed}")
    print(f"Провалено: {total - passed}")
    
    if passed == total:
        print("\n[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Интеграция Media Analyzer завершена успешно.")
    else:
        print(f"\n[WARNING] ПРОЙДЕНО {passed}/{total} ТЕСТОВ")
        print("Требуется дополнительная настройка.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)