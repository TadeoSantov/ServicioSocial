package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"time"

	"github.com/evaluador-examenes-orales/backend/internal/config"
	"github.com/evaluador-examenes-orales/backend/internal/models"
)

type AIClient struct {
	baseURL    string
	httpClient *http.Client
}

func NewAIClient(cfg *config.Config) *AIClient {
	return &AIClient{
		baseURL: cfg.AIServiceURL,
		httpClient: &http.Client{
			Timeout: 120 * time.Second,
		},
	}
}

// Health checks the AI service health endpoint
func (c *AIClient) Health() (*models.AIServiceStatus, error) {
	resp, err := c.httpClient.Get(c.baseURL + "/health")
	if err != nil {
		return &models.AIServiceStatus{Connected: false}, err
	}
	defer resp.Body.Close()

	var result struct {
		Status    string          `json:"status"`
		Providers map[string]bool `json:"providers"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return &models.AIServiceStatus{Connected: false}, err
	}

	return &models.AIServiceStatus{
		Connected: result.Status == "ok",
		Providers: result.Providers,
	}, nil
}

// Transcribe sends audio to the AI service for transcription
func (c *AIClient) Transcribe(audioData []byte, filename, language, whisperProvider string) (*models.TranscribeResponse, error) {
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile("audio", filename)
	if err != nil {
		return nil, fmt.Errorf("failed to create form file: %w", err)
	}
	if _, err := part.Write(audioData); err != nil {
		return nil, fmt.Errorf("failed to write audio data: %w", err)
	}

	writer.WriteField("language", language)
	writer.WriteField("whisper_provider", whisperProvider)
	writer.Close()

	req, err := http.NewRequest("POST", c.baseURL+"/api/v1/transcribe", body)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("AI service unreachable: %w", err)
	}
	defer resp.Body.Close()

	var result models.TranscribeResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}
	return &result, nil
}

// CleanTranscription sends text for cleaning
func (c *AIClient) CleanTranscription(transcription, llmProvider string) (*models.CleanTranscriptionResponse, error) {
	payload := models.CleanTranscriptionRequest{
		Transcription: transcription,
		LLMProvider:   llmProvider,
	}
	jsonData, _ := json.Marshal(payload)

	resp, err := c.httpClient.Post(c.baseURL+"/api/v1/clean", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("AI service unreachable: %w", err)
	}
	defer resp.Body.Close()

	var result models.CleanTranscriptionResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}
	return &result, nil
}

// DetectReading sends text for reading/AI detection
func (c *AIClient) DetectReading(transcription, llmProvider string) (*models.DetectReadingResponse, error) {
	payload := models.DetectReadingRequest{
		Transcription: transcription,
		LLMProvider:   llmProvider,
	}
	jsonData, _ := json.Marshal(payload)

	resp, err := c.httpClient.Post(c.baseURL+"/api/v1/detect-reading", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("AI service unreachable: %w", err)
	}
	defer resp.Body.Close()

	var result models.DetectReadingResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}
	return &result, nil
}

// Evaluate sends transcription + material + rubric for evaluation
func (c *AIClient) Evaluate(transcription, material, rubric, llmProvider string) (*models.EvaluateResponse, error) {
	payload := models.EvaluateRequest{
		Transcription: transcription,
		Material:      material,
		Rubric:        rubric,
		LLMProvider:   llmProvider,
	}
	jsonData, _ := json.Marshal(payload)

	resp, err := c.httpClient.Post(c.baseURL+"/api/v1/evaluate", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("AI service unreachable: %w", err)
	}
	defer resp.Body.Close()

	var result models.EvaluateResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}
	return &result, nil
}

// FullPipeline sends audio + params for the complete evaluation pipeline
func (c *AIClient) FullPipeline(audioData []byte, filename string, params models.FullPipelineRequest) (*models.FullPipelineResponse, error) {
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile("audio", filename)
	if err != nil {
		return nil, fmt.Errorf("failed to create form file: %w", err)
	}
	if _, err := part.Write(audioData); err != nil {
		return nil, fmt.Errorf("failed to write audio data: %w", err)
	}

	writer.WriteField("material", params.Material)
	writer.WriteField("rubric", params.Rubric)
	writer.WriteField("language", params.Language)
	writer.WriteField("whisper_provider", params.WhisperProvider)
	writer.WriteField("llm_provider", params.LLMProvider)
	writer.WriteField("clean_transcription", fmt.Sprintf("%t", params.CleanTranscription))
	writer.WriteField("detect_reading", fmt.Sprintf("%t", params.DetectReading))
	if params.GroqAPIKey != "" {
		writer.WriteField("groq_api_key", params.GroqAPIKey)
	}
	if params.MistralAPIKey != "" {
		writer.WriteField("mistral_api_key", params.MistralAPIKey)
	}
	if params.GoogleAPIKey != "" {
		writer.WriteField("google_api_key", params.GoogleAPIKey)
	}
	if params.AzureAPIKey != "" {
		writer.WriteField("azure_api_key", params.AzureAPIKey)
	}
	if params.AzureEndpoint != "" {
		writer.WriteField("azure_endpoint", params.AzureEndpoint)
	}
	writer.Close()

	req, err := http.NewRequest("POST", c.baseURL+"/api/v1/pipeline", body)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("AI service unreachable: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	var result models.FullPipelineResponse
	if err := json.Unmarshal(respBody, &result); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}
	return &result, nil
}
