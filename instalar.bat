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
echo Instalando dependencias...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un problema instalando las dependencias.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Instalacion completada exitosamente!
echo ============================================
echo.
echo Ahora configura tu archivo .env:
echo   1. Copia .env.example a .env
echo   2. Agrega tu GROQ_API_KEY
echo   3. (Opcional) Agrega tu GOOGLE_API_KEY
echo.
echo Luego ejecuta: ejecutar.bat
echo.
pause
