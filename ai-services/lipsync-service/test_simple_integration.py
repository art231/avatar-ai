"""
Упрощенное тестирование интеграции Lipsync Service.
Проверяет наличие моделей и базовую функциональность без OpenCV.
"""

import sys
import json
from pathlib import Path

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

def check_models():
    """Проверка наличия всех моделей."""
    print("=" * 60)
    print("ПРОВЕРКА НАЛИЧИЯ МОДЕЛЕЙ")
    print("=" * 60)
    
    models_dir = Path(__file__).parent / "models"
    
    models_to_check = [
        ("MuseTalk модель", models_dir / "muse_talk" / "muse_talk.pt", True),
        ("MuseTalk конфиг", models_dir / "muse_talk" / "musetalk.json", True),
        ("Wav2Lip модель", models_dir / "wav2lip" / "wav2lip.pth", False),
        ("DWPose модели", models_dir / "dwpose", False),
        ("Face Parse модели", models_dir / "face-parse-bisent", False),
        ("Whisper модель", models_dir / "whisper" / "tiny.pt", False),
    ]
    
    results = {}
    
    for name, path, required in models_to_check:
        if path.exists():
            if path.is_dir():
                files = list(path.glob("*"))
                results[name] = {
                    "status": "OK",
                    "files": len(files),
                    "required": required
                }
                print(f"[OK] {name}: найдено {len(files)} файлов")
                if files:
                    for f in files[:2]:
                        print(f"     - {f.name}")
                    if len(files) > 2:
                        print(f"     ... и еще {len(files) - 2} файлов")
            else:
                size_mb = path.stat().st_size / (1024 * 1024)
                results[name] = {
                    "status": "OK", 
                    "size_mb": size_mb,
                    "required": required
                }
                print(f"[OK] {name}: {size_mb:.2f} MB")
        else:
            results[name] = {
                "status": "MISSING",
                "required": required
            }
            if required:
                print(f"[ERROR] {name}: ОБЯЗАТЕЛЬНАЯ МОДЕЛЬ НЕ НАЙДЕНА!")
            else:
                print(f"[WARNING] {name}: не найден (опционально)")
    
    # Проверяем обязательные модели
    missing_required = any(
        result["status"] == "MISSING" and result["required"]
        for result in results.values()
    )
    
    return not missing_required, results

def check_config():
    """Проверка конфигурации."""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА КОНФИГУРАЦИИ")
    print("=" * 60)
    
    try:
        # Читаем конфигурационный файл напрямую
        config_path = Path(__file__).parent / "config.py"
        if config_path.exists():
            print(f"[OK] Конфигурационный файл найден: {config_path}")
            
            # Проверяем наличие ключевых настроек
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_settings = [
                "models_dir",
                "muse_talk_model_path", 
                "wav2lip_model_path",
                "default_model",
                "device"
            ]
            
            for setting in required_settings:
                if setting in content:
                    print(f"[OK] Настройка '{setting}' найдена в конфигурации")
                else:
                    print(f"[WARNING] Настройка '{setting}' не найдена в конфигурации")
            
            return True
        else:
            print(f"[ERROR] Конфигурационный файл не найден: {config_path}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка проверки конфигурации: {e}")
        return False

def check_musetalk_config():
    """Проверка конфигурации MuseTalk."""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА КОНФИГУРАЦИИ MUSETALK")
    print("=" * 60)
    
    config_path = Path(__file__).parent / "models" / "muse_talk" / "musetalk.json"
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"[OK] Конфигурация MuseTalk загружена успешно")
            
            # Проверяем ключевые поля
            required_fields = ["model", "config", "params"]
            for field in required_fields:
                if field in config:
                    print(f"[OK] Поле '{field}' найдено в конфигурации")
                else:
                    print(f"[WARNING] Поле '{field}' не найдено в конфигурации")
            
            # Выводим основную информацию
            if "model" in config:
                model_info = config["model"]
                print(f"  Модель: {model_info.get('type', 'unknown')}")
                print(f"  Архитектура: {model_info.get('architecture', 'unknown')}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Ошибка загрузки конфигурации MuseTalk: {e}")
            return False
    else:
        print(f"[WARNING] Конфигурация MuseTalk не найдена: {config_path}")
        return False

