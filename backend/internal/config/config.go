package config

import (
	"os"
	"strings"
)

type Config struct {
	// Server
	Port string
	Env  string

	// AI Service URL (Python FastAPI)
	AIServiceURL string

	// CORS
	CORSOrigins []string

	// API Keys (passed through to AI service or validated here)
	GroqAPIKey         string
	MistralAPIKey      string
	GoogleAPIKey       string
	AzureOpenAIAPIKey  string
	AzureOpenAIEndpoint string
}

func Load() *Config {
	return &Config{
		Port:                getEnv("PORT", "8080"),
		Env:                 getEnv("ENV", "development"),
		AIServiceURL:        getEnv("AI_SERVICE_URL", "http://localhost:8000"),
		CORSOrigins:         strings.Split(getEnv("CORS_ORIGINS", "http://localhost:3000"), ","),
		GroqAPIKey:          getEnv("GROQ_API_KEY", ""),
		MistralAPIKey:       getEnv("MISTRAL_API_KEY", ""),
		GoogleAPIKey:        getEnv("GOOGLE_API_KEY", ""),
		AzureOpenAIAPIKey:   getEnv("AZURE_OPENAI_API_KEY", ""),
		AzureOpenAIEndpoint: getEnv("AZURE_OPENAI_ENDPOINT", ""),
	}
}

func (c *Config) IsDevelopment() bool {
	return c.Env == "development"
}

func getEnv(key, fallback string) string {
	if val, ok := os.LookupEnv(key); ok {
		return val
	}
	return fallback
}
