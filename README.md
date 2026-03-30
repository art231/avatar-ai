# AvatarAI - Production-Ready AI Avatar Platform

Полнофункциональная платформа для создания и использования AI аватаров с поддержкой обучения моделей и генерации видео.

## 🚀 Особенности

- **Полный пайплайн обучения**: От загрузки изображений до готовой модели
- **Реальная интеграция AI**: XTTS v2, MuseTalk (Lipsync), Kohya_ss (LoRA)
- **Production-ready архитектура**: Clean Architecture, SOLID, CQRS
- **Масштабируемая инфраструктура**: Docker, микросервисы, Redis
- **Современный фронтенд**: Angular 17, Vite, TypeScript
- **Полное тестирование**: Unit и integration тесты

## 🏗️ Архитектура

### Backend (.NET 8)
- **Domain**: Сущности, интерфейсы, value objects
- **Application**: Use cases, DTOs, валидация, CQRS
- **Infrastructure**: EF Core, репозитории, внешние сервисы
- **Presentation**: Web API, контроллеры, middleware

### Frontend (Angular 17)
- **Domain**: Модели, интерфейсы
- **Application**: Сервисы, фасады
- **Infrastructure**: API клиенты, HTTP слои
- **UI**: Компоненты, страницы, layout

### AI Сервисы (Python)
- **audio-preprocessor**: Обработка аудио
- **media-analyzer**: Анализ изображений и лиц
- **lora-trainer**: Обучение LoRA моделей (Kohya_ss)
- **xtts-service**: Синтез речи (XTTS v2)
- **lipsync-service**: Синхронизация губ (MuseTalk)
- **training-pipeline**: Оркестрация обучения
- **video-renderer**: Рендеринг видео

## 🛠️ Требования

- Docker 20.10+
- Docker Compose 2.20+
- 16GB+ RAM (рекомендуется 32GB для обучения)
- NVIDIA GPU с 8GB+ VRAM (рекомендуется для обучения)
- 50GB+ свободного места на диске

## 🚀 Быстрый старт

### 1. Клонирование и настройка
```bash
git clone <repository-url>
cd avatar-ai
cp .env.example .env
# Отредактируйте .env при необходимости
```

### 2. Запуск через Docker Compose
```bash
docker-compose up -d
```

Сервисы будут доступны:
- **Frontend**: http://localhost:80
- **Backend API**: http://localhost:8080
- **Hangfire Dashboard**: http://localhost:8080/hangfire
- **AI Services**: Доступны через backend API

### 3. Проверка работоспособности
```bash
# Проверка health check
curl http://localhost:8080/health

# Проверка frontend
curl http://localhost:80/health
```

## 📁 Структура проекта

```
avatar-ai/
├── backend/                 # .NET 8 Backend
│   ├── src/
│   │   ├── AvatarAI.Api/   # Web API
│   │   ├── AvatarAI.Application/ # Use cases
│   │   ├── AvatarAI.Domain/ # Domain models
│   │   └── AvatarAI.Infrastructure/ # Infrastructure
│   └── Dockerfile
├── frontend/               # Angular 17 Frontend
│   ├── src/
│   │   ├── app/           # Angular приложение
│   │   ├── application/   # Сервисы
│   │   ├── domain/        # Модели
│   │   ├── infrastructure/# API клиенты
│   │   └── ui/            # Компоненты
│   └── Dockerfile
├── ai-services/           # Python AI сервисы
│   ├── audio-preprocessor/
│   ├── media-analyzer/
│   ├── lora-trainer/
│   ├── xtts-service/
│   ├── lipsync-service/
│   ├── training-pipeline/
│   └── video-renderer/
├── tests/                 # Тесты
│   ├── backend/
│   └── frontend/
├── docker/               # Docker конфигурации
├── docker-compose.yml    # Основной compose файл
└── README.md            # Эта документация
```

## 🔧 Конфигурация

### Основные переменные окружения (.env)
```env
# Database
POSTGRES_DB=avatarai
POSTGRES_USER=avatarai
POSTGRES_PASSWORD=secure_password

# Backend
ASPNETCORE_ENVIRONMENT=Production
ConnectionStrings__DefaultConnection=Host=postgres;Port=5432;Database=avatarai;Username=avatarai;Password=secure_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# AI Services
AI_SERVICES_BASE_URL=http://ai-services:5000
USE_GPU=true
MODELS_DIR=/data/models
```

### Настройка AI моделей
1. Поместите базовые модели в `data/models/`:
   - Stable Diffusion модель
   - XTTS v2 модель
   - MuseTalk модель

2. Или используйте автоматическую загрузку (требуется интернет):
```bash
docker-compose run --rm lora-trainer download-models
```

## 📊 Обучение аватара

### 1. Подготовка данных
- **Изображения**: 10-50 четких фото лица с разных ракурсов
- **Аудио**: 30-60 секунд чистой речи без фонового шума

### 2. Процесс обучения
1. Загрузите данные через веб-интерфейс
2. Запустите обучение
3. Отслеживайте прогресс в реальном времени
4. Получите готовую модель через 2-6 часов

### 3. Этапы пайплайна
```
1. Валидация данных → 2. Анализ лиц → 3. Обработка аудио
       ↓                       ↓               ↓
4. Обучение LoRA ←───────┐     │               │
       ↓                 │     ↓               ↓
5. Обучение голоса ←─────┴─────┴───────────────┘
       ↓
6. Интеграция моделей → 7. Проверка качества → 8. Деплой
```

