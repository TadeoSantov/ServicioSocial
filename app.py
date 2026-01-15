import streamlit as st
import os
import tempfile
import json
from engine import EvaluadorEngine

st.set_page_config(
    page_title="Evaluador Universal de Exámenes Orales",
    page_icon="🎓",
    layout="wide"
)

def get_color_for_metric(value: str) -> str:
    colors = {
        "excelente": "🟢",
        "buena": "🟡",
        "bueno": "🟡", 
        "regular": "🟠",
        "deficiente": "🔴"
    }
    return colors.get(value.lower(), "⚪")

def get_grade_color(grade: float) -> str:
    if grade >= 9:
        return "🏆"
    elif grade >= 7:
        return "✅"
    elif grade >= 6:
        return "⚠️"
    else:
        return "❌"

st.title("🎓 Evaluador Universal de Exámenes Orales")
st.markdown("**Powered by Groq + Google AI** | Whisper + Llama/Gemini | Evaluación Multi-Paso")

if "evaluacion_resultado" not in st.session_state:
    st.session_state.evaluacion_resultado = None

with st.sidebar:
    st.header("⚙️ Configuración")
    
    st.subheader("🤖 Modelo de Evaluación")
    proveedor_llm = st.selectbox(
        "Proveedor LLM",
        options=["groq", "google"],
        format_func=lambda x: {
            "groq": "🚀 Groq (Llama 3.3 70B)",
            "google": "🔷 Google AI (Gemini 1.5 Flash)"
        }.get(x, x),
        index=0,
        help="Selecciona el modelo para evaluar. Groq siempre se usa para transcripción."
    )
    
    st.divider()
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("⚠️ GROQ_API_KEY requerida")
        st.caption("Necesaria para transcripción con Whisper")
        groq_key_input = st.text_input("Groq API Key:", type="password", key="groq_key")
        if groq_key_input:
            os.environ["GROQ_API_KEY"] = groq_key_input
            groq_api_key = groq_key_input
    else:
        st.success("✅ Groq API Key configurada")
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if proveedor_llm == "google":
        if not google_api_key:
            st.warning("⚠️ GOOGLE_API_KEY requerida para Gemini")
            google_key_input = st.text_input("Google API Key:", type="password", key="google_key")
            if google_key_input:
                os.environ["GOOGLE_API_KEY"] = google_key_input
                google_api_key = google_key_input
        else:
            st.success("✅ Google API Key configurada")
    
    st.divider()
    
    st.subheader("🔧 Opciones de Procesamiento")
    
    limpiar_transcripcion = st.checkbox(
        "Limpiar transcripción", 
        value=True,
        help="Elimina muletillas como 'eh', 'mmm', 'este' antes de evaluar"
    )
    
    idioma_audio = st.selectbox(
        "Idioma del audio",
        options=["es", "en", "fr", "de", "pt", "it"],
        format_func=lambda x: {
            "es": "🇪🇸 Español",
            "en": "🇺🇸 English", 
            "fr": "🇫🇷 Français",
            "de": "🇩🇪 Deutsch",
            "pt": "🇧🇷 Português",
            "it": "🇮🇹 Italiano"
        }.get(x, x),
        index=0
    )
    
    st.divider()
    
    st.markdown("### 📚 Materias Soportadas")
    st.markdown("""
    - 🧬 **Biología**: Procesos celulares, anatomía
    - 🔢 **Matemáticas**: Teoremas, fórmulas
    - 📜 **Historia**: Eventos, fechas, personajes
    - ⚗️ **Química**: Reacciones, elementos
    - 🔭 **Física**: Leyes, experimentos
    - 📖 **Literatura**: Análisis, autores
    """)

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📖 Material de Referencia")
    st.caption("Pega el contenido que el alumno debe dominar")
    
    material_referencia = st.text_area(
        "Material de Referencia",
        height=280,
        placeholder="""Ejemplo - Fotosíntesis:

La fotosíntesis es el proceso mediante el cual las plantas convierten la luz solar en energía química. Ocurre en los cloroplastos y tiene dos fases:

1. Fase luminosa (en tilacoides): 
   - Captura energía solar
   - Produce ATP y NADPH
   - Libera O2

2. Fase oscura - Ciclo de Calvin (en estroma):
   - Usa ATP y NADPH
   - Fija CO2
   - Produce glucosa

Ecuación: 6CO2 + 6H2O + luz → C6H12O6 + 6O2""",
        label_visibility="collapsed"
    )

