# Руководство по ручной установке недостающих AI-компонентов

## Обзор
Проект AvatarAI имеет архитектурную основу, но требует ручной установки нескольких ключевых AI-моделей, которые не доступны через стандартные репозитории PyPI.

## Критические компоненты, требующие ручной установки

### 1. Coqui XTTS v2 (Клонирование голоса)
**Текущее состояние**: Частично реализовано через библиотеку TTS, но требует загрузки моделей.

#### Ручная установка:
```bash
# Внутри контейнера xtts-service:
docker exec -it avatar-ai-xtts-service-1 /bin/bash

# Загрузить модель XTTS v2
python3 -c "from TTS.api import TTS; tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2', progress_bar=True)"

# Или при запуске сервиса установить переменную окружения:
export TTS_HOME="/app/models"
export XTTS_MODEL_NAME="tts_models/multilingual/multi-dataset/xtts_v2"
```

#### Проверка работоспособности:
```python
from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
print(f"Model loaded: {tts is not None}")
print(f"Supported languages: {tts.languages}")
```

### 2. MuseTalk (Липсинк - синхронизация губ)
**Текущее состояние**: Заглушка с MediaPipe. Настоящий MuseTalk требует установки из исходников.

#### Ручная установка:
```bash
# 1. Клонировать репозиторий MuseTalk
cd /app
git clone https://github.com/TMElyralab/MuseTalk.git
cd MuseTalk

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Скачать предобученные модели
mkdir -p checkpoints
wget https://huggingface.co/TMElyralab/MuseTalk/resolve/main/musetalk_models.tar.gz
tar -xzf musetalk_models.tar.gz -C checkpoints/

# 4. Интегрировать с нашим сервисом
# Скопировать файлы интеграции из нашего проекта:
cp -r /app/src/musetalk_integration/* .
```

#### Интеграция с lipsync-service:
Обновить `services/lipsync_processor.py`:
```python
# Добавить реальную интеграцию MuseTalk
import sys
sys.path.append('/app/MuseTalk')
from musetalk import MuseTalkProcessor

class RealMuseTalkProcessor:
    def __init__(self):
        self.model = MuseTalkProcessor(
            device="cuda",
            checkpoint_path="/app/MuseTalk/checkpoints"
        )
```

### 3. Kohya_ss + ComfyUI (Обучение LoRA)
**Текущее состояние**: Упрощенная версия. Реальное обучение требует отдельной установки.

#### Ручная установка:
```bash
# Вариант A: Использовать готовый Docker образ
docker pull ghcr.io/kohya-ss/sd-scripts:latest

# Вариант B: Установка из исходников
cd /app
git clone https://github.com/kohya-ss/sd-scripts.git
cd sd-scripts
pip install -r requirements.txt

# Установка ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

#### Конфигурация для интеграции:
Создать файл `ai-services/lora-trainer/config_real.py`:
```python
import subprocess
import json
import os

