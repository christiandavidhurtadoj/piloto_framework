###
# Nombre: repositorio_datos.py
# Descripción: Módulo con los mecanismos de integración entre el Repositorio de Datos y el piloto de framework
# Autor: Christian David Hurtado Jimenez
###

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
import framework.conexiones.conexion_postgresql as conexion
from uuid import UUID
from datetime import date, datetime
from rich import print, panel
import json
from rich.json import JSON
from dotenv import load_dotenv
from sqlmodel import select
from azure.communication.email import EmailClient
from framework.modelos.repositorio_datos import (
    Parametro,
    Proceso,
    Precedencia,
    LogEjecucion,
    EstadoEjecucion,
    EstadoRegistro,
)

load_dotenv()

class DecodificadorJSON(json.JSONEncoder):
    """
	Decodificador personalizado para trasformar tipos de datos complejos a simples.
    De uso interno para la representación en texto de los datos de los procesos y parámtros
	"""

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        return json.JSONEncoder.default(self, obj)


class piloto_framework:
    """
	Permite la integración de procesos ETL/ELT con el piloto de framework.
    Contiene los mecanismos de integración entre el piloto de framework y el Repositorio de datos 
	"""

    def __init__(self):
        # definición de variables globales para el framework
        self.bd_motor, self.bd_sesion = conexion.conectar()
        self.proceso: Proceso | None = None
        self.proceso_padre: Proceso | None = None
        self.parametros: dict[str, str] = {}
        self.connection_string = os.environ.get("EMAIL_ENDPOINT")
        self.sender = os.environ.get("EMAIL_SENDER")
        self.__DEBUG__ = (
            True if os.environ.get("FW_DEBUG", "FALSE").upper() == "TRUE" else False
        )
        if self.__DEBUG__:
            print(
                panel.Panel(
                    "[italic bold]Enter debug mode...",
                    title="DEBUG",
                    border_style="yellow",
                    expand=True,
                )
            )

    def configurar_proceso(self, id_proceso):
        """
        Crea una representación lógica de un Proceso
        ``id_proceso`` es el identificador único del proceso
        """
        
        try:
            self.proceso = self.bd_sesion.get(Proceso, id_proceso)
            if not self.proceso:
                raise Exception(
                    "Proceso no configurado, ejecute [bold red]configurar_proceso(id_proceso: str)[/bold red]"
                )

            if self.proceso.id_proceso_padre:
                self.proceso_padre = self.bd_sesion.get(
                    Proceso, self.proceso.id_proceso_padre
                )

            hijos_con_error = self.bd_sesion.exec(
                select(Proceso).where(
                    Proceso.id_proceso_padre == self.proceso.id_proceso,
                    Proceso.estado_ultima_ejecucion == EstadoEjecucion.ERROR,
                )
            ).fetchall()

            precedencias_con_error = self.bd_sesion.exec(
                select(Proceso)
                .join(
                    Precedencia,
                    onclause=Proceso.id_proceso == Precedencia.id_proceso_precedente,
                )
                .where(
                    Precedencia.id_proceso == self.proceso.id_proceso,
                    Precedencia.estado_registro == EstadoRegistro.ACTIVO,
                    Proceso.estado_ultima_ejecucion == EstadoEjecucion.ERROR,
                )
            ).fetchall()

            if self.__DEBUG__:
                print(f"Hijos con error: {hijos_con_error}")
                print(f"Precedencias con error: {precedencias_con_error}")

            self.proceso._ejecutar = True
            self.proceso._error_precedencias = False

            if self.proceso.estado_registro == EstadoRegistro.INACTIVO:
                self.proceso._ejecutar = False
            elif len(precedencias_con_error) > 0:
                self.proceso._ejecutar = False
                self.proceso._error_precedencias = True
            elif ( 
                    self.proceso_padre 
                    and (
                            self.proceso_padre.estado_ultima_ejecucion == EstadoEjecucion.ERROR 
                            or len(hijos_con_error) > 0
                    )
                    and self.proceso.estado_ultima_ejecucion == EstadoEjecucion.CORRECTO 
                ):
                self.proceso._ejecutar = False
            else:
                self.proceso._ejecutar = True
        except Exception as error:
            print(
                panel.Panel(
                    str(error),
                    title="Error",
                    border_style="red",
                    expand=False,
                )
            )

    def ver_datos_proceso(self):
        """
        Imprimir en pantalla los datos de un Proceso 
        """

        if not self.proceso:
            print(
                panel.Panel(
                    "Proceso no configurado, ejecute [bold red]configurar_proceso(id_proceso: str)[/bold red]",
                    title="Error",
                    border_style="red",
                    expand=False,
                )
            )
        else:
            proceso_txt = json.dumps(self.proceso.model_dump(), cls=DecodificadorJSON)
            print(
                panel.Panel(
                    JSON(proceso_txt),
                    title="Detalles del proceso",
                    border_style="green",
                    expand=False,
                ),
            )

    def valor_parametro(self, nombre_parametro):
        """
        Retorna el valor del parámetro según está configurado en el Repositorio de datos
        ``nombre_parametro`` nombre del parámetro que contiene el valor requerido
        """

        consulta = select(Parametro).where(
            Parametro.nombre_parametro == nombre_parametro,
            Parametro.estado_registro == EstadoRegistro.ACTIVO,
        )
        parametro = self.bd_sesion.exec(consulta).first()
        if self.__DEBUG__:
            print(parametro)
        return parametro.valor_parametro if parametro else ""

    def configurar_parametros(self, parametros):
        """
        Configura los parámetros requeridos en el listado interno de parámetros del proceso ``self.parametros``
        Incluye un elemento con estructura [parametro:valor] para cada uno de los parámetros a configurar
        ``parametros`` listado de parámetros a configurar
        """

        for parametro in parametros:
            self.parametros[parametro] = self.valor_parametro(parametro)

    def ver_parametros(self):
        """
        Imprimir en pantalla los parámetros configurados en el Proceso
        """

        if len(self.parametros) == 0:
            print(
                panel.Panel(
                    "No hay parámetros configurados, ejecute [bold red]configurar_parametros(parametros: dict\\[str])[/bold red]",
                    title="Error",
                    border_style="red",
                    expand=False,
                )
            )
        else:
            parametros_txt = json.dumps(self.parametros, cls=DecodificadorJSON)
            print(
                panel.Panel(
                    JSON(parametros_txt),
                    title="Parámetros",
                    border_style="green",
                    expand=False,
                ),
            )

    def notificacion_proceso(self, log: LogEjecucion | None):
        """
        Envía una notificación vía correo electrónico al responsable del Proceso
        """

        if not self.proceso:
            print(
                panel.Panel(
                    "Proceso no configurado, ejecute [bold red]configurar_proceso(id_proceso: str)[/bold red]",
                    title="Error",
                    border_style="red",
                    expand=False,
                )
            )
        elif not log:
            print(
                panel.Panel(
                    "Ejecución de proceso no encontrada",
                    title="Error",
                    border_style="red",
                    expand=False,
                )
            )
        else:
            inicio = log.fecha_inicio_ejecucion or datetime.now()
            fin = log.fecha_fin_ejecucion or datetime.now()
            diferencia = fin - inicio
            try:
                client = EmailClient.from_connection_string(self.connection_string)
                message = {
                    "senderAddress": self.sender,
                    "recipients": {"to": [{"address": log.email_responsable_proceso}]},
                    "content": {
                        "subject": "Notificación ejecución de proceso",
                        "plainText": (
                            f"""Notificación de ejecución de proceso registrado en el Piloto de Framework.\r\n\r\n
        Identificador de ejecución: {log.id_ejecucion}\r\n
        Proceso: {log.nombre_proceso}\r\n
        Estado de la ejecución: {log.estado_ejecucion}\r\n
        Inicio de ejecución: {log.fecha_inicio_ejecucion}\r\n
        Fin de ejecución: {log.fecha_fin_ejecucion}\r\n
        Tiempo de ejecución (s): {diferencia.total_seconds()} segundos"""
                        ),
                        "html": f"""
                    <!doctype html>
                    <html>
                    <head>
                        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    </head>
                    <body style="font-family: sans-serif;">
                        <div style="display: block; margin: auto; max-width: 1100px; font-size: 16px">
                        <h1 style="font-size: 20px; font-weight: bold; margin-top: 20px">
                            Notificación de ejecución de proceso registrado en el Framework
                        </h1>
                        <p>
                        <span style="display: block">
                        <span style="font-weight: bold; padding-left:10px">Identificador de ejecución:</span>
                        <span style="padding-left:10px">{log.id_ejecucion}</span>
                        </span>
                        <span style="display: block">
                        <span style="font-weight: bold; padding-left:10px">Nombre:</span>
                        <span style="padding-left:10px">{log.nombre_proceso}</span>
                        </span>
                        <span style="display: block">
                        <span style="font-weight: bold; padding-left:10px">Estado de la ejecución:</span>
                        <span style="padding-left:10px">{log.estado_ejecucion}</span>
                        </span>
                        <span style="display: block">
                        <span style="font-weight: bold; padding-left:10px">Inicio de ejecución:</span>
                        <span style="padding-left:10px">{log.fecha_inicio_ejecucion}</span>
                        </span>
                        <span style="display: block">
                        <span style="font-weight: bold; padding-left:10px">Fin de ejecución:</span>
                        <span style="padding-left:10px">{log.fecha_fin_ejecucion}</span>
                        </span>
                        <span style="display: block">
                        <span style="font-weight: bold; padding-left:10px">Tiempo de ejecución (s):</span>
                        <span style="padding-left:10px">{round(diferencia.total_seconds())} segundos</span>
                        </span>
                        </p>
                        </div>
                    </body>
                    </html>
                    """,
                    },
                }
                poller = client.begin_send(message)
                result = poller.result()
                print(result)
                # print("Message sent: ", result.message_id)
            except Exception as error:
                print(error)
                # raise(error)

    def registro_log(
        self, fecha_inicio_ejecucion, estado, mensaje, registros_procesados
    ):
        """
        Captura y almacena los datos particulares de la ejecución de un Proceso
        """

        if not self.proceso:
            print(
                panel.Panel(
                    "Proceso no configurado, ejecute [bold red]configurar_proceso(id_proceso: str)[/bold red]",
                    title="Error",
                    border_style="red",
                    expand=False,
                )
            )
            return None
        else:
            log = LogEjecucion(
                id_proceso=self.proceso.id_proceso,
                nombre_proceso=self.proceso.nombre_proceso,
                estado_ejecucion=estado,
                mensaje_ejecucion=mensaje,
                fecha_inicio_ejecucion=fecha_inicio_ejecucion,
                fecha_fin_ejecucion=datetime.now(),
                tipo_carga_proceso=self.proceso.tipo_carga_proceso.name,
                fecha_inicio_extraccion=self.proceso.fecha_inicio_extraccion,
                fecha_fin_extraccion=self.proceso.fecha_fin_extraccion,
                email_responsable_proceso=self.proceso.email_responsable_proceso,
                registros_procesados=registros_procesados,
            )
            self.proceso.estado_ultima_ejecucion = log.estado_ejecucion
            self.bd_sesion.add(log)
            self.bd_sesion.add(self.proceso)
            self.bd_sesion.commit()
            self.bd_sesion.refresh(log)
            if self.__DEBUG__:
                print(log)
            log_resumido = {
                "id_ejecucion": log.id_ejecucion,
                "id_proceso": log.id_proceso,
                "fecha_inicio_ejecucion": log.fecha_inicio_ejecucion,
                "fecha_fin_ejecucion": log.fecha_fin_ejecucion,
                "estado": log.estado_ejecucion,
            }
            if log.estado_ejecucion == EstadoEjecucion.CORRECTO:
                color_borde = "green"
            else:
                color_borde = "red"
                log_resumido["mensaje"] = log.mensaje_ejecucion

            log_str = json.dumps(log_resumido, cls=DecodificadorJSON)
            print(
                panel.Panel(
                    JSON(log_str),
                    title="Registro de log",
                    border_style=color_borde,
                    expand=False,
                ),
            )
            self.notificacion_proceso(log)
            return log
