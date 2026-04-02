"""
Обновленный процессор липсинка для Дня 13.
Использует реальные модели Wav2Lip/MuseTalk если они доступны, иначе fallback.
"""

import os
import cv2
import numpy as np
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import librosa
import soundfile as sf
import subprocess
import tempfile
import json
import time
from loguru import logger
import warnings
warnings.filterwarnings("ignore")

# Импортируем реальный процессор
try:
    from .real_lipsync_processor import RealLipSyncProcessor, RealLipSyncProcessorFactory
    REAL_PROCESSOR_AVAILABLE = True
    logger.info("Real lip sync processor available")
except ImportError as e:
    logger.error(f"Failed to import real processor: {e}")
    REAL_PROCESSOR_AVAILABLE = False

# Импортируем улучшенный процессор для fallback
try:
    from .enhanced_lipsync_processor import EnhancedLipSyncProcessor, LipSyncProcessorFactory
    ENHANCED_PROCESSOR_AVAILABLE = True
    logger.info("Enhanced lip sync processor available")
except ImportError as e:
    logger.error(f"Failed to import enhanced processor: {e}")
    ENHANCED_PROCESSOR_AVAILABLE = False


class LipSyncProcessor:
    """Основной процессор липсинка, использующий реальные модели если доступны."""
    
    def __init__(self, processor_type: str = "wav2lip"):
        self.processor_type = processor_type
        self.processor = None
        self.logger = logger
        
        self._init_processor()
    
    def _init_processor(self):
        """Инициализировать выбранный процессор."""
        try:
            # Сначала пробуем использовать реальный процессор
            if REAL_PROCESSOR_AVAILABLE:
                self.processor = RealLipSyncProcessorFactory.create_processor(self.processor_type)
                self.logger.info(f"Initialized real {self.processor_type} processor")
            
            # Если реальный процессор не доступен, используем улучшенный
            elif ENHANCED_PROCESSOR_AVAILABLE:
                self.processor = LipSyncProcessorFactory.create_processor(self.processor_type)
                self.logger.info(f"Initialized enhanced {self.processor_type} processor")
            
            # Если ничего не доступно, используем простой fallback
            else:
                self.logger.warning("No enhanced or real processor available, using simple fallback")
                self.processor = SimpleLipSyncProcessor(self.processor_type)
                
        except Exception as e:
            self.logger.error(f"Failed to initialize processor: {e}")
            self.processor = SimpleLipSyncProcessor(self.processor_type)
            self.logger.info("Fell back to simple processor")
    
    def process(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        quality: str = "high",
        sync_accuracy: float = 0.9
    ) -> bool:
        """Обработать синхронизацию губ."""
        if self.processor is None:
            self.logger.error("No processor available")
            return False
        
        try:
            # Обработка с выбранным процессором
            return self.processor.process_video(
                video_path, audio_path, output_path, quality, sync_accuracy
            )
        except Exception as e:
            self.logger.error(f"Error in lip sync processing: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Проверить здоровье процессора липсинка."""
        if self.processor is None:
            return {
                "processor_available": False,
                "processor_type": self.processor_type,
                "error": "No processor initialized"
            }
        
        try:
            if hasattr(self.processor, 'health_check'):
                health = self.processor.health_check()
            else:
                health = {}
            
            health["processor_type"] = self.processor_type
            health["processor_available"] = True
            health["real_processor"] = REAL_PROCESSOR_AVAILABLE
            health["enhanced_processor"] = ENHANCED_PROCESSOR_AVAILABLE
            
            return health
        except Exception as e:
            return {
                "processor_available": False,
                "processor_type": self.processor_type,
                "error": str(e),
                "real_processor": REAL_PROCESSOR_AVAILABLE,
                "enhanced_processor": ENHANCED_PROCESSOR_AVAILABLE
            }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Получить список доступных моделей."""
        models = []
        
        # Добавляем реальные модели если доступны
        if REAL_PROCESSOR_AVAILABLE:
            try:
                real_models = RealLipSyncProcessorFactory.get_available_processors()
                models.extend(real_models)
            except Exception as e:
                self.logger.error(f"Failed to get real processors: {e}")
        
        # Добавляем улучшенные модели если доступны
        if ENHANCED_PROCESSOR_AVAILABLE:
            try:
                enhanced_models = LipSyncProcessorFactory.get_available_processors()
                models.extend(enhanced_models)
            except Exception as e:
                self.logger.error(f"Failed to get enhanced processors: {e}")
        
        # Если нет моделей, добавляем fallback
        if not models:
            models = [
                {
                    "name": "simple_wav2lip",
                    "type": "wav2lip",
                    "description": "Simple Wav2Lip processor with basic lip sync simulation",
                    "quality": "low",
                    "accuracy": 0.7,
                    "real_model_required": False
                },
                {
                    "name": "simple_muse_talk",
                    "type": "muse_talk",
                    "description": "Simple MuseTalk processor with basic lip sync simulation",
                    "quality": "low",
                    "accuracy": 0.7,
                    "real_model_required": False
                }
            ]
        
        return models


class SimpleLipSyncProcessor:
    """Простой процессор липсинка для fallback."""
    
    def __init__(self, processor_type: str = "wav2lip"):
        self.processor_type = processor_type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger = logger
        
        # Параметры видео
        self.fps = 25
        self.sample_rate = 16000
        
        self.logger.info(f"Simple {processor_type} processor initialized on {self.device}")
    
    def extract_audio_features(self, audio_path: Path) -> np.ndarray:
        """Извлечение аудио-фич для синхронизации губ."""
        try:
            # Загружаем аудио
            audio, sr = librosa.load(str(audio_path), sr=self.sample_rate)
            
            # Нормализуем
            audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
            
            # Извлекаем энергию сигнала для каждого кадра видео
            hop_length = int(sr / self.fps)  # Один кадр видео
            energy = []
            
            for i in range(0, len(audio), hop_length):
                frame_audio = audio[i:i+hop_length]
                if len(frame_audio) > 0:
                    # Энергия кадра
                    frame_energy = np.sqrt(np.mean(frame_audio**2))
                    energy.append(frame_energy)
                else:
                    energy.append(0.0)
            
            # Нормализуем энергию
            energy = np.array(energy)
            if np.max(energy) > 0:
                energy = energy / np.max(energy)
            
            return energy
            
        except Exception as e:
            self.logger.error(f"Failed to extract audio features: {e}")
            # Возвращаем фиктивные данные
            return np.ones(100) * 0.5
    
    def detect_face_region(self, frame: np.ndarray) -> Tuple[int, int, int, int]:
        """Обнаружение области лица на кадре."""
        height, width = frame.shape[:2]
        
        # Простая эвристика для определения области лица
        # Предполагаем, что лицо в центре кадра
        face_width = min(200, width - 40)
        face_height = min(200, height - 40)
        
        x = (width - face_width) // 2
        y = (height - face_height) // 2
        
        return x, y, x + face_width, y + face_height
    
    def draw_animated_mouth(self, frame: np.ndarray, face_bbox: Tuple[int, int, int, int], 
                           energy: float, frame_idx: int) -> np.ndarray:
        """Рисование анимированного рта на основе аудио-энергии."""
        x_min, y_min, x_max, y_max = face_bbox
        frame_copy = frame.copy()
        
        # Центр лица
        face_center_x = (x_min + x_max) // 2
        face_center_y = (y_min + y_max) // 2
        
        # Размеры рта на основе энергии
        mouth_width = int(30 + energy * 30)
        mouth_height = int(15 + energy * 20)
        
        # Позиция рта (немного ниже центра лица)
        mouth_y = face_center_y + int((y_max - y_min) * 0.2)
        
        # Цвет в зависимости от типа процессора
        if self.processor_type == "muse_talk":
            mouth_color = (0, 0, 255)  # Красный для MuseTalk
        else:
            mouth_color = (0, 255, 0)  # Зеленый для Wav2Lip
        
        # Рисуем рот (эллипс)
        cv2.ellipse(
            frame_copy,
            (face_center_x, mouth_y),
            (mouth_width // 2, mouth_height // 2),
            0, 0, 360,
            mouth_color,
            2
        )
        
        # Добавляем информационную панель
        info_text = f"{self.processor_type.upper()} (Simple) - Sync: {energy:.2f}"
        cv2.putText(
            frame_copy,
            info_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        return frame_copy
    
    def process_video(self, video_path: Path, audio_path: Path, output_path: Path, 
                     quality: str = "high", sync_accuracy: float = 0.9) -> bool:
        """Обработка видео с липсинком."""
        try:
            self.logger.info(f"Processing lip sync: {video_path.name} + {audio_path.name}")
            
            # Извлекаем аудио-фичи
            audio_energy = self.extract_audio_features(audio_path)
            self.logger.info(f"Extracted audio energy for {len(audio_energy)} frames")
            
            # Открываем исходное видео
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            # Получаем параметры видео
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Создаем writer для выходного видео
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            frame_idx = 0
            face_bbox = None
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Определяем область лица на первом кадре
                if face_bbox is None:
                    face_bbox = self.detect_face_region(frame)
                
                # Получаем энергию для текущего кадра
                if frame_idx < len(audio_energy):
                    energy = audio_energy[frame_idx]
                else:
                    # Если аудио короче видео, повторяем паттерн
                    energy = audio_energy[frame_idx % len(audio_energy)]
                
                # Применяем точность синхронизации
                energy = energy * sync_accuracy
                
                # Рисуем анимированный рот
                frame_with_mouth = self.draw_animated_mouth(frame, face_bbox, energy, frame_idx)
                
                # Записываем кадр
                out.write(frame_with_mouth)
                frame_idx += 1
                
                # Логируем прогресс
                if frame_idx % 50 == 0:
                    self.logger.info(f"Processed {frame_idx}/{total_frames} frames")
            
            # Освобождаем ресурсы
            cap.release()
            out.release()
            
            # Проверяем результат
            if output_path.exists() and output_path.stat().st_size > 0:
                self.logger.info(f"Successfully created output video: {output_path}")
                return True
            else:
                self.logger.error("Failed to create output video")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing video: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья процессора."""
        return {
            "processor_type": self.processor_type,
            "device": self.device,
            "status": "ready",
            "capabilities": ["simple_lip_sync", "audio_extraction"],
            "fps": self.fps,
            "sample_rate": self.sample_rate
        }