class RealLoRATrainer:
    def train_lora(self, images_dir, output_path):
        # Использование реального kohya_ss
        cmd = [
            "python", "sd-scripts/train_network.py",
            "--pretrained_model_name_or_path", "stabilityai/stable-diffusion-2-1",
            "--train_data_dir", images_dir,
            "--output_dir", output_path,
            "--network_module", "networks.lora",
            "--network_dim", "32",
            "--network_alpha", "16",
            "--save_model_as", "safetensors",
            "--train_batch_size", "1",
            "--max_train_steps", "1000",
            "--mixed_precision", "fp16"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
```

### 4. InsightFace + GFPGAN (Анализ лиц и улучшение)
**Текущее состояние**: Частично реализовано. Требуется донастройка.

#### Ручная установка:
```bash
# InsightFace уже установлен, но нужно скачать модели
python3 -c "import insightface; app = insightface.app.FaceAnalysis(); app.prepare(ctx_id=0)"

# GFPGAN для улучшения лиц
pip install gfpgan
wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth -O /app/models/GFPGANv1.4.pth
```

### 5. Redis кэширование голосовых эмбеддингов
**Текущее состояние**: Интерфейс есть, но требует настройки Redis.

#### Настройка:
```bash
# 1. Убедиться, что Redis запущен
docker-compose up -d redis

# 2. Проверить соединение
python3 -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"

# 3. Настроить TTL для кэша (в конфигурации)
export REDIS_VOICE_CACHE_TTL=86400  # 24 часа
```

### 6. ComfyUI + ControlNet (Рендеринг видео)
**Текущее состояние**: HTTP API клиент отсутствует.

#### Ручная установка:
```bash
# Запуск ComfyUI как отдельного сервиса
docker run -d --gpus all -p 8188:8188 \
  -v /path/to/comfyui/models:/app/models \
  -v /path/to/comfyui/output:/app/output \
  --name comfyui \
  ghcr.io/comfyanonymous/comfyui:latest

# Интеграция через HTTP API
```

Пример интеграции в `video-renderer`:
```python
import websocket
import json

class ComfyUIClient:
    def __init__(self, host="comfyui", port=8188):
        self.ws_url = f"ws://{host}:{port}/ws"
        
    def generate_video(self, workflow):
        # Подключение к WebSocket API ComfyUI
        ws = websocket.create_connection(self.ws_url)
        ws.send(json.dumps(workflow))
        result = ws.recv()
        ws.close()
        return json.loads(result)
```

## Сценарии развертывания

### Сценарий 1: Полная установка (Production)
```bash
# 1. Установить все модели вручную
./scripts/install_all_models.sh

# 2. Запустить все сервисы
docker-compose -f docker-compose.yml -f docker-compose.ai-models.yml up -d

# 3. Проверить работоспособность
./scripts/test_pipeline.py --real-models
```

### Сценарий 2: MVP с заглушками (Development)
```bash
# Использовать существующую конфигурацию
docker-compose up -d

# Сервисы будут работать в режиме симуляции
# Можно тестировать архитектуру без реальных моделей
```

### Сценарий 3: Гибридный подход
```bash
# Запустить базовые сервисы
docker-compose up -d postgres redis backend web-ui

# Запустить AI сервисы с реальными моделями выборочно
docker-compose up -d xtts-service  # С реальным XTTS v2
docker-compose up -d lipsync-service  # С MuseTalk
```

## Устранение неполадок

### Проблема: Модели не загружаются
**Решение:**
```bash
# Проверить доступность GPU
nvidia-smi

# Проверить объем памяти
df -h /app/models

# Скачать модели вручную
python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='t2m/xtts-v2', local_dir='/app/models/xtts-v2')"
```

### Проблема: Недостаточно памяти GPU
**Решение:**
```yaml
# В docker-compose.yml уменьшить batch size
environment:
  - BATCH_SIZE=1
  - USE_FP16=true
```

### Проблема: ComfyUI не отвечает
**Решение:**
```bash
# Проверить логи
docker logs comfyui

# Перезапустить с правильными путями
docker run -d -p 8188:8188 -v $(pwd)/models:/app/models comfyui:latest
```

## Мониторинг и логирование

### Проверка состояния AI сервисов
```bash
# Все сервисы
curl http://localhost:5000/api/health

# XTTS сервис
curl http://localhost:5003/health

# Lip sync сервис
curl http://localhost:5006/health
```

### Логирование
```bash
# Просмотр логов в реальном времени
docker-compose logs -f xtts-service
docker-compose logs -f lipsync-service
docker-compose logs -f lora-trainer
```

## Обновление моделей

### Обновление XTTS v2
```bash
cd /app/xtts-service
pip install --upgrade TTS
python3 -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2', progress_bar=True)"
```

### Обновление MuseTalk
```bash
cd /app/MuseTalk
git pull
pip install -r requirements.txt --upgrade
```

## Производительность и оптимизация

### Настройки для разных GPU:
- **RTX 3060 12GB**: `BATCH_SIZE=1`, `USE_FP16=true`
- **RTX 4090 24GB**: `BATCH_SIZE=2`, `USE_FP16=true`
- **Без GPU**: `USE_CPU=true`, `BATCH_SIZE=1`

### Кэширование:
- Включить Redis кэширование голосовых эмбеддингов
- Использовать shared volume для моделей между сервисами
- Настроить TTL в зависимости от использования

## Безопасность

### Рекомендации:
1. Не размещать реальные модели в публичном репозитории
2. Использовать .env файлы для секретов
3. Ограничить доступ к API сервисам
4. Регулярно обновлять модели и зависимости

## Поддержка

### Полезные ссылки:
- [Coqui XTTS v2 Documentation](https://github.com/coqui-ai/TTS)
- [MuseTalk GitHub](https://github.com/TMElyralab/MuseTalk)
- [Kohya_ss Guide](https://github.com/kohya-ss/sd-scripts)
- [ComfyUI Documentation](https://github.com/comfyanonymous/ComfyUI)

### Сообщество:
- Discord сервер для AI видео генерации
- GitHub Issues для багов и вопросов
- Форум по локальному развертыванию AI моделей

---

*Примечание: Реальные AI модели требуют значительных ресурсов GPU (минимум 8GB VRAM для XTTS v2, 12GB для обучения LoRA). Для тестирования архитектуры можно использовать режим симуляции.*