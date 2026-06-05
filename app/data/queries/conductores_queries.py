"""
conductores_queries.py
Todas las consultas a la base de datos relacionadas con conductores.
"""

from datetime import datetime

from app.data.database import get_session
from app.data.models import Conductor, Usuario


# ─── Helper ORM → dict ────────────────────────────────────────────────────────

def _conductor_a_dict(conductor: Conductor) -> dict:
    """Convierte un ORM Conductor a diccionario."""
    usuario = conductor.usuario
    return {
        "id": conductor.id,
        "nombre": usuario.nombre if usuario else "—",
        "rut": usuario.rut if usuario else "—",
        "tipo_licencia": conductor.tipo_licencia,
        "licencia_vence": conductor.licencia_vence or "—",
        "habilitado": conductor.habilitado,
        "estado": conductor.estado_disponibilidad.replace("_", " "),
        "sucursal": usuario.sucursal.nombre if usuario and usuario.sucursal else "—",
        "asignacion_activa": None,  # TODO: Calcular de asignaciones activas si es necesario
        "usuario_id": conductor.usuario_id,
        "conductor_id": conductor.id,
    }


# ─── Consultas de lectura ─────────────────────────────────────────────────────

def obtener_todos_conductores() -> list[dict]:
    """Retorna todos los conductores de la base de datos."""
    with get_session() as session:
        conductores = session.query(Conductor).all()
        # Forzar carga de relaciones dentro de la sesión activa
        resultado = [_conductor_a_dict(c) for c in conductores]
    return resultado


def obtener_conductor_por_id(conductor_id: int) -> dict | None:
    """Retorna un conductor específico por su ID."""
    with get_session() as session:
        conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
        if conductor:
            return _conductor_a_dict(conductor)
    return None


def obtener_conductores_por_estado(estado: str) -> list[dict]:
    """Retorna conductores filtrados por estado de disponibilidad."""
    # Convertir estado display a estado BD (ej: "Disponible" → "Disponible", "En descanso" → "En_Descanso")
    estado_bd = estado.replace(" ", "_")
    
    with get_session() as session:
        conductores = (
            session.query(Conductor)
            .filter(Conductor.estado_disponibilidad == estado_bd)
            .all()
        )
        resultado = [_conductor_a_dict(c) for c in conductores]
    return resultado


# ─── Operaciones de actualización ─────────────────────────────────────────────

def actualizar_estado_conductor(conductor_id: int, nuevo_estado: str) -> bool:
    """
    Actualiza el estado de disponibilidad de un conductor.
    
    Args:
        conductor_id: ID del conductor
        nuevo_estado: Uno de: "Disponible", "Asignado", "No_Habilitado", "En_Descanso"
    
    Returns:
        True si fue exitoso, False en caso contrario.
    """
    # Convertir estado display a estado BD si es necesario
    estado_bd = nuevo_estado.replace(" ", "_")
    
    try:
        with get_session() as session:
            conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
            if not conductor:
                return False
            conductor.estado_disponibilidad = estado_bd
            # commit automático al salir del context manager
        return True
    except Exception as e:
        print(f"Error al actualizar estado del conductor: {e}")
        return False


def habilitar_conductor(conductor_id: int) -> bool:
    """Habilita un conductor (pone habilitado=True y estado=Disponible)."""
    try:
        with get_session() as session:
            conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
            if not conductor:
                return False
            conductor.habilitado = True
            conductor.estado_disponibilidad = "Disponible"
        return True
    except Exception as e:
        print(f"Error al habilitar conductor: {e}")
        return False


def deshabilitar_conductor(conductor_id: int) -> bool:
    """Deshabilita un conductor (pone habilitado=False y estado=No_Habilitado)."""
    try:
        with get_session() as session:
            conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
            if not conductor:
                return False
            conductor.habilitado = False
            conductor.estado_disponibilidad = "No_Habilitado"
        return True
    except Exception as e:
        print(f"Error al deshabilitar conductor: {e}")
        return False


def actualizar_licencia(conductor_id: int, nueva_fecha_vencimiento: str) -> bool:
    """
    Actualiza la fecha de vencimiento de la licencia.
    
    Args:
        conductor_id: ID del conductor
        nueva_fecha_vencimiento: Formato "YYYY-MM-DD"
    
    Returns:
        True si fue exitoso.
    """
    try:
        with get_session() as session:
            conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
            if not conductor:
                return False
            conductor.licencia_vence = nueva_fecha_vencimiento
        return True
    except Exception as e:
        print(f"Error al actualizar licencia: {e}")
        return False
