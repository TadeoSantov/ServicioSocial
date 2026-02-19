# Instalación y configuración

## Requisitos

- Python 3.8 o superior
- Cuenta en [Groq Cloud](https://console.groq.com/) — gratuita, solo necesitas registrarte
- (Opcional) API key de Mistral o Google Gemini si quieres usar un LLM alternativo

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

Las dependencias principales son:

| Paquete | Para qué sirve |
|---------|----------------|
| `streamlit` | Interfaz web |
| `groq` | Transcripción con Whisper + LLM |
| `mistralai` | LLM alternativo (Mistral) |
| `google-genai` | LLM alternativo (Gemini) |
| `openai` | Compatibilidad con Azure OpenAI |
| `audio-recorder-streamlit` | Grabación de audio en el navegador |
| `pydub` | Procesamiento de archivos de audio |
| `python-dotenv` | Carga de variables de entorno |

### 2. Configurar variables de entorno

Copia la plantilla y edítala:

```bash
copy .env.example .env
```

Abre `.env` y completa las keys que vayas a usar:

```env
# Requerida para transcripción
GROQ_API_KEY=gsk_...

# Al menos una de estas para evaluación
MISTRAL_API_KEY=...
GOOGLE_API_KEY=...
```

### 3. Obtener las API keys

**Groq (requerida)**
1. Ve a [console.groq.com](https://console.groq.com/)
2. Crea una cuenta (es gratuita)
3. En el menú lateral, entra a **API Keys**
4. Genera una nueva key y cópiala en `.env`

**Mistral (opcional)**
1. Ve a [console.mistral.ai](https://console.mistral.ai/)
2. Crea una cuenta
3. En **API Keys**, genera una key

**Google Gemini (opcional)**
1. Ve a [aistudio.google.com](https://aistudio.google.com/)
2. Haz clic en **Get API key**
3. Copia la key en `.env`

**Azure OpenAI (enterprise, opcional)**

Requiere una suscripción activa de Azure. Completa estas variables en `.env`:

```env
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_WHISPER_DEPLOYMENT=whisper
AZURE_API_VERSION=2024-12-01-preview
```

## Verificar la instalación

```bash
python -c "import streamlit, groq, dotenv; print('OK')"
```

Si imprime `OK`, todo está instalado correctamente.

## Notas de seguridad

- El archivo `.env` está excluido del control de versiones por `.gitignore`. No lo subas a GitHub.
- No compartas tu API key en código, issues ni pull requests.
- Los archivos de audio se procesan en memoria y no se almacenan en disco de forma permanente.
