"""
Script para crear el ejecutable del Evaluador de Exámenes Orales
"""
import PyInstaller.__main__
import os
import shutil

app_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(app_dir, "dist", "EvaluadorExamenesOrales")

print("🔨 Construyendo ejecutable...")

PyInstaller.__main__.run([
    'launcher.py',
    '--name=EvaluadorExamenesOrales',
    '--onedir',
    '--console',
    '--icon=NONE',
    '--add-data=app.py;.',
    '--add-data=engine.py;.',
    '--add-data=.env.example;.',
    '--hidden-import=streamlit',
    '--hidden-import=groq',
    '--hidden-import=google.generativeai',
    '--collect-all=streamlit',
    '--collect-all=altair',
    '--noconfirm',
])

print(f"\n✅ Ejecutable creado en: {dist_dir}")
print("\n📦 Para distribuir, copia toda la carpeta 'EvaluadorExamenesOrales'")
