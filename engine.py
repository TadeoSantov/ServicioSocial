import os
import json
import re
from typing import Dict, Any, Optional, List
from groq import Groq
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

load_dotenv()


class EvaluadorEngine:
    def __init__(
        self, 
        api_key: Optional[str] = None,
        proveedor: str = "groq",
        google_api_key: Optional[str] = None
    ):
        self.proveedor = proveedor.lower()
        
        self.groq_api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY no encontrada (requerida para transcripción)")
        
        self.groq_client = Groq(api_key=self.groq_api_key)
        self.whisper_model = "whisper-large-v3"
        
        if self.proveedor == "google":
            if not GOOGLE_AI_AVAILABLE:
                raise ImportError("google-generativeai no está instalado. Ejecuta: pip install google-generativeai")
            
            self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY no encontrada para usar Google AI")
            
            genai.configure(api_key=self.google_api_key)
            self.google_model = genai.GenerativeModel("gemini-1.5-flash")
            self.llm_model = "gemini-1.5-flash"
        else:
            self.llm_model = "llama-3.3-70b-versatile"
    
    def _llamar_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 4000) -> str:
        if self.proveedor == "google":
            prompt_completo = f"{system_prompt}\n\n---\n\nUSUARIO: {user_prompt}"
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            response = self.google_model.generate_content(
                prompt_completo,
                generation_config=generation_config
            )
            return response.text.strip()
        else:
            response = self.groq_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
    
    def transcribir_audio(self, audio_file_path: str, idioma: str = "es") -> Dict[str, Any]:
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), audio_file.read()),
                    model=self.whisper_model,
                    response_format="verbose_json",
                    language=idioma,
                )
            
            return {
                "success": True,
                "transcripcion": transcription.text,
                "duracion": getattr(transcription, 'duration', None),
                "idioma": idioma
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al transcribir audio: {str(e)}"
            }
    
    def limpiar_transcripcion(self, transcripcion: str) -> str:
        system_prompt = """Eres un asistente especializado en limpiar transcripciones de exámenes orales académicos.

TU TAREA:
1. Eliminar muletillas: "eh", "mmm", "este", "o sea", "bueno", "pues", "como que", "digamos"
2. Eliminar repeticiones innecesarias de palabras
3. Corregir errores obvios de transcripción
4. Mantener INTACTO todo el contenido académico, conceptos, términos técnicos y explicaciones

REGLAS CRÍTICAS:
- NO cambies el significado de ninguna afirmación del estudiante
- NO agregues información que el estudiante no dijo
- NO corrijas errores conceptuales del estudiante (esos son para evaluar)
- Mantén la estructura y orden de las ideas del estudiante

Devuelve SOLO la transcripción limpia, sin comentarios ni explicaciones."""
        
        try:
            return self._llamar_llm(
                system_prompt,
                f"Limpia esta transcripción:\n\n{transcripcion}",
                temperature=0.1,
                max_tokens=4000
            )
        except Exception as e:
            return transcripcion

    def _extraer_conceptos_clave(self, material_referencia: str) -> Dict[str, Any]:
        system_prompt = """Eres un experto en análisis de contenido académico. Tu tarea es extraer los conceptos clave de un material de referencia.

Analiza el material y extrae:
1. Conceptos principales (los más importantes que el estudiante DEBE mencionar)
2. Conceptos secundarios (importantes pero no críticos)
3. Datos específicos (fechas, fórmulas, nombres, cifras exactas)
4. Relaciones causales o procesos (si A entonces B, pasos de un proceso)

Responde en JSON:
{
  "conceptos_principales": ["concepto1", "concepto2"],
  "conceptos_secundarios": ["concepto1", "concepto2"],
  "datos_especificos": ["dato1", "dato2"],
  "relaciones_procesos": ["relación1", "proceso1"],
  "tema_detectado": "Biología|Matemáticas|Historia|Física|Química|Literatura|Otro",
  "nivel_dificultad": "Básico|Intermedio|Avanzado"
}"""

        try:
            resultado = self._llamar_llm(
                system_prompt,
                f"Material de referencia:\n\n{material_referencia}",
                temperature=0.1,
                max_tokens=2000
            )
            print(f"[DEBUG] Extracción conceptos - respuesta recibida: {len(resultado)} chars")
            resultado = self._limpiar_json(resultado)
            parsed = json.loads(resultado)
            print(f"[DEBUG] Conceptos principales encontrados: {len(parsed.get('conceptos_principales', []))}")
            return parsed
        
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON inválido en extracción de conceptos: {e}")
            return {
                "conceptos_principales": ["concepto general del tema"],
                "conceptos_secundarios": [],
                "datos_especificos": [],
                "relaciones_procesos": [],
                "tema_detectado": "General",
                "nivel_dificultad": "Intermedio"
            }
        except Exception as e:
            print(f"[ERROR] Error en extracción de conceptos: {e}")
            return {
                "conceptos_principales": [],
                "conceptos_secundarios": [],
                "datos_especificos": [],
                "relaciones_procesos": [],
                "tema_detectado": "Otro",
                "nivel_dificultad": "Intermedio"
            }

    def _analizar_respuesta_alumno(self, transcripcion: str, conceptos: Dict) -> Dict[str, Any]:
        system_prompt = f"""Eres un evaluador académico experto. Analiza la respuesta del estudiante comparándola con los conceptos clave esperados.

CONCEPTOS ESPERADOS:
- Principales (críticos): {json.dumps(conceptos.get('conceptos_principales', []), ensure_ascii=False)}
- Secundarios: {json.dumps(conceptos.get('conceptos_secundarios', []), ensure_ascii=False)}
- Datos específicos: {json.dumps(conceptos.get('datos_especificos', []), ensure_ascii=False)}
- Relaciones/Procesos: {json.dumps(conceptos.get('relaciones_procesos', []), ensure_ascii=False)}

INSTRUCCIONES:
1. Identifica qué conceptos principales mencionó correctamente
2. Identifica qué conceptos principales omitió
3. Identifica errores factuales o conceptuales
4. Identifica información inventada o incorrecta
5. Evalúa la claridad y coherencia de la explicación

Responde en JSON:
{{
  "conceptos_correctos": ["concepto1", "concepto2"],
  "conceptos_omitidos": ["concepto1", "concepto2"],
  "errores_factuales": [
    {{"error": "descripción del error", "gravedad": "leve|moderado|grave", "cita_alumno": "lo que dijo el alumno"}}
  ],
  "informacion_inventada": ["afirmación inventada"],
  "claridad_explicacion": "excelente|buena|regular|deficiente",
  "coherencia_argumentativa": "excelente|buena|regular|deficiente",
  "uso_vocabulario_tecnico": "excelente|bueno|regular|deficiente",
  "citas_destacadas": ["frases textuales del alumno que demuestran comprensión"]
}}"""

        try:
            resultado = self._llamar_llm(
                system_prompt,
                f"Respuesta del estudiante:\n\n{transcripcion}",
                temperature=0.1,
                max_tokens=3000
            )
            print(f"[DEBUG] Análisis respuesta - recibido: {len(resultado)} chars")
            resultado = self._limpiar_json(resultado)
            parsed = json.loads(resultado)
            print(f"[DEBUG] Conceptos correctos identificados: {len(parsed.get('conceptos_correctos', []))}")
            return parsed
        
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON inválido en análisis de respuesta: {e}")
            return {
                "conceptos_correctos": ["respuesta analizada"],
                "conceptos_omitidos": [],
                "errores_factuales": [],
                "informacion_inventada": [],
                "claridad_explicacion": "regular",
                "coherencia_argumentativa": "regular",
                "uso_vocabulario_tecnico": "regular",
                "citas_destacadas": []
            }
        except Exception as e:
            print(f"[ERROR] Error en análisis de respuesta: {e}")
            return {
                "conceptos_correctos": [],
                "conceptos_omitidos": [],
                "errores_factuales": [],
                "informacion_inventada": [],
                "claridad_explicacion": "regular",
                "coherencia_argumentativa": "regular",
                "uso_vocabulario_tecnico": "regular",
                "citas_destacadas": []
            }

    def _calcular_calificacion(
        self, 
        conceptos: Dict, 
        analisis: Dict, 
        rubrica: str
    ) -> Dict[str, Any]:
        system_prompt = f"""Eres un evaluador académico experto y justo. Debes calcular una calificación precisa basándote en el análisis realizado y la rúbrica del docente.

ANÁLISIS DEL EXAMEN:
- Conceptos correctos: {json.dumps(analisis.get('conceptos_correctos', []), ensure_ascii=False)}
- Conceptos omitidos: {json.dumps(analisis.get('conceptos_omitidos', []), ensure_ascii=False)}
- Errores factuales: {json.dumps(analisis.get('errores_factuales', []), ensure_ascii=False)}
- Información inventada: {json.dumps(analisis.get('informacion_inventada', []), ensure_ascii=False)}
- Claridad: {analisis.get('claridad_explicacion', 'regular')}
- Coherencia: {analisis.get('coherencia_argumentativa', 'regular')}
- Vocabulario técnico: {analisis.get('uso_vocabulario_tecnico', 'regular')}

RÚBRICA DEL DOCENTE:
{rubrica}

TEMA Y NIVEL:
- Tema: {conceptos.get('tema_detectado', 'General')}
- Nivel: {conceptos.get('nivel_dificultad', 'Intermedio')}

INSTRUCCIONES DE CALIFICACIÓN:
1. Usa la rúbrica del docente como guía principal
2. Si no hay rúbrica específica, usa estos criterios:
   - Conceptos principales correctos: 40% del puntaje
   - Conceptos secundarios correctos: 20% del puntaje
   - Ausencia de errores graves: 20% del puntaje
   - Claridad y coherencia: 10% del puntaje
   - Vocabulario técnico: 10% del puntaje
3. Penaliza errores graves (-1 punto cada uno)
4. Penaliza información inventada (-0.5 puntos cada una)
5. La calificación debe ser justa y fundamentada

Responde en JSON:
{{
  "calificacion_final": 8.5,
  "calificacion_por_criterio": [
    {{"criterio": "nombre", "puntaje": 3, "maximo": 4, "justificacion": "razón"}}
  ],
  "penalizaciones": [
    {{"razon": "descripción", "puntos_restados": 0.5}}
  ],
  "bonificaciones": [
    {{"razon": "descripción", "puntos_agregados": 0.5}}
  ],
  "nivel_confianza": "alto|medio|bajo",
  "justificacion_general": "Explicación de la calificación"
}}"""

        try:
            resultado = self._llamar_llm(
                system_prompt,
                "Calcula la calificación según las instrucciones.",
                temperature=0.1,
                max_tokens=2000
            )
            print(f"[DEBUG] Respuesta calificación raw: {resultado[:500]}...")
            resultado = self._limpiar_json(resultado)
            parsed = json.loads(resultado)
            print(f"[DEBUG] Calificación parseada: {parsed.get('calificacion_final', 'NO ENCONTRADA')}")
            return parsed
        
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON inválido en calificación: {e}")
            print(f"[ERROR] Texto recibido: {resultado[:1000] if resultado else 'VACÍO'}")
            calificacion_extraida = self._extraer_calificacion_fallback(resultado)
            return {
                "calificacion_final": calificacion_extraida,
                "calificacion_por_criterio": [],
                "penalizaciones": [],
                "bonificaciones": [],
                "nivel_confianza": "bajo",
                "justificacion_general": f"Calificación extraída del análisis del modelo."
            }
        except Exception as e:
            print(f"[ERROR] Error general en calificación: {e}")
            return {
                "calificacion_final": 5.0,
                "calificacion_por_criterio": [],
                "penalizaciones": [],
                "bonificaciones": [],
                "nivel_confianza": "bajo",
                "justificacion_general": f"Error al calcular: {str(e)}. Calificación estimada."
            }
    
    def _extraer_calificacion_fallback(self, texto: str) -> float:
        """Intenta extraer la calificación del texto cuando el JSON falla"""
        if not texto:
            return 5.0
        
        import re
        
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
                        print(f"[DEBUG] Calificación extraída por fallback: {cal}")
                        return cal
                except:
                    continue
        
        print(f"[DEBUG] No se pudo extraer calificación, usando 5.0 por defecto")
        return 5.0

    def _generar_feedback(
        self, 
        analisis: Dict, 
        calificacion: Dict, 
        conceptos: Dict
    ) -> Dict[str, Any]:
        system_prompt = f"""Eres un tutor académico experto, empático y constructivo. Genera feedback personalizado para el estudiante.

RESULTADOS DEL EXAMEN:
- Calificación: {calificacion.get('calificacion_final', 0)}/10
- Conceptos correctos: {json.dumps(analisis.get('conceptos_correctos', []), ensure_ascii=False)}
- Conceptos omitidos: {json.dumps(analisis.get('conceptos_omitidos', []), ensure_ascii=False)}
- Errores: {json.dumps(analisis.get('errores_factuales', []), ensure_ascii=False)}
- Citas destacadas: {json.dumps(analisis.get('citas_destacadas', []), ensure_ascii=False)}
- Tema: {conceptos.get('tema_detectado', 'General')}

INSTRUCCIONES:
1. Sé constructivo y motivador, pero honesto
2. Destaca primero lo positivo
3. Explica los errores de forma educativa
4. Da sugerencias concretas de mejora
5. Adapta el tono al nivel del estudiante

Responde en JSON:
{{
  "feedback_alumno": {{
    "resumen": "Resumen breve del desempeño",
    "fortalezas": ["fortaleza1", "fortaleza2"],
    "areas_mejora": ["área1", "área2"],
    "errores_corregidos": [
      {{"error": "lo que dijo mal", "correccion": "lo correcto", "explicacion": "por qué"}}
    ],
    "recomendaciones_estudio": ["recomendación1", "recomendación2"],
    "mensaje_motivacional": "Mensaje final motivador"
  }},
  "nota_docente": {{
    "observaciones": "Observaciones para el docente",
    "patron_errores": "Si hay un patrón en los errores",
    "sugerencia_refuerzo": "Qué temas reforzar",
    "comparacion_esperado": "Cómo se compara con lo esperado"
  }}
}}"""

        try:
            resultado = self._llamar_llm(
                system_prompt,
                "Genera el feedback según las instrucciones.",
                temperature=0.3,
                max_tokens=3000
            )
            resultado = self._limpiar_json(resultado)
            return json.loads(resultado)
        
        except Exception as e:
            return {
                "feedback_alumno": {
                    "resumen": "No se pudo generar el feedback",
                    "fortalezas": [],
                    "areas_mejora": [],
                    "errores_corregidos": [],
                    "recomendaciones_estudio": [],
                    "mensaje_motivacional": ""
                },
                "nota_docente": {
                    "observaciones": f"Error: {str(e)}",
                    "patron_errores": "",
                    "sugerencia_refuerzo": "",
                    "comparacion_esperado": ""
                }
            }

    def _limpiar_json(self, texto: str) -> str:
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
        
        start_idx = texto.find('{')
        end_idx = texto.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            texto = texto[start_idx:end_idx + 1]
        
        return texto.strip()

    def evaluar_examen(
        self, 
        material_referencia: str, 
        rubrica: str, 
        transcripcion_alumno: str
    ) -> Dict[str, Any]:
        try:
            print(f"[DEBUG] === INICIANDO EVALUACIÓN ===")
            print(f"[DEBUG] Proveedor: {self.proveedor}")
            print(f"[DEBUG] Modelo LLM: {self.llm_model}")
            print(f"[DEBUG] Longitud material: {len(material_referencia)} chars")
            print(f"[DEBUG] Longitud rúbrica: {len(rubrica)} chars")
            print(f"[DEBUG] Longitud transcripción: {len(transcripcion_alumno)} chars")
            
            print(f"[DEBUG] Paso 1: Extrayendo conceptos...")
            conceptos = self._extraer_conceptos_clave(material_referencia)
            print(f"[DEBUG] Conceptos extraídos: {len(conceptos.get('conceptos_principales', []))} principales")
            
            analisis = self._analizar_respuesta_alumno(transcripcion_alumno, conceptos)
            
            calificacion = self._calcular_calificacion(conceptos, analisis, rubrica)
            
            feedback = self._generar_feedback(analisis, calificacion, conceptos)
            
            evaluacion_completa = {
                "calificacion_final": calificacion.get("calificacion_final", 0),
                "nivel_confianza": calificacion.get("nivel_confianza", "medio"),
                "tema_detectado": conceptos.get("tema_detectado", "General"),
                "nivel_dificultad": conceptos.get("nivel_dificultad", "Intermedio"),
                
                "desglose_calificacion": {
                    "por_criterio": calificacion.get("calificacion_por_criterio", []),
                    "penalizaciones": calificacion.get("penalizaciones", []),
                    "bonificaciones": calificacion.get("bonificaciones", []),
                    "justificacion": calificacion.get("justificacion_general", "")
                },
                
                "analisis_conceptual": {
                    "conceptos_esperados": {
                        "principales": conceptos.get("conceptos_principales", []),
                        "secundarios": conceptos.get("conceptos_secundarios", [])
                    },
                    "conceptos_mencionados": analisis.get("conceptos_correctos", []),
                    "conceptos_omitidos": analisis.get("conceptos_omitidos", []),
                    "cobertura_porcentaje": self._calcular_cobertura(conceptos, analisis)
                },
                
                "errores_detectados": {
                    "factuales": analisis.get("errores_factuales", []),
                    "inventados": analisis.get("informacion_inventada", [])
                },
                
                "metricas_comunicacion": {
                    "claridad": analisis.get("claridad_explicacion", "regular"),
                    "coherencia": analisis.get("coherencia_argumentativa", "regular"),
                    "vocabulario_tecnico": analisis.get("uso_vocabulario_tecnico", "regular")
                },
                
                "feedback_alumno": feedback.get("feedback_alumno", {}),
                "nota_docente": feedback.get("nota_docente", {}),
                
                "citas_destacadas": analisis.get("citas_destacadas", [])
            }
            
            return {
                "success": True,
                "evaluacion": evaluacion_completa
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en la evaluación: {str(e)}"
            }

    def _calcular_cobertura(self, conceptos: Dict, analisis: Dict) -> float:
        principales = set(conceptos.get("conceptos_principales", []))
        secundarios = set(conceptos.get("conceptos_secundarios", []))
        correctos = set(analisis.get("conceptos_correctos", []))
        
        total_conceptos = len(principales) + len(secundarios)
        if total_conceptos == 0:
            return 100.0
        
        principales_cubiertos = len([c for c in correctos if any(c.lower() in p.lower() or p.lower() in c.lower() for p in principales)])
        secundarios_cubiertos = len([c for c in correctos if any(c.lower() in s.lower() or s.lower() in c.lower() for s in secundarios)])
        
        cobertura = ((principales_cubiertos * 2) + secundarios_cubiertos) / ((len(principales) * 2) + len(secundarios)) * 100
        return round(min(cobertura, 100.0), 1)

    def proceso_completo(
        self, 
        audio_file_path: str, 
        material_referencia: str, 
        rubrica: str,
        limpiar: bool = True,
        idioma: str = "es"
    ) -> Dict[str, Any]:
        resultado_transcripcion = self.transcribir_audio(audio_file_path, idioma)
        
        if not resultado_transcripcion["success"]:
            return resultado_transcripcion
        
        transcripcion = resultado_transcripcion["transcripcion"]
        
        if limpiar:
            transcripcion_limpia = self.limpiar_transcripcion(transcripcion)
        else:
            transcripcion_limpia = transcripcion
        
        resultado_evaluacion = self.evaluar_examen(
            material_referencia, 
            rubrica, 
            transcripcion_limpia
        )
        
        if not resultado_evaluacion["success"]:
            return resultado_evaluacion
        
        return {
            "success": True,
            "transcripcion_original": resultado_transcripcion["transcripcion"],
            "transcripcion_limpia": transcripcion_limpia,
            "duracion_audio": resultado_transcripcion.get("duracion"),
            "idioma": idioma,
            "evaluacion": resultado_evaluacion["evaluacion"]
        }
