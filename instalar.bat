@echo off
chcp 65001 >nul
echo ============================================
echo   Instalador - Evaluador de Examenes Orales
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado.
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.
echo [1/3] Instalando dependencias...
echo.

pip install -r requirements.txt
pip install pyaudio

if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un problema instalando las dependencias.
    pause
    exit /b 1
)

echo.
echo [2/3] Verificando archivo .env...
if not exist .env (
    echo Creando archivo .env desde plantilla...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edita el archivo .env y agrega tu GROQ_API_KEY
    echo Obten tu key en: https://console.groq.com/
)

echo.
echo [3/3] Instalacion completada!
echo ============================================
echo   Instalacion completada exitosamente!
echo ============================================
echo.
echo NUEVA FUNCIONALIDAD: Ahora puedes grabar audio directamente!
echo.
echo Ahora configura tu archivo .env:
echo   1. Copia .env.example a .env
echo   2. Agrega tu GROQ_API_KEY
echo   3. (Opcional) Agrega tu GOOGLE_API_KEY
echo.
echo Luego ejecuta: ejecutar.bat
echo.
pause
