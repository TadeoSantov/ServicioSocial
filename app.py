import streamlit as st
import os
import tempfile
import json
import concurrent.futures
from engine import EvaluadorEngine
from audio_recorder_streamlit import audio_recorder

st.set_page_config(
    page_title="Evaluador de Exámenes Orales",
    page_icon="E",
    layout="wide"
)

st.markdown("""
<style>
    :root {
        --primary: #1a1a2e;
        --accent: #4361ee;
        --accent-light: #eef1ff;
        --surface: #ffffff;
        --surface-alt: #f8f9fc;
        --border: #e2e5f1;
        --text: #1a1a2e;
        --text-muted: #6b7280;
        --success: #059669;
        --warning: #d97706;
        --danger: #dc2626;
    }

    .main-header {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        background: var(--primary);
        margin: -2rem -2rem 2rem -2rem;
        border-radius: 0 0 0.5rem 0.5rem;
        color: white;
    }

    .main-header h1 {
        font-size: 1.75rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        letter-spacing: -0.025em;
    }

    .main-header .subtitle {
        font-size: 0.875rem;
        opacity: 0.7;
        font-weight: 400;
    }

    .section-card {
        background: var(--surface);
        padding: 1.25rem;
        border-radius: 0.5rem;
        margin: 0.75rem 0;
        border: 1px solid var(--border);
    }

    .section-card h3 {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .section-card p {
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-bottom: 0.75rem;
    }

    .metric-card {
        background: var(--surface);
        padding: 1.25rem;
        border-radius: 0.5rem;
        border: 1px solid var(--border);
    }

    .stButton > button {
        border-radius: 0.375rem;
        font-weight: 500;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface-alt);
        border-radius: 0.375rem;
        padding: 0.125rem;
        border: 1px solid var(--border);
        gap: 0;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0.25rem;
        font-weight: 500;
        font-size: 0.85rem;
    }

    .stProgress > div > div > div > div {
        background: var(--accent);
    }

    .stTextArea > div > div > textarea {
        border-radius: 0.375rem;
        border: 1px solid var(--border);
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 0.875rem;
    }

    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid var(--border);
        color: var(--text-muted);
        font-size: 0.75rem;
    }

    .badge-experimental {
        display: inline-block;
        background: #fef3c7;
        color: #92400e;
        font-size: 0.65rem;
        font-weight: 600;
        padding: 0.125rem 0.5rem;
        border-radius: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .provider-info {
        font-size: 0.75rem;
        color: var(--text-muted);
        padding: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_quality_label(value: str) -> str:
    labels = {
        "excelente": "Excelente",
        "buena": "Buena",
        "bueno": "Bueno",
        "regular": "Regular",
        "deficiente": "Deficiente"
    }
    return labels.get(value.lower(), value.capitalize())

def get_quality_indicator(value: str) -> str:
    indicators = {
        "excelente": "●",
        "buena": "●",
        "bueno": "●",
        "regular": "◐",
        "deficiente": "○"
    }
    return indicators.get(value.lower(), "○")

st.markdown("""
<div class="main-header">
    <h1>Evaluador de Exámenes Orales</h1>
    <p class="subtitle">Sistema de evaluación automatizada multi-paso</p>
</div>
""", unsafe_allow_html=True)

if "evaluacion_resultado" not in st.session_state:
    st.session_state.evaluacion_resultado = None

# =============================================================================
# SIDEBAR — Configuration
# =============================================================================
with st.sidebar:
    st.markdown("### Configuración")

    # --- Transcription provider ---
    st.markdown("**Transcripción (Whisper)**")
    proveedor_whisper = st.selectbox(
        "Proveedor de transcripción",
        options=["groq", "azure"],
        format_func=lambda x: {
            "groq": "Groq — Whisper Large v3",
            "azure": "Azure Whisper (experimental)",
        }.get(x, x),
        index=0,
        help="Groq es el proveedor principal. Azure Whisper requiere configuración de Azure OpenAI.",
        label_visibility="collapsed",
    )

    st.divider()

    # --- LLM provider ---
    st.markdown("**Modelo de evaluación (LLM)**")
    proveedor_llm = st.selectbox(
        "Proveedor LLM",
        options=["mistral", "gemini", "azure_openai"],
        format_func=lambda x: {
            "mistral": "Mistral Large — Principal",
            "gemini": "Gemini 2.0 Flash — Backup",
            "azure_openai": "Azure OpenAI (experimental)",
        }.get(x, x),
        index=0,
        help="Mistral es el LLM principal. Gemini sirve como respaldo. Azure OpenAI es experimental.",
        label_visibility="collapsed",
    )

    st.divider()

    # --- API Keys ---
    st.markdown("**Claves de API**")

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY requerida para transcripción")
        groq_key_input = st.text_input("Groq API Key", type="password", key="groq_key")
        if groq_key_input:
            os.environ["GROQ_API_KEY"] = groq_key_input
            groq_api_key = groq_key_input
    else:
        st.caption("Groq — Configurada")

    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if proveedor_llm == "mistral":
        if not mistral_api_key:
            st.warning("MISTRAL_API_KEY requerida")
            mistral_key_input = st.text_input("Mistral API Key", type="password", key="mistral_key")
            if mistral_key_input:
                os.environ["MISTRAL_API_KEY"] = mistral_key_input
                mistral_api_key = mistral_key_input
        else:
            st.caption("Mistral — Configurada")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if proveedor_llm == "gemini":
        if not google_api_key:
            st.warning("GOOGLE_API_KEY requerida para Gemini")
            google_key_input = st.text_input("Google API Key", type="password", key="google_key")
            if google_key_input:
                os.environ["GOOGLE_API_KEY"] = google_key_input
                google_api_key = google_key_input
        else:
            st.caption("Google AI — Configurada")

    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if proveedor_llm == "azure_openai" or proveedor_whisper == "azure":
        if not azure_openai_api_key:
            st.warning("Configuración de Azure requerida")
            az_key = st.text_input("Azure OpenAI API Key", type="password", key="az_key")
            az_endpoint = st.text_input("Azure OpenAI Endpoint", key="az_endpoint", placeholder="https://tu-recurso.openai.azure.com")
            if az_key:
                os.environ["AZURE_OPENAI_API_KEY"] = az_key
                azure_openai_api_key = az_key
            if az_endpoint:
                os.environ["AZURE_OPENAI_ENDPOINT"] = az_endpoint
        else:
            st.caption("Azure OpenAI — Configurada")

    st.divider()

    # --- Processing options ---
    st.markdown("**Procesamiento**")

    limpiar_transcripcion = st.checkbox(
        "Limpiar transcripción",
        value=True,
        help="Elimina muletillas (eh, mmm, este) antes de evaluar"
    )

    detectar_lectura = st.checkbox(
        "Detectar lectura / audio IA",
        value=True,
        help="Analiza patrones de habla para detectar si el estudiante está leyendo o si el audio fue generado por IA"
    )

    idioma_audio = st.selectbox(
        "Idioma del audio",
        options=["es", "en", "fr", "de", "pt", "it"],
        format_func=lambda x: {
            "es": "Español",
            "en": "English",
            "fr": "Français",
            "de": "Deutsch",
            "pt": "Português",
            "it": "Italiano"
        }.get(x, x),
        index=0
    )

# =============================================================================
# MAIN CONTENT — Examples, Material, Rubric, Audio, Evaluate
# =============================================================================

ejemplo_seleccionado = st.selectbox(
    "Ejemplo predefinido (opcional)",
    options=["-- Ninguno --", "Ratatouille"],
    help="Carga un ejemplo para pruebas rápidas"
)

if "material_cargado" not in st.session_state:
    st.session_state.material_cargado = ""
if "rubrica_cargada" not in st.session_state:
    st.session_state.rubrica_cargada = ""

if ejemplo_seleccionado == "Ratatouille":
    try:
        with open("ejemplos/ratatouille_material.txt", "r", encoding="utf-8") as f:
            st.session_state.material_cargado = f.read()
        with open("ejemplos/ratatouille_rubrica.txt", "r", encoding="utf-8") as f:
            st.session_state.rubrica_cargada = f.read()
        st.success("Ejemplo cargado correctamente")
    except FileNotFoundError:
        st.error("No se encontraron los archivos de ejemplo en la carpeta 'ejemplos/'")
        st.session_state.material_cargado = ""
        st.session_state.rubrica_cargada = ""
else:
    st.session_state.material_cargado = ""
    st.session_state.rubrica_cargada = ""

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div class="section-card">
        <h3>Material de referencia</h3>
        <p>Contenido que el alumno debe dominar</p>
    </div>
    """, unsafe_allow_html=True)

    material_referencia = st.text_area(
        "Material de Referencia",
        value=st.session_state.material_cargado,
        height=280,
        placeholder="Pega aquí el contenido del tema a evaluar...",
        label_visibility="collapsed",
        key="material_ref_input"
    )

