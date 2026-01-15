"""
Launcher para Evaluador de Exámenes Orales
Ejecuta la aplicación Streamlit en una ventana del navegador
"""
import subprocess
import sys
import os
import time
import webbrowser
import socket

def find_free_port():
    """Encuentra un puerto libre"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def main():
    # Obtener el directorio del ejecutable
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    app_path = os.path.join(app_dir, "app.py")
    
    # Verificar que existe app.py
    if not os.path.exists(app_path):
        print(f"Error: No se encontró app.py en {app_dir}")
        input("Presiona Enter para salir...")
        return
    
    port = find_free_port()
    url = f"http://localhost:{port}"
    
    print("=" * 50)
    print("🎓 Evaluador Universal de Exámenes Orales")
    print("=" * 50)
    print(f"\n📍 Iniciando servidor en: {url}")
    print("⏳ Espera unos segundos mientras carga...")
    print("\n💡 Para cerrar, cierra esta ventana o presiona Ctrl+C")
    print("=" * 50)
    
    # Abrir navegador después de un delay
    def open_browser():
        time.sleep(3)
        webbrowser.open(url)
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.start()
    
    # Ejecutar Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            app_path,
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--theme.primaryColor", "#667eea"
        ], cwd=app_dir)
    except KeyboardInterrupt:
        print("\n👋 Cerrando aplicación...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()
