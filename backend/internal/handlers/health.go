package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/evaluador-examenes-orales/backend/internal/models"
	"github.com/evaluador-examenes-orales/backend/internal/services"
)

type HealthHandler struct {
	aiClient *services.AIClient
}

func NewHealthHandler(aiClient *services.AIClient) *HealthHandler {
	return &HealthHandler{aiClient: aiClient}
}

func (h *HealthHandler) Health(c *gin.Context) {
	aiStatus, _ := h.aiClient.Health()

	c.JSON(http.StatusOK, models.HealthResponse{
		Status:    "ok",
		Service:   "backend-gateway",
		Version:   "1.0.0",
		AIService: *aiStatus,
	})
}
