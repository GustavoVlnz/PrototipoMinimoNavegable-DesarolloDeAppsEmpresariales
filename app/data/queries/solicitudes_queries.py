"""
solicitudes_queries.py
app/data/queries/solicitudes_queries.py
"""

from datetime import datetime, date

from sqlalchemy import func
from sqlalchemy.orm import aliased

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

def _cargar_solicitudes(session, estado_bd: str | None = None) -> list[Solicitud]:
    SucOrigen  = aliased(Sucursal)
    SucDestino = aliased(Sucursal)

    q = (
        session.query(Solicitud)
        .join(SucOrigen,  Solicitud.sucursal_origen_id  == SucOrigen.id)
        .join(SucDestino, Solicitud.sucursal_destino_id == SucDestino.id)
        .order_by(Solicitud.fecha_creacion.desc())
    )

    if estado_bd:
        q = q.filter(Solicitud.estado_solicitud == estado_bd)

    solicitudes = q.all()

    for s in solicitudes:
        _ = s.sucursal_origen
        _ = s.sucursal_destino
        _ = s.solicitante

    return solicitudes


# ─── Consultas ────────────────────────────────────────────────────────────────

def obtener_todas(session) -> list[dict]:
    return [_solicitud_a_dict(s) for s in _cargar_solicitudes(session)]


def obtener_por_id(session, solicitud_id: int) -> dict | None:
    sol = session.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not sol:
        return None
    _ = sol.sucursal_origen
    _ = sol.sucursal_destino
    _ = sol.solicitante
    return _solicitud_a_dict(sol)


def filtrar_por_estado(session, estado_display: str) -> list[dict]:
    if estado_display == "Todos":
        return obtener_todas(session)
    return [
        _solicitud_a_dict(s)
        for s in _cargar_solicitudes(session, _estado_raw(estado_display))
    ]


def contar_hoy(session) -> int:
    hoy_inicio = datetime.combine(date.today(), datetime.min.time())
    hoy_fin    = datetime.combine(date.today(), datetime.max.time())
    return (
        session.query(func.count(Solicitud.id))
        .filter(Solicitud.fecha_creacion.between(hoy_inicio, hoy_fin))
        .scalar() or 0
    )


# ─── Mutaciones ───────────────────────────────────────────────────────────────

def crear(
    session,
    origen: str,
    destino: str,
    carga_kg: int,
    prioridad: str,
    creado_por_id: int,
) -> dict | None:
    suc_origen  = session.query(Sucursal).filter(Sucursal.nombre == origen).first()
    suc_destino = session.query(Sucursal).filter(Sucursal.nombre == destino).first()

    if not suc_origen or not suc_destino:
        return None

    nueva = Solicitud(
        sucursal_origen_id=suc_origen.id,
        sucursal_destino_id=suc_destino.id,
        carga_kg=carga_kg,
        prioridad=prioridad,
        estado_solicitud="Creada",
        creado_por=creado_por_id,
        fecha_creacion=datetime.now(),
    )
    session.add(nueva)
    session.commit()
    session.refresh(nueva)

    _ = nueva.sucursal_origen
    _ = nueva.sucursal_destino
    _ = nueva.solicitante

    return _solicitud_a_dict(nueva)


def actualizar_estado(session, solicitud_id: int, nuevo_estado_display: str) -> bool:
    sol = session.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not sol:
        return False
    sol.estado_solicitud = _estado_raw(nuevo_estado_display)
    session.commit()
    return True


def reprogramar(session, solicitud_id: int, nueva_prioridad: str) -> bool:
    sol = session.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not sol:
        return False
    sol.estado_solicitud = "Reprogramada"
    sol.prioridad        = nueva_prioridad
    session.commit()
    return True


def cancelar(session, solicitud_id: int) -> bool:
    return actualizar_estado(session, solicitud_id, "Cancelada")


# ─── Auxiliares para la UI ────────────────────────────────────────────────────

def obtener_sucursales(session) -> list[str]:
    rows = session.query(Sucursal.nombre).order_by(Sucursal.nombre).all()
    return [r.nombre for r in rows]


def obtener_encargados_sucursal(session) -> list[dict]:
    rows = (
        session.query(Usuario.id, Usuario.nombre)
        .filter(
            Usuario.rol    == "Encargado_Sucursal",
            Usuario.activo == True,
        )
        .order_by(Usuario.nombre)
        .all()
    )
    return [{"id": r.id, "nombre": r.nombre} for r in rows]