with col2:
    st.markdown("""
    <div class="section-card">
        <h3>Rúbrica de evaluación</h3>
        <p>Criterios y puntos para calificar</p>
    </div>
    """, unsafe_allow_html=True)

    rubrica = st.text_area(
        "Rúbrica",
        value=st.session_state.rubrica_cargada,
        height=280,
        placeholder="Define los criterios de evaluación y su puntaje...",
        label_visibility="collapsed"
    )

st.divider()

st.markdown("""
<div class="section-card">
    <h3>Audio del examen</h3>
    <p>Sube un archivo o graba directamente</p>
</div>
""", unsafe_allow_html=True)

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "audio_source" not in st.session_state:
    st.session_state.audio_source = None

tab_subir, tab_grabar = st.tabs(["Subir archivo", "Grabar audio"])

with tab_subir:
    audio_file = st.file_uploader(
        "Archivo de audio",
        type=["mp3", "wav", "m4a", "ogg", "flac", "webm"],
        help="Formatos soportados: MP3, WAV, M4A, OGG, FLAC, WEBM. Máximo 25 MB.",
        key="file_uploader"
    )

    if audio_file is not None:
        st.session_state.audio_bytes = audio_file.getvalue()
        st.session_state.audio_source = "uploaded"
        st.session_state.audio_filename = audio_file.name

        st.audio(audio_file)
        file_size_mb = len(audio_file.getvalue()) / (1024 * 1024)

        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.caption(f"Archivo: {audio_file.name}")
        with col_info2:
            if file_size_mb > 25:
                st.warning(f"{file_size_mb:.1f} MB — Excede el límite de 25 MB")
            else:
                st.caption(f"Tamaño: {file_size_mb:.2f} MB")

