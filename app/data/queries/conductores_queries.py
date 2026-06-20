"""
conductores_queries.py
Todas las consultas a la base de datos relacionadas con conductores.
"""

from app.data.models import Conductor, Usuario, Sucursal


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
        "estado_raw": conductor.estado_disponibilidad,
        "sucursal": usuario.sucursal.nombre if usuario and usuario.sucursal else "—",
        "asignacion_activa": None,  # TODO: Calcular de asignaciones activas si es necesario
        "usuario_id": conductor.usuario_id,
        "conductor_id": conductor.id,
    }


# ─── Consultas de lectura ─────────────────────────────────────────────────────

def obtener_todos_conductores(session) -> list[dict]:
    """Retorna todos los conductores de la base de datos."""
    conductores = session.query(Conductor).all()
    return [_conductor_a_dict(c) for c in conductores]


def obtener_conductor_por_id(session, conductor_id: int) -> dict | None:
    """Retorna un conductor específico por su ID."""
    conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
    return _conductor_a_dict(conductor) if conductor else None


def obtener_conductor_orm_por_id(session, conductor_id: int) -> Conductor | None:
    """
    Igual que obtener_conductor_por_id(), pero retorna el objeto ORM en
    vez de un dict. Se usa donde se necesita pasarlo directamente a
    transition_service.
    """
    return session.query(Conductor).filter(Conductor.id == conductor_id).first()


def obtener_conductores_por_estado(session, estado: str) -> list[dict]:
    """Retorna conductores filtrados por estado de disponibilidad."""
    estado_bd = estado.replace(" ", "_")
    conductores = (
        session.query(Conductor)
        .filter(Conductor.estado_disponibilidad == estado_bd)
        .all()
    )
    return [_conductor_a_dict(c) for c in conductores]


# ─── Operaciones de actualización ─────────────────────────────────────────────

def habilitar(session, conductor_id: int) -> tuple[bool, str | None]:
    """
    Habilita un conductor: No_Habilitado -> Disponible, y marca
    habilitado=True.
    """
    from app.logic import transition_service
    from app.logic.transition_service import TransitionError

    conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        return False, "El conductor no existe."

    try:
        transition_service.habilitar_conductor(session, conductor)
    except TransitionError as e:
        return False, str(e)

    conductor.habilitado = True
    session.commit()
    return True, None


def deshabilitar(session, conductor_id: int) -> tuple[bool, str | None]:
    """
    Deshabilita un conductor: Disponible o En_Descanso -> No_Habilitado.
    """
    from app.logic import transition_service
    from app.logic.transition_service import TransitionError

    conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        return False, "El conductor no existe."

    try:
        transition_service.deshabilitar_conductor(session, conductor)
    except TransitionError as e:
        return False, str(e)

    conductor.habilitado = False
    session.commit()
    return True, None


def poner_en_descanso(session, conductor_id: int) -> tuple[bool, str | None]:
    """Disponible -> En_Descanso."""
    from app.logic import transition_service
    from app.logic.transition_service import TransitionError

    conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        return False, "El conductor no existe."

    try:
        transition_service.poner_conductor_en_descanso(session, conductor)
    except TransitionError as e:
        return False, str(e)

    return True, None


def marcar_disponible(session, conductor_id: int) -> tuple[bool, str | None]:
    """En_Descanso -> Disponible."""
    from app.logic import transition_service
    from app.logic.transition_service import TransitionError

    conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        return False, "El conductor no existe."

    try:
        transition_service.marcar_conductor_disponible(session, conductor)
    except TransitionError as e:
        return False, str(e)

    return True, None


def actualizar_licencia(session, conductor_id: int, nueva_fecha_vencimiento: str) -> bool:
    """
    Actualiza la fecha de vencimiento de la licencia. No es un cambio
    de estado_disponibilidad, así que no pasa por transition_service.
    """
    try:
        conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
        if not conductor:
            return False
        conductor.licencia_vence = nueva_fecha_vencimiento
        session.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar licencia: {e}")
        return False


def crear_conductor(session, nombre: str, rut: str, tipo_licencia: str, sucursal_nombre: str) -> int | None:
    """
    Crea un nuevo conductor con su usuario asociado.
    """
    try:
        sucursal = session.query(Sucursal).filter(Sucursal.nombre == sucursal_nombre).first()
        if not sucursal:
            print(f"Sucursal '{sucursal_nombre}' no encontrada")
            return None

        nuevo_usuario = Usuario(
            nombre=nombre,
            rut=rut,
            rol="Tecnico_Mantencion",  # FIXME: ver docstring -- placeholder incorrecto
            activo=True,
            sucursal_id=sucursal.id,
        )
        session.add(nuevo_usuario)
        session.flush()  # Obtener el ID del usuario antes de crear el conductor

        nuevo_conductor = Conductor(
            usuario_id=nuevo_usuario.id,
            tipo_licencia=tipo_licencia,
            habilitado=True,
            estado_disponibilidad="Disponible",
        )
        session.add(nuevo_conductor)
        session.flush()

        conductor_id = nuevo_conductor.id
        session.commit()
        return conductor_id
    except Exception as e:
        print(f"Error al crear conductor: {e}")
        return None