drop table if exists configuracion.parametro;
create table configuracion.parametro (
    id_parametro uuid NOT NULL,
    nombre_parametro varchar(35) not null,
    valor_parametro varchar(100) not null,
    estado_registro varchar(15) not null,
    observaciones varchar(500),
    usuario_responsable varchar(50) not null,
    fecha_creacion timestamp not null,
    fecha_ultima_modificacion timestamp,
    constraint parametro_pkey primary key ( id_parametro )
)
;

drop table if exists configuracion.proceso;
create table configuracion.proceso (
	id_proceso uuid NOT NULL,
	id_proceso_padre uuid,
	nombre_proceso varchar(100) not null,
	descripcion_proceso varchar(300),
	tipo_carga_proceso varchar(20) not null,
	fecha_inicio_extraccion date,
	fecha_fin_extraccion date,
	email_responsable_proceso varchar(50),
	observaciones varchar(500),
	estado_registro varchar(15) not null,
	usuario_responsable varchar(50) not null,
	fecha_creacion timestamp not null,
	fecha_ultima_modificacion timestamp,
	constraint proceso_pkey primary key ( id_proceso )
)
;

drop table if exists configuracion.precedencia;
create table configuracion.precedencia(
    id_proceso uuid NOT NULL,
    id_proceso_precedente uuid NOT NULL,
	estado_registro varchar(15) NOT NULL,
    fecha_creacion timestamp not null,
    fecha_ultima_modificacion timestamp
)
;

drop table if exists ejecucion.log_ejecucion;
create table ejecucion.log_ejecucion (
    id_ejecucion uuid NOT NULL,
    id_proceso uuid NOT NULL,
    nombre_proceso varchar(100) not null,
    estado_ejecucion varchar(15) not null,
    mensaje_ejecucion varchar(500),
    fecha_inicio_ejecucion timestamp not null,
    fecha_fin_ejecucion timestamp,
    tipo_carga_proceso varchar(20) not null,
    email_responsable_proceso varchar(50),
	fecha_inicio_extraccion date,
	fecha_fin_extraccion date,
    usuario_ejecucion varchar(50) not null,
	registros_procesados integer,
    constraint log_ejecucion_pkey primary key ( id_ejecucion )
)
;

alter table configuracion.proceso
add constraint fk_proceso_proceso_padre
	foreign key ( id_proceso_padre )
	references configuracion.proceso ( id_proceso )
;

alter table configuracion.precedencia
add constraint fk_proceso_proceso
	foreign key ( id_proceso )
	references configuracion.proceso ( id_proceso )
;

alter table configuracion.precedencia
add constraint fk_proceso_proceso_precedente
	foreign key ( id_proceso_precedente )
	references configuracion.proceso ( id_proceso )
;

alter table ejecucion.log_ejecucion
add constraint fk_proceso
	foreign key ( id_proceso )
	references configuracion.proceso ( id_proceso )
;
