###
# Nombre: 00_orquestador.py
# Descripción: código que ejecuta las simulaciones de procesos ETL/ELT de forma secuencial e iterativa. 
# Autor: Christian David Hurtado Jimenez
###

import subprocess
import time

iteraciones = 1 #cantidad de iteraciones a ejecutar

ruta_cuaderno_01 = './simulaciones/01. simulación ETL - copia de datos.ipynb'
ruta_cuaderno_02 = './simulaciones/02. simulación ETL - procesamiento bodega de datos.ipynb'
formato_salida = 'html'

# Command to execute the notebook and save the output
comando_jupiter_01 = [
    'jupyter', 'nbconvert', 
    '--to', formato_salida, 
    '--execute', 
    ruta_cuaderno_01
    #'--output', output_path
]

comando_jupiter_02 = [
    'jupyter', 'nbconvert', 
    '--to', formato_salida, 
    '--execute', 
    ruta_cuaderno_02
    #'--output', output_path
]

listado_consecutivos = list(range(iteraciones))
for x in listado_consecutivos:
    try:
        print(f"inicio de iteración {x+1}...")
        subprocess.run(comando_jupiter_01, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Cuaderno '{ruta_cuaderno_01}' ejecutado correctamente.")
        subprocess.run(comando_jupiter_02, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Cuaderno '{ruta_cuaderno_02}' ejecutado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Se ha producido un error en la ejecución: {e}")
    except FileNotFoundError as e:
        print(e)
        print("comandos ``Jupyter`` o ``nbconvert`` no encontrados.")
    finally:
        print(f"pausa de iteración {x+1}...")
        print("--------------------------------------------")
        time.sleep(96)

