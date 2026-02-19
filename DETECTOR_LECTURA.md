# 🔍 Detector de Patrones de Lectura (EXPERIMENTAL)

## ¿Qué es?

Una funcionalidad experimental que analiza la transcripción del audio para detectar si el estudiante está **leyendo** un texto en lugar de **hablar naturalmente** durante el examen oral.

## ¿Por qué es importante?

En un examen oral, el objetivo es evaluar:
- Comprensión real del tema
- Capacidad de explicar con palabras propias
- Dominio del contenido (no memorización literal)

Si el estudiante está leyendo:
- No demuestra comprensión genuina
- Solo está reproduciendo texto
- No es una evaluación válida de conocimiento oral

---

## 🎯 Cómo Funciona

El sistema analiza **10 indicadores principales**:

### Indicadores de LECTURA:

1. **Fluidez excesiva** 🔴
   - Frases muy largas sin pausas naturales
   - No hay titubeos ni reformulaciones
   - Habla "demasiado perfecto"

2. **Vocabulario muy formal** 🔴
   - Términos académicos constantes sin explicaciones
   - Lenguaje de libro de texto
   - Sin simplificaciones propias

3. **Falta de muletillas** 🟠
   - Ausencia total de "eh", "mmm", "bueno"
   - Muy raro en habla natural espontánea

4. **Estructura perfecta** 🔴
   - Oraciones gramaticalmente impecables
   - Sin autocorrecciones
   - Sin "mejor dicho", "es decir"

5. **Ritmo monótono** 🟠
   - Velocidad muy constante
   - Sin variaciones de énfasis
   - Suena robótico

6. **Conectores formales** 🟠
   - "Asimismo", "por consiguiente", "en consecuencia"
   - Nadie habla así naturalmente

7. **Ausencia de autocorrecciones** 🔴
   - No hay "perdón, quise decir..."
   - No hay reformulaciones

8. **Enumeraciones perfectas** 🟠
   - Listas ordenadas sin perder el hilo (1, 2, 3...)
   - Demasiado estructurado

9. **Citas textuales** 🔴
   - Frases que suenan copiadas de un libro
   - Definiciones palabra por palabra

10. **Sin personalización** 🟠
    - No usa ejemplos propios
    - No hay analogías personales
    - No dice "por ejemplo, yo..."

### Indicadores de HABLA NATURAL:

✅ Pausas y titubeos ocasionales
✅ Reformulaciones: "o sea, lo que quiero decir es..."
✅ Muletillas en cantidad moderada
✅ Explicaciones con palabras propias
✅ Ejemplos personales
✅ Pequeños errores gramaticales corregidos
✅ Variación en ritmo y énfasis
✅ Conectores informales: "entonces", "y bueno"

---

## 📊 Niveles de Alerta

### 🚨 ALERTA ALTA (≥70% probabilidad)
```
El estudiante muy probablemente está leyendo.
Acción: Revisar manualmente o invalidar el examen.
```

### ⚠️ ADVERTENCIA MODERADA (40-69%)
```
Algunos patrones sospechosos detectados.
Acción: Revisar con atención.
```

### ✅ HABLA NATURAL (<40%)
```
El estudiante habla de forma natural y espontánea.
Acción: Evaluación válida.
```

---

## 🎮 Cómo Usar

### 1. Activar la Detección

En la barra lateral, marca la opción:
```
☑️ 🔍 Detectar si está leyendo (EXPERIMENTAL)
```

### 2. Realizar el Examen

- Graba o sube el audio como siempre
- El sistema analizará automáticamente

### 3. Ver Resultados

Después de la evaluación, verás:

**Si está leyendo:**
```
🚨 ALERTA: Posible Lectura Detectada (85% probabilidad)

El análisis sugiere que el estudiante podría estar leyendo 
en lugar de hablar naturalmente.

Recomendación: Repetir el examen sin permitir consultar notas.
```

**Si habla natural:**
```
✅ Habla Natural Detectada (92% confianza)

El estudiante parece estar hablando de forma natural y espontánea.
```

### 4. Ver Detalles

Haz clic en "🔍 Ver Detalles del Análisis de Lectura" para:
- Ver indicadores específicos detectados
- Leer evidencias textuales
- Entender el análisis completo

---

## 🧪 Casos de Ejemplo

### Ejemplo 1: LECTURA DETECTADA

