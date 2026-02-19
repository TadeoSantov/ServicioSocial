# Evaluador de Exámenes Orales

Aplicación web para evaluar exámenes orales con IA. Transcribe el audio del estudiante, lo compara contra el material de referencia y la rúbrica del docente, y devuelve una calificación con feedback detallado.

Funciona para cualquier materia: Biología, Historia, Matemáticas, Literatura, etc.

## Inicio rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar API keys
copy .env.example .env
# Editar .env y agregar GROQ_API_KEY

# 3. Ejecutar
streamlit run app.py
```

En Windows también puedes usar `ejecutar.bat`, que hace todo lo anterior automáticamente.

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [Instalación y configuración](docs/setup.md) | Requisitos, API keys, variables de entorno |
| [Guía de uso](docs/usage.md) | Flujo de trabajo, grabación, detector de lectura, ejemplos |
| [Arquitectura](docs/architecture.md) | Estructura del proyecto, modelos, pipeline de evaluación |
| [Solución de problemas](docs/troubleshooting.md) | Errores frecuentes y cómo resolverlos |

## Estructura del proyecto

```
evaluador-examenes-orales/
├── app.py                  # Interfaz Streamlit
├── engine.py               # Motor de IA (transcripción + evaluación)
├── launcher.py             # Lanzador con detección de puerto libre
├── ejecutar.bat            # Script de inicio para Windows
├── requirements.txt        # Dependencias Python
├── docker-compose.yml      # Orquestación de microservicios
├── .env.example            # Plantilla de variables de entorno
├── ejemplos/               # Material y rúbricas de prueba
├── frontend/               # UI Next.js (arquitectura enterprise)
├── backend/                # API Gateway en Go
├── ai-service/             # Microservicio Python/FastAPI
└── docs/                   # Documentación detallada
```

## Proveedores de IA soportados

| Proveedor | Uso | Requerido |
|-----------|-----|-----------|
| Groq | Transcripción con Whisper | Sí |
| Mistral | Evaluación LLM (principal) | Al menos uno |
| Google Gemini | Evaluación LLM (alternativo) | No |
| Azure OpenAI | LLM + Whisper (enterprise) | No |

## Licencia

MIT
