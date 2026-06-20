"""
mantenimiento_queries.py
app/data/queries/mantenimiento_queries.py
"""

from app.data.models import Mantenimiento, Vehiculo, Usuario
from app.logic import transition_service
from app.logic.transition_service import TransitionError


# ─── Helper ORM → dict ────────────────────────────────────────────────────────

def _mantenimiento_a_dict(m: Mantenimiento) -> dict:
    """Convierte un ORM Mantenimiento a diccionario compatible con la UI."""
    tecnico_nombre = "—"
    if m.tecnico_validador:
        tecnico_nombre = m.tecnico_validador.nombre
    elif m.flota_validador:
        tecnico_nombre = m.flota_validador.nombre

    return {
        "id":               m.folio(),
        "mantenimiento_id": m.id,
        "vehiculo_id":      m.vehiculo_id,
        "vehiculo_patente": m.vehiculo.patente if m.vehiculo else "—",
        "tipo":             m.tipo_mantencion.replace("_", " "),
        "tipo_raw":         m.tipo_mantencion,
        "descripcion":      m.descripcion or "—",
        "prioridad":        m.prioridad,
        "estado":           m.estado.replace("_", " "),
        "estado_raw":       m.estado,
        "generado":         m.fecha_ingreso.strftime("%Y-%m-%d %H:%M") if m.fecha_ingreso else "—",
        "egreso":           m.fecha_egreso_real.strftime("%Y-%m-%d %H:%M") if m.fecha_egreso_real else "—",
        "diagnostico":      m.diagnostico_tecnico or "—",
        "tecnico":          tecnico_nombre,
        "incidente_id":     m.incidente_id,
        "incidente_folio":  m.incidente.folio() if m.incidente else "—",
    }


# ─── Consultas de lectura ─────────────────────────────────────────────────────

def obtener_todos_mantenimientos(session) -> list[dict]:
    ordenes = session.query(Mantenimiento).all()
    return [_mantenimiento_a_dict(m) for m in ordenes]


def obtener_mantenimiento_por_id(session, mantenimiento_id: int) -> dict | None:
    m = session.query(Mantenimiento).filter(
        Mantenimiento.id == mantenimiento_id
    ).first()
    return _mantenimiento_a_dict(m) if m else None


def obtener_mantenimiento_orm_por_id(session, mantenimiento_id: int) -> Mantenimiento | None:
    """
    Igual que obtener_mantenimiento_por_id(), pero retorna el objeto ORM
    en vez de un dict.
    """
    return (
        session.query(Mantenimiento)
        .filter(Mantenimiento.id == mantenimiento_id)
        .first()
    )


def obtener_mantenimientos_por_estado(session, estado: str) -> list[dict]:
    estado_bd = estado.replace(" ", "_")
    ordenes = (
        session.query(Mantenimiento)
        .filter(Mantenimiento.estado == estado_bd)
        .all()
    )
    return [_mantenimiento_a_dict(m) for m in ordenes]


def obtener_mantenimientos_por_vehiculo(session, vehiculo_id: int) -> list[dict]:
    ordenes = (
        session.query(Mantenimiento)
        .filter(Mantenimiento.vehiculo_id == vehiculo_id)
        .all()
    )
    return [_mantenimiento_a_dict(m) for m in ordenes]


def obtener_tecnicos(session) -> list[dict]:
    """Retorna usuarios con rol Tecnico_Mantencion para poblar combos."""
    tecnicos = (
        session.query(Usuario)
        .filter(Usuario.rol == "Tecnico_Mantencion", Usuario.activo == True)
        .all()
    )
    return [{"id": t.id, "nombre": t.nombre} for t in tecnicos]


def obtener_patentes_vehiculos(session) -> list[dict]:
    """Retorna patentes y IDs de todos los vehículos para poblar combos."""
    vehiculos = session.query(Vehiculo).all()
    return [{"id": v.id, "patente": v.patente} for v in vehiculos]


# ─── Operaciones de creación ──────────────────────────────────────────────────

def crear_orden_mantenimiento(
    session,
    vehiculo_id: int,
    tipo_mantencion: str,
    descripcion: str,
    prioridad: str = "Media",
    incidente_id: int | None = None,
) -> tuple[bool, str | None]:
    """
    Crea una nueva orden de mantenimiento (OT) y pasa el vehículo a
    En_Mantencion vía transition_service.abrir_mantenimiento().
    """
    vehiculo = session.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo:
        return False, "El vehículo no existe."

    nueva = Mantenimiento(
        vehiculo_id=vehiculo_id,
        tipo_mantencion=tipo_mantencion,
        descripcion=descripcion,
        prioridad=prioridad,
        estado="Pendiente",
        incidente_id=incidente_id,
    )
    session.add(nueva)
    session.flush()  

    try:
        transition_service.abrir_mantenimiento(session, nueva)
    except TransitionError as e:
        session.rollback()
        return False, str(e)

    return True, None


# ─── Operaciones de actualización ─────────────────────────────────────────────

def avanzar_mantenimiento_orden(session, mantenimiento_id: int, nuevo_estado: str) -> tuple[bool, str | None]:
    """
    Avanza una OT a un estado intermedio (En_Revision, Programada,
    En_Espera_Repuestos). Para pasar a Completada usar completar_orden(),
    que además sincroniza la disponibilidad del vehículo.
    """
    m = session.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
    if not m:
        return False, "La orden de mantenimiento no existe."

    try:
        transition_service.avanzar_mantenimiento(session, m, nuevo_estado.replace(" ", "_"))
    except TransitionError as e:
        return False, str(e)

    return True, None


def completar_orden(session, mantenimiento_id: int, tecnico_id: int | None = None) -> tuple[bool, str | None]:
    """
    Marca la OT como Completada y re-evalúa la disponibilidad del
    vehículo.

    """
    m = session.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
    if not m:
        return False, "La orden de mantenimiento no existe."

    try:
        transition_service.completar_mantenimiento(session, m, tecnico_id)
    except TransitionError as e:
        return False, str(e)

    return True, None


def registrar_diagnostico(session, mantenimiento_id: int, diagnostico: str) -> bool:
    """
    Registra o actualiza el diagnóstico técnico de una OT. No es un
    cambio de estado, así que no pasa por transition_service.
    """
    try:
        m = session.query(Mantenimiento).filter(
            Mantenimiento.id == mantenimiento_id
        ).first()
        if not m:
            return False
        m.diagnostico_tecnico = diagnostico
        session.commit()
        return True
    except Exception as e:
        print(f"Error al registrar diagnóstico: {e}")
        return False