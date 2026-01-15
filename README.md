# 🎓 Evaluador Universal de Exámenes Orales

Aplicación web desarrollada con **Streamlit** y **Groq Cloud** que permite evaluar exámenes orales de cualquier materia (Biología, Matemáticas, Historia, etc.) utilizando IA de última generación.

## 🚀 Características

- **Universal**: Funciona para cualquier materia académica mediante RAG (Retrieval-Augmented Generation)
- **Transcripción automática**: Usa Whisper (distil-whisper-large-v3-en) para convertir audio a texto
- **Evaluación inteligente**: Llama 3.1 70B analiza y califica según tu material de referencia
- **Limpieza de transcripción**: Elimina muletillas ("eh", "mmm", "este") automáticamente
- **Feedback estructurado**: Calificación, análisis de conceptos, errores específicos y sugerencias
- **Interfaz intuitiva**: Diseño moderno y fácil de usar con Streamlit

## 📋 Requisitos Previos

- Python 3.8 o superior
- Cuenta en [Groq Cloud](https://console.groq.com/) (gratuita)
- API Key de Groq

## 🔧 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd C:\Users\innov\CascadeProjects\evaluador-examenes-orales
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar API Key

Crea un archivo `.env` en la raíz del proyecto:

```bash
copy .env.example .env
```

Edita el archivo `.env` y agrega tu API Key de Groq:

```
GROQ_API_KEY=gsk_tu_api_key_aqui
```

**¿Cómo obtener tu API Key?**
1. Ve a [console.groq.com](https://console.groq.com/)
2. Crea una cuenta gratuita
3. Ve a "API Keys" y genera una nueva key

## ▶️ Uso

### Iniciar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Flujo de trabajo

1. **Material de Referencia**: Pega el contenido que el alumno debe dominar (apuntes, libro, PDF)
2. **Rúbrica de Evaluación**: Define los criterios de calificación
3. **Audio del Examen**: Sube el archivo de audio (.mp3, .wav, .m4a)
4. **Evaluar**: Haz clic en "Evaluar Examen" y espera los resultados

### Ejemplo de uso - Biología (Fotosíntesis)

**Material de Referencia:**
```
La fotosíntesis es el proceso mediante el cual las plantas convierten la luz solar 
en energía química. Ocurre en los cloroplastos y tiene dos fases:

1. Fase luminosa (en tilacoides): Captura energía solar y produce ATP y NADPH
2. Fase oscura o Ciclo de Calvin (en estroma): Usa ATP y NADPH para fijar CO2 
   y producir glucosa

Ecuación general: 6CO2 + 6H2O + luz → C6H12O6 + 6O2
```

**Rúbrica:**
```
- Menciona las dos fases de la fotosíntesis (3 puntos)
- Explica dónde ocurre cada fase (2 puntos)
- Menciona los productos de cada fase (3 puntos)
- Recita correctamente la ecuación química (2 puntos)

Total: 10 puntos
```

## 🏗️ Arquitectura del Proyecto

```
evaluador-examenes-orales/
│
├── app.py                 # Interfaz de usuario (Streamlit)
├── engine.py              # Lógica de integración con Groq
├── requirements.txt       # Dependencias de Python
├── .env                   # Variables de entorno (API Keys)
├── .env.example          # Plantilla para configuración
├── .gitignore            # Archivos ignorados por Git
└── README.md             # Este archivo
```

## 🔍 Detalles Técnicos

### Modelos utilizados

- **Whisper**: `distil-whisper-large-v3-en` - Transcripción de audio a texto
- **LLM**: `llama-3.1-70b-versatile` - Evaluación y análisis

### Proceso de evaluación

1. **Transcripción**: El audio se envía a Whisper para convertirlo en texto
2. **Limpieza** (opcional): Se eliminan muletillas y repeticiones
3. **Evaluación**: El LLM recibe:
   - Material de referencia (contexto de verdad)
   - Rúbrica de evaluación (criterios)
   - Transcripción del alumno
4. **Resultado**: JSON estructurado con calificación y feedback

### Limitaciones

- **Tamaño de audio**: Máximo 25MB por archivo
- **Idioma**: Optimizado para español, pero funciona con otros idiomas
- **Duración**: Audios muy largos (>30 min) pueden requerir segmentación

## 🎯 Casos de Uso

### Biología
- Explicación de procesos celulares
- Ciclos bioquímicos
- Anatomía y fisiología

### Matemáticas
- Demostración de teoremas
- Resolución de problemas paso a paso
- Explicación de conceptos

### Historia
- Narración de eventos históricos
- Análisis de causas y consecuencias
- Cronologías y personajes

### Física/Química
- Explicación de leyes y principios
- Resolución de problemas
- Experimentos y procedimientos

## 🛠️ Personalización

### Cambiar modelos

Edita `engine.py` para usar otros modelos disponibles en Groq:

```python
self.whisper_model = "whisper-large-v3"  # Más preciso pero más lento
self.llm_model = "llama-3.3-70b-versatile"  # Modelo más reciente
```

### Ajustar temperatura

En `engine.py`, modifica el parámetro `temperature` para controlar la creatividad:

```python
temperature=0.2  # Más determinístico (recomendado para evaluaciones)
temperature=0.7  # Más creativo
```

## 🐛 Solución de Problemas

### Error: "GROQ_API_KEY no encontrada"
- Verifica que el archivo `.env` existe y contiene tu API Key
- Asegúrate de que no hay espacios extra en la key

### Error: "Audio file too large"
- Comprime el audio usando herramientas como Audacity
- Reduce la calidad del audio (128kbps es suficiente para voz)

### La transcripción está en inglés
- Verifica que el audio esté en español
- Considera usar `whisper-large-v3` en lugar de `distil-whisper`

## 📊 Rendimiento

- **Transcripción**: ~1-3 segundos por minuto de audio
- **Evaluación**: ~2-5 segundos
- **Total**: Un examen de 5 minutos se procesa en ~10-20 segundos

Gracias a la velocidad de Groq Cloud, la evaluación es casi instantánea.

## 🔐 Seguridad

- Nunca compartas tu archivo `.env` o tu API Key
- El archivo `.gitignore` ya excluye `.env` del control de versiones
- Los archivos de audio se eliminan automáticamente después del procesamiento

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Soporte

Si tienes preguntas o problemas:
- Revisa la sección de Solución de Problemas
- Abre un issue en GitHub
- Consulta la documentación de [Groq](https://console.groq.com/docs)

## 🎓 Créditos

Desarrollado con:
- [Streamlit](https://streamlit.io/) - Framework de UI
- [Groq Cloud](https://groq.com/) - Infraestructura de IA
- [Whisper](https://openai.com/research/whisper) - Modelo de transcripción
- [Llama 3.1](https://ai.meta.com/llama/) - Modelo de lenguaje

---

**¡Disfruta evaluando exámenes con IA! 🚀**
