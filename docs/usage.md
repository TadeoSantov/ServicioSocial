# Guía de uso

## Iniciar la aplicación

```bash
streamlit run app.py
```

La app abre en `http://localhost:8501`. En Windows puedes usar `ejecutar.bat` directamente desde el explorador de archivos.

---

## Flujo de trabajo

La evaluación sigue cuatro pasos en orden:

### 1. Material de referencia

Pega el contenido que el estudiante debía estudiar: apuntes, fragmentos del libro, resúmenes, etc. Este texto es la "verdad" contra la que se evalúa la respuesta.

No tiene que ser perfecto ni estar formateado. Basta con que contenga los conceptos clave.

### 2. Rúbrica de evaluación

Define los criterios de calificación y el puntaje de cada uno. Ejemplo:

```
- Menciona las dos fases de la fotosíntesis (3 puntos)
- Explica dónde ocurre cada fase (2 puntos)
- Menciona los productos de cada fase (3 puntos)
- Recita la ecuación química correctamente (2 puntos)

Total: 10 puntos
```

Mientras más específica sea la rúbrica, más precisa será la evaluación.

### 3. Audio del examen

Tienes dos opciones:

**Subir archivo** — Formatos aceptados: MP3, WAV, M4A, OGG, FLAC, WEBM. Tamaño máximo: 25 MB.

**Grabar en el navegador** — Sin software adicional. Funciona en Chrome, Edge y Firefox.
1. Ve a la pestaña "Grabar Audio"
2. Haz clic en el botón del micrófono
3. Permite el acceso al micrófono cuando el navegador lo solicite
4. Habla y haz clic nuevamente para detener
5. Escucha la grabación antes de continuar; si no quedó bien, puedes borrarla y repetir

### 4. Evaluar

Haz clic en **Evaluar Examen**. El proceso tarda entre 10 y 20 segundos para un audio de 5 minutos.

El resultado incluye:
- Calificación numérica
- Desglose por criterio de la rúbrica
- Conceptos que el estudiante dominó y los que le faltaron
- Feedback para el estudiante
- Notas para el docente

---

## Opciones adicionales

### Limpieza de transcripción

Activa esta opción en la barra lateral para eliminar muletillas ("eh", "mmm", "este", "o sea") del texto transcrito antes de evaluarlo. Útil cuando el estudiante habla con muchas pausas o repeticiones.

### Detector de lectura (experimental)

Detecta si el estudiante está leyendo un texto en lugar de hablar de forma espontánea. Se activa desde la barra lateral.

Analiza indicadores como:
- Fluidez excesiva sin pausas ni titubeos
- Vocabulario muy formal sin explicaciones propias
- Ausencia total de muletillas
- Estructura gramatical perfecta
- Conectores formales ("asimismo", "por consiguiente")

Niveles de alerta:

| Probabilidad | Interpretación |
|-------------|----------------|
| < 40% | Habla natural |
| 40 – 69% | Patrones sospechosos, revisar manualmente |
| ≥ 70% | Muy probable que esté leyendo |

Esta herramienta es de apoyo, no un veredicto. Algunos estudiantes con buen dominio del tema pueden activar falsos positivos.

---

## Ejemplos de prueba

La carpeta `ejemplos/` contiene material listo para usar sin tener que escribir nada:

| Archivo | Contenido |
|---------|-----------|
| `ratatouille_material.txt` | Sinopsis, personajes y temas de la película |
| `ratatouille_rubrica.txt` | Rúbrica de 10 puntos para el análisis |
| `ejemplo_biologia.md` | Fotosíntesis |
| `ejemplo_historia.md` | Revolución Francesa |
| `ejemplo_matematicas.md` | Teorema de Pitágoras |

Desde la interfaz puedes cargarlos directamente con el selector "Ejemplos Predefinidos" sin necesidad de copiar y pegar.

---

## Personalización de modelos

Si quieres cambiar los modelos que usa la app, edita `engine.py`:

```python
self.whisper_model = "whisper-large-v3"        # Más preciso, algo más lento
self.llm_model = "llama-3.3-70b-versatile"     # Modelo más reciente de Groq
```

Para ajustar qué tan determinística es la evaluación:

```python
temperature=0.2   # Recomendado para evaluaciones (más consistente)
temperature=0.5   # Más variación entre ejecuciones
```
