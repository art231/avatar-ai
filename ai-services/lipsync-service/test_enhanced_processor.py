"""
Тестирование улучшенного процессора липсинка.
Проверяет импорт, инициализацию и базовую функциональность.
"""

import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Тестирование импорта всех необходимых модулей."""
    print("=" * 60)
    print("Тестирование импорта модулей")
    print("=" * 60)
    
    imports_successful = True
    
    try:
        from services.enhanced_real_lipsync_processor import EnhancedRealLipSyncProcessor, EnhancedRealLipSyncProcessorFactory
        print("✅ EnhancedRealLipSyncProcessor импортирован успешно")
    except ImportError as e:
        print(f"❌ Ошибка импорта EnhancedRealLipSyncProcessor: {e}")
        imports_successful = False
    
    try:
        from services.real_lipsync_processor import RealLipSyncProcessor, RealLipSyncProcessorFactory
        print("✅ RealLipSyncProcessor импортирован успешно")
    except ImportError as e:
        print(f"⚠️  RealLipSyncProcessor не импортирован: {e}")
    
    try:
        from services.lipsync_processor_updated import LipSyncProcessor
        print("✅ LipSyncProcessor импортирован успешно")
    except ImportError as e:
        print(f"⚠️  LipSyncProcessor не импортирован: {e}")
    
    try:
        from config import settings
        print("✅ Конфигурация импортирована успешно")
    except ImportError as e:
        print(f"⚠️  Конфигурация не импортирована: {e}")
    
    return imports_successful

def test_model_availability():
    """Тестирование доступности моделей."""
    print("\n" + "=" * 60)
    print("Тестирование доступности моделей")
    print("=" * 60)
    
    models_dir = Path(__file__).parent / "models"
    
    models_to_check = [
        ("MuseTalk модель", models_dir / "muse_talk" / "muse_talk.pt"),
        ("MuseTalk конфиг", models_dir / "muse_talk" / "musetalk.json"),
        ("Wav2Lip модель", models_dir / "wav2lip" / "wav2lip.pth"),
        ("DWPose модели", models_dir / "dwpose"),
        ("Face Parse модели", models_dir / "face-parse-bisent"),
        ("Whisper модель", models_dir / "whisper" / "tiny.pt"),
    ]
    
    all_available = True
    
    for name, path in models_to_check:
        if path.exists():
            if path.is_dir():
                files = list(path.glob("*"))
                print(f"✅ {name}: найдено {len(files)} файлов")
                if files:
                    for f in files[:3]:  # Показываем первые 3 файла
                        print(f"   - {f.name}")
                    if len(files) > 3:
                        print(f"   ... и еще {len(files) - 3} файлов")
            else:
                size_mb = path.stat().st_size / (1024 * 1024)
                print(f"✅ {name}: {size_mb:.2f} MB")
        else:
            print(f"❌ {name}: не найден")
            all_available = False
    
    return all_available

def test_processor_initialization():
    """Тестирование инициализации процессоров."""
    print("\n" + "=" * 60)
    print("Тестирование инициализации процессоров")
    print("=" * 60)
    
    try:
        from services.enhanced_real_lipsync_processor import EnhancedRealLipSyncProcessor
        
        # Тестируем MuseTalk процессор
        print("Инициализация Enhanced MuseTalk процессора...")
        muse_talk_processor = EnhancedRealLipSyncProcessor("muse_talk")
        print(f"✅ MuseTalk процессор инициализирован")
        print(f"   Модели доступны: {muse_talk_processor.models_available}")
        print(f"   Устройство: {muse_talk_processor.device}")
        
        # Проверка здоровья
        health = muse_talk_processor.health_check()
        print(f"   Проверка здоровья: {health['status']}")
        print(f"   Возможности: {', '.join(health['capabilities'])}")
        
        # Тестируем Wav2Lip процессор
        print("\nИнициализация Enhanced Wav2Lip процессора...")
        wav2lip_processor = EnhancedRealLipSyncProcessor("wav2lip")
        print(f"✅ Wav2Lip процессор инициализирован")
        print(f"   Модели доступны: {wav2lip_processor.models_available}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации процессоров: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_factory():
    """Тестирование фабрики процессоров."""
    print("\n" + "=" * 60)
    print("Тестирование фабрики процессоров")
    print("=" * 60)
    
    try:
        from services.enhanced_real_lipsync_processor import EnhancedRealLipSyncProcessorFactory
        
        # Получаем список доступных процессоров
        processors = EnhancedRealLipSyncProcessorFactory.get_available_processors()
        print(f"✅ Найдено {len(processors)} процессоров:")
        
        for proc in processors:
            print(f"\n{proc['name']}:")
            print(f"  Тип: {proc['type']}")
            print(f"  Описание: {proc['description']}")
            print(f"  Качество: {proc['quality']}")
            print(f"  Точность: {proc['accuracy']}")
            print(f"  Основная модель: {'✅' if proc['main_model_available'] else '❌'}")
            print(f"  DWPose: {'✅' if proc.get('dwpose_available', False) else '❌'}")
            print(f"  Face Parse: {'✅' if proc.get('face_parse_available', False) else '❌'}")
            print(f"  Whisper: {'✅' if proc.get('whisper_available', False) else '❌'}")
        
        # Создаем процессор через фабрику
        print("\nСоздание процессора через фабрику...")
        processor = EnhancedRealLipSyncProcessorFactory.create_processor("muse_talk")
        print(f"✅ Процессор создан: {processor.processor_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования фабрики: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Тестирование конфигурации."""
    print("\n" + "=" * 60)
    print("Тестирование конфигурации")
    print("=" * 60)
    
    try:
        from config import settings
        
        print("Конфигурация системы:")
        print(f"  Имя приложения: {settings.app_name}")
        print(f"  Версия: {settings.app_version}")
        print(f"  Режим отладки: {settings.debug}")
        print(f"  Хост: {settings.host}")
        print(f"  Порт: {settings.port}")
        print(f"  Директория моделей: {settings.models_dir}")
        print(f"  Устройство: {settings.device}")
        print(f"  Модель по умолчанию: {settings.default_model}")
        
        print("\nПути к моделям:")
        print(f"  MuseTalk: {settings.muse_talk_model_path}")
        print(f"  Wav2Lip: {settings.wav2lip_model_path}")
        print(f"  DWPose: {settings.dwpose_model_path}")
        print(f"  Face Parse: {settings.face_parse_model_path}")
        print(f"  Whisper: {settings.whisper_model_path}")
        
        print("\nФлаги улучшенной обработки:")
        print(f"  Использовать DWPose: {settings.use_dwpose}")
        print(f"  Использовать Face Parse: {settings.use_face_parse}")
        print(f"  Использовать Whisper: {settings.use_whisper}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования конфигурации: {e}")
        return False

def main():
    """Основная функция тестирования."""
    print("Тестирование Lipsync Service с реальными моделями")
    print("=" * 60)
    
    results = []
    
    # Тестируем импорт
    results.append(("Импорт модулей", test_imports()))
    
    # Тестируем доступность моделей
    results.append(("Доступность моделей", test_model_availability()))
    
    # Тестируем конфигурацию
    results.append(("Конфигурация", test_configuration()))
    
    # Тестируем инициализацию процессоров
    results.append(("Инициализация процессоров", test_processor_initialization()))
    
    # Тестируем фабрику
    results.append(("Фабрика процессоров", test_factory()))
    
    # Вывод итогов
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
    
    print(f"\nВсего тестов: {total_tests}")
    print(f"Пройдено: {passed_tests}")
    print(f"Провалено: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Lipsync Service готов к работе с реальными моделями.")
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ.")
        print("Проверьте наличие всех моделей и корректность конфигурации.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)