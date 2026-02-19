// ── Request Types ───────────────────────────────────────────────────────────

export interface FullPipelineParams {
  material: string;
  rubric: string;
  language: string;
  whisperProvider: string;
  llmProvider: string;
  cleanTranscription: boolean;
  detectReading: boolean;
  groqApiKey?: string;
  mistralApiKey?: string;
  googleApiKey?: string;
  azureApiKey?: string;
  azureEndpoint?: string;
}

// ── Response Types ──────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  ai_service: {
    connected: boolean;
    providers?: Record<string, boolean>;
  };
}

export interface TranscribeResponse {
  success: boolean;
  transcription?: string;
  duration?: number;
  language?: string;
  provider?: string;
  error?: string;
}

export interface GradeBreakdown {
  by_criteria: Array<{
    criterio?: string;
    puntaje?: number;
    maximo?: number;
    justificacion?: string;
  }>;
  penalties: Array<{
    razon?: string;
    puntos_restados?: number;
  }>;
  bonuses: Array<{
    razon?: string;
    puntos_agregados?: number;
  }>;
  justification: string;
}

export interface ConceptualAnalysis {
  expected_concepts: {
    principales?: string[];
    secundarios?: string[];
  };
  mentioned_concepts: string[];
  omitted_concepts: string[];
  coverage_percentage: number;
}

export interface DetectedErrors {
  factual: Array<{
    error?: string;
    gravedad?: string;
    cita_alumno?: string;
  }>;
  fabricated: string[];
}

export interface CommunicationMetrics {
  clarity: string;
  coherence: string;
  technical_vocabulary: string;
}

export interface StudentFeedback {
  resumen?: string;
  fortalezas?: string[];
  areas_mejora?: string[];
  errores_corregidos?: Array<{
    error?: string;
    correccion?: string;
    explicacion?: string;
  }>;
  recomendaciones_estudio?: string[];
  mensaje_motivacional?: string;
}

export interface TeacherNotes {
  observaciones?: string;
  patron_errores?: string;
  sugerencia_refuerzo?: string;
  comparacion_esperado?: string;
}

export interface EvaluationResult {
  final_grade: number;
  confidence_level: string;
  detected_topic: string;
  difficulty_level: string;
  grade_breakdown: GradeBreakdown;
  conceptual_analysis: ConceptualAnalysis;
  detected_errors: DetectedErrors;
  communication_metrics: CommunicationMetrics;
  student_feedback: StudentFeedback;
  teacher_notes: TeacherNotes;
  highlighted_quotes: string[];
}

export interface ReadingPattern {
  clasificacion?: string;
  esta_leyendo?: boolean;
  es_ia_generada?: boolean;
  nivel_confianza?: string;
  probabilidad_lectura?: number;
  probabilidad_ia?: number;
  indicadores_detectados?: Array<{
    indicador?: string;
    categoria?: string;
    descripcion?: string;
    gravedad?: string;
  }>;
  evidencias_lectura?: string[];
  evidencias_naturalidad?: string[];
  evidencias_ia?: string[];
  conteo_imperfecciones?: {
    muletillas?: number;
    autocorrecciones?: number;
    frases_incompletas?: number;
    errores_gramaticales?: number;
    pausas_detectadas?: number;
  };
  analisis_detallado?: string;
  recomendacion?: string;
}

export interface FullPipelineResponse {
  success: boolean;
  original_transcription?: string;
  cleaned_transcription?: string;
  audio_duration?: number;
  language?: string;
  reading_pattern?: ReadingPattern;
  evaluation?: EvaluationResult;
  error?: string;
}
