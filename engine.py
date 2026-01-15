import os
import json
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class EvaluadorEngine:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY no encontrada en las variables de entorno")
        
        self.client = Groq(api_key=api_key)
        self.whisper_model = "whisper-large-v3"
        self.llm_model = "llama-3.3-70b-versatile"
    
    def transcribir_audio(self, audio_file_path: str) -> Dict[str, Any]:
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), audio_file.read()),
                    model=self.whisper_model,
                    response_format="verbose_json",
                )
            
            return {
                "success": True,
                "transcripcion": transcription.text,
                "duracion": getattr(transcription, 'duration', None)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al transcribir audio: {str(e)}"
            }
    
    def limpiar_transcripcion(self, transcripcion: str) -> str:
        system_prompt = """Eres un asistente que limpia transcripciones de audio eliminando muletillas, 
        repeticiones innecesarias y errores de transcripción, pero manteniendo el contenido académico intacto.
        
        Elimina: "eh", "mmm", "este", "o sea", repeticiones de palabras.
        Mantén: todos los conceptos, términos técnicos y explicaciones del estudiante.
        
        Devuelve SOLO la transcripción limpia, sin comentarios adicionales."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Limpia esta transcripción:\n\n{transcripcion}"}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return transcripcion
    
    def evaluar_examen(
        self, 
        material_referencia: str, 
        rubrica: str, 
        transcripcion_alumno: str
    ) -> Dict[str, Any]:
        system_prompt = f"""Actúa como un Evaluador Académico experto y multidisciplinario. Tu objetivo es calificar un examen oral comparando la transcripción de un alumno contra el material de referencia proporcionado por el docente.

INFORMACIÓN PROPORCIONADA:
1. MATERIAL DE REFERENCIA (Base de verdad): {material_referencia}
2. RÚBRICA DE EVALUACIÓN: {rubrica}
3. TRANSCRIPCIÓN DEL EXAMEN: {transcripcion_alumno}

INSTRUCCIONES DE EVALUACIÓN:
- Analiza si el alumno menciona los conceptos clave del Material de Referencia.
- Sé riguroso: si el alumno inventa datos o contradice el material de referencia, márcalo como un error grave.
- Si el tema es Matemáticas/Ciencias, valida la precisión de fórmulas y pasos lógicos.
- Si el tema es Historia/Humanidades, valida la coherencia narrativa y precisión de fechas/personajes.
- Asigna una calificación numérica del 0 al 10 basada en la rúbrica.

FORMATO DE RESPUESTA (JSON estricto):
{{
  "calificacion_final": "número del 0-10",
  "analisis_conceptos": "Breve análisis de qué cubrió y qué olvidó",
  "errores_especificos": ["Error 1", "Error 2"],
  "feedback_para_alumno": "Texto motivador y correctivo",
  "sugerencia_docente": "Nota interna para el profesor"
}}

Responde ÚNICAMENTE con el JSON, sin texto adicional."""

        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Evalúa el examen según las instrucciones."}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            resultado_texto = response.choices[0].message.content.strip()
            
            if resultado_texto.startswith("```json"):
                resultado_texto = resultado_texto.replace("```json", "").replace("```", "").strip()
            elif resultado_texto.startswith("```"):
                resultado_texto = resultado_texto.replace("```", "").strip()
            
            resultado_json = json.loads(resultado_texto)
            
            return {
                "success": True,
                "evaluacion": resultado_json
            }
        
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Error al parsear JSON: {str(e)}",
                "raw_response": resultado_texto if 'resultado_texto' in locals() else "No response"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en la evaluación: {str(e)}"
            }
    
    def proceso_completo(
        self, 
        audio_file_path: str, 
        material_referencia: str, 
        rubrica: str,
        limpiar: bool = True
    ) -> Dict[str, Any]:
        resultado_transcripcion = self.transcribir_audio(audio_file_path)
        
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
            "evaluacion": resultado_evaluacion["evaluacion"]
        }
