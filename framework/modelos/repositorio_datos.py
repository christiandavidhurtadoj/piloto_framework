###
# Nombre: repositorio_datos.py
# Descripción: Módulo para gestionar la representación lógica de las tablas  del Repositorio de Datos
# Autor: Christian David Hurtado Jimenez
###

import os
import uuid
import enum
from dotenv import load_dotenv
from datetime import date, datetime
from pydantic import PrivateAttr
from sqlmodel import Column, SQLModel, Field, Enum

load_dotenv()

class EstadoRegistro(str, enum.Enum):
	"""
	Listado de posibles estados de registro: Activo / Inactivo
	"""
	
	ACTIVO = "Activo"
	INACTIVO = "Inactivo"

class EstadoEjecucion(str, enum.Enum):
	"""
	Listado de posibles estados de ejecución: CORRECTO / ERROR
	"""

	CORRECTO = "Correcto"
	ERROR = "Error"

class TipoCarga(str, enum.Enum):
	"""
	Listado de posibles tipos de carga: Inicial / Incremental
	"""

	INI = "Carga Inicial"
	INC = "Carga Incremental"

class Parametro(SQLModel, table = True):
	"""
	Representación lógica de la tabla ``parametro`` del Repositorio de datos
	"""

	__tablename__ = 'parametro'
	__table_args__ = {'schema': 'configuracion'}
	id_parametro: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
	nombre_parametro: str = Field(max_length=35)
	valor_parametro: str = Field(max_length=100)
	estado_registro: EstadoRegistro = Field(max_length=15,sa_column=Column(Enum(EstadoRegistro)),default=EstadoRegistro.ACTIVO)
	observaciones: str | None = Field(default=None, max_length=500)
	usuario_responsable: str = Field(max_length=50,default=os.environ["PSQL_USUARIO"])
	fecha_creacion: datetime = Field(default_factory=datetime.now)
	fecha_ultima_modificacion: datetime | None = Field(default=None)

class Proceso(SQLModel, table = True):
	"""
	Representación lógica de la tabla ``proceso`` del Repositorio de datos
	"""

	__tablename__ = 'proceso'
	__table_args__ = {'schema': 'configuracion'}
	id_proceso: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
	id_proceso_padre: uuid.UUID | None = Field(default=None, foreign_key='configuracion.proceso.id_proceso')
	nombre_proceso: str = Field(max_length=100)
	descripcion_proceso: str | None = Field(default=None, max_length=300)
	tipo_carga_proceso: TipoCarga = Field(sa_column=Column(Enum(TipoCarga)),default=TipoCarga.INI)
	fecha_inicio_extraccion: date | None = Field(default=None)
	fecha_fin_extraccion: date | None = Field(default=None)
	email_responsable_proceso: str | None = Field(default=None, max_length=50)
	observaciones: str | None = Field(default=None, max_length=500)
	estado_ultima_ejecucion: EstadoEjecucion | None = Field(max_length=15,sa_column=Column(Enum(EstadoEjecucion)))   
	estado_registro: EstadoRegistro = Field(max_length=15,sa_column=Column(Enum(EstadoRegistro)),default=EstadoRegistro.ACTIVO)
	usuario_responsable: str = Field(max_length=50,default=os.environ["PSQL_USUARIO"])
	fecha_creacion: datetime = Field(default_factory=datetime.now)
	fecha_ultima_modificacion: datetime | None = Field(default=None)
	_ejecutar: bool = PrivateAttr(default=True)
	_error_precedencias: bool = PrivateAttr(default=False)
	_marca_ejecucion: bool = PrivateAttr(default=True)
	_proceso_padre: SQLModel | None = PrivateAttr(default=None)


class Precedencia(SQLModel, table=True):
	"""
	Representación lógica de la tabla ``precedencia`` del Repositorio de datos
	"""

	__tablename__ = 'precedencia'
	__table_args__ = {'schema': 'configuracion'}
	id_proceso: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, foreign_key='configuracion.proceso.id_proceso')
	id_proceso_precedente: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, foreign_key='configuracion.proceso.id_proceso')
	estado_registro: EstadoRegistro = Field(max_length=15,sa_column=Column(Enum(EstadoRegistro)),default=EstadoRegistro.ACTIVO)
	fecha_creacion: datetime = Field(default_factory=datetime.now)
	fecha_ultima_modificacion: datetime | None = Field(default=None)


class LogEjecucion(SQLModel, table=True):
	"""
	Representación lógica de la tabla ``log_ejecucion`` del Repositorio de datos
	"""

	__tablename__ = 'log_ejecucion'
	__table_args__ = {'schema': 'ejecucion'}
	id_ejecucion: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
	id_proceso: uuid.UUID = Field(default_factory=uuid.uuid4, foreign_key='configuracion.proceso.id_proceso')
	nombre_proceso: str = Field(max_length=100)
	estado_ejecucion: EstadoEjecucion = Field(max_length=15,sa_column=Column(Enum(EstadoEjecucion)))   
	mensaje_ejecucion: str | None = Field(default=None)
	fecha_inicio_ejecucion: datetime = Field(default_factory=datetime.now)
	fecha_fin_ejecucion: datetime | None = Field(default=None)
	tipo_carga_proceso: str = Field(max_length=20)
	email_responsable_proceso: str | None = Field(default=None, max_length=50)
	fecha_inicio_extraccion: date | None = Field(default=None)
	fecha_fin_extraccion: date | None = Field(default=None)
	usuario_ejecucion: str = Field(max_length=50,default=os.environ["PSQL_USUARIO"])
	registros_procesados: int | None = Field(default=0)
