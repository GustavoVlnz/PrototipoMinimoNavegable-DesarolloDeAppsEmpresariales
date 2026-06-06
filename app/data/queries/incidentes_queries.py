"""
incidentes_queries.py
Todas las consultas a la base de datos relacionadas con incidentes.
"""

from datetime import datetime

from app.data.database import get_session
from app.data.models import Incidente, Asignacion


# ─── Helper ORM → dict ────────────────────────────────────────────────────────

def _incidente_a_dict(inc: Incidente) -> dict:
    """Convierte un ORM Incidente a diccionario."""
    asignacion = inc.asignacion
    return {
        "id": inc.folio(),
        "incidente_id": inc.id,
        "asignacion_id": asignacion.folio() if asignacion else "—",
        "asignacion_db_id": inc.asignacion_id,
        "vehiculo_patente": asignacion.vehiculo.patente if asignacion and asignacion.vehiculo else "—",
        "conductor": asignacion.conductor.usuario.nombre if asignacion and asignacion.conductor and asignacion.conductor.usuario else "—",
        "tipo": inc.clasificacion_gravedad.replace("_", " "),
        "tipo_raw": inc.clasificacion_gravedad,
        "gravedad": inc.clasificacion_gravedad.replace("_", " "),
        "gravedad_raw": inc.clasificacion_gravedad,
        "descripcion": inc.descripcion_falla or "—",
        "estado": inc.estado_incidente.replace("_", " "),
        "estado_raw": inc.estado_incidente,
        "hora_reporte": inc.fecha_hora_reporte.strftime("%Y-%m-%d %H:%M") if inc.fecha_hora_reporte else "—",
        "requiere_asistencia": inc.requiere_asistencia,
        "kilometro_ruta": inc.kilometro_ruta or 0,
        "supervisor": None,  # TODO: obtener del campo gestionado_por
    }


# ─── Consultas de lectura ─────────────────────────────────────────────────────

def obtener_todos_incidentes() -> list[dict]:
    """Retorna todos los incidentes de la base de datos."""
    with get_session() as session:
        incidentes = session.query(Incidente).all()
        resultado = [_incidente_a_dict(i) for i in incidentes]
    return resultado


def obtener_incidente_por_id(incidente_id: int) -> dict | None:
    """Retorna un incidente específico por su ID."""
    with get_session() as session:
        incidente = session.query(Incidente).filter(Incidente.id == incidente_id).first()
        if incidente:
            return _incidente_a_dict(incidente)
    return None


def obtener_incidentes_por_estado(estado: str) -> list[dict]:
    """Retorna incidentes filtrados por estado."""
    # Convertir estado display a estado BD (ej: "En gestión" → "En_Gestion")
    estado_bd = estado.replace(" ", "_")
    
    with get_session() as session:
        incidentes = (
            session.query(Incidente)
            .filter(Incidente.estado_incidente == estado_bd)
            .all()
        )
        resultado = [_incidente_a_dict(i) for i in incidentes]
    return resultado


def obtener_incidentes_por_asignacion(asignacion_id: int) -> list[dict]:
    """Retorna incidentes de una asignación específica."""
    with get_session() as session:
        incidentes = (
            session.query(Incidente)
            .filter(Incidente.asignacion_id == asignacion_id)
            .all()
        )
        resultado = [_incidente_a_dict(i) for i in incidentes]
    return resultado


def obtener_incidentes_por_gravedad(gravedad: str) -> list[dict]:
    """Retorna incidentes filtrados por gravedad."""
    gravedad_bd = gravedad.replace(" ", "_")
    
    with get_session() as session:
        incidentes = (
            session.query(Incidente)
            .filter(Incidente.clasificacion_gravedad == gravedad_bd)
            .all()
        )
        resultado = [_incidente_a_dict(i) for i in incidentes]
    return resultado


# ─── Operaciones de creación ──────────────────────────────────────────────────

def crear_incidente(
    asignacion_id: int,
    clasificacion_gravedad: str,
    descripcion_falla: str,
    requiere_asistencia: bool = False,
    kilometro_ruta: int | None = None,
) -> bool:
    """
    Crea un nuevo incidente.
    
    Args:
        asignacion_id: ID de la asignación relacionada
        clasificacion_gravedad: Uno de: "Incidente_Menor", "Falla_Operativa", "Falla_Critica"
        descripcion_falla: Descripción del incidente
        requiere_asistencia: Si requiere asistencia
        kilometro_ruta: Kilómetro donde ocurrió
    
    Returns:
        True si fue exitoso.
    """
    try:
        with get_session() as session:
            nuevo_incidente = Incidente(
                asignacion_id=asignacion_id,
                clasificacion_gravedad=clasificacion_gravedad,
                descripcion_falla=descripcion_falla,
                requiere_asistencia=requiere_asistencia,
                kilometro_ruta=kilometro_ruta,
                estado_incidente="Registrado",
            )
            session.add(nuevo_incidente)
        return True
    except Exception as e:
        print(f"Error al crear incidente: {e}")
        return False


# ─── Operaciones de actualización ─────────────────────────────────────────────

def actualizar_estado_incidente(incidente_id: int, nuevo_estado: str) -> bool:
    """
    Actualiza el estado de un incidente.
    
    Args:
        incidente_id: ID del incidente
        nuevo_estado: Uno de: "Registrado", "En_Analisis", "En_Gestion", "Resuelto", "Cerrado"
    
    Returns:
        True si fue exitoso.
    """
    estado_bd = nuevo_estado.replace(" ", "_")
    
    try:
        with get_session() as session:
            incidente = session.query(Incidente).filter(Incidente.id == incidente_id).first()
            if not incidente:
                return False
            incidente.estado_incidente = estado_bd
        return True
    except Exception as e:
        print(f"Error al actualizar estado del incidente: {e}")
        return False


def actualizar_descripcion_incidente(incidente_id: int, nueva_descripcion: str) -> bool:
    """Actualiza la descripción de un incidente."""
    try:
        with get_session() as session:
            incidente = session.query(Incidente).filter(Incidente.id == incidente_id).first()
            if not incidente:
                return False
            incidente.descripcion_falla = nueva_descripcion
        return True
    except Exception as e:
        print(f"Error al actualizar descripción: {e}")
        return False


def marcar_requerido_asistencia(incidente_id: int, requiere: bool = True) -> bool:
    """Marca si el incidente requiere asistencia."""
    try:
        with get_session() as session:
            incidente = session.query(Incidente).filter(Incidente.id == incidente_id).first()
            if not incidente:
                return False
            incidente.requiere_asistencia = requiere
        return True
    except Exception as e:
        print(f"Error al marcar asistencia: {e}")
        return False


def asignar_supervisor(incidente_id: int, usuario_id: int) -> bool:
    """Asigna un supervisor/gestor al incidente."""
    try:
        with get_session() as session:
            incidente = session.query(Incidente).filter(Incidente.id == incidente_id).first()
            if not incidente:
                return False
            incidente.gestionado_por = usuario_id
        return True
    except Exception as e:
        print(f"Error al asignar supervisor: {e}")
        return False
