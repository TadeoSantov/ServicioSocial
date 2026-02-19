@echo off
chcp 65001 >nul
echo ============================================
echo   Evaluador Universal de Examenes Orales
echo ============================================
echo.
echo Iniciando aplicacion...
echo La aplicacion se abrira en tu navegador.
echo.
echo Para cerrar, presiona Ctrl+C o cierra esta ventana.
echo ============================================
echo.

streamlit run app.py --server.headless true --browser.gatherUsageStats false

pause
