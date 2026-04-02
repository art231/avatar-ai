"""
Генерация тестовых данных для проверки Lipsync Service.
Создает простое видео с лицом и аудио с речью.
"""

import cv2
import numpy as np
import soundfile as sf
import librosa
from pathlib import Path
import os

def generate_test_video(output_path: Path, duration_seconds: int = 5, fps: int = 25):
    """
    Генерация тестового видео с лицом в центре.
    Лицо будет немного двигаться для реалистичности.
    """
    print(f"Генерация тестового видео: {output_path}")
    
    # Параметры видео
    width, height = 640, 480
    total_frames = duration_seconds * fps
    
    # Создаем VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    for frame_idx in range(total_frames):
        # Создаем черный фон
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Координаты лица (немного двигаются)
        face_center_x = width // 2 + int(20 * np.sin(frame_idx * 0.1))
        face_center_y = height // 2 + int(10 * np.cos(frame_idx * 0.05))
        face_radius = 100
        
        # Рисуем лицо (круг)
        cv2.circle(frame, (face_center_x, face_center_y), face_radius, (255, 255, 255), -1)
        
        # Глаза
        eye_radius = 15
        left_eye_x = face_center_x - 40
        right_eye_x = face_center_x + 40
        eyes_y = face_center_y - 30
        
        cv2.circle(frame, (left_eye_x, eyes_y), eye_radius, (0, 0, 0), -1)
        cv2.circle(frame, (right_eye_x, eyes_y), eye_radius, (0, 0, 0), -1)
        
        # Рот (нейтральное положение)
        mouth_width = 60
        mouth_height = 20
        mouth_y = face_center_y + 40
        
        cv2.ellipse(
            frame,
            (face_center_x, mouth_y),
            (mouth_width // 2, mouth_height // 2),
            0, 0, 360,
            (0, 0, 0),
            2
        )
        
        # Добавляем текст с номером кадра
        cv2.putText(
            frame,
            f"Test Face Frame: {frame_idx}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # Записываем кадр
        out.write(frame)
        
        if frame_idx % 25 == 0:
            print(f"  Сгенерирован кадр {frame_idx}/{total_frames}")
    
    out.release()
    print(f"Видео создано: {output_path} ({output_path.stat().st_size} bytes)")
    
    return output_path

def generate_test_audio(output_path: Path, duration_seconds: int = 5, sample_rate: int = 16000):
    """
    Генерация тестового аудио с речью-подобным сигналом.
    Использует синусоиды разных частот для имитации речи.
    """
    print(f"Генерация тестового аудио: {output_path}")
    
    # Генерируем временную ось
    t = np.linspace(0, duration_seconds, duration_seconds * sample_rate, False)
    
    # Создаем рече-подобный сигнал:
    # - Основной тон (голос) ~ 100-200 Гц
    # - Форманты (резонансы) ~ 500-2000 Гц
    # - Шум для реалистичности
    
    # Основной тон (меняется как в речи)
    base_freq = 150 + 50 * np.sin(2 * np.pi * 0.5 * t)  # Меняющаяся частота
    voice_signal = 0.5 * np.sin(2 * np.pi * base_freq * t)
    
    # Форманты (резонансы речевого тракта)
    formant1 = 0.2 * np.sin(2 * np.pi * 500 * t)
    formant2 = 0.1 * np.sin(2 * np.pi * 1500 * t)
    formant3 = 0.05 * np.sin(2 * np.pi * 2500 * t)
    
    # Немного шума для реалистичности
    noise = 0.02 * np.random.randn(len(t))
    
    # Комбинируем сигналы
    audio_signal = voice_signal + formant1 + formant2 + formant3 + noise
    
    # Нормализуем
    audio_signal = audio_signal / np.max(np.abs(audio_signal))
    
    # Применяем огибающую (начало и конец)
    envelope = np.ones_like(t)
    attack_samples = int(0.1 * sample_rate)  # 100 мс атака
    release_samples = int(0.2 * sample_rate)  # 200 мс релиз
    
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[-release_samples:] = np.linspace(1, 0, release_samples)
    
    audio_signal = audio_signal * envelope
    
    # Сохраняем как WAV файл
    sf.write(str(output_path), audio_signal, sample_rate)
    
    print(f"Аудио создано: {output_path} ({output_path.stat().st_size} bytes)")
    
    # Также создаем текстовую транскрипцию для тестирования
    transcript_path = output_path.with_suffix('.txt')
    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write("Тестовая речь для проверки синхронизации губ. Привет, это тестовое аудио.")
    
    print(f"Транскрипция создана: {transcript_path}")
    
    return output_path

def create_test_data_directory():
    """Создать директорию для тестовых данных."""
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    
    video_path = test_dir / "test_face_video.mp4"
    audio_path = test_dir / "test_speech_audio.wav"
    
    # Генерируем данные
    generate_test_video(video_path, duration_seconds=3)  # 3 секунды для быстрого теста
    generate_test_audio(audio_path, duration_seconds=3)
    
    print(f"\nТестовые данные созданы в: {test_dir}")
    print(f"  Видео: {video_path}")
    print(f"  Аудио: {audio_path}")
    
    return test_dir, video_path, audio_path

if __name__ == "__main__":
    print("=" * 60)
    print("Генерация тестовых данных для Lipsync Service")
    print("=" * 60)
    
    test_dir, video_path, audio_path = create_test_data_directory()
    
    print("\nПроверка созданных файлов:")
    print(f"  Видео существует: {video_path.exists()}")
    print(f"  Размер видео: {video_path.stat().st_size} bytes")
    print(f"  Аудио существует: {audio_path.exists()}")
    print(f"  Размер аудио: {audio_path.stat().st_size} bytes")
    
    print("\nГотово! Тестовые данные созданы успешно.")