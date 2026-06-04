"""
solicitudes_queries.py
Todas las consultas a la base de datos relacionadas con solicitudes de transporte.

"""

from datetime import datetime, date

from sqlalchemy import func
from sqlalchemy.orm import aliased

from app.data.database import get_session
from app.data.models import Solicitud, Sucursal, Usuario


# ─── Mapeo de estados ─────────────────────────────────────────────────────────

_ESTADO_DISPLAY = {
    "Creada":                 "Creada",
    "En_Evaluacion":          "En evaluación",
    "Aprobada":               "Confirmada",
    "Rechazada":              "Rechazada",
    "Pendiente_Reasignacion": "Pendiente",
    "Cancelada":              "Cancelada",
    "Reprogramada":           "Reprogramada",
}

_ESTADO_RAW = {v: k for k, v in _ESTADO_DISPLAY.items()}


def _estado_display(estado_raw: str) -> str:
    return _ESTADO_DISPLAY.get(estado_raw, estado_raw)


def _estado_raw(estado_display: str) -> str:
    return _ESTADO_RAW.get(estado_display, estado_display)


# ─── Helper ORM → dict ────────────────────────────────────────────────────────

def _solicitud_a_dict(sol: Solicitud) -> dict:

    return {
        "id":          sol.folio(),
        "id_numerico": sol.id,
        "origen":      sol.sucursal_origen.nombre  if sol.sucursal_origen  else "—",
        "destino":     sol.sucursal_destino.nombre if sol.sucursal_destino else "—",
        "carga_kg":    sol.carga_kg,
        "prioridad":   sol.prioridad,
        "estado":      _estado_display(sol.estado_solicitud),
        "estado_raw":  sol.estado_solicitud,
        "creada":      sol.fecha_creacion.strftime("%Y-%m-%d %H:%M") if sol.fecha_creacion else "—",
        "solicitante": sol.solicitante.nombre if sol.solicitante else "Sin especificar",
    }


# ─── Query base reutilizable ──────────────────────────────────────────────────

def _cargar_solicitudes(db, estado_bd: str | None = None) -> list[Solicitud]:
    """
    Query base con aliases para los dos joins a la tabla sucursales.
    Fuerza la carga de relaciones dentro de la sesión antes de cerrarla.
    """
    SucOrigen  = aliased(Sucursal)
    SucDestino = aliased(Sucursal)

    q = (
        db.query(Solicitud)
        .join(SucOrigen,  Solicitud.sucursal_origen_id  == SucOrigen.id)
        .join(SucDestino, Solicitud.sucursal_destino_id == SucDestino.id)
        .order_by(Solicitud.fecha_creacion.desc())
    )

    if estado_bd:
        q = q.filter(Solicitud.estado_solicitud == estado_bd)

    solicitudes = q.all()

    # Forzar carga de todas las relaciones dentro de la sesión activa
    for s in solicitudes:
        _ = s.sucursal_origen
        _ = s.sucursal_destino
        _ = s.solicitante

    return solicitudes


# ─── Consultas ────────────────────────────────────────────────────────────────

def obtener_todas() -> list[dict]:
    """Retorna todas las solicitudes ordenadas por fecha descendente."""
    with get_session() as db:
        return [_solicitud_a_dict(s) for s in _cargar_solicitudes(db)]


def obtener_por_id(solicitud_id: int) -> dict | None:
    """
    Busca una solicitud por su ID numérico.
    Retorna el diccionario con todos sus datos o None si no existe.
    """
    with get_session() as db:
        sol = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        if not sol:
            return None
        # Forzar carga de relaciones
        _ = sol.sucursal_origen
        _ = sol.sucursal_destino
        _ = sol.solicitante
        return _solicitud_a_dict(sol)


def filtrar_por_estado(estado_display: str) -> list[dict]:
    """
    Retorna solicitudes que coincidan con el estado del filtro de la UI.
    Pasar "Todos" retorna todas.
    """
    if estado_display == "Todos":
        return obtener_todas()

    with get_session() as db:
        return [_solicitud_a_dict(s)
                for s in _cargar_solicitudes(db, _estado_raw(estado_display))]


def contar_hoy() -> int:
    """
    Cuenta cuántas solicitudes fueron creadas hoy.
    Usado por el TopBar para mostrar 'N solicitudes registradas hoy'.
    """
    hoy_inicio = datetime.combine(date.today(), datetime.min.time())
    hoy_fin    = datetime.combine(date.today(), datetime.max.time())

    with get_session() as db:
        return (
            db.query(func.count(Solicitud.id))
            .filter(Solicitud.fecha_creacion.between(hoy_inicio, hoy_fin))
            .scalar() or 0
        )


# ─── Mutaciones ───────────────────────────────────────────────────────────────

def crear(
    origen: str,
    destino: str,
    carga_kg: int,
    prioridad: str,
    solicitante_nombre: str,
) -> dict | None:
    """
    Crea una nueva solicitud en la base de datos.
    Retorna el diccionario de la solicitud creada, o None si falló.
    """
    with get_session() as db:
        suc_origen  = db.query(Sucursal).filter(Sucursal.nombre == origen).first()
        suc_destino = db.query(Sucursal).filter(Sucursal.nombre == destino).first()

        if not suc_origen or not suc_destino:
            return None

        usuario = db.query(Usuario).filter(Usuario.nombre == solicitante_nombre).first()

        nueva = Solicitud(
            sucursal_origen_id=suc_origen.id,
            sucursal_destino_id=suc_destino.id,
            carga_kg=carga_kg,
            prioridad=prioridad,
            estado_solicitud="Creada",
            creado_por=usuario.id if usuario else None,
            fecha_creacion=datetime.now(),
        )
        db.add(nueva)
        db.flush()

        # Cargar relaciones antes de cerrar la sesión
        _ = nueva.sucursal_origen
        _ = nueva.sucursal_destino
        _ = nueva.solicitante

        return _solicitud_a_dict(nueva)


def actualizar_estado(solicitud_id: int, nuevo_estado_display: str) -> bool:
    """
    Cambia el estado de una solicitud.
    Retorna True si fue exitoso.
    """
    with get_session() as db:
        sol = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        if not sol:
            return False
        sol.estado_solicitud = _estado_raw(nuevo_estado_display)
        return True


def reprogramar(solicitud_id: int, nueva_prioridad: str) -> bool:
    """
    Cambia estado a Reprogramada y actualiza la prioridad en una sola operación.
    Equivale al botón «Reprogramar» del diálogo de detalle.
    """
    with get_session() as db:
        sol = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
        if not sol:
            return False
        sol.estado_solicitud = "Reprogramada"
        sol.prioridad        = nueva_prioridad
        return True


def cancelar(solicitud_id: int) -> bool:
    """Marca la solicitud como Cancelada."""
    return actualizar_estado(solicitud_id, "Cancelada")


# ─── Auxiliares para la UI ────────────────────────────────────────────────────

def obtener_sucursales() -> list[str]:
    """
    Retorna los nombres de todas las sucursales.
    Usado por NuevaSolicitudDialog para poblar los ComboBox de origen/destino.
    """
    with get_session() as db:
        rows = db.query(Sucursal.nombre).order_by(Sucursal.nombre).all()
        return [r.nombre for r in rows]