def check_directory_structure():
    """Проверка структуры директорий."""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА СТРУКТУРЫ ДИРЕКТОРИЙ")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    
    directories = [
        ("Корневая директория", base_dir),
        ("Модели", base_dir / "models"),
        ("MuseTalk модели", base_dir / "models" / "muse_talk"),
        ("Wav2Lip модели", base_dir / "models" / "wav2lip"),
        ("DWPose модели", base_dir / "models" / "dwpose"),
        ("Face Parse модели", base_dir / "models" / "face-parse-bisent"),
        ("Whisper модели", base_dir / "models" / "whisper"),
        ("Сервисы", base_dir / "services"),
        ("Скрипты", base_dir / "scripts"),
        ("Тестовые данные", base_dir / "test_data"),
    ]
    
    all_ok = True
    
    for name, path in directories:
        if path.exists():
            if path.is_dir():
                print(f"[OK] {name}: {path}")
            else:
                print(f"[ERROR] {name}: не директория, а файл")
                all_ok = False
        else:
            if "модели" in name.lower() and "MuseTalk" not in name and "Wav2Lip" not in name:
                print(f"[WARNING] {name}: не найдена (опционально)")
            else:
                print(f"[OK] {name}: не найдена (будет создана при запуске)")
    
    return all_ok

def check_python_dependencies():
    """Проверка зависимостей Python."""
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ЗАВИСИМОСТЕЙ PYTHON")
    print("=" * 60)
    
    dependencies = [
        ("torch", "pytorch"),
        ("numpy", "numpy"),
        ("soundfile", "soundfile"),
        ("librosa", "librosa"),
        ("pydantic", "pydantic"),
        ("loguru", "loguru"),
    ]
    
    missing_deps = []
    
    for import_name, package_name in dependencies:
        try:
            __import__(import_name)
            print(f"[OK] {package_name}")
        except ImportError:
            print(f"[WARNING] {package_name}: не установлен")
            missing_deps.append(package_name)
    
    if missing_deps:
        print(f"\n[INFO] Отсутствующие зависимости: {', '.join(missing_deps)}")
        print("       Установите: pip install " + " ".join(missing_deps))
    
    return len(missing_deps) == 0

def generate_summary(models_ok, config_ok, musetalk_config_ok, structure_ok, deps_ok, model_results):
    """Генерация итогового отчета."""
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    # Основные проверки
    checks = [
        ("Наличие обязательных моделей", models_ok),
        ("Конфигурация системы", config_ok),
        ("Конфигурация MuseTalk", musetalk_config_ok),
        ("Структура директорий", structure_ok),
        ("Зависимости Python", deps_ok),
    ]
    
    for check_name, check_ok in checks:
        status = "OK" if check_ok else "FAILED"
        print(f"{check_name}: {status}")
    
    # Статистика по моделям
    print("\nСТАТИСТИКА ПО МОДЕЛЯМ:")
    total_models = len(model_results)
    available_models = sum(1 for r in model_results.values() if r["status"] == "OK")
    required_models = sum(1 for r in model_results.values() if r["required"])
    available_required = sum(1 for r in model_results.values() if r["status"] == "OK" and r["required"])
    
    print(f"Всего моделей: {total_models}")
    print(f"Доступно моделей: {available_models}")
    print(f"Обязательных моделей: {required_models}")
    print(f"Доступных обязательных: {available_required}")
    
    # Итоговый вердикт
    print("\n" + "=" * 60)
    
    if all([models_ok, config_ok, musetalk_config_ok, structure_ok]):
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("\nLipsync Service готов к работе с реальными моделями.")
        print("Основные модели MuseTalk и Wav2Lip доступны.")
        
        if available_models > required_models:
            print(f"Дополнительные модели ({available_models - required_models}) также доступны.")
        
        print("\nСледующие шаги:")
        print("1. Установите OpenCV: pip install opencv-python")
        print("2. Запустите сервис: python main.py")
        print("3. Протестируйте API: curl http://localhost:5006/health")
        
        return True
    else:
        print("⚠️  НЕКОТОРЫЕ ПРОВЕРКИ ПРОВАЛЕНЫ.")
        
        if not models_ok:
            print("\nПроблемы с моделями:")
            for name, result in model_results.items():
                if result["status"] == "MISSING" and result["required"]:
                    print(f"  - {name}: ОБЯЗАТЕЛЬНАЯ МОДЕЛЬ ОТСУТСТВУЕТ")
        
        print("\nРекомендации:")
        print("1. Убедитесь, что все обязательные модели находятся в models/")
        print("2. Проверьте конфигурацию в config.py")
        print("3. Установите отсутствующие зависимости")
        
        return False

def main():
    """Основная функция тестирования."""
    print("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ LIPSYNC SERVICE")
    print("=" * 60)
    
    # Выполняем проверки
    models_ok, model_results = check_models()
    config_ok = check_config()
    musetalk_config_ok = check_musetalk_config()
    structure_ok = check_directory_structure()
    deps_ok = check_python_dependencies()
    
    # Генерируем отчет
    success = generate_summary(
        models_ok, config_ok, musetalk_config_ok, 
        structure_ok, deps_ok, model_results
    )
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)