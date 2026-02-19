package models

// ── Request Models ──────────────────────────────────────────────────────────

type TranscribeRequest struct {
	Language        string `form:"language" json:"language" binding:"omitempty"`
	WhisperProvider string `form:"whisper_provider" json:"whisper_provider" binding:"omitempty"`
}

type CleanTranscriptionRequest struct {
	Transcription string `json:"transcription" binding:"required"`
	LLMProvider   string `json:"llm_provider" binding:"omitempty"`
}

type DetectReadingRequest struct {
	Transcription string `json:"transcription" binding:"required"`
	LLMProvider   string `json:"llm_provider" binding:"omitempty"`
}

type EvaluateRequest struct {
	Transcription string `json:"transcription" binding:"required"`
	Material      string `json:"material" binding:"required"`
	Rubric        string `json:"rubric" binding:"required"`
	LLMProvider   string `json:"llm_provider" binding:"omitempty"`
}

type FullPipelineRequest struct {
	Material           string `form:"material" json:"material" binding:"required"`
	Rubric             string `form:"rubric" json:"rubric" binding:"required"`
	Language           string `form:"language" json:"language" binding:"omitempty"`
	WhisperProvider    string `form:"whisper_provider" json:"whisper_provider" binding:"omitempty"`
	LLMProvider        string `form:"llm_provider" json:"llm_provider" binding:"omitempty"`
	CleanTranscription bool   `form:"clean_transcription" json:"clean_transcription"`
	DetectReading      bool   `form:"detect_reading" json:"detect_reading"`
	GroqAPIKey         string `form:"groq_api_key" json:"groq_api_key,omitempty"`
	MistralAPIKey      string `form:"mistral_api_key" json:"mistral_api_key,omitempty"`
	GoogleAPIKey       string `form:"google_api_key" json:"google_api_key,omitempty"`
	AzureAPIKey        string `form:"azure_api_key" json:"azure_api_key,omitempty"`
	AzureEndpoint      string `form:"azure_endpoint" json:"azure_endpoint,omitempty"`
}

// ── Response Models ─────────────────────────────────────────────────────────

type HealthResponse struct {
	Status    string            `json:"status"`
	Service   string            `json:"service"`
	Version   string            `json:"version"`
	AIService AIServiceStatus   `json:"ai_service"`
}

type AIServiceStatus struct {
	Connected bool              `json:"connected"`
	Providers map[string]bool   `json:"providers,omitempty"`
}

type TranscribeResponse struct {
	Success       bool    `json:"success"`
	Transcription string  `json:"transcription,omitempty"`
	Duration      float64 `json:"duration,omitempty"`
	Language      string  `json:"language,omitempty"`
	Provider      string  `json:"provider,omitempty"`
	Error         string  `json:"error,omitempty"`
}

type CleanTranscriptionResponse struct {
	Success bool   `json:"success"`
	Cleaned string `json:"cleaned,omitempty"`
	Error   string `json:"error,omitempty"`
}

type DetectReadingResponse struct {
	Success            bool                   `json:"success"`
	Classification     string                 `json:"classification,omitempty"`
	IsReading          bool                   `json:"is_reading,omitempty"`
	IsAIGenerated      bool                   `json:"is_ai_generated,omitempty"`
	ConfidenceLevel    string                 `json:"confidence_level,omitempty"`
	ReadingProbability int                    `json:"reading_probability,omitempty"`
	AIProbability      int                    `json:"ai_probability,omitempty"`
	Indicators         []map[string]any       `json:"indicators,omitempty"`
	ReadingEvidence    []string               `json:"reading_evidence,omitempty"`
	NaturalnessEvidence []string              `json:"naturalness_evidence,omitempty"`
	AIEvidence         []string               `json:"ai_evidence,omitempty"`
	ImperfectionCount  map[string]int         `json:"imperfection_count,omitempty"`
	DetailedAnalysis   string                 `json:"detailed_analysis,omitempty"`
	Recommendation     string                 `json:"recommendation,omitempty"`
	Error              string                 `json:"error,omitempty"`
}

type GradeBreakdown struct {
	ByCriteria    []map[string]any `json:"by_criteria"`
	Penalties     []map[string]any `json:"penalties"`
	Bonuses       []map[string]any `json:"bonuses"`
	Justification string           `json:"justification"`
}

type ConceptualAnalysis struct {
	ExpectedConcepts   map[string]any `json:"expected_concepts"`
	MentionedConcepts  []string       `json:"mentioned_concepts"`
	OmittedConcepts    []string       `json:"omitted_concepts"`
	CoveragePercentage float64        `json:"coverage_percentage"`
}

type DetectedErrors struct {
	Factual    []map[string]any `json:"factual"`
	Fabricated []string         `json:"fabricated"`
}

type CommunicationMetrics struct {
	Clarity             string `json:"clarity"`
	Coherence           string `json:"coherence"`
	TechnicalVocabulary string `json:"technical_vocabulary"`
}

type EvaluationResult struct {
	FinalGrade           float64              `json:"final_grade"`
	ConfidenceLevel      string               `json:"confidence_level"`
	DetectedTopic        string               `json:"detected_topic"`
	DifficultyLevel      string               `json:"difficulty_level"`
	GradeBreakdown       GradeBreakdown       `json:"grade_breakdown"`
	ConceptualAnalysis   ConceptualAnalysis   `json:"conceptual_analysis"`
	DetectedErrors       DetectedErrors       `json:"detected_errors"`
	CommunicationMetrics CommunicationMetrics `json:"communication_metrics"`
	StudentFeedback      map[string]any       `json:"student_feedback"`
	TeacherNotes         map[string]any       `json:"teacher_notes"`
	HighlightedQuotes    []string             `json:"highlighted_quotes"`
}

type EvaluateResponse struct {
	Success    bool              `json:"success"`
	Evaluation *EvaluationResult `json:"evaluation,omitempty"`
	Error      string            `json:"error,omitempty"`
}

type FullPipelineResponse struct {
	Success                bool              `json:"success"`
	OriginalTranscription  string            `json:"original_transcription,omitempty"`
	CleanedTranscription   string            `json:"cleaned_transcription,omitempty"`
	AudioDuration          float64           `json:"audio_duration,omitempty"`
	Language               string            `json:"language,omitempty"`
	ReadingPattern         map[string]any    `json:"reading_pattern,omitempty"`
	Evaluation             *EvaluationResult `json:"evaluation,omitempty"`
	Error                  string            `json:"error,omitempty"`
}

type ErrorResponse struct {
	Error   string `json:"error"`
	Code    int    `json:"code"`
	Details string `json:"details,omitempty"`
}
