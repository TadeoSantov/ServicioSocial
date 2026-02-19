from fastapi import APIRouter
from app.models import HealthResponse
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    providers = {
        "groq_whisper": bool(settings.groq_api_key),
        "mistral_llm": bool(settings.mistral_api_key),
        "gemini_llm": bool(settings.google_api_key),
        "azure_openai": bool(settings.azure_openai_api_key),
    }
    return HealthResponse(
        status="ok",
        service="ai-service",
        version="1.0.0",
        providers=providers,
    )