## 🎬 Генерация видео

### 1. Создание видео
1. Выберите обученный аватар
2. Введите текст для озвучки
3. Настройте параметры (голос, фон, длительность)
4. Запустите генерацию

### 2. Процесс генерации
```
Текст → Синтез речи → Lipsync → Рендеринг → Видео
```

### 3. Время генерации
- **Короткое видео (10-30 сек)**: 1-2 минуты
- **Среднее видео (30-60 сек)**: 3-5 минут
- **Длинное видео (1-2 мин)**: 5-10 минут

## 🧪 Тестирование

### Unit тесты
```bash
# Backend тесты
cd backend
dotnet test

# Frontend тесты
cd frontend
npm test
```

### Integration тесты
```bash
# Запуск тестов в Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### E2E тесты
```bash
# Запуск Cypress тестов
cd frontend
npm run e2e
```

## 🔍 Мониторинг и логи

### Логи
```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f lora-trainer
```

### Метрики
- **Backend**: Prometheus метрики на `/metrics`
- **AI сервисы**: Health checks на `/health`
- **База данных**: pg_stat активности

### Дашборды
- **Hangfire**: http://localhost:8080/hangfire
- **Grafana**: http://localhost:3000 (если настроено)
- **Prometheus**: http://localhost:9090 (если настроено)

## ⚡ Производительность

### Оптимизация
1. **GPU ускорение**: Включите `USE_GPU=true` в .env
2. **Кэширование**: Redis для кэширования результатов
3. **Пакетная обработка**: Очереди для длительных задач
4. **CDN**: Для статических файлов и видео

### Масштабирование
```yaml
# docker-compose.scale.yml
services:
  backend:
    scale: 3
  ai-services:
    scale: 2
```

## 🔒 Безопасность

### Рекомендации для production
1. **HTTPS**: Настройте SSL/TLS сертификаты
2. **Аутентификация**: JWT токены с refresh
3. **Авторизация**: RBAC на уровне API
4. **Rate limiting**: Ограничение запросов
5. **WAF**: Web Application Firewall
6. **Аудит**: Логирование всех действий

### Конфиденциальные данные
- Храните секреты в HashiCorp Vault или AWS Secrets Manager
- Не коммитьте .env файлы
- Используйте разные ключи для разных окружений

## 🚨 Устранение неполадок

### Общие проблемы

#### 1. Недостаточно памяти
```
Error: CUDA out of memory
```
**Решение**: Уменьшите batch size в настройках обучения или используйте CPU.

#### 2. Медленная загрузка моделей
```
Model loading timeout
```
**Решение**: Предзагрузите модели в `data/models/` или увеличьте таймауты.

#### 3. Проблемы с Docker
```
Container fails to start
```
**Решение**: Проверьте логи `docker-compose logs <service>` и доступность портов.

#### 4. Ошибки базы данных
```
Database connection failed
```
**Решение**: Убедитесь, что PostgreSQL запущен и доступен.

### Отладка
```bash
# Проверка состояния сервисов
docker-compose ps

# Проверка логов
docker-compose logs --tail=100 <service>

# Вход в контейнер для отладки
docker-compose exec <service> bash

# Перезапуск сервиса
docker-compose restart <service>
```

## 📈 Масштабирование

### Горизонтальное масштабирование
```bash
# Масштабирование backend
docker-compose up -d --scale backend=3

# Масштабирование AI сервисов
docker-compose up -d --scale lora-trainer=2 --scale xtts-service=2
```

### Вертикальное масштабирование
```yaml
# docker-compose.override.yml
services:
  lora-trainer:
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '4.0'
    devices:
      - "/dev/nvidia0:/dev/nvidia0"
```

## 🤝 Вклад в проект

### Установка для разработки
```bash
# Backend
cd backend
dotnet restore
dotnet build

# Frontend
cd frontend
npm install
npm run dev

# AI сервисы
cd ai-services/lora-trainer
pip install -r requirements.txt
python main.py
```

### Правила коммитов
- Используйте Conventional Commits
- Пишите тесты для нового функционала
- Обновляйте документацию
- Следуйте code style проекта

### Code style
- **Backend**: .editorconfig, Roslyn анализаторы
- **Frontend**: ESLint, Prettier
- **Python**: Black, isort, flake8

## 📄 Лицензия

MIT License - смотрите файл [LICENSE](LICENSE)

## 📞 Поддержка

- **Issues**: [GitHub Issues](https://github.com/your-org/avatar-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/avatar-ai/discussions)
- **Документация**: [Wiki](https://github.com/your-org/avatar-ai/wiki)

## 🙏 Благодарности

- [Kohya_ss](https://github.com/kohya-ss/sd-scripts) за LoRA training
- [Coqui TTS](https://github.com/coqui-ai/TTS) за XTTS v2
- [MuseTalk](https://github.com/TMElyralab/MuseTalk) за lipsync
- Сообщество Stable Diffusion за модели и инструменты

---

**AvatarAI** - это production-ready платформа для создания AI аватаров с полным циклом от обучения до генерации видео. Система готова к развертыванию в production с поддержкой масштабирования, мониторинга и безопасности.