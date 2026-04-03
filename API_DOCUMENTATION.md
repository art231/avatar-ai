# AvatarAI API Documentation
## Текущее состояние API (анализ)

### Базовый URL
- Бэкенд: `http://localhost:5000/api` (через Docker)
- Фронтенд ожидает: `/api` (проксируется через nginx)

### Контроллеры и эндпоинты

#### 1. AvatarsController (`/api/avatars`)

**GET /api/avatars**
- Описание: Получение списка аватаров
- Параметры: `userId` (опционально, Guid?)
- Ответ: `IEnumerable<AvatarDto>`
- Статусы: 200 OK, 500 Internal Server Error

**GET /api/avatars/{id}**
- Описание: Получение аватара по ID
- Параметры: `id` (Guid)
- Ответ: `AvatarDto`
- Статусы: 200 OK, 404 Not Found, 500 Internal Server Error

**POST /api/avatars**
- Описание: Создание нового аватара
- Тело запроса: `CreateAvatarRequest` (JSON)
  ```json
  {
    "userId": "guid",
    "name": "string"
  }
  ```
- Ответ: `AvatarDto` (201 Created)
- Статусы: 201 Created, 400 Bad Request, 500 Internal Server Error

#### 2. GenerationTasksController (`/api/generationtasks`)

**GET /api/generationtasks**
- Описание: Получение списка задач генерации
- Параметры: `avatarId` (опционально, Guid?), `userId` (опционально, Guid?)
- Ответ: `IEnumerable<GenerationTaskDto>`
- Статусы: 200 OK, 500 Internal Server Error

**GET /api/generationtasks/{id}**
- Описание: Получение задачи генерации по ID
- Параметры: `id` (Guid)
- Ответ: `GenerationTaskDto`
- Статусы: 200 OK, 404 Not Found, 500 Internal Server Error

**GET /api/generationtasks/{id}/progress**
- Описание: Получение прогресса задачи
- Параметры: `id` (Guid)
- Ответ: Кастомный объект прогресса
- Статусы: 200 OK, 404 Not Found, 500 Internal Server Error

**POST /api/generationtasks**
- Описание: Создание новой задачи генерации
- Тело запроса: `CreateGenerationTaskRequest` (JSON)
  ```json
  {
    "avatarId": "guid",
    "speechText": "string",
    "actionPrompt": "string" (опционально)
  }
  ```
- Ответ: `GenerationTaskDto` (201 Created)
- Статусы: 201 Created, 400 Bad Request, 500 Internal Server Error

### DTO структуры

#### AvatarDto
```csharp
public class AvatarDto
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public string Name { get; set; } = string.Empty;
    public AvatarStatus Status { get; set; } // Enum
    public string? LoraPath { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public VoiceProfileDto? VoiceProfile { get; set; }
    public List<GenerationTaskDto> GenerationTasks { get; set; } = new();
}
```

#### GenerationTaskDto
```csharp
public class GenerationTaskDto
{
    public Guid Id { get; set; }
    public Guid AvatarId { get; set; }
    public Guid UserId { get; set; }
    public string SpeechText { get; set; } = string.Empty;
    public string? ActionPrompt { get; set; }
    public TaskStatus Status { get; set; } // Enum
    public TaskStage Stage { get; set; } // Enum
    public decimal Progress { get; set; }
    public string? OutputPath { get; set; }
    public string? ErrorMessage { get; set; }
    public Dictionary<string, object> Metadata { get; set; } = new();
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public List<TaskLogDto> TaskLogs { get; set; } = new();
}
```

#### VoiceProfileDto
```csharp
public class VoiceProfileDto
{
    public Guid Id { get; set; }
    public Guid AvatarId { get; set; }
    public string AudioSamplePath { get; set; } = string.Empty;
    public string? XttsModelPath { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}
```

### Несоответствия с фронтендом

#### 1. Создание аватара
- **Фронтенд ожидает**: FormData с полями:
  - `name` (string)
  - `description` (string, опционально)
  - `images[]` (File[], массив изображений)
  - `voiceSample` (File, опционально)
- **Бэкенд принимает**: JSON с полями:
  - `userId` (Guid)
  - `name` (string)

#### 2. Получение аватаров
- **Фронтенд ожидает**: Массив аватаров с полями:
  - `id` (string)
  - `name` (string)
  - `description` (string, опционально)
  - `status` ('training' | 'active' | 'failed')
  - `trainedImages` (number)
  - `trainedVoice` (boolean)
  - `createdAt` (string)
  - `updatedAt` (string)
- **Бэкенд возвращает**: Массив AvatarDto без полей `description`, `trainedImages`, `trainedVoice`

#### 3. Создание задачи генерации
- **Фронтенд отправляет**: JSON с полями:
  - `avatarId` (string)
  - `text` (string)
  - `voiceStyle` (string, опционально)
  - `videoLength` (string, опционально)
  - `resolution` (string, опционально)
  - `background` (string, опционально)
- **Бэкенд ожидает**: JSON с полями:
  - `avatarId` (Guid)
  - `speechText` (string)
  - `actionPrompt` (string, опционально)

#### 4. Отсутствующие эндпоинты
1. `POST /api/avatars/{id}/train` - запуск тренировки аватара
2. `GET /api/avatars/{id}/training-progress` - прогресс тренировки
3. `POST /api/avatars/{id}/generate` - генерация видео
4. `POST /api/generationtasks/{id}/cancel` - отмена задачи
5. `POST /api/generationtasks/{id}/retry` - повтор задачи
6. `PUT /api/avatars/{id}` - обновление аватара
7. `DELETE /api/avatars/{id}` - удаление аватара
8. `DELETE /api/generationtasks/{id}` - удаление задачи

### Рекомендации по исправлению

#### Приоритет 1 (Критично):
1. Изменить `AvatarsController.CreateAvatar` для поддержки FormData и загрузки файлов
2. Расширить `AvatarDto` для включения полей `description`, `trainedImages`, `trainedVoice`
3. Изменить `GenerationTasksController.CreateGenerationTask` для поддержки настроек

#### Приоритет 2 (Важно):
1. Добавить недостающие эндпоинты
2. Синхронизировать статусы и enum'ы
3. Добавить поддержку обновления и удаления

#### Приоритет 3 (Опционально):
1. Добавить пагинацию
2. Добавить фильтрацию и сортировку
3. Оптимизировать запросы (include, select)