"""
mantenimiento_queries.py
app/data/queries/mantenimiento_queries.py
"""

from datetime import datetime

from app.data.database import get_session
from app.data.models import Mantenimiento, Vehiculo, Usuario, Incidente


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

def obtener_todos_mantenimientos() -> list[dict]:
    """Retorna todas las órdenes de mantenimiento."""
    with get_session() as session:
        ordenes = session.query(Mantenimiento).all()
        resultado = [_mantenimiento_a_dict(m) for m in ordenes]
    return resultado


def obtener_mantenimiento_por_id(mantenimiento_id: int) -> dict | None:
    """Retorna una orden de mantenimiento por su ID."""
    with get_session() as session:
        m = session.query(Mantenimiento).filter(
            Mantenimiento.id == mantenimiento_id
        ).first()
        if m:
            return _mantenimiento_a_dict(m)
    return None


def obtener_mantenimientos_por_estado(estado: str) -> list[dict]:
    """Retorna órdenes filtradas por estado."""
    estado_bd = estado.replace(" ", "_")
    with get_session() as session:
        ordenes = (
            session.query(Mantenimiento)
            .filter(Mantenimiento.estado == estado_bd)
            .all()
        )
        resultado = [_mantenimiento_a_dict(m) for m in ordenes]
    return resultado


def obtener_mantenimientos_por_vehiculo(vehiculo_id: int) -> list[dict]:
    """Retorna el historial de mantenimiento de un vehículo."""
    with get_session() as session:
        ordenes = (
            session.query(Mantenimiento)
            .filter(Mantenimiento.vehiculo_id == vehiculo_id)
            .all()
        )
        resultado = [_mantenimiento_a_dict(m) for m in ordenes]
    return resultado


def obtener_tecnicos() -> list[dict]:
    """Retorna usuarios con rol Tecnico_Mantencion para poblar combos."""
    with get_session() as session:
        tecnicos = (
            session.query(Usuario)
            .filter(Usuario.rol == "Tecnico_Mantencion", Usuario.activo == True)
            .all()
        )
        return [{"id": t.id, "nombre": t.nombre} for t in tecnicos]


def obtener_patentes_vehiculos() -> list[dict]:
    """Retorna patentes y IDs de todos los vehículos para poblar combos."""
    with get_session() as session:
        vehiculos = session.query(Vehiculo).all()
        return [{"id": v.id, "patente": v.patente} for v in vehiculos]


# ─── Operaciones de creación ──────────────────────────────────────────────────

def crear_orden_mantenimiento(
    vehiculo_id: int,
    tipo_mantencion: str,
    descripcion: str,
    prioridad: str = "Media",
    incidente_id: int | None = None,
) -> bool:
    """
    Crea una nueva orden de mantenimiento (OT).

    Args:
        vehiculo_id:     ID del vehículo a mantener.
        tipo_mantencion: "Preventiva" o "Correctiva".
        descripcion:     Descripción del trabajo a realizar.
        prioridad:       "Alta", "Media" o "Baja".
        incidente_id:    ID del incidente origen (opcional).

    Returns:
        True si fue exitoso.
    """
    try:
        with get_session() as session:
            nueva = Mantenimiento(
                vehiculo_id=vehiculo_id,
                tipo_mantencion=tipo_mantencion,
                descripcion=descripcion,
                prioridad=prioridad,
                estado="Pendiente",
                incidente_id=incidente_id,
            )
            session.add(nueva)

            # Cambiar estado del vehículo a En_Mantencion
            v = session.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
            if v:
                v.estado_operacional = "En_Mantencion"
        return True
    except Exception as e:
        print(f"Error al crear orden de mantenimiento: {e}")
        return False


# ─── Operaciones de actualización ─────────────────────────────────────────────

def actualizar_estado_mantenimiento(mantenimiento_id: int, nuevo_estado: str) -> bool:
    """
    Actualiza el estado de una orden de mantenimiento.

    Args:
        mantenimiento_id: ID de la orden.
        nuevo_estado:     Uno de: "Pendiente", "En_Revision",
                          "En_Espera_Repuestos", "Programada", "Completada".

    Returns:
        True si fue exitoso.
    """
    estado_bd = nuevo_estado.replace(" ", "_")
    try:
        with get_session() as session:
            m = session.query(Mantenimiento).filter(
                Mantenimiento.id == mantenimiento_id
            ).first()
            if not m:
                return False
            m.estado = estado_bd
            if estado_bd == "Completada":
                m.fecha_egreso_real = datetime.utcnow()
        return True
    except Exception as e:
        print(f"Error al actualizar estado de mantenimiento: {e}")
        return False


def habilitar_vehiculo(mantenimiento_id: int, tecnico_id: int | None = None) -> bool:
    """
    Marca la OT como Completada y devuelve el vehículo a estado Disponible.
    Opcionalmente registra el técnico validador.

    Args:
        mantenimiento_id: ID de la orden de mantenimiento.
        tecnico_id:       ID del usuario técnico que valida (opcional).

    Returns:
        True si fue exitoso.
    """
    try:
        with get_session() as session:
            m = session.query(Mantenimiento).filter(
                Mantenimiento.id == mantenimiento_id
            ).first()
            if not m:
                return False

            m.estado = "Completada"
            m.fecha_egreso_real = datetime.utcnow()
            if tecnico_id:
                m.validado_por_tecnico = tecnico_id

            # Devolver vehículo a Disponible y registrar última mantención
            v = session.query(Vehiculo).filter(
                Vehiculo.id == m.vehiculo_id
            ).first()
            if v:
                v.estado_operacional = "Disponible"
                v.ultima_mantencion = datetime.utcnow().strftime("%Y-%m-%d")
        return True
    except Exception as e:
        print(f"Error al habilitar vehículo: {e}")
        return False


def registrar_diagnostico(mantenimiento_id: int, diagnostico: str) -> bool:
    """Registra o actualiza el diagnóstico técnico de una OT."""
    try:
        with get_session() as session:
            m = session.query(Mantenimiento).filter(
                Mantenimiento.id == mantenimiento_id
            ).first()
            if not m:
                return False
            m.diagnostico_tecnico = diagnostico
        return True
    except Exception as e:
        print(f"Error al registrar diagnóstico: {e}")
        return False