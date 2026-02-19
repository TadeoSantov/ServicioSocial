# 🎬 Ejemplos Predefinidos para Pruebas

Esta carpeta contiene temas de ejemplo que puedes cargar automáticamente para probar la aplicación sin tener que escribir material y rúbricas desde cero.

## 📚 Ejemplos Disponibles

### 🎬 Ratatouille (Película de Pixar)

**Tema:** Análisis de la película Ratatouille (2007)
**Nivel:** Secundaria/Preparatoria
**Materia:** Cine/Literatura/Análisis de Medios

**Archivos:**
- `ratatouille_material.txt` - Material de referencia completo sobre la película
- `ratatouille_rubrica.txt` - Rúbrica de evaluación detallada (10 puntos)

**Contenido del Material:**
- Sinopsis completa
- Personajes principales (Remy, Linguini, Colette, Anton Ego, etc.)
- Temas y mensajes (perseguir sueños, prejuicios, identidad)
- Momentos clave de la película
- Datos técnicos y curiosidades
- Análisis del simbolismo

**Criterios de Evaluación:**
1. Trama y Personajes (3 pts)
2. Temas y Mensajes (3 pts)
3. Momentos Clave (2 pts)
4. Detalles Técnicos (2 pts)
5. Bonificaciones por análisis profundo (+1 pt)

**Ideal para probar:**
- ✅ Detección de lectura (si el estudiante lee vs. habla naturalmente)
- ✅ Análisis de comprensión vs. memorización
- ✅ Evaluación de temas no académicos tradicionales
- ✅ Grabación de audio con respuestas propias

---

## 🎤 Cómo Usar los Ejemplos

### Opción 1: Cargar desde la Interfaz

1. Inicia la aplicación: `streamlit run app.py`
2. En la sección "🎬 Ejemplos Predefinidos (Para Pruebas)"
3. Selecciona: **"🎬 Ratatouille (Película)"**
4. El material y la rúbrica se cargarán automáticamente
5. Solo necesitas grabar o subir el audio del estudiante

### Opción 2: Copiar Manualmente

1. Abre `ratatouille_material.txt`
2. Copia todo el contenido
3. Pégalo en el campo "Material de Referencia"
4. Repite con `ratatouille_rubrica.txt` → "Rúbrica de Evaluación"

---

## 💡 Ejemplos de Respuestas para Probar

### Respuesta NATURAL (Habla espontánea):

> "Bueno, Ratatouille es... eh... una película de Pixar del 2007, ¿no? Trata sobre Remy, que es una rata, pero no una rata común, sino que tiene un talento increíble para cocinar. O sea, él sueña con ser chef, lo cual es súper raro porque... pues, las ratas normalmente no cocinan, ¿verdad? 
>
> Entonces, Remy conoce a Linguini, que es un chavo medio torpe que trabaja en el restaurante de Gusteau, y juntos hacen equipo. La cosa es que Remy controla a Linguini jalándole el cabello, como si fuera una marioneta, y así pueden cocinar platos increíbles.
>
> El mensaje principal es 'cualquiera puede cocinar', pero no significa que todos sean buenos cocineros, sino que... mmm... un gran chef puede venir de cualquier lugar, incluso una rata. Y al final, Anton Ego, que es el crítico más temido, prueba el ratatouille y le recuerda a la comida de su mamá, y eso lo cambia completamente."

**Resultado esperado:** ✅ Habla natural detectada (20-30% probabilidad de lectura)

### Respuesta LEYENDO (Texto formal):

> "Ratatouille es una película de animación producida por Pixar Animation Studios y distribuida por Walt Disney Pictures en el año 2007. La trama se centra en Remy, un roedor con habilidades culinarias excepcionales y un sentido del gusto y olfato extraordinarios. A diferencia de su familia, que se conforma con consumir desperdicios, Remy aspira a convertirse en un chef de alta cocina, inspirado por Auguste Gusteau, reconocido cocinero francés fallecido.
>
> Tras separarse de su colonia en París, Remy establece una alianza con Alfredo Linguini, empleado de limpieza del restaurante Gusteau's. Mediante un sistema de control donde Remy manipula los movimientos de Linguini desde debajo de su gorro de chef, logran crear platos extraordinarios que impresionan a la crítica gastronómica.
>
> El mensaje central de la película, expresado mediante la filosofía de Gusteau 'cualquiera puede cocinar', no implica que todas las personas posean talento culinario, sino que un gran artista puede emerger de cualquier origen, independientemente de las limitaciones sociales o biológicas."

**Resultado esperado:** 🚨 Lectura detectada (85-95% probabilidad)

---

## 🧪 Casos de Prueba Sugeridos

### Prueba 1: Comprensión Básica
**Graba diciendo:**
- Quién es Remy y qué quiere
- Quién es Linguini
- Cómo trabajan juntos
- Qué pasa al final

**Calificación esperada:** 6-7/10

### Prueba 2: Análisis Profundo
**Graba explicando:**
- Los temas de la película (prejuicios, identidad)
- El significado del mensaje "cualquiera puede cocinar"
- La transformación de Anton Ego
- Simbolismo de las ratas como outsiders

**Calificación esperada:** 8-10/10

### Prueba 3: Detección de Lectura
**Lee el material textualmente**
- Usa frases exactas del archivo
- Habla sin pausas ni muletillas
- Vocabulario muy formal

**Resultado esperado:** 🚨 Alerta de lectura detectada

---

## 📝 Agregar Más Ejemplos

Para agregar tus propios ejemplos:

1. Crea dos archivos en esta carpeta:
   - `[tema]_material.txt` - Contenido de referencia
   - `[tema]_rubrica.txt` - Criterios de evaluación

2. Edita `app.py` y agrega tu ejemplo al selector:
```python
ejemplo_seleccionado = st.selectbox(
    "Cargar ejemplo:",
    options=[
        "-- Ninguno --", 
        "🎬 Ratatouille (Película)",
        "🆕 Tu Nuevo Tema"  # Agregar aquí
    ]
)
```

3. Agrega el código para cargar tus archivos:
```python
elif ejemplo_seleccionado == "🆕 Tu Nuevo Tema":
    with open("ejemplos/tutema_material.txt", "r", encoding="utf-8") as f:
        st.session_state.material_cargado = f.read()
    with open("ejemplos/tutema_rubrica.txt", "r", encoding="utf-8") as f:
        st.session_state.rubrica_cargada = f.read()
```

---

## 🎯 Próximos Ejemplos Planeados

- [ ] 🧬 Fotosíntesis (Biología)
- [ ] 🔢 Teorema de Pitágoras (Matemáticas)
- [ ] 📜 Revolución Mexicana (Historia)
- [ ] ⚗️ Tabla Periódica (Química)
- [ ] 🎨 El Quijote (Literatura)
- [ ] 🌍 Cambio Climático (Ciencias Ambientales)

---

**¡Contribuye con tus propios ejemplos!** 🚀