with col2:
    st.header("📋 Rúbrica de Evaluación")
    st.caption("Define los criterios y puntos para calificar")
    
    rubrica = st.text_area(
        "Rúbrica",
        height=280,
        placeholder="""Ejemplo de Rúbrica (10 puntos):

1. Definición de fotosíntesis (2 pts)
   - Menciona conversión de luz a energía química

2. Fase luminosa (3 pts)
   - Ubicación: tilacoides (1 pt)
   - Productos: ATP, NADPH, O2 (2 pts)

3. Fase oscura/Calvin (3 pts)
   - Ubicación: estroma (1 pt)
   - Proceso: fijación de CO2 (1 pt)
   - Producto: glucosa (1 pt)

4. Ecuación química (2 pts)
   - Reactivos correctos (1 pt)
   - Productos correctos (1 pt)""",
        label_visibility="collapsed"
    )

st.divider()

st.header("🎤 Audio del Examen Oral")

col_audio1, col_audio2 = st.columns([2, 1])

with col_audio1:
    audio_file = st.file_uploader(
        "Sube el archivo de audio del examen",
        type=["mp3", "wav", "m4a", "ogg", "flac", "webm"],
        help="Formatos: MP3, WAV, M4A, OGG, FLAC, WEBM (máx. 25MB)"
    )

with col_audio2:
    st.info("💡 **Tip**: Graba con tu celular o usa la grabadora del navegador")

if audio_file is not None:
    st.audio(audio_file)
    file_size_mb = len(audio_file.getvalue()) / (1024 * 1024)
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.caption(f"� Archivo: {audio_file.name}")
    with col_info2:
        if file_size_mb > 25:
            st.warning(f"⚠️ {file_size_mb:.1f} MB - Excede límite de 25MB")
        else:
            st.caption(f"📊 Tamaño: {file_size_mb:.2f} MB")

st.divider()

if st.button("🚀 Evaluar Examen", type="primary", use_container_width=True):
    if not material_referencia.strip():
        st.error("❌ Ingresa el Material de Referencia")
    elif not rubrica.strip():
        st.error("❌ Ingresa la Rúbrica de Evaluación")
    elif not audio_file:
        st.error("❌ Sube un archivo de audio")
    elif not groq_api_key:
        st.error("❌ Configura tu GROQ_API_KEY (requerida para transcripción)")
    elif proveedor_llm == "google" and not google_api_key:
        st.error("❌ Configura tu GOOGLE_API_KEY para usar Gemini")
    else:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(audio_file.getvalue())
                tmp_file_path = tmp_file.name
            
            evaluador = EvaluadorEngine(
                api_key=groq_api_key,
                proveedor=proveedor_llm,
                google_api_key=google_api_key if proveedor_llm == "google" else None
            )
            
            with st.status("🔄 Evaluando examen...", expanded=True) as status:
                st.write("🎧 **Paso 1/4**: Transcribiendo audio con Whisper...")
                
                resultado = evaluador.proceso_completo(
                    tmp_file_path,
                    material_referencia,
                    rubrica,
                    limpiar=limpiar_transcripcion,
                    idioma=idioma_audio
                )
                
                if resultado["success"]:
                    st.write("✅ Transcripción completada")
                    st.write("🔍 **Paso 2/4**: Extrayendo conceptos clave...")
                    st.write("✅ Conceptos extraídos")
                    st.write("📊 **Paso 3/4**: Analizando respuesta del alumno...")
                    st.write("✅ Análisis completado")
                    st.write("🎯 **Paso 4/4**: Calculando calificación y generando feedback...")
                    st.write("✅ Evaluación finalizada")
                    status.update(label="✅ Evaluación completada", state="complete")
                else:
                    status.update(label="❌ Error en el proceso", state="error")
            
            os.unlink(tmp_file_path)
            
            if resultado["success"]:
                st.session_state.evaluacion_resultado = resultado
                st.rerun()
            else:
                st.error(f"❌ Error: {resultado.get('error', 'Error desconocido')}")
        
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")

