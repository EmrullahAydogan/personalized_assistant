from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import aiofiles
import os
from app.services.voice_service import VoiceService
from app.core.config import settings

router = APIRouter()
voice_service = VoiceService()


class TextToSpeechRequest(BaseModel):
    text: str
    language: Optional[str] = None
    slow: bool = False


class SpeechToTextResponse(BaseModel):
    text: str


@router.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(
    audio: UploadFile = File(...),
    language: Optional[str] = None,
):
    """Convert speech audio to text"""

    # Save uploaded file temporarily
    temp_file_path = os.path.join(settings.UPLOAD_DIR, f"temp_{audio.filename}")

    try:
        async with aiofiles.open(temp_file_path, 'wb') as f:
            content = await audio.read()
            await f.write(content)

        # Transcribe audio
        text = await voice_service.speech_to_text(temp_file_path, language)

        return SpeechToTextResponse(text=text)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech recognition failed: {str(e)}",
        )
    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            voice_service.cleanup_temp_file(temp_file_path)


@router.post("/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """Convert text to speech audio"""

    try:
        # Generate speech
        audio_file_path = await voice_service.text_to_speech(
            request.text,
            request.language,
            request.slow,
        )

        # Return audio file
        return FileResponse(
            audio_file_path,
            media_type="audio/mpeg",
            filename="speech.mp3",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text-to-speech failed: {str(e)}",
        )


@router.post("/record")
async def record_audio(duration: int = 5):
    """Record audio from microphone"""

    try:
        # Record audio
        audio_file_path = await voice_service.record_audio(duration)

        # Return audio file
        return FileResponse(
            audio_file_path,
            media_type="audio/wav",
            filename="recording.wav",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio recording failed: {str(e)}",
        )
