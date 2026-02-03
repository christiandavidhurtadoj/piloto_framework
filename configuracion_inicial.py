from sqlalchemy import text
from sqlmodel import SQLModel, delete
from framework.modelos.repositorio_datos import Parametro, Proceso, Precedencia, LogEjecucion, TipoCarga
import framework.conexiones.conexion_postgresql as conexion

def create_db_and_tables():
    motor, sesion = conexion.conectar()
    SQLModel.metadata.create_all(motor)
    sesion.exec(text("DELETE FROM ejecucion.log_ejecucion_copia"))
    sesion.exec(text("INSERT INTO ejecucion.log_ejecucion_copia SELECT * FROM ejecucion.log_ejecucion"))
    sesion.exec(delete(Parametro))
    sesion.exec(delete(LogEjecucion))
    sesion.exec(delete(Precedencia))
    sesion.exec(delete(Proceso))
    sesion.commit()

    parametro_1 = Parametro(
        nombre_parametro="tabla_destino_p1",
        valor_parametro="simulacion.procesos_judiciales_colombia",
        observaciones="tabla destino para la ejecuión del proceso #1 de ejemplo",
    )
    parametro_2 = Parametro(
        nombre_parametro="limite_fuente_p1",
        valor_parametro="15365",
        observaciones="límite de lectura de registros desde la fuente",
    )
    parametro_3 = Parametro(
        nombre_parametro="url_fuente_p1",
        valor_parametro="www.datos.gov.co",
        observaciones="url de acceso al portal de datos abiertos de Colombia",
    )
    parametro_4 = Parametro(
        nombre_parametro="id_fuente_p1",
        valor_parametro="52tq-ag6c",
        observaciones="identificador de la fuente en el portal de datos abiertos de Colombia",
    )
    ##
    parametro_5 = Parametro(
        nombre_parametro="tabla_destino_dim_entidad_pub",
        valor_parametro="simulacion.dim_entidad_publica",
        observaciones="tabla destino para la dimensión Entidad Pública",
    )
    parametro_6 = Parametro(
        nombre_parametro="tabla_destino_dim_entidad_sec",
        valor_parametro="simulacion.dim_entidad_seccional",
        observaciones="tabla destino para la dimensión Entidad Seccional",
    )
    parametro_7 = Parametro(
        nombre_parametro="tabla_destino_dim_departamento",
        valor_parametro="simulacion.dim_departamento",
        observaciones="tabla destino para la dimensión Departamento",
    )
    parametro_8 = Parametro(
        nombre_parametro="tabla_destino_hechos_procjud_det",
        valor_parametro="simulacion.fact_proceso_judicial_detalle",
        observaciones="tabla destino para la tabla de hechos Proceso Judicial Detallado",
    )
    parametro_9 = Parametro(
        nombre_parametro="tabla_destino_hechos_procjud_res",
        valor_parametro="simulacion.fact_proceso_judicial_resumen",
        observaciones="tabla destino para la tabla de hechos Proceso Judicial Resumido",
    )

    sesion.add(parametro_1)
    sesion.add(parametro_2)
    sesion.add(parametro_3)
    sesion.add(parametro_4)
    sesion.add(parametro_5)
    sesion.add(parametro_6)
    sesion.add(parametro_7)
    sesion.add(parametro_8)
    sesion.add(parametro_9)

    proceso_1 = Proceso(
        id_proceso="3ed3ccc9-7651-44df-b0c2-5fd19446abbf",
        nombre_proceso="proceso de prueba #11000",
        descripcion_proceso="proceso de ejemplo para la ejecución general del FW",
        email_responsable_proceso="sirghoro@gmail.com",
        tipo_carga_proceso=TipoCarga.INI,
    )
    proceso_2 = Proceso(
        id_proceso="a0b51bd8-ad38-4cf1-b587-eb2ac1d9cf34",
        nombre_proceso="Descargar datos procesos judiciales",
        descripcion_proceso="Proceso que descarga los procesos judiciales de Colombia desde el portal de Datos Abiertos de Colombia y los carga en una tabla destino",
        email_responsable_proceso="sirghoro@gmail.com",
        tipo_carga_proceso=TipoCarga.INC,
    )
    proceso_3 = Proceso(
        id_proceso="e3153df7-92ff-448a-ac5b-61031adfa4f3",
        nombre_proceso="Procesar bodega de datos",
        descripcion_proceso="Proceso que gestiona una bodega de datos a partir de la información de los procesos judiciales de Colombia",
        email_responsable_proceso="sirghoro@gmail.com",
        tipo_carga_proceso=TipoCarga.INI,
    )
    proceso_4 = Proceso(
        id_proceso="317d33d8-025f-4eb1-baea-097873cc306d",
        nombre_proceso="Procesar dimensión Entidad Pública",
        descripcion_proceso="Proceso que gestiona la dimensión Entidad Pública de Colombia",
        email_responsable_proceso="sirghoro@gmail.com",
        tipo_carga_proceso=TipoCarga.INI,
        id_proceso_padre=proceso_3.id_proceso,
    )
    proceso_5 = Proceso(
        id_proceso="57a54413-72e6-4a9e-bcb7-61044f447401",
        nombre_proceso="Procesar dimensión Entidad Seccional",
        descripcion_proceso="Proceso que gestiona la dimensión Entidad Seccional de Colombia",
        email_responsable_proceso="sirghoro@gmail.com",
        tipo_carga_proceso=TipoCarga.INI,
        id_proceso_padre=proceso_3.id_proceso,
    )
    proceso_6 = Proceso(
        id_proceso="83669434-13d7-40e3-92e3-fd67e24718e1",
        nombre_proceso="Procesar dimensión Departamento",
        descripcion_proceso="Proceso que gestiona la dimensión Departamento de Colombia",
        email_responsable_proceso="sirghoro@gmail.com",
        tipo_carga_proceso=TipoCarga.INI,
        id_proceso_padre=proceso_3.id_proceso,
    )
    proceso_7 = Proceso(
        id_proceso="782045a8-59f1-4411-9a7c-145eeefb6d2d",
        nombre_proceso="Procesar hechos Proceso Judicial Detallado",
        descripcion_proceso="Proceso que gestiona la tabla de hechos Proceso Judicial Detallado",
        email_responsable_proceso="sirghoro@gmail.com",
        tipo_carga_proceso=TipoCarga.INC,
        id_proceso_padre=proceso_3.id_proceso,
    )
    proceso_8 = Proceso(
        id_proceso="e72b69f0-d128-440a-ad97-03616d9b85c6",
        nombre_proceso="Procesar hechos Proceso Judicial Resumido",
        descripcion_proceso="Proceso que gestiona la tabla de hechos Proceso Judicial Resumido",
        email_responsable_proceso="sirghoro@gmail.com",
        tipo_carga_proceso=TipoCarga.INC,
        id_proceso_padre=proceso_3.id_proceso,
    )
    
    sesion.add(proceso_1)
    sesion.add(proceso_2)
    sesion.add(proceso_3)
    sesion.add(proceso_4)
    sesion.add(proceso_5)
    sesion.add(proceso_6)
    sesion.add(proceso_7)
    sesion.add(proceso_8)
    sesion.commit()
    
    #precedencia_1 = Precedencia(
    #    id_proceso=proceso_3.id_proceso,
    #    id_proceso_precedente=proceso_2.id_proceso,
    #)
    precedencia_2 = Precedencia(
        id_proceso=proceso_7.id_proceso,
        id_proceso_precedente=proceso_4.id_proceso,
    )
    precedencia_3 = Precedencia(
        id_proceso=proceso_7.id_proceso,
        id_proceso_precedente=proceso_5.id_proceso,
    )
    precedencia_4 = Precedencia(
        id_proceso=proceso_7.id_proceso,
        id_proceso_precedente=proceso_6.id_proceso,
    )
    precedencia_5 = Precedencia(
        id_proceso=proceso_8.id_proceso,
        id_proceso_precedente=proceso_7.id_proceso
    )
    #sesion.add(precedencia_1)
    sesion.add(precedencia_2)
    sesion.add(precedencia_3)
    sesion.add(precedencia_4)
    sesion.add(precedencia_5)
    sesion.commit()

    sesion.exec(text("INSERT INTO ejecucion.log_ejecucion SELECT * FROM ejecucion.log_ejecucion_copia"))
    sesion.commit()

create_db_and_tables()
