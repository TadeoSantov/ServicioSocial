# Arquitectura

## Modo de uso principal

La app corre como una aplicación Streamlit de un solo proceso. Es la forma más simple de usarla y no requiere Docker ni servicios adicionales.

```
Usuario → Navegador → Streamlit (app.py) → engine.py → Groq API
```

`app.py` maneja toda la interfaz. `engine.py` contiene la lógica de negocio: transcripción, limpieza, detección de lectura y evaluación. Ambos se comunican directamente, sin red de por medio.

## Pipeline de evaluación

```
Audio (.mp3 / .wav / grabación)
        │
        ▼
  Transcripción (Whisper via Groq)
        │
        ▼
  Limpieza de muletillas (opcional, LLM)
        │
        ▼
  Detección de lectura (opcional, LLM)
        │
        ▼
  Evaluación contra rúbrica (LLM)
        │
        ▼
  Resultado: calificación + feedback estructurado
```

Cada paso es independiente. Si la limpieza está desactivada, el texto transcrito pasa directamente a la evaluación.

## Modelos utilizados

| Tarea | Modelo por defecto | Proveedor |
|-------|--------------------|-----------|
| Transcripción | `distil-whisper-large-v3-en` | Groq |
| Limpieza de texto | `llama-3.3-70b-versatile` | Groq |
| Detección de lectura | `llama-3.3-70b-versatile` | Groq |
| Evaluación | `llama-3.3-70b-versatile` | Groq / Mistral / Gemini |

El modelo de evaluación puede cambiarse desde la barra lateral de la app sin tocar código.

## Arquitectura enterprise (microservicios)

El proyecto también incluye una arquitectura de microservicios para despliegues a mayor escala:

```
Usuario → Next.js (frontend) → Go API Gateway → Python FastAPI (ai-service)
            :3000                  :8080               :8000
```

| Carpeta | Tecnología | Responsabilidad |
|---------|-----------|-----------------|
| `frontend/` | Next.js 14 + TypeScript + TailwindCSS | Interfaz web |
| `backend/` | Go 1.22 + Gin | API Gateway, validación, CORS |
| `ai-service/` | Python 3.12 + FastAPI | Transcripción, evaluación, LLMs |

Para levantar todo con Docker:

```bash
docker-compose up --build
```

Esta arquitectura permite escalar cada servicio de forma independiente y está preparada para producción en AWS ECS, GCP Cloud Run o Azure Container Apps.

## Estructura de archivos

```
evaluador-examenes-orales/
│
├── app.py                  # Interfaz Streamlit (modo simple)
├── engine.py               # Motor de IA: transcripción + evaluación
├── launcher.py             # Lanzador: detecta puerto libre, abre navegador
├── ejecutar.bat            # Script de inicio para Windows
├── requirements.txt        # Dependencias Python (modo simple)
├── docker-compose.yml      # Orquestación de los tres microservicios
├── .env.example            # Plantilla de variables de entorno
│
├── frontend/               # Next.js
│   ├── src/
│   │   ├── app/            # Páginas y layouts (App Router)
│   │   ├── components/     # Componentes React
│   │   ├── lib/            # Cliente API, utilidades
│   │   └── types/          # Tipos TypeScript
│   └── Dockerfile
│
├── backend/                # Go API Gateway
│   ├── cmd/server/         # Punto de entrada
│   ├── internal/
│   │   ├── config/
│   │   ├── handlers/       # Handlers HTTP
│   │   ├── middleware/     # Logging, recovery, request ID
│   │   ├── models/
│   │   └── services/       # Cliente del ai-service
│   └── Dockerfile
│
├── ai-service/             # Python FastAPI
│   ├── app/
│   │   ├── routers/        # Endpoints de la API
│   │   ├── services/       # Lógica de Whisper y LLMs
│   │   ├── models.py       # Schemas Pydantic
│   │   └── config.py       # Configuración
│   ├── main.py
│   └── Dockerfile
│
├── ejemplos/               # Material y rúbricas de prueba
└── docs/                   # Esta documentación
```

## Endpoints del API (modo microservicios)

El Go backend expone estos endpoints en `:8080` y los delega al ai-service en `:8000`:

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del sistema |
| POST | `/api/v1/transcribe` | Transcribir audio (multipart) |
| POST | `/api/v1/clean` | Limpiar transcripción (JSON) |
| POST | `/api/v1/detect-reading` | Detectar lectura (JSON) |
| POST | `/api/v1/evaluate` | Evaluar transcripción (JSON) |
| POST | `/api/v1/pipeline` | Pipeline completo: audio → evaluación |

La documentación interactiva del ai-service está disponible en `http://localhost:8000/docs` (Swagger UI).
