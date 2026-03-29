# AvatarAI - Production System for Photo-realistic Video Generation

AvatarAI is a production system for creating photo-realistic videos with digital human avatars. Users provide photos or short videos and voice samples - the system automatically generates videos where the avatar speaks the given text with synchronized lip movements.

## Key Features

- **Voice Cloning**: Clone unique voice from 5-30 second audio samples
- **Speech Synthesis**: Generate speech in cloned voice from arbitrary text
- **Personal LoRA Models**: Create personal LoRA models from human photos
- **Video Generation**: Generate videos with realistic facial expressions and movements
- **Lip Sync**: Synchronize lip movements with audio track
- **Fully Local Deployment**: Deploy via Docker Compose

## System Architecture

### Docker Compose Services

| Service | Technology | Port | Purpose |
|---------|------------|------|---------|
| postgres | PostgreSQL 15 | 5432 | Main database |
| redis | Redis 7 | 6379 | Task queue / cache |
| backend | .NET 8 Web API | 5000 | REST API + CQRS |
| frontend | Angular 17 + Vite | 3000 | Frontend UI |
| audio-preprocessor | Python 3.11 + Demucs | 5004 | Audio cleaning |
| xtts-service | Coqui XTTS v2 | 5003 | Voice cloning / TTS |
| media-analyzer | Python 3.11 + InsightFace | 5005 | Photo/video analysis |
| lipsync-service | MuseTalk | 5006 | Lip synchronization |

### Backend Architecture (.NET 8 - Clean Architecture)

- **Domain Layer**: Entities, value objects, repository interfaces, enums, domain events
- **Application Layer**: CQRS commands/queries (MediatR), DTOs, validation (FluentValidation), service interfaces
- **Infrastructure Layer**: EF Core 8, repositories, AI service clients, file storage, background tasks (Hangfire)
- **API Layer**: Controllers, Middleware, Swagger, JWT authentication, Health Checks

## Prerequisites

### Hardware Requirements

- **GPU**: NVIDIA RTX 3060 12GB (minimum) / RTX 4090 24GB (recommended)
- **RAM**: 32 GB (minimum), 64 GB (recommended)
- **Storage**: 200+ GB NVMe SSD
- **OS**: Ubuntu 22.04 LTS or Windows 11 with WSL2
- **CUDA**: 12.1+ / NVIDIA Driver 525+
- **Docker**: Docker Engine 24+ with NVIDIA Container Toolkit

### Software Requirements

- Docker Engine 24.0.0+
- Docker Compose 2.20.0+
- NVIDIA Container Toolkit
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd avatar-ai
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
# Edit .env file with your configuration
```

### 3. Build and Start Services

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/swagger
- **Health Checks**: http://localhost:5000/health

### 5. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Development

### Project Structure

```
avatar-ai/
├── backend/                 # .NET 8 Backend (Clean Architecture)
│   ├── src/
│   │   ├── AvatarAI.Domain/      # Domain layer
│   │   ├── AvatarAI.Application/ # Application layer
│   │   ├── AvatarAI.Infrastructure/ # Infrastructure layer
│   │   └── AvatarAI.Api/         # API layer
│   └── Dockerfile
├── frontend/               # Angular 17 Frontend
│   ├── src/
│   │   ├── domain/         # Domain models
│   │   ├── application/    # Application services
│   │   ├── infrastructure/ # Infrastructure services
│   │   └── ui/             # UI components
│   └── Dockerfile
├── ai-services/            # Python AI Services
│   ├── audio-preprocessor/ # Audio preprocessing
│   ├── xtts-service/       # Voice cloning/TTS
│   ├── media-analyzer/     # Media analysis
│   └── lipsync-service/    # Lip synchronization
├── docker/                 # Docker configurations
├── docker-compose.yml      # Docker Compose configuration
├── .env.example           # Environment variables template
└── README.md              # This file
```

### Backend Development

```bash
cd backend

# Restore dependencies
dotnet restore

# Build solution
dotnet build

# Run tests
dotnet test

# Run migrations
dotnet ef database update
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## AI Services

### Audio Preprocessing Service (Port 5004)

- **Technology**: Python 3.11 + Demucs + FFmpeg
- **Purpose**: Clean audio samples, remove background noise, normalize volume
- **Input**: Audio file (5-30 seconds, any format)
- **Output**: Cleaned WAV file (mono, 22050 Hz, normalized to -23 LUFS)

### XTTS Service (Port 5003)

- **Technology**: Coqui XTTS v2
- **Purpose**: Voice cloning and speech synthesis
- **Input**: Cleaned audio sample + text
- **Output**: Synthesized speech WAV file (24000 Hz, stereo)

### Media Analyzer Service (Port 5005)

- **Technology**: Python 3.11 + InsightFace + OpenCV
- **Purpose**: Analyze photos/videos, detect faces, extract embeddings
- **Input**: Photo (JPG/PNG) or video (MP4/MOV/AVI) up to 100 MB
- **Output**: Aligned face frames 512×512 + metadata

### Lipsync Service (Port 5006)

- **Technology**: MuseTalk v1.0 (ByteDance)
- **Purpose**: Lip synchronization with audio
- **Input**: Video + audio track
- **Output**: Lip-synced video with audio

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh token

### Avatars
- `GET /api/avatars` - Get user's avatars
- `POST /api/avatars` - Create new avatar
- `GET /api/avatars/{id}` - Get avatar details
- `PUT /api/avatars/{id}` - Update avatar
- `DELETE /api/avatars/{id}` - Delete avatar

### Voice Profiles
- `POST /api/avatars/{avatarId}/voice-profiles` - Create voice profile
- `GET /api/avatars/{avatarId}/voice-profiles` - Get voice profile
- `DELETE /api/avatars/{avatarId}/voice-profiles` - Delete voice profile

### Generation Tasks
- `POST /api/generation-tasks` - Create generation task
- `GET /api/generation-tasks` - Get user's tasks
- `GET /api/generation-tasks/{id}` - Get task details
- `GET /api/generation-tasks/{id}/progress` - Get task progress (SSE)

## MVP Pipeline

The Minimum Viable Product (MVP) provides:
1. **Photo + Voice Sample + Text → Talking Avatar Video**
2. **No LoRA training required** (uses SadTalker/MuseTalk directly)
3. **Basic voice cloning** with Coqui XTTS v2
4. **Lip synchronization** with MuseTalk

## Monitoring

### Health Checks
- `GET /health` - Overall system health
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

### Logging
- Structured logging with Serilog
- Log levels: Debug, Information, Warning, Error
- Output: Console + File + Elasticsearch (optional)

## Troubleshooting

### Common Issues

1. **GPU not detected in Docker**
   ```bash
   # Check NVIDIA Container Toolkit installation
   docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
   ```

2. **Port conflicts**
   - Check if ports 3000, 5000, 5432, 6379 are available
   - Modify ports in `docker-compose.yml` if needed

3. **Database connection issues**
   ```bash
   # Check PostgreSQL container
   docker-compose logs postgres
   
   # Test database connection
   docker-compose exec postgres psql -U avatarai -d avatarai
   ```

4. **Insufficient GPU memory**
   - Reduce batch sizes in AI service configurations
   - Use smaller models where possible
   - Consider upgrading GPU hardware

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub Issues page.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request