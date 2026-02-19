import os
import tempfile
import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models import (
    FullPipelineResponse, EvaluationResult, GradeBreakdown,
    ConceptualAnalysis, DetectedErrors, CommunicationMetrics,
)
from app.config import settings
from app.services.engine import EvaluadorEngine

router = APIRouter(prefix="/api/v1", tags=["Pipeline"])
logger = logging.getLogger(__name__)


@router.post("/pipeline", response_model=FullPipelineResponse)
async def full_pipeline(
    audio: UploadFile = File(...),
    material: str = Form(...),
    rubric: str = Form(...),
    language: str = Form("es"),
    whisper_provider: str = Form("groq"),
    llm_provider: str = Form("mistral"),
    clean_transcription: bool = Form(True),
    detect_reading: bool = Form(True),
    groq_api_key: str = Form(None),
    mistral_api_key: str = Form(None),
    google_api_key: str = Form(None),
    azure_api_key: str = Form(None),
    azure_endpoint: str = Form(None),
):
    if audio.size and audio.size > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds 25 MB limit")

    ext = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name

        engine = EvaluadorEngine(
            proveedor_llm=llm_provider,
            proveedor_whisper=whisper_provider,
            groq_api_key=groq_api_key or settings.groq_api_key or None,
            mistral_api_key=mistral_api_key or settings.mistral_api_key or None,
            google_api_key=google_api_key or settings.google_api_key or None,
            azure_openai_api_key=azure_api_key or settings.azure_openai_api_key or None,
            azure_openai_endpoint=azure_endpoint or settings.azure_openai_endpoint or None,
            azure_openai_deployment=settings.azure_openai_deployment or None,
            azure_whisper_deployment=settings.azure_whisper_deployment or None,
            azure_api_version=settings.azure_api_version or None,
        )

        result = engine.proceso_completo(
            audio_path=tmp_path,
            material=material,
            rubrica=rubric,
            limpiar=clean_transcription,
            idioma=language,
            detectar_lectura=detect_reading,
        )

        if not result["success"]:
            return FullPipelineResponse(success=False, error=result.get("error"))

        ev = result.get("evaluacion", {})
        evaluation = EvaluationResult(
            final_grade=ev.get("calificacion_final", 0),
            confidence_level=ev.get("nivel_confianza", "medium"),
            detected_topic=ev.get("tema_detectado", "General"),
            difficulty_level=ev.get("nivel_dificultad", "Intermediate"),
            grade_breakdown=GradeBreakdown(
                by_criteria=ev.get("desglose_calificacion", {}).get("por_criterio", []),
                penalties=ev.get("desglose_calificacion", {}).get("penalizaciones", []),
                bonuses=ev.get("desglose_calificacion", {}).get("bonificaciones", []),
                justification=ev.get("desglose_calificacion", {}).get("justificacion", ""),
            ),
            conceptual_analysis=ConceptualAnalysis(
                expected_concepts=ev.get("analisis_conceptual", {}).get("conceptos_esperados", {}),
                mentioned_concepts=ev.get("analisis_conceptual", {}).get("conceptos_mencionados", []),
                omitted_concepts=ev.get("analisis_conceptual", {}).get("conceptos_omitidos", []),
                coverage_percentage=ev.get("analisis_conceptual", {}).get("cobertura_porcentaje", 0),
            ),
            detected_errors=DetectedErrors(
                factual=ev.get("errores_detectados", {}).get("factuales", []),
                fabricated=ev.get("errores_detectados", {}).get("inventados", []),
            ),
            communication_metrics=CommunicationMetrics(
                clarity=ev.get("metricas_comunicacion", {}).get("claridad", "regular"),
                coherence=ev.get("metricas_comunicacion", {}).get("coherencia", "regular"),
                technical_vocabulary=ev.get("metricas_comunicacion", {}).get("vocabulario_tecnico", "regular"),
            ),
            student_feedback=ev.get("feedback_alumno", {}),
            teacher_notes=ev.get("nota_docente", {}),
            highlighted_quotes=ev.get("citas_destacadas", []),
        )

        return FullPipelineResponse(
            success=True,
            original_transcription=result.get("transcripcion_original"),
            cleaned_transcription=result.get("transcripcion_limpia"),
            audio_duration=result.get("duracion_audio"),
            language=result.get("idioma"),
            reading_pattern=result.get("patron_lectura"),
            evaluation=evaluation,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
