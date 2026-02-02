###
# Nombre: conexion_postgresql.py
# Descripción: Módulo para establecer la conexión con el Repositorio de Datos para el piloto de framework
# Autor: Christian David Hurtado Jimenez
###

import os #gestión las variables de entorno del sistema
from dotenv import load_dotenv #gestión de variables de entorno en el entorno virtual
from sqlmodel import Session, create_engine #gestión 


load_dotenv() #leer las variables de entorno con los datos de conexión a PostgreSQL
_PSQL_SERVIDOR = os.environ.get("PSQL_SERVIDOR") #nombre del servidor de PostgreSQL
_PSQL_BASEDATOS = os.environ.get("PSQL_BASEDATOS") #nombre de la base de datos
_PSQL_USUARIO = os.environ.get("PSQL_USUARIO") #nombre de usuario
_PSQL_CLAVE = os.environ.get("PSQL_CLAVE") #contraseña de acceso
_echo = True if os.environ.get("FW_DEBUG", "FALSE").upper() == "TRUE" else False #imprimir en consola las consultas SQL ejecutadas

###
# Función: conectar
# Descripción: establece la conexión al repositorio de datos y retorna la sesión 
# Autor: Christian Hurtado
###
def conectar():
    """
    Retorna un motor y una sesión de sqlalchemy para interactuar con el Repositorio de datos
    """
    motor = None
    sesion = None
    try:
        cadena_conexion = f"postgresql://{_PSQL_USUARIO}:{_PSQL_CLAVE}@{_PSQL_SERVIDOR}/{_PSQL_BASEDATOS}?client_encoding=utf8"
        motor = create_engine(cadena_conexion, echo=_echo)
        sesion = Session(motor)
    except (Exception) as error:
        print(error)
        raise error
    finally:
        return motor, sesion