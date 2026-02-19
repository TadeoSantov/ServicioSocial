package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/evaluador-examenes-orales/backend/internal/models"
	"github.com/evaluador-examenes-orales/backend/internal/services"
)

type EvaluationHandler struct {
	aiClient *services.AIClient
}

func NewEvaluationHandler(aiClient *services.AIClient) *EvaluationHandler {
	return &EvaluationHandler{aiClient: aiClient}
}

func (h *EvaluationHandler) CleanTranscription(c *gin.Context) {
	var req models.CleanTranscriptionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "Invalid request body",
			Code:    http.StatusBadRequest,
			Details: err.Error(),
		})
		return
	}

	if req.LLMProvider == "" {
		req.LLMProvider = "mistral"
	}

	result, err := h.aiClient.CleanTranscription(req.Transcription, req.LLMProvider)
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

func (h *EvaluationHandler) DetectReading(c *gin.Context) {
	var req models.DetectReadingRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "Invalid request body",
			Code:    http.StatusBadRequest,
			Details: err.Error(),
		})
		return
	}

	if req.LLMProvider == "" {
		req.LLMProvider = "mistral"
	}

	result, err := h.aiClient.DetectReading(req.Transcription, req.LLMProvider)
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

func (h *EvaluationHandler) Evaluate(c *gin.Context) {
	var req models.EvaluateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "Invalid request body",
			Code:    http.StatusBadRequest,
			Details: err.Error(),
		})
		return
	}

	if req.LLMProvider == "" {
		req.LLMProvider = "mistral"
	}

	result, err := h.aiClient.Evaluate(req.Transcription, req.Material, req.Rubric, req.LLMProvider)
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
