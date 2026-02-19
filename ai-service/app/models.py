from pydantic import BaseModel, Field
from typing import Optional


# ── Request Models ──────────────────────────────────────────────────────────

class TranscribeRequest(BaseModel):
    language: str = Field(default="es", description="ISO language code")
    whisper_provider: str = Field(default="groq", description="groq | azure")


class CleanTranscriptionRequest(BaseModel):
    transcription: str
    llm_provider: str = Field(default="mistral", description="mistral | gemini | azure_openai")


class DetectReadingRequest(BaseModel):
    transcription: str
    llm_provider: str = Field(default="mistral", description="mistral | gemini | azure_openai")


class EvaluateRequest(BaseModel):
    transcription: str
    material: str
    rubric: str
    llm_provider: str = Field(default="mistral", description="mistral | gemini | azure_openai")


class FullPipelineRequest(BaseModel):
    material: str
    rubric: str
    language: str = Field(default="es")
    whisper_provider: str = Field(default="groq")
    llm_provider: str = Field(default="mistral")
    clean_transcription: bool = Field(default=True)
    detect_reading: bool = Field(default=True)


# ── Response Models ─────────────────────────────────────────────────────────

class TranscribeResponse(BaseModel):
    success: bool
    transcription: Optional[str] = None
    duration: Optional[float] = None
    language: Optional[str] = None
    provider: Optional[str] = None
    error: Optional[str] = None


class CleanTranscriptionResponse(BaseModel):
    success: bool
    cleaned: Optional[str] = None
    error: Optional[str] = None


class DetectReadingResponse(BaseModel):
    success: bool
    classification: Optional[str] = None
    is_reading: Optional[bool] = None
    is_ai_generated: Optional[bool] = None
    confidence_level: Optional[str] = None
    reading_probability: Optional[int] = None
    ai_probability: Optional[int] = None
    indicators: Optional[list] = None
    reading_evidence: Optional[list] = None
    naturalness_evidence: Optional[list] = None
    ai_evidence: Optional[list] = None
    imperfection_count: Optional[dict] = None
    detailed_analysis: Optional[str] = None
    recommendation: Optional[str] = None
    error: Optional[str] = None


class GradeBreakdown(BaseModel):
    by_criteria: list = Field(default_factory=list)
    penalties: list = Field(default_factory=list)
    bonuses: list = Field(default_factory=list)
    justification: str = ""


class ConceptualAnalysis(BaseModel):
    expected_concepts: dict = Field(default_factory=dict)
    mentioned_concepts: list = Field(default_factory=list)
    omitted_concepts: list = Field(default_factory=list)
    coverage_percentage: float = 0.0


class DetectedErrors(BaseModel):
    factual: list = Field(default_factory=list)
    fabricated: list = Field(default_factory=list)


class CommunicationMetrics(BaseModel):
    clarity: str = "regular"
    coherence: str = "regular"
    technical_vocabulary: str = "regular"


class EvaluationResult(BaseModel):
    final_grade: float = 0.0
    confidence_level: str = "medium"
    detected_topic: str = "General"
    difficulty_level: str = "Intermediate"
    grade_breakdown: GradeBreakdown = Field(default_factory=GradeBreakdown)
    conceptual_analysis: ConceptualAnalysis = Field(default_factory=ConceptualAnalysis)
    detected_errors: DetectedErrors = Field(default_factory=DetectedErrors)
    communication_metrics: CommunicationMetrics = Field(default_factory=CommunicationMetrics)
    student_feedback: dict = Field(default_factory=dict)
    teacher_notes: dict = Field(default_factory=dict)
    highlighted_quotes: list = Field(default_factory=list)


class EvaluateResponse(BaseModel):
    success: bool
    evaluation: Optional[EvaluationResult] = None
    error: Optional[str] = None


class FullPipelineResponse(BaseModel):
    success: bool
    original_transcription: Optional[str] = None
    cleaned_transcription: Optional[str] = None
    audio_duration: Optional[float] = None
    language: Optional[str] = None
    reading_pattern: Optional[dict] = None
    evaluation: Optional[EvaluationResult] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    providers: dict
