import os
import tempfile
import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models import TranscribeResponse
from app.config import settings
from app.services.engine import EvaluadorEngine

router = APIRouter(prefix="/api/v1", tags=["Transcription"])
logger = logging.getLogger(__name__)


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("es"),
    whisper_provider: str = Form("groq"),
):
    if audio.size and audio.size > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds 25 MB limit")

    allowed_types = [
        "audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg",
        "audio/flac", "audio/webm", "audio/x-m4a", "audio/mp3",
        "application/octet-stream",
    ]
    if audio.content_type and audio.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail=f"Unsupported audio type: {audio.content_type}")

    ext = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        engine = EvaluadorEngine(
            proveedor_llm="mistral",
            proveedor_whisper=whisper_provider,
            groq_api_key=settings.groq_api_key or None,
            azure_openai_api_key=settings.azure_openai_api_key or None,
            azure_openai_endpoint=settings.azure_openai_endpoint or None,
            azure_whisper_deployment=settings.azure_whisper_deployment or None,
            azure_api_version=settings.azure_api_version or None,
        )

        result = engine.transcribir_audio(tmp_path, language)

        if not result["success"]:
            return TranscribeResponse(success=False, error=result.get("error"))

        return TranscribeResponse(
            success=True,
            transcription=result["transcripcion"],
            duration=result.get("duracion"),
            language=result.get("idioma"),
            provider=result.get("proveedor"),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Transcription failed")
        raise HTTPException(status_code=500, detail=f"Transcription error: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
