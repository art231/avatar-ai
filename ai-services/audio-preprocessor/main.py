from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import shutil
from pathlib import Path
import logging
from loguru import logger

from services.audio_processor import AudioProcessor
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.add("logs/audio_preprocessor.log", rotation="500 MB", retention="30 days")

app = FastAPI(
    title="AvatarAI Audio Preprocessor",
    description="Audio preprocessing service for AvatarAI system",
    version="1.0.0"
)

# Initialize audio processor
audio_processor = AudioProcessor()

class PreprocessRequest(BaseModel):
    input_path: str
    output_path: Optional[str] = None
    sample_rate: int = 22050
    remove_silence: bool = True
    normalize_loudness: bool = True
    target_lufs: float = -23.0

class PreprocessResponse(BaseModel):
    success: bool
    output_path: str
    processing_time: float
    audio_info: dict
    message: str

@app.get("/")
async def root():
    return {"message": "AvatarAI Audio Preprocessor Service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "audio-preprocessor"}

@app.post("/preprocess", response_model=PreprocessResponse)
async def preprocess_audio(
    file: UploadFile = File(...),
    sample_rate: int = 22050,
    remove_silence: bool = True,
    normalize_loudness: bool = True,
    target_lufs: float = -23.0
):
    """
    Preprocess audio file: clean, normalize, remove silence, convert format
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_id = str(uuid.uuid4())
        input_filename = f"input_{unique_id}{file_ext}"
        output_filename = f"cleaned_{unique_id}.wav"
        
        # Create directories if they don't exist
        input_dir = Path("/data/input")
        output_dir = Path("/data/output")
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        input_path = input_dir / input_filename
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process audio
        output_path = output_dir / output_filename
        result = audio_processor.process_audio(
            input_path=str(input_path),
            output_path=str(output_path),
            sample_rate=sample_rate,
            remove_silence=remove_silence,
            normalize_loudness=normalize_loudness,
            target_lufs=target_lufs
        )
        
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)
        
        return PreprocessResponse(
            success=True,
            output_path=str(output_path),
            processing_time=result["processing_time"],
            audio_info=result["audio_info"],
            message="Audio preprocessing completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

@app.get("/download/{filename}")
async def download_audio(filename: str):
    """
    Download processed audio file
    """
    file_path = Path("/data/output") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/wav"
    )

@app.get("/files")
async def list_files():
    """
    List available processed files
    """
    output_dir = Path("/data/output")
    if not output_dir.exists():
        return {"files": []}
    
    files = []
    for file_path in output_dir.glob("*.wav"):
        stats = file_path.stat()
        files.append({
            "filename": file_path.name,
            "size_bytes": stats.st_size,
            "created": stats.st_ctime
        })
    
    return {"files": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5004,
        reload=True,
        log_level="info"
    )