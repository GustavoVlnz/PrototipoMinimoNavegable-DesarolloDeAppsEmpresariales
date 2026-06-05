from app.data.queries import asignaciones_queries
from app.data.models import Asignacion, Solicitud, Vehiculo, Conductor

class AsignacionServiceError(Exception):
    pass

def puede_hacer_checkout(estado: str) -> bool:
    return estado == "Confirmada"

def puede_registrar_entrega(estado: str) -> bool:
    return estado == "En ejecución"

def puede_cerrar(estado: str) -> bool:
    return estado in ("Completada", "Completada con incidencia")

def registrar_asignacion(session, solicitud_id, vehiculo_id, conductor_id, asignado_por):
    solicitud = session.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not solicitud or solicitud.estado_solicitud != "Aprobada":
        raise AsignacionServiceError("La solicitud no existe o no está aprobada.")

    vehiculo = session.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo or vehiculo.estado_operacional != "Disponible":
        raise AsignacionServiceError("El vehículo no está disponible.")

    conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor or conductor.estado_disponibilidad != "Disponible":
        raise AsignacionServiceError("El conductor no está disponible.")

    vehiculo.estado_operacional = "Reservado"
    conductor.estado_disponibilidad = "Asignado"

    return asignaciones_queries.crear(session, solicitud_id, vehiculo_id, conductor_id, asignado_por)

def procesar_checkout(session, asignacion_id: int):
    asig = (
        session.query(Asignacion)
        .filter(Asignacion.id == asignacion_id)
        .first()
    )

    if not asig:
        raise AsignacionServiceError(
            "La asignación no existe."
        )

    if asig.estado_asignacion != "Confirmada":
        raise AsignacionServiceError(
            "Estado inválido para Check-out."
        )

    asig.estado_asignacion = "En_Ejecucion"
    asig.vehiculo.estado_operacional = "En_Ruta"

    session.commit()

def procesar_entrega(
    session,
    asignacion_id: int,
    fue_conforme: bool
):
    asig = (
        session.query(Asignacion)
        .filter(Asignacion.id == asignacion_id)
        .first()
    )

    if not asig:
        raise AsignacionServiceError(
            "La asignación no existe."
        )

    if asig.estado_asignacion != "En_Ejecucion":
        raise AsignacionServiceError(
            "La asignación no está en ruta."
        )

    asig.vehiculo.estado_operacional = "Disponible"
    asig.conductor.estado_disponibilidad = "Disponible"

    asig.estado_asignacion = (
        "Completada"
        if fue_conforme
        else "Completada_Con_Incidencia"
    )

    session.commit()

def procesar_cancelacion(session, asignacion_id: int):
    asig = (
        session.query(Asignacion)
        .filter(Asignacion.id == asignacion_id)
        .first()
    )

    if not asig:
        raise AsignacionServiceError(
            "La asignación no existe."
        )

    if asig.estado_asignacion not in (
        "Confirmada",
        "Pendiente",
    ):
        raise AsignacionServiceError(
            "No se puede cancelar en este estado."
        )

    asig.vehiculo.estado_operacional = "Disponible"
    asig.conductor.estado_disponibilidad = "Disponible"
    asig.solicitud.estado_solicitud = "Aprobada"
    asig.estado_asignacion = "Fallida"

    session.commit()

def procesar_cierre(session, asignacion_id: int):
    asig = session.query(Asignacion).filter(Asignacion.id == asignacion_id).first()

    if not asig:
        raise AsignacionServiceError("La asignación no existe.")

    if asig.estado_asignacion not in ("Completada", "Completada_Con_Incidencia"):
        raise AsignacionServiceError("La asignación debe estar completada.")

    asig.estado_asignacion = "Cerrada"
    asig.solicitud.estado_solicitud = "Cancelada"
    session.commit()