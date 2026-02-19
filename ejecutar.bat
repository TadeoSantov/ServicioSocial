@echo off
chcp 65001 >nul
echo ============================================
echo   Evaluador de Examenes Orales
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado.
    echo Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar archivo .env
if not exist .env (
    echo [AVISO] No se encontro .env - creando desde plantilla...
    copy .env.example .env >nul
    echo Edita el archivo .env y agrega tu GROQ_API_KEY antes de continuar.
    pause
    exit /b 1
)

REM Instalar dependencias si hace falta
echo [1/2] Verificando dependencias...
pip install -r requirements.txt -q

echo [2/2] Iniciando aplicacion...
echo La aplicacion se abrira en tu navegador automaticamente.
echo Para cerrar, presiona Ctrl+C o cierra esta ventana.
echo ============================================
echo.

python launcher.py

pause
