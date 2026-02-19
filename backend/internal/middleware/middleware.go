package middleware

import (
	"fmt"
	"log"
	"math/rand"
	"time"

	"github.com/gin-gonic/gin"
)

func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method

		c.Next()

		latency := time.Since(start)
		status := c.Writer.Status()

		log.Printf("[%s] %s %s | %d | %v",
			time.Now().Format("2006-01-02 15:04:05"),
			method, path, status, latency,
		)
	}
}

func Recovery() gin.HandlerFunc {
	return gin.Recovery()
}

func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = generateID()
		}
		c.Set("request_id", requestID)
		c.Header("X-Request-ID", requestID)
		c.Next()
	}
}

func generateID() string {
	return fmt.Sprintf("%s-%08x", time.Now().Format("20060102150405"), rand.Uint32())
}
