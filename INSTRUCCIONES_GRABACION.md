# 🎙️ Guía Rápida: Grabación de Audio

## Nueva Funcionalidad Agregada

Ahora la app tiene **dos formas** de proporcionar el audio del examen:

### 📤 Opción 1: Subir Archivo (Como antes)
- Sube archivos MP3, WAV, M4A, OGG, FLAC, WEBM
- Máximo 25MB
- Ideal para audios pregrabados

### 🎙️ Opción 2: Grabar Directamente (NUEVO)
- Graba desde tu navegador sin software adicional
- Usa tu micrófono integrado o externo
- Audio en formato WAV de alta calidad
- Puedes escuchar antes de evaluar

---

## 🚀 Cómo Usar la Grabación

### Paso 1: Instalar la nueva dependencia
```bash
pip install audio-recorder-streamlit
```

O ejecuta el instalador actualizado:
```bash
instalar.bat
```

### Paso 2: Iniciar la app
```bash
streamlit run app.py
```

### Paso 3: Grabar tu examen
1. Ve a la sección **"🎤 Audio del Examen Oral"**
2. Selecciona la pestaña **"🎙️ Grabar Audio"**
3. Haz clic en el **botón del micrófono**
4. El navegador pedirá permiso - haz clic en **"Permitir"**
5. Habla claramente tu respuesta al examen
6. Haz clic nuevamente en el micrófono para **detener**
7. Escucha la grabación para verificar
8. Si no te gusta, haz clic en **"🗑️ Borrar grabación"** y vuelve a grabar

### Paso 4: Evaluar
- Haz clic en **"🚀 Evaluar Examen"**
- La app procesará tu grabación igual que un archivo subido

---

## 🔧 Requisitos Técnicos

### Navegadores Compatibles
- ✅ Google Chrome (recomendado)
- ✅ Microsoft Edge
- ✅ Firefox
- ✅ Safari (macOS)
- ⚠️ Navegadores móviles (funcionalidad limitada)

### Permisos Necesarios
- **Acceso al micrófono**: El navegador solicitará permiso la primera vez
- Si no funciona, verifica en la configuración del navegador que el sitio tiene permiso

### Solución de Problemas

**No aparece el botón de grabar:**
```bash
pip install --upgrade audio-recorder-streamlit
```

**El navegador no pide permiso:**
- Ve a Configuración del navegador → Privacidad → Permisos de sitio
- Permite el acceso al micrófono para `localhost:8501`

**La grabación suena mal:**
- Verifica que tu micrófono esté correctamente conectado
- Habla a 20-30 cm del micrófono
- Evita ruido de fondo

---

## 📊 Comparación de Opciones

| Característica | Subir Archivo | Grabar Directo |
|----------------|---------------|----------------|
| **Velocidad** | Rápido | Instantáneo |
| **Calidad** | Depende del archivo | Alta (44.1kHz) |
| **Edición** | Puedes editar antes | No editable |
| **Conveniencia** | Necesitas grabar aparte | Todo en uno |
| **Formatos** | MP3, WAV, M4A, etc. | WAV |

---

## 💡 Consejos para Mejores Resultados

### Para la Grabación:
1. **Ambiente silencioso**: Graba en un lugar sin ruido
2. **Distancia correcta**: 20-30 cm del micrófono
3. **Habla claro**: Pronuncia bien cada palabra
4. **Velocidad moderada**: No hables ni muy rápido ni muy lento
5. **Verifica antes**: Escucha la grabación antes de evaluar

### Para la Evaluación:
1. **Material completo**: Asegúrate de incluir todo el contenido relevante
2. **Rúbrica clara**: Define criterios específicos y puntos
3. **Limpieza activada**: Deja marcada la opción para eliminar muletillas
4. **Idioma correcto**: Selecciona el idioma del audio

---

## 🔐 Privacidad

- ✅ El audio se procesa localmente en tu navegador
- ✅ Se envía a Groq solo para transcripción
- ✅ No se almacena permanentemente
- ✅ Se elimina automáticamente después de evaluar

---

## 📞 Soporte

Si tienes problemas:
1. Verifica que instalaste `audio-recorder-streamlit`
2. Revisa los permisos del navegador
3. Prueba con otro navegador
4. Consulta el README principal

---

**¡Disfruta de la nueva funcionalidad de grabación! 🎉**
