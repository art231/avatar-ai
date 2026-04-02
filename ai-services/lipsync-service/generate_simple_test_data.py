"""
Упрощенная генерация тестовых данных без OpenCV.
Создает только аудио файл для тестирования.
"""

import numpy as np
import soundfile as sf
from pathlib import Path

def generate_test_audio(output_path: Path, duration_seconds: int = 3, sample_rate: int = 16000):
    """
    Генерация тестового аудио с речью-подобным сигналом.
    """
    print(f"Генерация тестового аудио: {output_path}")
    
    # Генерируем временную ось
    t = np.linspace(0, duration_seconds, duration_seconds * sample_rate, False)
    
    # Создаем рече-подобный сигнал
    base_freq = 150 + 50 * np.sin(2 * np.pi * 0.5 * t)
    voice_signal = 0.5 * np.sin(2 * np.pi * base_freq * t)
    
    # Форманты
    formant1 = 0.2 * np.sin(2 * np.pi * 500 * t)
    formant2 = 0.1 * np.sin(2 * np.pi * 1500 * t)
    
    # Комбинируем
    audio_signal = voice_signal + formant1 + formant2
    
    # Нормализуем
    audio_signal = audio_signal / np.max(np.abs(audio_signal))
    
    # Огибающая
    envelope = np.ones_like(t)
    attack_samples = int(0.1 * sample_rate)
    release_samples = int(0.2 * sample_rate)
    
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[-release_samples:] = np.linspace(1, 0, release_samples)
    
    audio_signal = audio_signal * envelope
    
    # Сохраняем
    sf.write(str(output_path), audio_signal, sample_rate)
    
    print(f"Аудио создано: {output_path} ({output_path.stat().st_size} bytes)")
    return output_path

def create_simple_video_description():
    """
    Создает текстовое описание тестового видео вместо реального видео файла.
    """
    video_desc = """Тестовое видео описание:
    - Разрешение: 640x480
    - Длительность: 3 секунды
    - FPS: 25
    - Содержание: Лицо в центре кадра, нейтральное выражение
    - Формат: MP4 (H.264)
    
    Для реального тестирования нужен реальный видео файл.
    Можно использовать любой короткий видео файл с лицом.
    """
    
    desc_path = Path(__file__).parent / "test_data" / "test_video_description.txt"
    desc_path.parent.mkdir(exist_ok=True)
    
    with open(desc_path, 'w', encoding='utf-8') as f:
        f.write(video_desc)
    
    print(f"Описание видео создано: {desc_path}")
    return desc_path

def create_test_data():
    """Создать тестовые данные."""
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    
    # Создаем аудио
    audio_path = test_dir / "test_speech.wav"
    generate_test_audio(audio_path, duration_seconds=3)
    
    # Создаем описание видео
    video_desc_path = create_simple_video_description()
    
    # Создаем простой текстовый файл с инструкциями
    instructions = f"""Инструкция по тестированию Lipsync Service:

1. Тестовые данные созданы в: {test_dir}
2. Аудио файл: {audio_path.name}
3. Для видео: используйте любой MP4 файл с лицом или создайте с помощью:
   - OpenCV: cv2.VideoWriter
   - FFmpeg: ffmpeg -f lavfi -i testsrc=duration=3:size=640x480:rate=25 test_video.mp4
   - Или любой короткий видео файл с лицом

4. Для тестирования Lipsync Service:
   python -c "
from pathlib import Path
from services.lipsync_processor_updated import LipSyncProcessor

processor = LipSyncProcessor('muse_talk')
video_path = Path('path/to/your/video.mp4')
audio_path = Path('{audio_path}')
output_path = Path('output_lipsync.mp4')

success = processor.process(video_path, audio_path, output_path)
    print(f'Success: {{success}}')
   "
"""
    
    instructions_path = test_dir / "TEST_INSTRUCTIONS.txt"
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"\nТестовые данные созданы в: {test_dir}")
    print(f"  Аудио: {audio_path}")
    print(f"  Описание видео: {video_desc_path}")
    print(f"  Инструкции: {instructions_path}")
    
    return test_dir, audio_path

if __name__ == "__main__":
    print("=" * 60)
    print("Упрощенная генерация тестовых данных")
    print("=" * 60)
    
    test_dir, audio_path = create_test_data()
    
    print("\nГотово! Для полного тестирования нужен видео файл.")
    print("Можно использовать существующие тестовые видео или создать новое.")