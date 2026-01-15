import streamlit as st
import os
import tempfile
from engine import EvaluadorEngine

st.set_page_config(
    page_title="Evaluador Universal de Exámenes Orales",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Evaluador Universal de Exámenes Orales")
st.markdown("**Powered by Groq Cloud** | Whisper + Llama 3.1 70B")

if "evaluacion_resultado" not in st.session_state:
    st.session_state.evaluacion_resultado = None

with st.sidebar:
    st.header("⚙️ Configuración")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY no configurada")
        st.info("Configura tu API Key en el archivo .env")
        api_key_input = st.text_input("O ingresa tu API Key aquí:", type="password")
        if api_key_input:
            os.environ["GROQ_API_KEY"] = api_key_input
            api_key = api_key_input
    else:
        st.success("✅ API Key configurada")
    
    st.divider()
    
    limpiar_transcripcion = st.checkbox(
        "Limpiar transcripción (eliminar muletillas)", 
        value=True,
        help="Usa IA para eliminar 'eh', 'mmm', repeticiones antes de evaluar"
    )
    
    st.divider()
    
    st.markdown("### 📚 Ejemplos de Uso")
    st.markdown("""
    - **Biología**: Fotosíntesis, Ciclo de Krebs
    - **Matemáticas**: Teorema de Pitágoras
    - **Historia**: Revolución Francesa
    - **Física**: Leyes de Newton
    """)

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📖 Material de Referencia")
    st.markdown("Pega aquí el contenido que el alumno debe dominar (apuntes, libro, PDF copiado)")
    
    material_referencia = st.text_area(
        "Material de Referencia",
        height=300,
        placeholder="""Ejemplo para Biología:
        
La fotosíntesis es el proceso mediante el cual las plantas convierten la luz solar en energía química. 
Ocurre en los cloroplastos y tiene dos fases:

1. Fase luminosa (en tilacoides): Captura energía solar y produce ATP y NADPH
2. Fase oscura o Ciclo de Calvin (en estroma): Usa ATP y NADPH para fijar CO2 y producir glucosa

Ecuación general: 6CO2 + 6H2O + luz → C6H12O6 + 6O2
        """,
        label_visibility="collapsed"
    )

with col2:
    st.header("📋 Rúbrica de Evaluación")
    st.markdown("Define los criterios de evaluación")
    
    rubrica = st.text_area(
        "Rúbrica",
        height=300,
        placeholder="""Ejemplo de Rúbrica:

- Menciona las dos fases de la fotosíntesis (3 puntos)
- Explica dónde ocurre cada fase (2 puntos)
- Menciona los productos de cada fase (3 puntos)
- Recita correctamente la ecuación química (2 puntos)

Total: 10 puntos
        """,
        label_visibility="collapsed"
    )

st.divider()

st.header("🎤 Audio del Examen Oral")

col_audio1, col_audio2 = st.columns([2, 1])

with col_audio1:
    audio_file = st.file_uploader(
        "Sube el archivo de audio del examen",
        type=["mp3", "wav", "m4a", "ogg", "flac"],
        help="Formatos soportados: MP3, WAV, M4A, OGG, FLAC (máx. 25MB)"
    )

with col_audio2:
    st.info("💡 **Tip**: Graba el examen con tu celular y súbelo aquí")

if audio_file is not None:
    st.audio(audio_file, format=f"audio/{audio_file.type.split('/')[-1]}")
    
    file_size_mb = len(audio_file.getvalue()) / (1024 * 1024)
    st.caption(f"📊 Tamaño del archivo: {file_size_mb:.2f} MB")
    
    if file_size_mb > 25:
        st.warning("⚠️ El archivo supera los 25MB. Considera comprimirlo o cortarlo.")

st.divider()

if st.button("🚀 Evaluar Examen", type="primary", use_container_width=True):
    if not material_referencia or not rubrica:
        st.error("❌ Debes completar el Material de Referencia y la Rúbrica")
    elif not audio_file:
        st.error("❌ Debes subir un archivo de audio")
    elif not api_key:
        st.error("❌ Debes configurar tu GROQ_API_KEY")
    else:
        with st.spinner("🔄 Procesando examen..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(audio_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                evaluador = EvaluadorEngine()
                
                with st.status("Procesando...", expanded=True) as status:
                    st.write("🎧 Transcribiendo audio con Whisper...")
                    resultado = evaluador.proceso_completo(
                        tmp_file_path,
                        material_referencia,
                        rubrica,
                        limpiar=limpiar_transcripcion
                    )
                    
                    if resultado["success"]:
                        st.write("✅ Transcripción completada")
                        st.write("🤖 Evaluando con Llama 3.1 70B...")
                        st.write("✅ Evaluación completada")
                        status.update(label="✅ Proceso completado", state="complete")
                    else:
                        status.update(label="❌ Error en el proceso", state="error")
                
                os.unlink(tmp_file_path)
                
                if resultado["success"]:
                    st.session_state.evaluacion_resultado = resultado
                    st.success("✅ Evaluación completada exitosamente")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {resultado.get('error', 'Error desconocido')}")
                    if "raw_response" in resultado:
                        with st.expander("Ver respuesta raw"):
                            st.code(resultado["raw_response"])
            
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")

if st.session_state.evaluacion_resultado:
    resultado = st.session_state.evaluacion_resultado
    evaluacion = resultado["evaluacion"]
    
    st.divider()
    st.header("📊 Resultados de la Evaluación")
    
    col_nota1, col_nota2, col_nota3 = st.columns(3)
    
    with col_nota1:
        st.metric(
            label="Calificación Final",
            value=f"{evaluacion['calificacion_final']}/10"
        )
    
    with col_nota2:
        duracion = resultado.get("duracion_audio")
        if duracion:
            st.metric(
                label="Duración del Audio",
                value=f"{duracion:.1f}s"
            )
    
    with col_nota3:
        palabras = len(resultado["transcripcion_limpia"].split())
        st.metric(
            label="Palabras Transcritas",
            value=palabras
        )
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Feedback", "📋 Análisis", "🎯 Errores", "📄 Transcripción"])
    
    with tab1:
        st.subheader("Feedback para el Alumno")
        st.info(evaluacion["feedback_para_alumno"])
        
        st.subheader("Nota para el Docente")
        st.warning(evaluacion["sugerencia_docente"])
    
    with tab2:
        st.subheader("Análisis de Conceptos")
        st.write(evaluacion["analisis_conceptos"])
    
    with tab3:
        st.subheader("Errores Específicos Detectados")
        if evaluacion["errores_especificos"]:
            for i, error in enumerate(evaluacion["errores_especificos"], 1):
                st.error(f"**{i}.** {error}")
        else:
            st.success("✅ No se detectaron errores específicos")
    
    with tab4:
        st.subheader("Transcripción Original")
        st.text_area(
            "Transcripción cruda de Whisper",
            value=resultado["transcripcion_original"],
            height=200,
            disabled=True
        )
        
        if limpiar_transcripcion:
            st.subheader("Transcripción Limpia")
            st.text_area(
                "Transcripción procesada (sin muletillas)",
                value=resultado["transcripcion_limpia"],
                height=200,
                disabled=True
            )
    
    if st.button("🔄 Nueva Evaluación"):
        st.session_state.evaluacion_resultado = None
        st.rerun()

st.divider()
st.caption("Desarrollado con ❤️ usando Streamlit + Groq Cloud | Whisper + Llama 3.1 70B")