with tab_grabar:
    col_rec1, col_rec2 = st.columns([2, 1])

    with col_rec1:
        audio_bytes = audio_recorder(
            text="Clic para grabar",
            recording_color="#dc2626",
            neutral_color="#4361ee",
            icon_name="microphone",
            icon_size="3x",
            pause_threshold=3.0,
            sample_rate=44100
        )

    with col_rec2:
        st.markdown("""
        **Instrucciones:**
        1. Clic en el micrófono
        2. Permite acceso al micrófono
        3. Habla claramente
        4. Clic de nuevo para detener
        """)

    if audio_bytes:
        st.session_state.audio_bytes = audio_bytes
        st.session_state.audio_source = "recorded"
        st.session_state.audio_filename = "grabacion.wav"

        st.success("Audio grabado correctamente")
        st.audio(audio_bytes, format="audio/wav")

        audio_size_mb = len(audio_bytes) / (1024 * 1024)
        st.caption(f"Tamaño: {audio_size_mb:.2f} MB")

        if st.button("Borrar grabación", key="clear_recording"):
            st.session_state.audio_bytes = None
            st.session_state.audio_source = None
            st.rerun()

st.divider()

# =============================================================================
# EVALUATE BUTTON
# =============================================================================

def _validate_keys() -> str | None:
    if proveedor_whisper == "groq" and not groq_api_key:
        return "Configura GROQ_API_KEY para transcripción"
    if proveedor_whisper == "azure" and not os.getenv("AZURE_OPENAI_API_KEY"):
        return "Configura Azure OpenAI para transcripción"
    if proveedor_llm == "mistral" and not os.getenv("MISTRAL_API_KEY"):
        return "Configura MISTRAL_API_KEY"
    if proveedor_llm == "gemini" and not os.getenv("GOOGLE_API_KEY"):
        return "Configura GOOGLE_API_KEY"
    if proveedor_llm == "azure_openai" and not os.getenv("AZURE_OPENAI_API_KEY"):
        return "Configura Azure OpenAI API Key"
    return None

