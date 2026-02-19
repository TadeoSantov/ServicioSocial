import logging

from fastapi import APIRouter, HTTPException
from app.models import (
    CleanTranscriptionRequest, CleanTranscriptionResponse,
    DetectReadingRequest, DetectReadingResponse,
    EvaluateRequest, EvaluateResponse,
    EvaluationResult, GradeBreakdown, ConceptualAnalysis,
    DetectedErrors, CommunicationMetrics,
)
from app.config import settings
from app.services.engine import EvaluadorEngine

router = APIRouter(prefix="/api/v1", tags=["Evaluation"])
logger = logging.getLogger(__name__)


def _build_engine(llm_provider: str) -> EvaluadorEngine:
    return EvaluadorEngine(
        proveedor_llm=llm_provider,
        proveedor_whisper="groq",
        groq_api_key=settings.groq_api_key or None,
        mistral_api_key=settings.mistral_api_key or None,
        google_api_key=settings.google_api_key or None,
        azure_openai_api_key=settings.azure_openai_api_key or None,
        azure_openai_endpoint=settings.azure_openai_endpoint or None,
        azure_openai_deployment=settings.azure_openai_deployment or None,
        azure_api_version=settings.azure_api_version or None,
    )


@router.post("/clean", response_model=CleanTranscriptionResponse)
async def clean_transcription(req: CleanTranscriptionRequest):
    try:
        engine = _build_engine(req.llm_provider)
        cleaned = engine.limpiar_transcripcion(req.transcription)
        return CleanTranscriptionResponse(success=True, cleaned=cleaned)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Clean transcription failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-reading", response_model=DetectReadingResponse)
async def detect_reading(req: DetectReadingRequest):
    try:
        engine = _build_engine(req.llm_provider)
        result = engine.detectar_patron_lectura(req.transcription)
        return DetectReadingResponse(
            success=True,
            classification=result.get("clasificacion"),
            is_reading=result.get("esta_leyendo"),
            is_ai_generated=result.get("es_ia_generada"),
            confidence_level=result.get("nivel_confianza"),
            reading_probability=result.get("probabilidad_lectura"),
            ai_probability=result.get("probabilidad_ia"),
            indicators=result.get("indicadores_detectados"),
            reading_evidence=result.get("evidencias_lectura"),
            naturalness_evidence=result.get("evidencias_naturalidad"),
            ai_evidence=result.get("evidencias_ia"),
            imperfection_count=result.get("conteo_imperfecciones"),
            detailed_analysis=result.get("analisis_detallado"),
            recommendation=result.get("recomendacion"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Detect reading failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_exam(req: EvaluateRequest):
    try:
        engine = _build_engine(req.llm_provider)
        result = engine.evaluar_examen(req.material, req.rubric, req.transcription)

        if not result["success"]:
            return EvaluateResponse(success=False, error=result.get("error"))

        ev = result["evaluacion"]
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

        return EvaluateResponse(success=True, evaluation=evaluation)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Evaluation failed")
        raise HTTPException(status_code=500, detail=str(e))