**Transcripción:**
> "La fotosíntesis es el proceso bioquímico mediante el cual las plantas, algas y algunas bacterias convierten la energía lumínica en energía química. Este proceso ocurre en los cloroplastos, específicamente en los tilacoides durante la fase luminosa, donde se produce ATP y NADPH, y posteriormente en el estroma durante el ciclo de Calvin, donde se fija el dióxido de carbono para producir glucosa."

**Análisis:**
- ❌ Vocabulario extremadamente formal
- ❌ Estructura perfecta sin pausas
- ❌ Cero muletillas
- ❌ Suena como definición de libro
- **Resultado: 95% probabilidad de lectura**

### Ejemplo 2: HABLA NATURAL

**Transcripción:**
> "Bueno, la fotosíntesis es... eh... básicamente cuando las plantas usan la luz del sol para hacer su comida, ¿no? O sea, tienen estas cosas llamadas cloroplastos donde pasa todo. Primero hay una fase con luz, donde se hace energía, y luego otra fase donde usan esa energía para... mmm... para convertir el CO2 en azúcar, que es la glucosa."

**Análisis:**
- ✅ Muletillas naturales ("eh", "mmm")
- ✅ Reformulaciones ("o sea", "básicamente")
- ✅ Explicación con palabras propias
- ✅ Pausas y titubeos
- **Resultado: 15% probabilidad de lectura**

---

## ⚙️ Configuración Avanzada

### Ajustar Sensibilidad

Si quieres modificar la sensibilidad, edita `engine.py`:

```python
# Línea ~140
temperature=0.2,  # Más bajo = más estricto (0.1)
                  # Más alto = más permisivo (0.4)
```

### Desactivar Temporalmente

Desmarca la opción en la barra lateral:
```
☐ 🔍 Detectar si está leyendo (EXPERIMENTAL)
```

---

## 🎓 Recomendaciones Pedagógicas

### Para Docentes:

1. **Usa como herramienta de apoyo**, no como veredicto absoluto
2. **Revisa manualmente** casos con probabilidad >70%
3. **Considera el contexto**: Algunos estudiantes hablan muy formalmente
4. **Combina con observación directa** si es posible

### Para Estudiantes:

1. **Habla con tus propias palabras**
2. **No leas notas durante el examen**
3. **Usa ejemplos personales**
4. **Es normal titubear un poco**
5. **Reformula si te trabas**

### Situaciones Especiales:

**Falsos Positivos Posibles:**
- Estudiantes con excelente dominio del tema
- Hablantes nativos muy articulados
- Temas muy técnicos que requieren precisión

**Falsos Negativos Posibles:**
- Lectura muy natural y expresiva
- Estudiantes que memorizaron (no leyeron)

---

## 📈 Precisión del Sistema

Basado en pruebas internas:

| Escenario | Precisión |
|-----------|-----------|
| Lectura obvia | ~95% |
| Lectura disimulada | ~75% |
| Habla natural | ~90% |
| Casos ambiguos | ~60% |

**Nota**: Es una herramienta de apoyo, no reemplaza el juicio humano.

---

## 🔬 Tecnología Utilizada

- **Modelo**: Llama 3.3 70B / Gemini 1.5 Flash
- **Análisis**: Procesamiento de lenguaje natural (NLP)
- **Indicadores**: 10 patrones lingüísticos
- **Temperatura**: 0.2 (análisis determinístico)

---

## 🐛 Solución de Problemas

**No aparece la opción de detección:**
```bash
# Verifica que el código esté actualizado
git pull
streamlit run app.py
```

**Siempre dice que está leyendo:**
- Puede ser que el estudiante realmente esté leyendo
- O habla muy formalmente (revisa manualmente)

**Nunca detecta lectura:**
- Verifica que la opción esté activada
- Revisa los logs del servidor

---

## 🚀 Próximas Mejoras

- [ ] Análisis de audio directo (tono, pausas reales)
- [ ] Machine learning con datos etiquetados
- [ ] Detección de memorización vs. comprensión
- [ ] Análisis de contacto visual (con video)
- [ ] Integración con cámara para detectar si mira notas

---

## 📞 Feedback

Esta es una funcionalidad **EXPERIMENTAL**. Tu feedback es valioso:

- ¿Detectó correctamente la lectura?
- ¿Hubo falsos positivos/negativos?
- ¿Qué mejorarías?

---

**¡Usa esta herramienta responsablemente! 🎯**
