package handlers

import (
	"io"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/evaluador-examenes-orales/backend/internal/models"
	"github.com/evaluador-examenes-orales/backend/internal/services"
)

type TranscriptionHandler struct {
	aiClient *services.AIClient
}

func NewTranscriptionHandler(aiClient *services.AIClient) *TranscriptionHandler {
	return &TranscriptionHandler{aiClient: aiClient}
}

func (h *TranscriptionHandler) Transcribe(c *gin.Context) {
	file, header, err := c.Request.FormFile("audio")
	if err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error: "Audio file is required",
			Code:  http.StatusBadRequest,
		})
		return
	}
	defer file.Close()

	// 25 MB limit
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

	language := c.DefaultPostForm("language", "es")
	whisperProvider := c.DefaultPostForm("whisper_provider", "groq")

	result, err := h.aiClient.Transcribe(audioData, header.Filename, language, whisperProvider)
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
