# Use NVIDIA CUDA base image with Python
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0"
ENV TTS_HOME="/app/models"
ENV XTTS_MODEL_NAME="tts_models/multilingual/multi-dataset/xtts_v2"

# Install system dependencies for TTS
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    ffmpeg \
    libsndfile1 \
    libsox-fmt-all \
    sox \
    git \
    curl \
    wget \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel ninja

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install TTS with XTTS v2 support
RUN pip install --no-cache-dir \
    TTS==0.21.0 \
    torch==2.1.0 \
    torchaudio==2.1.0 \
    transformers==4.36.2 \
    tokenizers==0.15.1

# Create app directory
WORKDIR /app

# Copy application code
COPY . .

# Create directories with proper permissions
RUN mkdir -p /data/input /data/output /app/models /app/logs && \
    chmod -R 755 /data /app/models /app/logs

# Pre-download XTTS v2 model (optional - can be downloaded at runtime)
# Uncomment to pre-download model during build (increases image size)
# RUN python3 -c "from TTS.api import TTS; tts = TTS('${XTTS_MODEL_NAME}', progress_bar=True, gpu=False)"

# Expose port
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5003/health || exit 1

# Run the application with production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5003", "--workers", "2"]