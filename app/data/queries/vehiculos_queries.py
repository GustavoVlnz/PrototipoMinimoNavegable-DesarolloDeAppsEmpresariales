"""
vehiculos_queries.py
app/data/queries/vehiculos_queries.py
"""

from app.data.database import get_session
from app.data.models import Vehiculo, Sucursal, Mantenimiento


# ─── Helper ORM → dict ────────────────────────────────────────────────────────

def _vehiculo_a_dict(v: Vehiculo) -> dict:
    """Convierte un ORM Vehiculo a diccionario compatible con la UI."""
    ultima_mnt = "Sin registro"
    if v.mantenimientos:
        completadas = [
            m for m in v.mantenimientos if m.estado == "Completada" and m.fecha_egreso_real
        ]
        if completadas:
            ultima = max(completadas, key=lambda m: m.fecha_egreso_real)
            ultima_mnt = ultima.fecha_egreso_real.strftime("%Y-%m-%d")
        elif v.ultima_mantencion:
            ultima_mnt = v.ultima_mantencion
    elif v.ultima_mantencion:
        ultima_mnt = v.ultima_mantencion

    return {
        "vehiculo_id":      v.id,
        "patente":          v.patente,
        "tipo":             v.tipo.replace("_", " "),
        "tipo_raw":         v.tipo,
        "modelo":           v.marca_modelo or "—",
        "capacidad_kg":     v.capacidad_kg,
        "estado":           v.estado_operacional.replace("_", " "),
        "estado_raw":       v.estado_operacional,
        "ubicacion":        v.sucursal_actual.nombre if v.sucursal_actual else "—",
        "kilometraje":      v.kilometraje or 0,
        "observacion":      v.observacion or "",
        "ultima_mantencion": ultima_mnt,
        "seguro_vence":     v.seguro_vence or "—",
        "permiso_vence":    v.permiso_vence or "—",
        "revision_tecnica": v.revision_tecnica or "—",
    }


# ─── Consultas de lectura ─────────────────────────────────────────────────────

def obtener_todos_vehiculos() -> list[dict]:
    """Retorna todos los vehículos de la flota."""
    with get_session() as session:
        vehiculos = session.query(Vehiculo).all()
        resultado = [_vehiculo_a_dict(v) for v in vehiculos]
    return resultado


def obtener_vehiculo_por_id(vehiculo_id: int) -> dict | None:
    """Retorna un vehículo específico por su ID."""
    with get_session() as session:
        v = session.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
        if v:
            return _vehiculo_a_dict(v)
    return None


def obtener_vehiculo_por_patente(patente: str) -> dict | None:
    """Retorna un vehículo por su patente."""
    with get_session() as session:
        v = session.query(Vehiculo).filter(Vehiculo.patente == patente).first()
        if v:
            return _vehiculo_a_dict(v)
    return None


def obtener_vehiculos_por_estado(estado: str) -> list[dict]:
    """Retorna vehículos filtrados por estado operacional."""
    estado_bd = estado.replace(" ", "_")
    with get_session() as session:
        vehiculos = (
            session.query(Vehiculo)
            .filter(Vehiculo.estado_operacional == estado_bd)
            .all()
        )
        resultado = [_vehiculo_a_dict(v) for v in vehiculos]
    return resultado


def obtener_vehiculos_disponibles() -> list[dict]:
    """Retorna solo los vehículos con estado 'Disponible'."""
    return obtener_vehiculos_por_estado("Disponible")


def obtener_sucursales() -> list[str]:
    """Retorna lista de nombres de sucursales para poblar combos."""
    with get_session() as session:
        sucursales = session.query(Sucursal).all()
        return [s.nombre for s in sucursales]


# ─── Operaciones de creación ──────────────────────────────────────────────────

def crear_vehiculo(
    patente: str,
    tipo: str,
    marca_modelo: str,
    capacidad_kg: int,
    sucursal_nombre: str,
) -> bool:
    """
    Registra un nuevo vehículo en la flota.

    Args:
        patente:         Patente única del vehículo (ej: "BKRT-42").
        tipo:            Uno de: "Camioneta", "Furgon", "Camion_Liviano".
        marca_modelo:    Descripción del modelo (ej: "Toyota Hilux").
        capacidad_kg:    Capacidad de carga en kilogramos.
        sucursal_nombre: Nombre de la sucursal donde se ubica.

    Returns:
        True si fue exitoso.
    """
    try:
        with get_session() as session:
            sucursal = session.query(Sucursal).filter(
                Sucursal.nombre == sucursal_nombre
            ).first()

            nuevo = Vehiculo(
                patente=patente.upper(),
                tipo=tipo.replace(" ", "_"),
                marca_modelo=marca_modelo,
                capacidad_kg=capacidad_kg,
                estado_operacional="Disponible",
                sucursal_actual_id=sucursal.id if sucursal else None,
                kilometraje=0,
            )
            session.add(nuevo)
        return True
    except Exception as e:
        print(f"Error al crear vehículo: {e}")
        return False


# ─── Operaciones de actualización ─────────────────────────────────────────────

def actualizar_estado_vehiculo(vehiculo_id: int, nuevo_estado: str) -> bool:
    """
    Actualiza el estado operacional de un vehículo.

    Args:
        vehiculo_id:  ID del vehículo.
        nuevo_estado: Uno de: "Disponible", "Reservado", "En_Ruta",
                      "En_Mantencion", "Fuera_de_Servicio", "Bloqueado".

    Returns:
        True si fue exitoso.
    """
    estado_bd = nuevo_estado.replace(" ", "_")
    try:
        with get_session() as session:
            v = session.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
            if not v:
                return False
            v.estado_operacional = estado_bd
        return True
    except Exception as e:
        print(f"Error al actualizar estado del vehículo: {e}")
        return False


def actualizar_observacion_vehiculo(vehiculo_id: int, observacion: str) -> bool:
    """Actualiza el campo de observación de un vehículo."""
    try:
        with get_session() as session:
            v = session.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
            if not v:
                return False
            v.observacion = observacion
        return True
    except Exception as e:
        print(f"Error al actualizar observación: {e}")
        return False