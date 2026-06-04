"""
solicitudes_service.py

"""

from app.data.queries.solicitudes_queries import (
    crear,
    reprogramar,
    cancelar,
    obtener_encargados_sucursal,
)


# Estados en los que una solicitud puede ser modificada
ESTADOS_ACTIVOS = ("Creada", "En evaluación", "Pendiente", "Reprogramada")


# ─── Validaciones ─────────────────────────────────────────────────────────────

def validar_nueva_solicitud(origen: str, destino: str, carga_kg: int) -> str | None:
    if origen == destino:
        return "El origen y el destino no pueden ser la misma sucursal."
    if carga_kg <= 0:
        return "La carga debe ser mayor a 0 kg."
    return None


def validar_encargados_disponibles() -> str | None:
    if not obtener_encargados_sucursal():
        return (
            "No hay encargados de sucursal registrados en el sistema.\n"
            "No es posible crear solicitudes."
        )
    return None


def puede_modificar(estado: str) -> bool:
    return estado in ESTADOS_ACTIVOS


# ─── Acciones ─────────────────────────────────────────────────────────────────

def registrar_solicitud(
    origen: str,
    destino: str,
    carga_kg: int,
    prioridad: str,
    creado_por_id: int,
) -> tuple[dict | None, str | None]:
    error = validar_nueva_solicitud(origen, destino, carga_kg)
    if error:
        return None, error

    resultado = crear(
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


def ejecutar_reprogramar(solicitud_id: int, nueva_prioridad: str) -> str | None:
    if not reprogramar(solicitud_id, nueva_prioridad):
        return "No se pudo reprogramar la solicitud."
    return None


def ejecutar_cancelar(solicitud_id: int) -> str | None:
    if not cancelar(solicitud_id):
        return "No se pudo cancelar la solicitud."
    return None