if st.button("Evaluar examen", type="primary", use_container_width=True):
    if not material_referencia.strip():
        st.error("Ingresa el material de referencia")
    elif not rubrica.strip():
        st.error("Ingresa la rúbrica de evaluación")
    elif not st.session_state.audio_bytes:
        st.error("Sube un archivo de audio o graba uno")
    else:
        key_error = _validate_keys()
        if key_error:
            st.error(key_error)
        else:
            try:
                file_extension = st.session_state.audio_filename.split('.')[-1] if '.' in st.session_state.audio_filename else 'wav'
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                    tmp_file.write(st.session_state.audio_bytes)
                    tmp_file_path = tmp_file.name

                evaluador = EvaluadorEngine(
                    proveedor_llm=proveedor_llm,
                    proveedor_whisper=proveedor_whisper,
                    groq_api_key=groq_api_key,
                    mistral_api_key=os.getenv("MISTRAL_API_KEY"),
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                )

                with st.status("Evaluando examen...", expanded=True) as status:
                    st.write("Paso 1/6 — Transcribiendo audio con Whisper...")
                    res_trans = evaluador.transcribir_audio(tmp_file_path, idioma_audio)
                    if not res_trans["success"]:
                        status.update(label="Error en transcripción", state="error")
                        st.error(res_trans.get("error", "Error en transcripción"))
                        resultado = res_trans
                    else:
                        transcripcion = res_trans["transcripcion"]
                        st.write("Transcripción completada")

                        patron_lectura = None
                        if detectar_lectura and limpiar_transcripcion:
                            st.write("Paso 2/6 — Analizando patrones y limpiando transcripción (en paralelo)...")
                            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                                fut_lectura = pool.submit(evaluador.detectar_patron_lectura, transcripcion)
                                fut_limpieza = pool.submit(evaluador.limpiar_transcripcion, transcripcion)
                                patron_lectura = fut_lectura.result()
                                transcripcion_limpia = fut_limpieza.result()
                            st.write("Análisis de patrones y limpieza completados")
                        elif detectar_lectura:
                            st.write("Paso 2/6 — Analizando patrones de lectura...")
                            patron_lectura = evaluador.detectar_patron_lectura(transcripcion)
                            transcripcion_limpia = transcripcion
                            st.write("Análisis de patrones completado")
                        elif limpiar_transcripcion:
                            st.write("Paso 2/6 — Limpiando transcripción...")
                            transcripcion_limpia = evaluador.limpiar_transcripcion(transcripcion)
                            st.write("Limpieza completada")
                        else:
                            transcripcion_limpia = transcripcion

                        st.write("Paso 3/6 — Extrayendo conceptos clave...")
                        conceptos = evaluador._extraer_conceptos(material_referencia)

                        st.write("Paso 4/6 — Analizando respuesta del alumno...")
                        analisis = evaluador._analizar_respuesta(transcripcion_limpia, conceptos)

                        st.write("Paso 5/6 — Calculando calificación...")
                        calificacion = evaluador._calcular_calificacion(conceptos, analisis, rubrica)

                        st.write("Paso 6/6 — Generando feedback...")
                        feedback = evaluador._generar_feedback(analisis, calificacion, conceptos)

                        evaluacion = {
                            "calificacion_final": calificacion.get("calificacion_final", 0),
                            "nivel_confianza": calificacion.get("nivel_confianza", "medio"),
                            "tema_detectado": conceptos.get("tema_detectado", "General"),
                            "nivel_dificultad": conceptos.get("nivel_dificultad", "Intermedio"),
                            "desglose_calificacion": {
                                "por_criterio": calificacion.get("calificacion_por_criterio", []),
                                "penalizaciones": calificacion.get("penalizaciones", []),
                                "bonificaciones": calificacion.get("bonificaciones", []),
                                "justificacion": calificacion.get("justificacion_general", ""),
                            },
                            "analisis_conceptual": {
                                "conceptos_esperados": {
                                    "principales": conceptos.get("conceptos_principales", []),
                                    "secundarios": conceptos.get("conceptos_secundarios", []),
                                },
                                "conceptos_mencionados": analisis.get("conceptos_correctos", []),
                                "conceptos_omitidos": analisis.get("conceptos_omitidos", []),
                                "cobertura_porcentaje": evaluador._calcular_cobertura(conceptos, analisis),
                            },
                            "errores_detectados": {
                                "factuales": analisis.get("errores_factuales", []),
                                "inventados": analisis.get("informacion_inventada", []),
                            },
                            "metricas_comunicacion": {
                                "claridad": analisis.get("claridad_explicacion", "regular"),
                                "coherencia": analisis.get("coherencia_argumentativa", "regular"),
                                "vocabulario_tecnico": analisis.get("uso_vocabulario_tecnico", "regular"),
                            },
                            "feedback_alumno": feedback.get("feedback_alumno", {}),
                            "nota_docente": feedback.get("nota_docente", {}),
                            "citas_destacadas": analisis.get("citas_destacadas", []),
                        }

                        resultado = {
                            "success": True,
                            "transcripcion_original": res_trans["transcripcion"],
                            "transcripcion_limpia": transcripcion_limpia,
                            "duracion_audio": res_trans.get("duracion"),
                            "idioma": idioma_audio,
                            "patron_lectura": patron_lectura,
                            "evaluacion": evaluacion,
                        }
                        status.update(label="Evaluación completada", state="complete")

                os.unlink(tmp_file_path)

                if resultado["success"]:
                    st.session_state.evaluacion_resultado = resultado
                    st.rerun()
                else:
                    st.error(f"Error: {resultado.get('error', 'Error desconocido')}")

            except Exception as e:
                st.error(f"Error inesperado: {str(e)}")

