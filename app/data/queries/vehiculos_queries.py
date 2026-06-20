"""
vehiculos_queries.py
app/data/queries/vehiculos_queries.py
"""

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

def obtener_todos_vehiculos(session) -> list[dict]:
    vehiculos = session.query(Vehiculo).all()
    return [_vehiculo_a_dict(v) for v in vehiculos]


def obtener_vehiculo_por_id(session, vehiculo_id: int) -> dict | None:
    v = session.query(Vehiculo).filter(
        Vehiculo.id == vehiculo_id
    ).first()
    return _vehiculo_a_dict(v) if v else None


def obtener_vehiculo_por_patente(session, patente: str) -> dict | None:
    v = session.query(Vehiculo).filter(
        Vehiculo.patente == patente
    ).first()
    return _vehiculo_a_dict(v) if v else None


def obtener_vehiculos_por_estado(session, estado: str) -> list[dict]:
    estado_bd = estado.replace(" ", "_")
    vehiculos = (
        session.query(Vehiculo)
        .filter(Vehiculo.estado_operacional == estado_bd)
        .all()
    )
    return [_vehiculo_a_dict(v) for v in vehiculos]


def obtener_vehiculos_disponibles(session) -> list[dict]:
    return obtener_vehiculos_por_estado(session, "Disponible")


def obtener_sucursales(session) -> list[str]:
    sucursales = session.query(Sucursal).all()
    return [s.nombre for s in sucursales]


# ─── Operaciones de creación ──────────────────────────────────────────────────

def crear_vehiculo(
    session,
    patente: str,
    tipo: str,
    marca_modelo: str,
    capacidad_kg: int,
    sucursal_nombre: str,
) -> bool:
    try:
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
        session.commit()
        return True

    except Exception as e:
        print(f"Error al crear vehículo: {e}")
        return False


# ─── Operaciones de actualización ─────────────────────────────────────────────

def actualizar_estado_vehiculo(
    session,
    vehiculo_id: int,
    nuevo_estado: str
) -> bool:

    estado_bd = nuevo_estado.replace(" ", "_")

    try:
        v = session.query(Vehiculo).filter(
            Vehiculo.id == vehiculo_id
        ).first()

        if not v:
            return False

        v.estado_operacional = estado_bd
        session.commit()
        return True

    except Exception as e:
        print(f"Error al actualizar estado del vehículo: {e}")
        return False

def actualizar_observacion_vehiculo(
    session,
    vehiculo_id: int,
    observacion: str
) -> bool:

    try:
        v = session.query(Vehiculo).filter(
            Vehiculo.id == vehiculo_id
        ).first()

        if not v:
            return False

        v.observacion = observacion
        session.commit()
        return True

    except Exception as e:
        print(f"Error al actualizar observación: {e}")
        return False