package main

import (
	"log"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"

	"github.com/evaluador-examenes-orales/backend/internal/config"
	"github.com/evaluador-examenes-orales/backend/internal/handlers"
	"github.com/evaluador-examenes-orales/backend/internal/middleware"
	"github.com/evaluador-examenes-orales/backend/internal/services"
)

func main() {
	_ = godotenv.Load()

	cfg := config.Load()

	if !cfg.IsDevelopment() {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.New()
	r.Use(middleware.Logger())
	r.Use(middleware.Recovery())
	r.Use(middleware.RequestID())

	r.Use(cors.New(cors.Config{
		AllowOrigins:     cfg.CORSOrigins,
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization", "X-Request-ID"},
		ExposeHeaders:    []string{"X-Request-ID"},
		AllowCredentials: true,
	}))

	// AI service client
	aiClient := services.NewAIClient(cfg)

	// Handlers
	healthH := handlers.NewHealthHandler(aiClient)
	transcriptionH := handlers.NewTranscriptionHandler(aiClient)
	evaluationH := handlers.NewEvaluationHandler(aiClient)
	pipelineH := handlers.NewPipelineHandler(aiClient)

	// Routes
	r.GET("/health", healthH.Health)

	api := r.Group("/api/v1")
	{
		api.POST("/transcribe", transcriptionH.Transcribe)
		api.POST("/clean", evaluationH.CleanTranscription)
		api.POST("/detect-reading", evaluationH.DetectReading)
		api.POST("/evaluate", evaluationH.Evaluate)
		api.POST("/pipeline", pipelineH.FullPipeline)
	}

	log.Printf("Backend gateway starting on :%s", cfg.Port)
	log.Printf("AI Service URL: %s", cfg.AIServiceURL)
	log.Printf("Environment: %s", cfg.Env)

	if err := r.Run(":" + cfg.Port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
