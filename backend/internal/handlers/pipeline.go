package handlers

import (
	"io"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/evaluador-examenes-orales/backend/internal/models"
	"github.com/evaluador-examenes-orales/backend/internal/services"
)

type PipelineHandler struct {
	aiClient *services.AIClient
}

func NewPipelineHandler(aiClient *services.AIClient) *PipelineHandler {
	return &PipelineHandler{aiClient: aiClient}
}

func (h *PipelineHandler) FullPipeline(c *gin.Context) {
	file, header, err := c.Request.FormFile("audio")
	if err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error: "Audio file is required",
			Code:  http.StatusBadRequest,
		})
		return
	}
	defer file.Close()

	if header.Size > 25*1024*1024 {
		c.JSON(http.StatusRequestEntityTooLarge, models.ErrorResponse{
			Error: "Audio file exceeds 25 MB limit",
			Code:  http.StatusRequestEntityTooLarge,
		})
		return
	}

	audioData, err := io.ReadAll(file)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Error: "Failed to read audio file",
			Code:  http.StatusInternalServerError,
		})
		return
	}

	material := c.PostForm("material")
	rubric := c.PostForm("rubric")

	if material == "" || rubric == "" {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error: "Material and rubric are required",
			Code:  http.StatusBadRequest,
		})
		return
	}

	params := models.FullPipelineRequest{
		Material:           material,
		Rubric:             rubric,
		Language:           c.DefaultPostForm("language", "es"),
		WhisperProvider:    c.DefaultPostForm("whisper_provider", "groq"),
		LLMProvider:        c.DefaultPostForm("llm_provider", "mistral"),
		CleanTranscription: c.DefaultPostForm("clean_transcription", "true") == "true",
		DetectReading:      c.DefaultPostForm("detect_reading", "true") == "true",
		GroqAPIKey:         c.PostForm("groq_api_key"),
		MistralAPIKey:      c.PostForm("mistral_api_key"),
		GoogleAPIKey:       c.PostForm("google_api_key"),
		AzureAPIKey:        c.PostForm("azure_api_key"),
		AzureEndpoint:      c.PostForm("azure_endpoint"),
	}

	result, err := h.aiClient.FullPipeline(audioData, header.Filename, params)
	if err != nil {
		c.JSON(http.StatusBadGateway, models.ErrorResponse{
			Error:   "AI service error",
			Code:    http.StatusBadGateway,
			Details: err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, result)
}