if st.session_state.evaluacion_resultado:
    resultado = st.session_state.evaluacion_resultado
    evaluacion = resultado["evaluacion"]
    
    st.divider()
    
    calificacion = float(evaluacion.get("calificacion_final", 0))
    grade_icon = get_grade_color(calificacion)
    
    st.header(f"📊 Resultados de la Evaluación {grade_icon}")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        st.metric(
            label="🎯 Calificación Final",
            value=f"{calificacion}/10",
            delta=f"Confianza: {evaluacion.get('nivel_confianza', 'medio')}"
        )
    
    with col_m2:
        cobertura = evaluacion.get("analisis_conceptual", {}).get("cobertura_porcentaje", 0)
        st.metric(
            label="📚 Cobertura de Conceptos",
            value=f"{cobertura}%"
        )
    
    with col_m3:
        duracion = resultado.get("duracion_audio")
        if duracion:
            mins = int(duracion // 60)
            secs = int(duracion % 60)
            st.metric(
                label="⏱️ Duración",
                value=f"{mins}:{secs:02d}"
            )
        else:
            palabras = len(resultado.get("transcripcion_limpia", "").split())
            st.metric(label="📝 Palabras", value=palabras)
    
    with col_m4:
        tema = evaluacion.get("tema_detectado", "General")
        nivel = evaluacion.get("nivel_dificultad", "Intermedio")
        st.metric(
            label="📖 Tema Detectado",
            value=tema,
            delta=f"Nivel: {nivel}"
        )
    
    metricas = evaluacion.get("metricas_comunicacion", {})
    col_met1, col_met2, col_met3 = st.columns(3)
    
    with col_met1:
        claridad = metricas.get("claridad", "regular")
        st.markdown(f"**Claridad**: {get_color_for_metric(claridad)} {claridad.capitalize()}")
    
    with col_met2:
        coherencia = metricas.get("coherencia", "regular")
        st.markdown(f"**Coherencia**: {get_color_for_metric(coherencia)} {coherencia.capitalize()}")
    
    with col_met3:
        vocabulario = metricas.get("vocabulario_tecnico", "regular")
        st.markdown(f"**Vocabulario Técnico**: {get_color_for_metric(vocabulario)} {vocabulario.capitalize()}")
    
    st.divider()
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Feedback Alumno", 
        "�‍🏫 Nota Docente",
        "📊 Desglose",
        "🔍 Análisis Conceptual",
        "⚠️ Errores",
        "📄 Transcripción"
    ])
    
    with tab1:
        feedback = evaluacion.get("feedback_alumno", {})
        
        st.subheader("📋 Resumen del Desempeño")
        st.info(feedback.get("resumen", "No disponible"))
        
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            st.subheader("💪 Fortalezas")
            fortalezas = feedback.get("fortalezas", [])
            if fortalezas:
                for f in fortalezas:
                    st.success(f"✅ {f}")
            else:
                st.caption("No se identificaron fortalezas específicas")
        
        with col_f2:
            st.subheader("📈 Áreas de Mejora")
            areas = feedback.get("areas_mejora", [])
            if areas:
                for a in areas:
                    st.warning(f"📌 {a}")
            else:
                st.caption("No se identificaron áreas de mejora")
        
        errores_corregidos = feedback.get("errores_corregidos", [])
        if errores_corregidos:
            st.subheader("📚 Correcciones Educativas")
            for i, ec in enumerate(errores_corregidos, 1):
                with st.expander(f"Corrección {i}: {ec.get('error', 'Error')[:50]}..."):
                    st.error(f"**Lo que dijiste:** {ec.get('error', 'N/A')}")
                    st.success(f"**Lo correcto:** {ec.get('correccion', 'N/A')}")
                    st.info(f"**Explicación:** {ec.get('explicacion', 'N/A')}")
        
        recomendaciones = feedback.get("recomendaciones_estudio", [])
        if recomendaciones:
            st.subheader("📖 Recomendaciones de Estudio")
            for r in recomendaciones:
                st.markdown(f"• {r}")
        
        mensaje = feedback.get("mensaje_motivacional", "")
        if mensaje:
            st.subheader("💬 Mensaje Final")
            st.success(mensaje)
    
    with tab2:
        nota_docente = evaluacion.get("nota_docente", {})
        
        st.subheader("📋 Observaciones Generales")
        st.write(nota_docente.get("observaciones", "No disponible"))
        
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.subheader("🔄 Patrón de Errores")
            patron = nota_docente.get("patron_errores", "")
            if patron:
                st.warning(patron)
            else:
                st.caption("No se detectó un patrón específico")
        
        with col_d2:
            st.subheader("📚 Sugerencia de Refuerzo")
            refuerzo = nota_docente.get("sugerencia_refuerzo", "")
            if refuerzo:
                st.info(refuerzo)
            else:
                st.caption("Sin sugerencias adicionales")
        
        st.subheader("📊 Comparación con lo Esperado")
        comparacion = nota_docente.get("comparacion_esperado", "")
        if comparacion:
            st.write(comparacion)
        else:
            st.caption("No disponible")
    
    with tab3:
        desglose = evaluacion.get("desglose_calificacion", {})
        
        st.subheader("📊 Calificación por Criterio")
        criterios = desglose.get("por_criterio", [])
        if criterios:
            for c in criterios:
                puntaje = c.get("puntaje", 0)
                maximo = c.get("maximo", 10)
                porcentaje = (puntaje / maximo * 100) if maximo > 0 else 0
                
                st.markdown(f"**{c.get('criterio', 'Criterio')}**")
                st.progress(porcentaje / 100)
                st.caption(f"{puntaje}/{maximo} pts - {c.get('justificacion', '')}")
                st.markdown("---")
        else:
            st.caption("No hay desglose por criterio disponible")
        
        col_pb1, col_pb2 = st.columns(2)
        
        with col_pb1:
            st.subheader("➖ Penalizaciones")
            penalizaciones = desglose.get("penalizaciones", [])
            if penalizaciones:
                for p in penalizaciones:
                    st.error(f"**-{p.get('puntos_restados', 0)} pts**: {p.get('razon', 'N/A')}")
            else:
                st.success("✅ Sin penalizaciones")
        
        with col_pb2:
            st.subheader("➕ Bonificaciones")
            bonificaciones = desglose.get("bonificaciones", [])
            if bonificaciones:
                for b in bonificaciones:
                    st.success(f"**+{b.get('puntos_agregados', 0)} pts**: {b.get('razon', 'N/A')}")
            else:
                st.caption("Sin bonificaciones")
        
        st.subheader("📝 Justificación General")
        st.info(desglose.get("justificacion", "No disponible"))
    
    with tab4:
        analisis = evaluacion.get("analisis_conceptual", {})
        
        esperados = analisis.get("conceptos_esperados", {})
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.subheader("📌 Conceptos Principales Esperados")
            principales = esperados.get("principales", [])
            if principales:
                for p in principales:
                    st.markdown(f"• {p}")
            else:
                st.caption("No definidos")
        
        with col_a2:
            st.subheader("📎 Conceptos Secundarios")
            secundarios = esperados.get("secundarios", [])
            if secundarios:
                for s in secundarios:
                    st.markdown(f"• {s}")
            else:
                st.caption("No definidos")
        
        st.divider()
        
        col_a3, col_a4 = st.columns(2)
        
        with col_a3:
            st.subheader("✅ Conceptos Mencionados Correctamente")
            mencionados = analisis.get("conceptos_mencionados", [])
            if mencionados:
                for m in mencionados:
                    st.success(f"✓ {m}")
            else:
                st.warning("No se identificaron conceptos correctos")
        
        with col_a4:
            st.subheader("❌ Conceptos Omitidos")
            omitidos = analisis.get("conceptos_omitidos", [])
            if omitidos:
                for o in omitidos:
                    st.error(f"✗ {o}")
            else:
                st.success("✅ No se omitieron conceptos importantes")
        
        citas = evaluacion.get("citas_destacadas", [])
        if citas:
            st.subheader("💬 Citas Destacadas del Alumno")
            for cita in citas:
                st.info(f'"{cita}"')
    
    with tab5:
        errores = evaluacion.get("errores_detectados", {})
        
        st.subheader("⚠️ Errores Factuales")
        factuales = errores.get("factuales", [])
        if factuales:
            for i, e in enumerate(factuales, 1):
                gravedad = e.get("gravedad", "moderado")
                icon = "🔴" if gravedad == "grave" else "🟠" if gravedad == "moderado" else "🟡"
                
                with st.expander(f"{icon} Error {i}: {e.get('error', 'Error')[:60]}..."):
                    st.markdown(f"**Descripción:** {e.get('error', 'N/A')}")
                    st.markdown(f"**Gravedad:** {gravedad.upper()}")
                    if e.get("cita_alumno"):
                        st.markdown(f"**El alumno dijo:** \"{e.get('cita_alumno')}\"")
        else:
            st.success("✅ No se detectaron errores factuales")
        
        st.subheader("🚫 Información Inventada")
        inventados = errores.get("inventados", [])
        if inventados:
            for inv in inventados:
                st.error(f"❌ {inv}")
        else:
            st.success("✅ No se detectó información inventada")
    
    with tab6:
        st.subheader("🎤 Transcripción Original (Whisper)")
        st.text_area(
            "Transcripción cruda",
            value=resultado.get("transcripcion_original", ""),
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )
        
        st.subheader("✨ Transcripción Limpia (Procesada)")
        st.text_area(
            "Transcripción limpia",
            value=resultado.get("transcripcion_limpia", ""),
            height=200,
            disabled=True,
            label_visibility="collapsed"
        )
        
        with st.expander("📥 Exportar Evaluación Completa (JSON)"):
            st.json(evaluacion)
            st.download_button(
                label="⬇️ Descargar JSON",
                data=json.dumps(evaluacion, ensure_ascii=False, indent=2),
                file_name="evaluacion_examen.json",
                mime="application/json"
            )
    
    st.divider()
    
    if st.button("🔄 Nueva Evaluación", type="secondary", use_container_width=True):
        st.session_state.evaluacion_resultado = None
        st.rerun()

st.divider()
st.caption("Desarrollado con ❤️ usando Streamlit + Groq Cloud | Whisper + Llama 3.3 70B | Sistema de Evaluación Multi-Paso")