# =============================================================================
# RESULTS
# =============================================================================

if st.session_state.evaluacion_resultado:
    resultado = st.session_state.evaluacion_resultado
    evaluacion = resultado["evaluacion"]

    st.divider()

    calificacion = float(evaluacion.get("calificacion_final", 0))

    st.markdown("""
    <div class="section-card">
        <h3>Resultados de la evaluación</h3>
    </div>
    """, unsafe_allow_html=True)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.metric(
            label="Calificación final",
            value=f"{calificacion}/10",
            delta=f"Confianza: {evaluacion.get('nivel_confianza', 'medio')}"
        )

    with col_m2:
        cobertura = evaluacion.get("analisis_conceptual", {}).get("cobertura_porcentaje", 0)
        st.metric(label="Cobertura de conceptos", value=f"{cobertura}%")

    with col_m3:
        duracion = resultado.get("duracion_audio")
        if duracion:
            mins = int(duracion // 60)
            secs = int(duracion % 60)
            st.metric(label="Duración", value=f"{mins}:{secs:02d}")
        else:
            palabras = len(resultado.get("transcripcion_limpia", "").split())
            st.metric(label="Palabras", value=palabras)

    with col_m4:
        tema = evaluacion.get("tema_detectado", "General")
        nivel = evaluacion.get("nivel_dificultad", "Intermedio")
        st.metric(label="Tema detectado", value=tema, delta=f"Nivel: {nivel}")

    # --- Reading / AI detection ---
    patron_lectura = resultado.get("patron_lectura")
    if patron_lectura:
        clasificacion = patron_lectura.get("clasificacion", "natural")
        prob_lectura = patron_lectura.get("probabilidad_lectura", 0)
        prob_ia = patron_lectura.get("probabilidad_ia", 0)
        es_ia = patron_lectura.get("es_ia_generada", False)
        esta_leyendo = patron_lectura.get("esta_leyendo", False)
        conteo = patron_lectura.get("conteo_imperfecciones", {})

        if es_ia or prob_ia >= 60:
            st.error(f"""
            **Audio generado por IA detectado** — {prob_ia}% de probabilidad

            El sistema detecta que este audio fue generado por un sintetizador de voz (TTS), no por un estudiante real.

            **Recomendación:** {patron_lectura.get('recomendacion', 'Solicitar que el alumno repita el examen de forma presencial')}
            """)

            with st.expander("Detalles del análisis"):
                st.markdown(f"**Análisis:** {patron_lectura.get('analisis_detallado', 'No disponible')}")

                if conteo:
                    st.markdown("**Conteo de imperfecciones humanas:**")
                    st.markdown(f"- Muletillas: **{conteo.get('muletillas', 0)}**")
                    st.markdown(f"- Autocorrecciones: **{conteo.get('autocorrecciones', 0)}**")
                    st.markdown(f"- Frases incompletas: **{conteo.get('frases_incompletas', 0)}**")
                    st.markdown(f"- Errores gramaticales: **{conteo.get('errores_gramaticales', 0)}**")
                    st.markdown(f"- Pausas detectadas: **{conteo.get('pausas_detectadas', 0)}**")

                evidencias_ia = patron_lectura.get("evidencias_ia", [])
                if evidencias_ia:
                    st.markdown("**Evidencias de IA:**")
                    for ev in evidencias_ia:
                        st.markdown(f"> \"{ev}\"")

                indicadores = patron_lectura.get("indicadores_detectados", [])
                if indicadores:
                    st.markdown("**Indicadores detectados:**")
                    for ind in indicadores:
                        cat = ind.get('categoria', 'ia').upper()
                        gravedad = ind.get('gravedad', 'media').upper()
                        st.markdown(f"- [{cat}] [{gravedad}] **{ind.get('indicador')}**: {ind.get('descripcion')}")

        elif prob_lectura >= 70 or esta_leyendo:
            st.error(f"""
            **Posible lectura detectada** — {prob_lectura}% de probabilidad

            El análisis sugiere que el estudiante podría estar leyendo en lugar de hablar naturalmente.

            **Recomendación:** {patron_lectura.get('recomendacion', 'Revisar manualmente')}
            """)

            with st.expander("Detalles del análisis de lectura"):
                st.markdown(f"**Análisis:** {patron_lectura.get('analisis_detallado', 'No disponible')}")

                indicadores = patron_lectura.get("indicadores_detectados", [])
                if indicadores:
                    st.markdown("**Indicadores detectados:**")
                    for ind in indicadores:
                        gravedad_label = f"[{ind.get('gravedad', 'media').upper()}]"
                        st.markdown(f"- {gravedad_label} **{ind.get('indicador')}**: {ind.get('descripcion')}")

                evidencias = patron_lectura.get("evidencias_lectura", [])
                if evidencias:
                    st.markdown("**Evidencias:**")
                    for ev in evidencias:
                        st.markdown(f"> \"{ev}\"")

        elif prob_lectura >= 40 or prob_ia >= 30:
            st.warning(f"""
            **Advertencia moderada** — Lectura: {prob_lectura}% | IA: {prob_ia}%

            Se detectaron algunos patrones sospechosos, pero no es concluyente.
            """)

            with st.expander("Ver análisis"):
                st.markdown(f"**Análisis:** {patron_lectura.get('analisis_detallado', 'No disponible')}")

        else:
            st.success(f"""
            **Habla natural detectada** — {100 - max(prob_lectura, prob_ia)}% de confianza

            El estudiante parece estar hablando de forma natural y espontánea.
            """)

            evidencias_nat = patron_lectura.get("evidencias_naturalidad", [])
            if evidencias_nat and len(evidencias_nat) > 0:
                with st.expander("Ejemplos de habla natural"):
                    for ev in evidencias_nat[:3]:
                        st.markdown(f"> \"{ev}\"")

    # --- Communication metrics ---
    metricas = evaluacion.get("metricas_comunicacion", {})
    col_met1, col_met2, col_met3 = st.columns(3)

    with col_met1:
        claridad = metricas.get("claridad", "regular")
        st.markdown(f"**Claridad:** {get_quality_indicator(claridad)} {get_quality_label(claridad)}")

    with col_met2:
        coherencia = metricas.get("coherencia", "regular")
        st.markdown(f"**Coherencia:** {get_quality_indicator(coherencia)} {get_quality_label(coherencia)}")

    with col_met3:
        vocabulario = metricas.get("vocabulario_tecnico", "regular")
        st.markdown(f"**Vocabulario técnico:** {get_quality_indicator(vocabulario)} {get_quality_label(vocabulario)}")

    st.divider()

    # --- Tabs ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Feedback alumno",
        "Nota docente",
        "Desglose",
        "Análisis conceptual",
        "Errores",
        "Transcripción"
    ])

    with tab1:
        feedback = evaluacion.get("feedback_alumno", {})

        st.subheader("Resumen del desempeño")
        st.info(feedback.get("resumen", "No disponible"))

        col_f1, col_f2 = st.columns(2)

        with col_f1:
            st.subheader("Fortalezas")
            fortalezas = feedback.get("fortalezas", [])
            if fortalezas:
                for f in fortalezas:
                    st.success(f)
            else:
                st.caption("No se identificaron fortalezas específicas")

        with col_f2:
            st.subheader("Áreas de mejora")
            areas = feedback.get("areas_mejora", [])
            if areas:
                for a in areas:
                    st.warning(a)
            else:
                st.caption("No se identificaron áreas de mejora")

        errores_corregidos = feedback.get("errores_corregidos", [])
        if errores_corregidos:
            st.subheader("Correcciones educativas")
            for i, ec in enumerate(errores_corregidos, 1):
                with st.expander(f"Corrección {i}: {ec.get('error', 'Error')[:50]}..."):
                    st.error(f"**Lo que dijo:** {ec.get('error', 'N/A')}")
                    st.success(f"**Lo correcto:** {ec.get('correccion', 'N/A')}")
                    st.info(f"**Explicación:** {ec.get('explicacion', 'N/A')}")

        recomendaciones = feedback.get("recomendaciones_estudio", [])
        if recomendaciones:
            st.subheader("Recomendaciones de estudio")
            for r in recomendaciones:
                st.markdown(f"- {r}")

        mensaje = feedback.get("mensaje_motivacional", "")
        if mensaje:
            st.subheader("Mensaje final")
            st.success(mensaje)

    with tab2:
        nota_docente = evaluacion.get("nota_docente", {})

        st.subheader("Observaciones generales")
        st.write(nota_docente.get("observaciones", "No disponible"))

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.subheader("Patrón de errores")
            patron = nota_docente.get("patron_errores", "")
            if patron:
                st.warning(patron)
            else:
                st.caption("No se detectó un patrón específico")

        with col_d2:
            st.subheader("Sugerencia de refuerzo")
            refuerzo = nota_docente.get("sugerencia_refuerzo", "")
            if refuerzo:
                st.info(refuerzo)
            else:
                st.caption("Sin sugerencias adicionales")

        st.subheader("Comparación con lo esperado")
        comparacion = nota_docente.get("comparacion_esperado", "")
        if comparacion:
            st.write(comparacion)
        else:
            st.caption("No disponible")

    with tab3:
        desglose = evaluacion.get("desglose_calificacion", {})

        st.subheader("Calificación por criterio")
        criterios = desglose.get("por_criterio", [])
        if criterios:
            for c in criterios:
                puntaje = c.get("puntaje", 0)
                maximo = c.get("maximo", 10)
                porcentaje = (puntaje / maximo * 100) if maximo > 0 else 0

                st.markdown(f"**{c.get('criterio', 'Criterio')}**")
                st.progress(porcentaje / 100)
                st.caption(f"{puntaje}/{maximo} pts — {c.get('justificacion', '')}")
                st.markdown("---")
        else:
            st.caption("No hay desglose por criterio disponible")

        col_pb1, col_pb2 = st.columns(2)

        with col_pb1:
            st.subheader("Penalizaciones")
            penalizaciones = desglose.get("penalizaciones", [])
            if penalizaciones:
                for p in penalizaciones:
                    st.error(f"**-{p.get('puntos_restados', 0)} pts:** {p.get('razon', 'N/A')}")
            else:
                st.success("Sin penalizaciones")

        with col_pb2:
            st.subheader("Bonificaciones")
            bonificaciones = desglose.get("bonificaciones", [])
            if bonificaciones:
                for b in bonificaciones:
                    st.success(f"**+{b.get('puntos_agregados', 0)} pts:** {b.get('razon', 'N/A')}")
            else:
                st.caption("Sin bonificaciones")

        st.subheader("Justificación general")
        st.info(desglose.get("justificacion", "No disponible"))

    with tab4:
        analisis = evaluacion.get("analisis_conceptual", {})
        esperados = analisis.get("conceptos_esperados", {})

        col_a1, col_a2 = st.columns(2)

        with col_a1:
            st.subheader("Conceptos principales esperados")
            principales = esperados.get("principales", [])
            if principales:
                for p in principales:
                    st.markdown(f"- {p}")
            else:
                st.caption("No definidos")

        with col_a2:
            st.subheader("Conceptos secundarios")
            secundarios = esperados.get("secundarios", [])
            if secundarios:
                for s in secundarios:
                    st.markdown(f"- {s}")
            else:
                st.caption("No definidos")

        st.divider()

        col_a3, col_a4 = st.columns(2)

        with col_a3:
            st.subheader("Conceptos mencionados correctamente")
            mencionados = analisis.get("conceptos_mencionados", [])
            if mencionados:
                for m in mencionados:
                    st.success(m)
            else:
                st.warning("No se identificaron conceptos correctos")

        with col_a4:
            st.subheader("Conceptos omitidos")
            omitidos = analisis.get("conceptos_omitidos", [])
            if omitidos:
                for o in omitidos:
                    st.error(o)
            else:
                st.success("No se omitieron conceptos importantes")

        citas = evaluacion.get("citas_destacadas", [])
        if citas:
            st.subheader("Citas destacadas del alumno")
            for cita in citas:
                st.info(f'"{cita}"')

    with tab5:
        errores = evaluacion.get("errores_detectados", {})

        st.subheader("Errores factuales")
        factuales = errores.get("factuales", [])
        if factuales:
            for i, e in enumerate(factuales, 1):
                gravedad = e.get("gravedad", "moderado")
                gravedad_label = f"[{gravedad.upper()}]"

                with st.expander(f"{gravedad_label} Error {i}: {e.get('error', 'Error')[:60]}..."):
                    st.markdown(f"**Descripción:** {e.get('error', 'N/A')}")
                    st.markdown(f"**Gravedad:** {gravedad.upper()}")
                    if e.get("cita_alumno"):
                        st.markdown(f"**El alumno dijo:** \"{e.get('cita_alumno')}\"")
        else:
            st.success("No se detectaron errores factuales")

        st.subheader("Información inventada")
        inventados = errores.get("inventados", [])
        if inventados:
            for inv in inventados:
                st.error(inv)
        else:
            st.success("No se detectó información inventada")

    with tab6:
        st.subheader("Transcripción original (Whisper)")
        st.text_area(
            "Transcripción cruda",
            value=resultado.get("transcripcion_original", ""),
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )

        st.subheader("Transcripción procesada")
        st.text_area(
            "Transcripción limpia",
            value=resultado.get("transcripcion_limpia", ""),
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )

        with st.expander("Exportar evaluación completa (JSON)"):
            st.json(evaluacion)
            st.download_button(
                label="Descargar JSON",
                data=json.dumps(evaluacion, ensure_ascii=False, indent=2),
                file_name="evaluacion_examen.json",
                mime="application/json"
            )

    st.divider()

    if st.button("Nueva evaluación", type="secondary", use_container_width=True):
        st.session_state.evaluacion_resultado = None
        st.session_state.audio_bytes = None
        st.session_state.audio_source = None
        st.rerun()

# =============================================================================
# FOOTER
# =============================================================================

st.divider()
st.markdown("""
<div class="footer">
    <p>Whisper (Groq) &middot; Mistral Large &middot; Gemini 2.0 Flash</p>
</div>
""", unsafe_allow_html=True)
