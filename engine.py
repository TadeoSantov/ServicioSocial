import os
import json
import re
import logging
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types as genai_types
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

try:
    from openai import AzureOpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False

load_dotenv()

logger = logging.getLogger(__name__)


class EvaluadorEngine:

    WHISPER_GROQ = "groq"
    WHISPER_AZURE = "azure"

    LLM_MISTRAL = "mistral"
    LLM_GEMINI = "gemini"
    LLM_AZURE = "azure_openai"

    def __init__(
        self,
        proveedor_llm: str = "mistral",
        proveedor_whisper: str = "groq",
        groq_api_key: Optional[str] = None,
        mistral_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
        azure_openai_api_key: Optional[str] = None,
        azure_openai_endpoint: Optional[str] = None,
        azure_openai_deployment: Optional[str] = None,
        azure_whisper_deployment: Optional[str] = None,
        azure_api_version: Optional[str] = None,
    ):
        self.proveedor_llm = proveedor_llm.lower()
        self.proveedor_whisper = proveedor_whisper.lower()

        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if self.proveedor_whisper == self.WHISPER_GROQ:
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY requerida para transcripcion con Whisper")
            self.groq_client = Groq(api_key=self.groq_api_key)
        self.whisper_model = "whisper-large-v3"

        self._init_llm(
            mistral_api_key, google_api_key,
            azure_openai_api_key, azure_openai_endpoint,
            azure_openai_deployment, azure_api_version,
        )
        self._init_whisper_azure(
            azure_openai_api_key, azure_openai_endpoint,
            azure_whisper_deployment, azure_api_version,
        )

    def _init_llm(
        self,
        mistral_api_key: Optional[str],
        google_api_key: Optional[str],
        azure_openai_api_key: Optional[str],
        azure_openai_endpoint: Optional[str],
        azure_openai_deployment: Optional[str],
        azure_api_version: Optional[str],
    ) -> None:
        if self.proveedor_llm == self.LLM_MISTRAL:
            if not MISTRAL_AVAILABLE:
                raise ImportError("mistralai no instalado. Ejecuta: pip install mistralai")
            self.mistral_api_key = mistral_api_key or os.getenv("MISTRAL_API_KEY")
            if not self.mistral_api_key:
                raise ValueError("MISTRAL_API_KEY no encontrada")
            self.mistral_client = Mistral(api_key=self.mistral_api_key)
            self.llm_model = "mistral-large-latest"

        elif self.proveedor_llm == self.LLM_GEMINI:
            if not GOOGLE_AI_AVAILABLE:
                raise ImportError("google-genai no instalado. Ejecuta: pip install google-genai")
            self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY no encontrada")
            self.google_client = genai.Client(api_key=self.google_api_key)
            self.llm_model = "gemini-2.0-flash"

        elif self.proveedor_llm == self.LLM_AZURE:
            if not AZURE_OPENAI_AVAILABLE:
                raise ImportError("openai no instalado. Ejecuta: pip install openai")
            self.azure_openai_api_key = azure_openai_api_key or os.getenv("AZURE_OPENAI_API_KEY")
            self.azure_openai_endpoint = azure_openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
            self.azure_openai_deployment = azure_openai_deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
            self.azure_api_version = azure_api_version or os.getenv("AZURE_API_VERSION", "2024-12-01-preview")
            if not self.azure_openai_api_key or not self.azure_openai_endpoint:
                raise ValueError("AZURE_OPENAI_API_KEY y AZURE_OPENAI_ENDPOINT requeridos")
            self.azure_client = AzureOpenAI(
                api_key=self.azure_openai_api_key,
                api_version=self.azure_api_version,
                azure_endpoint=self.azure_openai_endpoint,
            )
            self.llm_model = self.azure_openai_deployment

    def _init_whisper_azure(
        self,
        azure_openai_api_key: Optional[str],
        azure_openai_endpoint: Optional[str],
        azure_whisper_deployment: Optional[str],
        azure_api_version: Optional[str],
    ) -> None:
        if self.proveedor_whisper != self.WHISPER_AZURE:
            return
        if not AZURE_OPENAI_AVAILABLE:
            raise ImportError("openai no instalado. Ejecuta: pip install openai")
        self.azure_openai_api_key = azure_openai_api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = azure_openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_whisper_deployment = azure_whisper_deployment or os.getenv("AZURE_WHISPER_DEPLOYMENT", "whisper")
        self.azure_api_version = azure_api_version or os.getenv("AZURE_API_VERSION", "2024-12-01-preview")
        if not self.azure_openai_api_key or not self.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY y AZURE_OPENAI_ENDPOINT requeridos para Azure Whisper")
        if not hasattr(self, "azure_client"):
            self.azure_client = AzureOpenAI(
                api_key=self.azure_openai_api_key,
                api_version=self.azure_api_version,
                azure_endpoint=self.azure_openai_endpoint,
            )

    # -------------------------------------------------------------------------
    # LLM dispatch
    # -------------------------------------------------------------------------

    def _llamar_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> str:
        if self.proveedor_llm == self.LLM_MISTRAL:
            response = self.mistral_client.chat.complete(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()

        if self.proveedor_llm == self.LLM_GEMINI:
            prompt_completo = f"{system_prompt}\n\n---\n\nUSUARIO: {user_prompt}"
            config = genai_types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            response = self.google_client.models.generate_content(
                model=self.llm_model,
                contents=prompt_completo,
                config=config,
            )
            return response.text.strip()

        if self.proveedor_llm == self.LLM_AZURE:
            response = self.azure_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()

        raise ValueError(f"Proveedor LLM no soportado: {self.proveedor_llm}")

    def _parse_llm_json(self, raw: str) -> Dict[str, Any]:
        cleaned = self._sanitize_json(raw)
        return json.loads(cleaned)

    def _sanitize_json(self, texto: str) -> str:
        if not texto:
            return "{}"
        texto = texto.strip()
        if texto.startswith("```json"):
            texto = texto[7:]
        elif texto.startswith("```"):
            texto = texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]
        texto = texto.strip()
        start = texto.find("{")
        end = texto.rfind("}")
        if start != -1 and end != -1 and end > start:
            texto = texto[start : end + 1]
        return texto.strip()

    # -------------------------------------------------------------------------
    # Transcripcion
    # -------------------------------------------------------------------------

    def transcribir_audio(self, audio_path: str, idioma: str = "es") -> Dict[str, Any]:
        if self.proveedor_whisper == self.WHISPER_AZURE:
            return self._transcribir_azure(audio_path, idioma)
        return self._transcribir_groq(audio_path, idioma)

    def _build_whisper_prompt(self, idioma: str) -> str:
        nombre_idioma = "espanol" if idioma == "es" else idioma
        return f"Transcripcion precisa en {nombre_idioma}. Incluir puntuacion correcta."

    def _transcribir_groq(self, audio_path: str, idioma: str) -> Dict[str, Any]:
        try:
            with open(audio_path, "rb") as f:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), f.read()),
                    model=self.whisper_model,
                    response_format="verbose_json",
                    language=idioma,
                    temperature=0.0,
                    prompt=self._build_whisper_prompt(idioma),
                )
            return {
                "success": True,
                "transcripcion": transcription.text,
                "duracion": getattr(transcription, "duration", None),
                "idioma": idioma,
                "proveedor": "groq",
            }
        except Exception as e:
            logger.error("Transcripcion Groq fallida: %s", e)
            return {"success": False, "error": f"Error en transcripcion Groq: {e}"}

    def _transcribir_azure(self, audio_path: str, idioma: str) -> Dict[str, Any]:
        try:
            with open(audio_path, "rb") as f:
                transcription = self.azure_client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), f.read()),
                    model=self.azure_whisper_deployment,
                    response_format="verbose_json",
                    language=idioma,
                    temperature=0.0,
                    prompt=self._build_whisper_prompt(idioma),
                )
            return {
                "success": True,
                "transcripcion": transcription.text,
                "duracion": getattr(transcription, "duration", None),
                "idioma": idioma,
                "proveedor": "azure",
            }
        except Exception as e:
            logger.error("Transcripcion Azure fallida: %s", e)
            return {"success": False, "error": f"Error en transcripcion Azure: {e}"}

    # -------------------------------------------------------------------------
    # Deteccion de lectura
    # -------------------------------------------------------------------------

    _PROMPT_DETECCION_LECTURA = """Eres un experto forense en analisis de patrones de habla. Tu trabajo es detectar si una transcripcion proviene de:
A) Habla natural y espontanea de un estudiante real
B) Lectura en voz alta de un texto preparado
C) Audio generado por inteligencia artificial (TTS/text-to-speech)

IMPORTANTE: Debes ser MUY ESTRICTO. Si hay duda, clasifica como sospechoso.

=== INDICADORES DE AUDIO GENERADO POR IA (TTS) ===
Estos son los mas criticos. Un TTS moderno produce transcripciones con estas caracteristicas:
1. Perfeccion gramatical absoluta: Cero errores, cero autocorrecciones, cero frases incompletas
2. Fluidez artificial: Oraciones completas y bien formadas de principio a fin, sin interrupciones
3. Ausencia total de imperfecciones: No hay "eh", "mmm", "este", "uh", pausas, ni titubeos
4. Vocabulario uniformemente articulado: Cada palabra se pronuncia con claridad perfecta (Whisper transcribe sin errores)
5. Estructura de texto escrito: La transcripcion parece un ensayo o articulo, no una conversacion oral
6. Longitud de oraciones consistente: Las frases tienen longitud similar, sin variacion natural
7. Sin respiraciones ni ruido: Whisper no detecta pausas por respiracion ni ruido ambiental
8. Tono expositivo neutro: Suena como un narrador, no como alguien explicando algo que sabe
9. Conectores de texto escrito: "Ademas", "Por otra parte", "En conclusion", "Cabe destacar"
10. Sin marcas de interaccion: No hay "bueno", "mira", "a ver", "digamos" ni frases dirigidas a alguien

=== INDICADORES DE LECTURA EN VOZ ALTA ===
1. Fluidez excesiva pero con algunas pausas por respiracion
2. Vocabulario formal constante sin explicaciones propias
3. Pocas muletillas pero puede haber alguna al perder el lugar
4. Estructura perfecta de parrafos
5. Conectores formales: "asimismo", "por consiguiente", "en consecuencia"
6. Enumeraciones perfectas sin perder el hilo
7. Puede haber tropiezos al leer palabras dificiles

=== INDICADORES DE HABLA NATURAL (estudiante real) ===
1. Muletillas frecuentes: "eh", "mmm", "este", "o sea", "bueno", "pues", "como que"
2. Autocorrecciones: "o sea", "mejor dicho", "es decir", "me refiero a", "bueno no, mas bien"
3. Frases incompletas que se reformulan a medio camino
4. Repeticiones involuntarias de palabras
5. Pausas irregulares y cambios de ritmo
6. Errores gramaticales menores no corregidos
7. Explicaciones con palabras simples y propias: "es como cuando...", "por ejemplo yo..."
8. Conectores informales: "entonces", "y bueno", "pues", "y ya"
9. Ejemplos personales o analogias improvisadas
10. Variacion en la complejidad de las oraciones (mezcla de cortas y largas)

=== REGLA DE DECISION ===
- Si la transcripcion tiene 0 muletillas, 0 autocorrecciones, 0 frases incompletas y gramatica perfecta: es CASI SEGURO IA o lectura (probabilidad >= 80)
- Si ademas tiene estructura de texto escrito y conectores formales: probabilidad >= 90
- Solo clasifica como "natural" si hay evidencia CLARA de imperfecciones humanas

Responde en JSON:
{{
  "clasificacion": "natural|lectura|ia_generada",
  "esta_leyendo": true/false,
  "es_ia_generada": true/false,
  "nivel_confianza": "alto|medio|bajo",
  "probabilidad_lectura": 0-100,
  "probabilidad_ia": 0-100,
  "indicadores_detectados": [
    {{"indicador": "nombre", "categoria": "ia|lectura|natural", "descripcion": "que se detecto", "gravedad": "alta|media|baja"}}
  ],
  "evidencias_lectura": ["cita textual 1", "cita textual 2"],
  "evidencias_naturalidad": ["cita textual 1", "cita textual 2"],
  "evidencias_ia": ["cita textual 1", "cita textual 2"],
  "conteo_imperfecciones": {{
    "muletillas": 0,
    "autocorrecciones": 0,
    "frases_incompletas": 0,
    "errores_gramaticales": 0,
    "pausas_detectadas": 0
  }},
  "analisis_detallado": "Explicacion de la clasificacion",
  "recomendacion": "Que hacer con esta informacion"
}}"""

    def detectar_patron_lectura(self, transcripcion: str) -> Dict[str, Any]:
        try:
            raw = self._llamar_llm(
                self._PROMPT_DETECCION_LECTURA,
                f"Transcripcion del estudiante:\n\n{transcripcion}",
                temperature=0.2,
                max_tokens=2000,
            )
            parsed = self._parse_llm_json(raw)
            logger.info(
                "Deteccion: clasificacion=%s | lectura=%d%% | ia=%d%%",
                parsed.get("clasificacion", "?"),
                parsed.get("probabilidad_lectura", 0),
                parsed.get("probabilidad_ia", 0),
            )
            return parsed
        except Exception as e:
            logger.error("Error en deteccion de lectura: %s", e)
            return {
                "clasificacion": "natural",
                "esta_leyendo": False,
                "es_ia_generada": False,
                "nivel_confianza": "bajo",
                "probabilidad_lectura": 0,
                "probabilidad_ia": 0,
                "indicadores_detectados": [],
                "evidencias_lectura": [],
                "evidencias_naturalidad": [],
                "evidencias_ia": [],
                "conteo_imperfecciones": {
                    "muletillas": 0,
                    "autocorrecciones": 0,
                    "frases_incompletas": 0,
                    "errores_gramaticales": 0,
                    "pausas_detectadas": 0,
                },
                "analisis_detallado": f"No se pudo analizar: {e}",
                "recomendacion": "Revisar manualmente",
            }

    # -------------------------------------------------------------------------
    # Limpieza de transcripcion
    # -------------------------------------------------------------------------

    _PROMPT_LIMPIEZA = """Eres un asistente especializado en limpiar transcripciones de audio oral.

TU TAREA:
1. Eliminar muletillas: "eh", "mmm", "este", "o sea", "bueno", "pues", "como que", "digamos"
2. Eliminar repeticiones innecesarias de palabras
3. Corregir errores obvios de transcripcion
4. Mantener INTACTO todo el contenido, conceptos, terminos y explicaciones del hablante

REGLAS CRITICAS:
- NO cambies el significado de ninguna afirmacion
- NO agregues informacion que el hablante no dijo
- NO corrijas errores conceptuales (esos son para evaluar)
- Manten la estructura y orden de las ideas

Devuelve SOLO la transcripcion limpia, sin comentarios ni explicaciones."""

    def limpiar_transcripcion(self, transcripcion: str) -> str:
        try:
            return self._llamar_llm(
                self._PROMPT_LIMPIEZA,
                f"Limpia esta transcripcion:\n\n{transcripcion}",
                temperature=0.1,
                max_tokens=4000,
            )
        except Exception as e:
            logger.warning("No se pudo limpiar transcripcion, usando original: %s", e)
            return transcripcion

    # -------------------------------------------------------------------------
    # Pipeline de evaluacion (pasos internos)
    # -------------------------------------------------------------------------

    def _extraer_conceptos(self, material: str) -> Dict[str, Any]:
        system_prompt = """Eres un experto en analisis de contenido. Extrae los conceptos clave del material de referencia proporcionado.

Analiza el material y extrae:
1. Conceptos principales (los mas importantes que la persona DEBE mencionar)
2. Conceptos secundarios (importantes pero no criticos)
3. Datos especificos (fechas, formulas, nombres, cifras exactas, titulos, etc.)
4. Relaciones causales o procesos (si A entonces B, pasos de un proceso, conexiones entre ideas)

Responde en JSON:
{
  "conceptos_principales": ["concepto1", "concepto2"],
  "conceptos_secundarios": ["concepto1", "concepto2"],
  "datos_especificos": ["dato1", "dato2"],
  "relaciones_procesos": ["relacion1", "proceso1"],
  "tema_detectado": "Identifica el tema libremente",
  "nivel_dificultad": "Basico|Intermedio|Avanzado"
}"""

        try:
            raw = self._llamar_llm(
                system_prompt,
                f"Material de referencia:\n\n{material}",
                temperature=0.1,
                max_tokens=2000,
            )
            parsed = self._parse_llm_json(raw)
            logger.info(
                "Conceptos extraidos: %d principales",
                len(parsed.get("conceptos_principales", [])),
            )
            return parsed
        except json.JSONDecodeError as e:
            logger.error("JSON invalido en extraccion de conceptos: %s", e)
            return self._conceptos_fallback("General")
        except Exception as e:
            logger.error("Error en extraccion de conceptos: %s", e)
            return self._conceptos_fallback("Otro")

    @staticmethod
    def _conceptos_fallback(tema: str) -> Dict[str, Any]:
        return {
            "conceptos_principales": [],
            "conceptos_secundarios": [],
            "datos_especificos": [],
            "relaciones_procesos": [],
            "tema_detectado": tema,
            "nivel_dificultad": "Intermedio",
        }

    def _analizar_respuesta(self, transcripcion: str, conceptos: Dict) -> Dict[str, Any]:
        system_prompt = f"""Eres un evaluador experto. Analiza la respuesta de la persona comparandola con los conceptos clave esperados.

CONCEPTOS ESPERADOS:
- Principales (criticos): {json.dumps(conceptos.get('conceptos_principales', []), ensure_ascii=False)}
- Secundarios: {json.dumps(conceptos.get('conceptos_secundarios', []), ensure_ascii=False)}
- Datos especificos: {json.dumps(conceptos.get('datos_especificos', []), ensure_ascii=False)}
- Relaciones/Procesos: {json.dumps(conceptos.get('relaciones_procesos', []), ensure_ascii=False)}

INSTRUCCIONES:
1. Identifica que conceptos principales menciono correctamente
2. Identifica que conceptos principales omitio
3. Identifica errores factuales o conceptuales
4. Identifica informacion inventada o incorrecta
5. Evalua la claridad y coherencia de la explicacion

Responde en JSON:
{{
  "conceptos_correctos": ["concepto1", "concepto2"],
  "conceptos_omitidos": ["concepto1", "concepto2"],
  "errores_factuales": [
    {{"error": "descripcion del error", "gravedad": "leve|moderado|grave", "cita_alumno": "lo que dijo el alumno"}}
  ],
  "informacion_inventada": ["afirmacion inventada"],
  "claridad_explicacion": "excelente|buena|regular|deficiente",
  "coherencia_argumentativa": "excelente|buena|regular|deficiente",
  "uso_vocabulario_tecnico": "excelente|bueno|regular|deficiente",
  "citas_destacadas": ["frases textuales del alumno que demuestran comprension"]
}}"""

        try:
            raw = self._llamar_llm(
                system_prompt,
                f"Respuesta del estudiante:\n\n{transcripcion}",
                temperature=0.1,
                max_tokens=3000,
            )
            parsed = self._parse_llm_json(raw)
            logger.info(
                "Conceptos correctos identificados: %d",
                len(parsed.get("conceptos_correctos", [])),
            )
            return parsed
        except json.JSONDecodeError as e:
            logger.error("JSON invalido en analisis de respuesta: %s", e)
            return self._analisis_fallback()
        except Exception as e:
            logger.error("Error en analisis de respuesta: %s", e)
            return self._analisis_fallback()

    @staticmethod
    def _analisis_fallback() -> Dict[str, Any]:
        return {
            "conceptos_correctos": [],
            "conceptos_omitidos": [],
            "errores_factuales": [],
            "informacion_inventada": [],
            "claridad_explicacion": "regular",
            "coherencia_argumentativa": "regular",
            "uso_vocabulario_tecnico": "regular",
            "citas_destacadas": [],
        }

    def _calcular_calificacion(
        self, conceptos: Dict, analisis: Dict, rubrica: str
    ) -> Dict[str, Any]:
        system_prompt = f"""Eres un evaluador experto y justo. Calcula una calificacion precisa basandote en el analisis realizado y la rubrica proporcionada.

ANALISIS DEL EXAMEN:
- Conceptos correctos: {json.dumps(analisis.get('conceptos_correctos', []), ensure_ascii=False)}
- Conceptos omitidos: {json.dumps(analisis.get('conceptos_omitidos', []), ensure_ascii=False)}
- Errores factuales: {json.dumps(analisis.get('errores_factuales', []), ensure_ascii=False)}
- Informacion inventada: {json.dumps(analisis.get('informacion_inventada', []), ensure_ascii=False)}
- Claridad: {analisis.get('claridad_explicacion', 'regular')}
- Coherencia: {analisis.get('coherencia_argumentativa', 'regular')}
- Vocabulario tecnico: {analisis.get('uso_vocabulario_tecnico', 'regular')}

RUBRICA DEL DOCENTE:
{rubrica}

TEMA Y NIVEL:
- Tema: {conceptos.get('tema_detectado', 'General')}
- Nivel: {conceptos.get('nivel_dificultad', 'Intermedio')}

INSTRUCCIONES DE CALIFICACION:
1. Usa la rubrica del docente como guia principal
2. Si no hay rubrica especifica, usa estos criterios:
   - Conceptos principales correctos: 40%
   - Conceptos secundarios correctos: 20%
   - Ausencia de errores graves: 20%
   - Claridad y coherencia: 10%
   - Vocabulario tecnico: 10%
3. Penaliza errores graves (-1 punto cada uno)
4. Penaliza informacion inventada (-0.5 puntos cada una)
5. La calificacion debe ser justa y fundamentada

Responde en JSON:
{{
  "calificacion_final": 8.5,
  "calificacion_por_criterio": [
    {{"criterio": "nombre", "puntaje": 3, "maximo": 4, "justificacion": "razon"}}
  ],
  "penalizaciones": [
    {{"razon": "descripcion", "puntos_restados": 0.5}}
  ],
  "bonificaciones": [
    {{"razon": "descripcion", "puntos_agregados": 0.5}}
  ],
  "nivel_confianza": "alto|medio|bajo",
  "justificacion_general": "Explicacion de la calificacion"
}}"""

        try:
            raw = self._llamar_llm(
                system_prompt,
                "Calcula la calificacion segun las instrucciones.",
                temperature=0.1,
                max_tokens=2000,
            )
            parsed = self._parse_llm_json(raw)
            logger.info("Calificacion: %s", parsed.get("calificacion_final"))
            return parsed
        except json.JSONDecodeError as e:
            logger.error("JSON invalido en calificacion: %s", e)
            score = self._extraer_calificacion_fallback(raw)
            return self._calificacion_fallback(score, "Calificacion extraida del texto.")
        except Exception as e:
            logger.error("Error en calificacion: %s", e)
            return self._calificacion_fallback(5.0, f"Error al calcular: {e}")

    @staticmethod
    def _calificacion_fallback(score: float, justificacion: str) -> Dict[str, Any]:
        return {
            "calificacion_final": score,
            "calificacion_por_criterio": [],
            "penalizaciones": [],
            "bonificaciones": [],
            "nivel_confianza": "bajo",
            "justificacion_general": justificacion,
        }

    def _extraer_calificacion_fallback(self, texto: str) -> float:
        if not texto:
            return 5.0
        patrones = [
            r'"calificacion_final"\s*:\s*(\d+\.?\d*)',
            r'calificacion[:\s]+(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*/\s*10',
            r'nota[:\s]+(\d+\.?\d*)',
            r'puntaje[:\s]+(\d+\.?\d*)',
        ]
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                try:
                    cal = float(match.group(1))
                    if 0 <= cal <= 10:
                        logger.info("Calificacion extraida por fallback: %s", cal)
                        return cal
                except ValueError:
                    continue
        logger.warning("No se pudo extraer calificacion, usando 5.0 por defecto")
        return 5.0

    def _generar_feedback(
        self, analisis: Dict, calificacion: Dict, conceptos: Dict
    ) -> Dict[str, Any]:
        system_prompt = f"""Eres un evaluador experto, empatico y constructivo. Genera feedback personalizado para la persona evaluada.

RESULTADOS DEL EXAMEN:
- Calificacion: {calificacion.get('calificacion_final', 0)}/10
- Conceptos correctos: {json.dumps(analisis.get('conceptos_correctos', []), ensure_ascii=False)}
- Conceptos omitidos: {json.dumps(analisis.get('conceptos_omitidos', []), ensure_ascii=False)}
- Errores: {json.dumps(analisis.get('errores_factuales', []), ensure_ascii=False)}
- Citas destacadas: {json.dumps(analisis.get('citas_destacadas', []), ensure_ascii=False)}
- Tema: {conceptos.get('tema_detectado', 'General')}

INSTRUCCIONES:
1. Se constructivo y motivador, pero honesto
2. Destaca primero lo positivo
3. Explica los errores de forma educativa
4. Da sugerencias concretas de mejora
5. Adapta el tono al nivel del estudiante

Responde en JSON:
{{
  "feedback_alumno": {{
    "resumen": "Resumen breve del desempeno",
    "fortalezas": ["fortaleza1", "fortaleza2"],
    "areas_mejora": ["area1", "area2"],
    "errores_corregidos": [
      {{"error": "lo que dijo mal", "correccion": "lo correcto", "explicacion": "por que"}}
    ],
    "recomendaciones_estudio": ["recomendacion1", "recomendacion2"],
    "mensaje_motivacional": "Mensaje final motivador"
  }},
  "nota_docente": {{
    "observaciones": "Observaciones para el docente",
    "patron_errores": "Si hay un patron en los errores",
    "sugerencia_refuerzo": "Que temas reforzar",
    "comparacion_esperado": "Como se compara con lo esperado"
  }}
}}"""

        try:
            raw = self._llamar_llm(
                system_prompt,
                "Genera el feedback segun las instrucciones.",
                temperature=0.3,
                max_tokens=3000,
            )
            return self._parse_llm_json(raw)
        except Exception as e:
            logger.error("Error generando feedback: %s", e)
            return {
                "feedback_alumno": {
                    "resumen": "No se pudo generar el feedback",
                    "fortalezas": [],
                    "areas_mejora": [],
                    "errores_corregidos": [],
                    "recomendaciones_estudio": [],
                    "mensaje_motivacional": "",
                },
                "nota_docente": {
                    "observaciones": f"Error: {e}",
                    "patron_errores": "",
                    "sugerencia_refuerzo": "",
                    "comparacion_esperado": "",
                },
            }

    # -------------------------------------------------------------------------
    # Cobertura conceptual
    # -------------------------------------------------------------------------

    @staticmethod
    def _calcular_cobertura(conceptos: Dict, analisis: Dict) -> float:
        principales = set(conceptos.get("conceptos_principales", []))
        secundarios = set(conceptos.get("conceptos_secundarios", []))
        correctos = set(analisis.get("conceptos_correctos", []))

        total = len(principales) + len(secundarios)
        if total == 0:
            return 100.0

        principales_ok = len([
            c for c in correctos
            if any(c.lower() in p.lower() or p.lower() in c.lower() for p in principales)
        ])
        secundarios_ok = len([
            c for c in correctos
            if any(c.lower() in s.lower() or s.lower() in c.lower() for s in secundarios)
        ])

        peso_total = (len(principales) * 2) + len(secundarios)
        if peso_total == 0:
            return 100.0
        cobertura = ((principales_ok * 2) + secundarios_ok) / peso_total * 100
        return round(min(cobertura, 100.0), 1)

    # -------------------------------------------------------------------------
    # Metodos publicos
    # -------------------------------------------------------------------------

    def evaluar_examen(
        self, material: str, rubrica: str, transcripcion: str
    ) -> Dict[str, Any]:
        try:
            logger.info(
                "Iniciando evaluacion | LLM=%s | modelo=%s | material=%d chars | rubrica=%d chars | transcripcion=%d chars",
                self.proveedor_llm, self.llm_model,
                len(material), len(rubrica), len(transcripcion),
            )

            conceptos = self._extraer_conceptos(material)
            analisis = self._analizar_respuesta(transcripcion, conceptos)
            calificacion = self._calcular_calificacion(conceptos, analisis, rubrica)
            feedback = self._generar_feedback(analisis, calificacion, conceptos)

            resultado = {
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
                    "cobertura_porcentaje": self._calcular_cobertura(conceptos, analisis),
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

            return {"success": True, "evaluacion": resultado}

        except Exception as e:
            logger.exception("Error en evaluacion")
            return {"success": False, "error": f"Error en la evaluacion: {e}"}

    def proceso_completo(
        self,
        audio_path: str,
        material: str,
        rubrica: str,
        limpiar: bool = True,
        idioma: str = "es",
        detectar_lectura: bool = True,
    ) -> Dict[str, Any]:
        resultado_transcripcion = self.transcribir_audio(audio_path, idioma)
        if not resultado_transcripcion["success"]:
            return resultado_transcripcion

        transcripcion = resultado_transcripcion["transcripcion"]

        patron_lectura = None
        if detectar_lectura:
            logger.info("Detectando patrones de lectura...")
            patron_lectura = self.detectar_patron_lectura(transcripcion)

        transcripcion_limpia = (
            self.limpiar_transcripcion(transcripcion) if limpiar else transcripcion
        )

        resultado_evaluacion = self.evaluar_examen(material, rubrica, transcripcion_limpia)
        if not resultado_evaluacion["success"]:
            return resultado_evaluacion

        return {
            "success": True,
            "transcripcion_original": resultado_transcripcion["transcripcion"],
            "transcripcion_limpia": transcripcion_limpia,
            "duracion_audio": resultado_transcripcion.get("duracion"),
            "idioma": idioma,
            "patron_lectura": patron_lectura,
            "evaluacion": resultado_evaluacion["evaluacion"],
        }
