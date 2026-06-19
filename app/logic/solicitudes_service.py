"""
solicitudes_service.py
app/logic/solicitudes_service.py
"""

from app.data.models import Solicitud
from app.data.queries.solicitudes_queries import (
    crear,
    obtener_encargados_sucursal,
)
from app.logic import transition_service
from app.logic.transition_service import TransitionError


ESTADOS_ACTIVOS = ("Creada", "En_Evaluacion", "Pendiente_Reasignacion", "Reprogramada")


# ─── Validaciones ─────────────────────────────────────────────────────────────

def validar_nueva_solicitud(origen: str, destino: str, carga_kg: int) -> str | None:
    """Retorna un mensaje de error o None si los datos son válidos."""
    if origen == destino:
        return "El origen y el destino no pueden ser la misma sucursal."
    if carga_kg <= 0:
        return "La carga debe ser mayor a 0 kg."
    return None


def validar_encargados_disponibles(session) -> str | None:
    """Retorna un mensaje de error si no hay encargados, o None si los hay."""
    if not obtener_encargados_sucursal(session):
        return (
            "No hay encargados de sucursal registrados en el sistema.\n"
            "No es posible crear solicitudes."
        )
    return None


def puede_modificar(estado_raw: str) -> bool:
    """
    Indica si una solicitud en el estado dado (valor RAW del Enum) puede
    ser editada o cancelada desde este módulo.
    """
    return estado_raw in ESTADOS_ACTIVOS


# ─── Acciones ─────────────────────────────────────────────────────────────────

def registrar_solicitud(
    session,
    origen: str,
    destino: str,
    carga_kg: int,
    prioridad: str,
    creado_por_id: int,
) -> tuple[dict | None, str | None]:
    """
    Valida y crea una nueva solicitud.
    Retorna (resultado_dict, None) en éxito o (None, mensaje_error) en fallo.
    """
    error = validar_nueva_solicitud(origen, destino, carga_kg)
    if error:
        return None, error

    resultado = crear(
        session,
        origen=origen,
        destino=destino,
        carga_kg=carga_kg,
        prioridad=prioridad,
        creado_por_id=creado_por_id,
    )

    if not resultado:
        return None, (
            "No se pudo registrar la solicitud.\n"
            "Verifica que origen y destino sean sucursales válidas."
        )

    return resultado, None


def ejecutar_reprogramar(
    session,
    solicitud_id: int,
    nueva_prioridad: str,
) -> str | None:
    """
    Retorna None si tuvo éxito, o un mensaje de error.

    """
    sol = session.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not sol:
        return "No se encontró la solicitud."

    try:
        transition_service.reprogramar_solicitud(session, sol, nueva_prioridad)
    except TransitionError as e:
        return str(e)

    return None


def ejecutar_cancelar(
    session,
    solicitud_id: int,
) -> str | None:
    """Retorna None si tuvo éxito, o un mensaje de error."""
    sol = session.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not sol:
        return "No se encontró la solicitud."

    try:
        transition_service.cancelar_solicitud(session, sol)
    except TransitionError as e:
        return str(e)

    return None