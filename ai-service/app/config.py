import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Groq (Whisper transcription)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    # Mistral (LLM)
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")

    # Google Gemini (LLM)
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # Azure OpenAI (LLM + Whisper)
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    azure_whisper_deployment: str = os.getenv("AZURE_WHISPER_DEPLOYMENT", "whisper")
    azure_api_version: str = os.getenv("AZURE_API_VERSION", "2024-12-01-preview")

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]


settings = Settings()
