# Solución de problemas

## Errores de configuración

### "GROQ_API_KEY no encontrada" o similar

El archivo `.env` no existe o la variable está vacía.

```bash
# Verificar que el archivo existe
dir .env

# Si no existe, crearlo desde la plantilla
copy .env.example .env
```

Abre `.env` y asegúrate de que la línea se ve así (sin espacios, sin comillas):

```
GROQ_API_KEY=gsk_abc123...
```

### La app abre pero no hace nada al evaluar

Generalmente es porque la API key es inválida o expiró. Revisa la consola donde corre Streamlit — ahí aparece el error real. Si ves `401` o `authentication`, la key está mal.

---

## Errores de audio

### "Audio file too large"

Groq acepta archivos de hasta 25 MB. Para reducir el tamaño:

- Convierte a MP3 con bitrate de 128 kbps (suficiente para voz)
- Usa [Audacity](https://www.audacityteam.org/) o `ffmpeg`:

```bash
ffmpeg -i audio_original.wav -b:a 128k audio_comprimido.mp3
```

### La transcripción sale en inglés o con errores

- Verifica que el audio realmente esté en español
- Prueba con el modelo `whisper-large-v3` en lugar del modelo por defecto (edita `engine.py`)
- Asegúrate de que el audio no tenga mucho ruido de fondo

### No aparece el botón de grabar

```bash
pip install --upgrade audio-recorder-streamlit
```

Si el navegador no pide permiso del micrófono, ve a Configuración → Privacidad → Permisos de sitio y permite el micrófono para `localhost`.

---

## Errores de instalación

### Error al instalar dependencias en Windows

Algunos paquetes como `pydub` requieren que `ffmpeg` esté instalado en el sistema:

1. Descarga ffmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extrae y agrega la carpeta `bin` al PATH del sistema
3. Verifica: `ffmpeg -version`

### `pip install` falla con errores de permisos

```bash
pip install -r requirements.txt --user
```

---

## Problemas de rendimiento

### La evaluación tarda mucho

Los tiempos normales son:
- Transcripción: 1–3 segundos por minuto de audio
- Evaluación: 2–5 segundos

Si tarda más de 30 segundos, puede ser un problema de conectividad con la API de Groq. Verifica tu conexión a internet.

### La app se congela al grabar

Cierra otras pestañas del navegador que puedan estar usando el micrófono. Reinicia Streamlit con `Ctrl+C` y vuelve a ejecutar.

---

## Resultados inesperados

### La calificación parece incorrecta

- Revisa que el material de referencia contenga los conceptos que esperas que el estudiante mencione
- Asegúrate de que la rúbrica sea específica: "menciona X (2 puntos)" funciona mejor que "explica el tema (10 puntos)"
- Prueba con temperatura más baja en `engine.py`: `temperature=0.1`

### El detector de lectura siempre marca alerta

Algunos estudiantes con muy buen dominio del tema hablan de forma muy fluida y pueden activar falsos positivos. Considera el contexto antes de tomar una decisión. El detector es una herramienta de apoyo, no un veredicto.

### El detector nunca detecta lectura aunque el estudiante está leyendo

Verifica que la opción esté activada en la barra lateral. Si está activada y no detecta, puede ser que el estudiante lea de forma muy expresiva y natural.

---

## Docker (modo microservicios)

### Los contenedores no levantan

```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs ai-service
```

### El frontend no conecta con el backend

Verifica que las variables `CORS_ORIGINS` y `AI_SERVICE_URL` en `.env` coincidan con los puertos que están corriendo.
