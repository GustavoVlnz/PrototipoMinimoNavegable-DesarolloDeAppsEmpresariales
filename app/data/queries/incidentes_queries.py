"""
incidentes_queries.py
app/data/queries/incidentes_queries.py

Todas las consultas a la base de datos relacionadas con incidentes.
"""

from datetime import datetime

from sqlalchemy.orm import joinedload

from app.logic import transition_service
from app.data.database import get_session
from app.data.models import Incidente, Asignacion, Solicitud, Conductor


_ESTADO_INCIDENTE_DISPLAY = {
    "Registrado": "Registrado",
    "En_Analisis": "En análisis",
    "En_Gestion": "En gestión",
    "Resuelto": "Resuelto",
    "Cerrado": "Cerrado",
}

_GRAVEDAD_DISPLAY = {
    "Incidente_Menor": "Incidente menor",
    "Falla_Operativa": "Falla operativa",
    "Falla_Critica": "Falla crítica",
}

_ESTADO_ASIGNACION_DISPLAY = {
    "Solicitada": "Solicitada",
    "Pendiente": "Pendiente",
    "Confirmada": "Confirmada",
    "En_Ejecucion": "En ejecución",
    "Con_Incidencia": "Con incidencia",
    "Completada": "Completada",
    "Completada_Con_Incidencia": "Completada con incidencia",
    "Fallida": "Fallida",
    "Fallida_Parcial": "Fallida parcial",
    "Cerrada": "Cerrada",
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _nombre_conductor(asignacion: Asignacion) -> str:
    if asignacion and asignacion.conductor and asignacion.conductor.usuario:
        return asignacion.conductor.usuario.nombre
    return "—"


def _ruta_asignacion(asignacion: Asignacion) -> str:
    if not asignacion or not asignacion.solicitud:
        return "—"

    origen = (
        asignacion.solicitud.sucursal_origen.nombre
        if asignacion.solicitud.sucursal_origen
        else "—"
    )
    destino = (
        asignacion.solicitud.sucursal_destino.nombre
        if asignacion.solicitud.sucursal_destino
        else "—"
    )
    return f"{origen} → {destino}"


def _incidente_a_dict(inc: Incidente) -> dict:
    """Convierte un ORM Incidente a diccionario compatible con la UI."""
    asignacion = inc.asignacion

    return {
        "id": inc.folio(),
        "incidente_id": inc.id,
        "asignacion_id": asignacion.folio() if asignacion else "—",
        "asignacion_db_id": inc.asignacion_id,

        "vehiculo_patente": (
            asignacion.vehiculo.patente
            if asignacion and asignacion.vehiculo
            else "—"
        ),
        "conductor": _nombre_conductor(asignacion),
        "ruta": _ruta_asignacion(asignacion),

        "tipo": _GRAVEDAD_DISPLAY.get(
            inc.clasificacion_gravedad,
            inc.clasificacion_gravedad.replace("_", " "),
        ),
        "tipo_raw": inc.clasificacion_gravedad,

        "gravedad": _GRAVEDAD_DISPLAY.get(
            inc.clasificacion_gravedad,
            inc.clasificacion_gravedad.replace("_", " "),
        ),
        "gravedad_raw": inc.clasificacion_gravedad,

        "descripcion": inc.descripcion_falla or "—",

        "estado": _ESTADO_INCIDENTE_DISPLAY.get(
            inc.estado_incidente,
            inc.estado_incidente.replace("_", " "),
        ),
        "estado_raw": inc.estado_incidente,

        "hora_reporte": (
            inc.fecha_hora_reporte.strftime("%Y-%m-%d %H:%M")
            if inc.fecha_hora_reporte
            else "—"
        ),
        "requiere_asistencia": inc.requiere_asistencia,
        "kilometro_ruta": inc.kilometro_ruta or 0,
        "supervisor": inc.supervisor.nombre if inc.supervisor else "—",
    }


def _asignacion_para_incidente_a_dict(asig: Asignacion) -> dict:
    """Convierte una asignación ORM a datos visibles para reportar incidente."""
    return {
        "id": asig.folio(),
        "asignacion_db_id": asig.id,
        "vehiculo_id": asig.vehiculo_id,
        "vehiculo_patente": asig.vehiculo.patente if asig.vehiculo else "—",
        "conductor_id": asig.conductor_id,
        "conductor": _nombre_conductor(asig),
        "ruta": _ruta_asignacion(asig),
        "prioridad": asig.solicitud.prioridad if asig.solicitud else "—",
        "estado": _ESTADO_ASIGNACION_DISPLAY.get(
            asig.estado_asignacion,
            asig.estado_asignacion.replace("_", " "),
        ),
        "estado_raw": asig.estado_asignacion,
    }


def _query_incidentes_base(session):
    return (
        session.query(Incidente)
        .options(
            joinedload(Incidente.asignacion)
            .joinedload(Asignacion.solicitud)
            .joinedload(Solicitud.sucursal_origen),
            joinedload(Incidente.asignacion)
            .joinedload(Asignacion.solicitud)
            .joinedload(Solicitud.sucursal_destino),
            joinedload(Incidente.asignacion).joinedload(Asignacion.vehiculo),
            joinedload(Incidente.asignacion)
            .joinedload(Asignacion.conductor)
            .joinedload(Conductor.usuario),
            joinedload(Incidente.supervisor),
        )
    )


def _query_asignaciones_base(session):
    return (
        session.query(Asignacion)
        .options(
            joinedload(Asignacion.solicitud).joinedload(Solicitud.sucursal_origen),
            joinedload(Asignacion.solicitud).joinedload(Solicitud.sucursal_destino),
            joinedload(Asignacion.vehiculo),
            joinedload(Asignacion.conductor).joinedload(Conductor.usuario),
        )
    )


# ─── Consultas de lectura ─────────────────────────────────────────────────────

def obtener_todos_incidentes() -> list[dict]:
    """Retorna todos los incidentes de la base de datos."""
    with get_session() as session:
        incidentes = (
            _query_incidentes_base(session)
            .order_by(Incidente.id.desc())
            .all()
        )
        return [_incidente_a_dict(i) for i in incidentes]


def obtener_incidente_por_id(incidente_id: int) -> dict | None:
    """Retorna un incidente específico por su ID."""
    with get_session() as session:
        incidente = (
            _query_incidentes_base(session)
            .filter(Incidente.id == incidente_id)
            .first()
        )
        return _incidente_a_dict(incidente) if incidente else None


def obtener_incidentes_por_estado(estado: str) -> list[dict]:
    """Retorna incidentes filtrados por estado."""
    estado_bd = estado.replace(" ", "_")

    with get_session() as session:
        incidentes = (
            _query_incidentes_base(session)
            .filter(Incidente.estado_incidente == estado_bd)
            .order_by(Incidente.id.desc())
            .all()
        )
        return [_incidente_a_dict(i) for i in incidentes]


def obtener_incidentes_por_asignacion(asignacion_id: int) -> list[dict]:
    """Retorna incidentes de una asignación específica."""
    with get_session() as session:
        incidentes = (
            _query_incidentes_base(session)
            .filter(Incidente.asignacion_id == asignacion_id)
            .order_by(Incidente.id.desc())
            .all()
        )
        return [_incidente_a_dict(i) for i in incidentes]


def obtener_incidentes_por_gravedad(gravedad: str) -> list[dict]:
    """Retorna incidentes filtrados por gravedad."""
    gravedad_bd = gravedad.replace(" ", "_")

    with get_session() as session:
        incidentes = (
            _query_incidentes_base(session)
            .filter(Incidente.clasificacion_gravedad == gravedad_bd)
            .order_by(Incidente.id.desc())
            .all()
        )
        return [_incidente_a_dict(i) for i in incidentes]


def obtener_asignaciones_para_incidente() -> list[dict]:
    """
    Retorna asignaciones que pueden recibir incidentes.

    Regla PMV:
    Solo se reportan incidentes sobre asignaciones activas en ruta o ya
    marcadas con incidencia.
    """
    estados_validos = ["En_Ejecucion", "Con_Incidencia"]

    with get_session() as session:
        asignaciones = (
            _query_asignaciones_base(session)
            .filter(Asignacion.estado_asignacion.in_(estados_validos))
            .order_by(Asignacion.id.desc())
            .all()
        )
        return [_asignacion_para_incidente_a_dict(a) for a in asignaciones]


def obtener_asignacion_para_incidente(asignacion_id: int) -> dict | None:
    """Retorna los datos operativos de una asignación para precargar el formulario."""
    with get_session() as session:
        asignacion = (
            _query_asignaciones_base(session)
            .filter(Asignacion.id == asignacion_id)
            .first()
        )
        return _asignacion_para_incidente_a_dict(asignacion) if asignacion else None


# ─── Operaciones de creación ──────────────────────────────────────────────────

def crear_incidente(
    asignacion_id: int,
    clasificacion_gravedad: str,
    descripcion_falla: str,
    requiere_asistencia: bool = False,
    kilometro_ruta: int | None = None,
) -> bool:
    """
    Crea un nuevo incidente vinculado a una asignación real.

    Importante:
    No recibe vehículo ni conductor desde la UI. Ambos se obtienen por
    relación desde la asignación.
    """
    try:
        with get_session() as session:
            asignacion = (
                session.query(Asignacion)
                .filter(Asignacion.id == asignacion_id)
                .first()
            )

            if not asignacion:
                return False

            if asignacion.estado_asignacion not in ("En_Ejecucion", "Con_Incidencia"):
                return False

            nuevo_incidente = Incidente(
                asignacion_id=asignacion.id,
                clasificacion_gravedad=clasificacion_gravedad,
                descripcion_falla=descripcion_falla.strip(),
                requiere_asistencia=requiere_asistencia,
                kilometro_ruta=kilometro_ruta,
                estado_incidente="Registrado",
                fecha_hora_reporte=datetime.utcnow(),
            )

            session.add(nuevo_incidente)
            if asignacion.estado_asignacion == "En_Ejecucion":
                transition_service.marcar_asignacion_con_incidencia(session, asignacion)
            else:
                session.commit()
        return True

    except Exception as e:
        print(f"Error al crear incidente: {e}")
        return False


# ─── Operaciones de actualización ─────────────────────────────────────────────

def actualizar_estado_incidente(incidente_id: int, nuevo_estado: str) -> bool:
    """
    Actualiza el estado de un incidente.

    Estados válidos:
    Registrado, En_Analisis, En_Gestion, Resuelto, Cerrado
    """
    estado_bd = nuevo_estado.replace(" ", "_")

    try:
        with get_session() as session:
            incidente = (
                session.query(Incidente)
                .filter(Incidente.id == incidente_id)
                .first()
            )

            if not incidente:
                return False

            incidente.estado_incidente = estado_bd
            session.commit()

        return True

    except Exception as e:
        print(f"Error al actualizar estado del incidente: {e}")
        return False


def actualizar_descripcion_incidente(incidente_id: int, nueva_descripcion: str) -> bool:
    """Actualiza la descripción de un incidente."""
    try:
        with get_session() as session:
            incidente = (
                session.query(Incidente)
                .filter(Incidente.id == incidente_id)
                .first()
            )

            if not incidente:
                return False

            incidente.descripcion_falla = nueva_descripcion
            session.commit()

        return True

    except Exception as e:
        print(f"Error al actualizar descripción: {e}")
        return False


def marcar_requerido_asistencia(incidente_id: int, requiere: bool = True) -> bool:
    """Marca si el incidente requiere asistencia."""
    try:
        with get_session() as session:
            incidente = (
                session.query(Incidente)
                .filter(Incidente.id == incidente_id)
                .first()
            )

            if not incidente:
                return False

            incidente.requiere_asistencia = requiere
            session.commit()

        return True

    except Exception as e:
        print(f"Error al marcar asistencia: {e}")
        return False


def asignar_supervisor(incidente_id: int, usuario_id: int) -> bool:
    """Asigna un supervisor/gestor al incidente."""
    try:
        with get_session() as session:
            incidente = (
                session.query(Incidente)
                .filter(Incidente.id == incidente_id)
                .first()
            )

            if not incidente:
                return False
            incidente.gestionado_por = usuario_id
            session.commit()
        return True

    except Exception as e:
        print(f"Error al asignar supervisor: {e}")
        return False