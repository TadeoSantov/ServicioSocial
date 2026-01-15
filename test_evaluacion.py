"""Script de prueba para diagnosticar el motor de evaluación"""
import os
from dotenv import load_dotenv
load_dotenv()

from engine import EvaluadorEngine

# Material de referencia del usuario
material = """La fotosintesis es el proceso biologico mediante el cual las plantas y algas transforman la energia de la luz solar en energia quimica estable en forma de glucosa. Este proceso ocurre exclusivamente dentro de los organelos llamados cloroplastos que contienen clorofila para captar los fotones de luz. La ecuacion general indica que la planta consume seis moleculas de dioxido de carbono y seis moleculas de agua para producir una molecula de glucosa y seis moleculas de oxigeno como residuo. El intercambio de gases se realiza a traves de los estomas que son pequenos poros situados en la superficie de las hojas. Es un error grave confundir los cloroplastos con las mitocondrias o decir que la planta libera agua en lugar de oxigeno.

El proceso se divide en dos etapas principales llamadas fase luminosa y fase oscura. La fase luminosa ocurre en las membranas de los tilaquoides dentro del cloroplasto. En esta etapa la energia solar rompe la molecula de agua en un proceso llamado fotolisis del agua lo que permite liberar oxigeno al ambiente y producir energia quimica llamada ATP y NADPH. La segunda etapa es la fase oscura o ciclo de Calvin que ocurre en el estroma del cloroplasto. Aqui se utiliza la energia fabricada en la fase anterior para fijar el dioxido de carbono y sintetizar la glucosa. Se debe aclarar que la fase oscura es independiente de la luz y no ocurre solamente de noche. El alumno debe diferenciar correctamente entre los estomas de la hoja y el estroma del cloroplasto."""

rubrica = """El modelo de evaluacion debe calificar la respuesta del alumno basandose en los siguientes puntos. Primero debe verificar la precision tecnica buscando que el alumno nombre correctamente los cloroplastos como el lugar del proceso y los tilaquoides y estroma como las ubicaciones de las fases. Segundo debe evaluar el dominio del proceso confirmando que el alumno entienda que el oxigeno proviene del rompimiento del agua y que la glucosa proviene del dioxido de carbono. Tercero debe calificar la claridad evitando el uso de muletillas excesivas.

La IA tiene la instruccion de detectar errores especificos. Si el alumno menciona que el proceso ocurre en las mitocondrias se considera un error critico. Si afirma que la fotolisis rompe el dioxido de carbono en lugar del agua debe ser penalizado. Tambien es un error decir que la fase oscura es exclusiva de la noche o que la planta produce energia pura en lugar de glucosa. El reporte final debe ser una calificacion del 1 al 10 con una lista de los conceptos mencionados correctamente y una explicacion de los errores detectados segun este texto de referencia."""

# Respuesta simulada de un alumno (para prueba)
respuesta_alumno = """La fotosíntesis es cuando las plantas usan la luz del sol para hacer su comida. 
Ocurre en los cloroplastos que tienen clorofila. Hay dos fases: la fase luminosa que ocurre en los tilacoides 
donde se rompe el agua y se produce ATP y NADPH, y también se libera oxígeno. 
La otra fase es el ciclo de Calvin que ocurre en el estroma donde se usa el CO2 para hacer glucosa.
La ecuación es 6CO2 + 6H2O con luz da glucosa y oxígeno."""

print("=" * 60)
print("PRUEBA DE EVALUACIÓN - MOTOR")
print("=" * 60)

# Probar con Groq
print("\n>>> Probando con GROQ (Llama 3.3)...")
try:
    evaluador = EvaluadorEngine(proveedor="groq")
    resultado = evaluador.evaluar_examen(material, rubrica, respuesta_alumno)
    
    if resultado["success"]:
        eval_data = resultado["evaluacion"]
        print(f"\n✅ ÉXITO!")
        print(f"   Calificación: {eval_data.get('calificacion_final', 'N/A')}/10")
        print(f"   Confianza: {eval_data.get('nivel_confianza', 'N/A')}")
        print(f"   Tema: {eval_data.get('tema_detectado', 'N/A')}")
    else:
        print(f"\n❌ ERROR: {resultado.get('error', 'Error desconocido')}")
except Exception as e:
    print(f"\n❌ EXCEPCIÓN: {e}")

print("\n" + "=" * 60)
