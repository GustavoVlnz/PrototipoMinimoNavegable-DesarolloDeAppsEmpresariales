#app/logic/asignaciones_service.py
"""
Este archivo quedo reducido a registrar_asignacion(), que es la unica
operacion de Asignacion que necesita una capa de service propia: busca
y valida tres entidades distintas (solicitud, vehiculo, conductor) con
reglas que van mas alla de "es valida esta transicion de estado"
(existencia, disponibilidad, pertenencia).

"""

from app.data.queries import asignaciones_queries
from app.data.models import Solicitud, Vehiculo, Conductor
from app.logic import transition_service
from app.logic.transition_service import TransitionError


class AsignacionServiceError(Exception):
    pass


def registrar_asignacion(session, solicitud_id, vehiculo_id, conductor_id, asignado_por):
    """
    Crea una nueva Asignacion a partir de una Solicitud Aprobada, un
    Vehiculo Disponible y un Conductor Disponible.

    """
    solicitud = session.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if not solicitud or solicitud.estado_solicitud != "Aprobada":
        raise AsignacionServiceError("La solicitud no existe o no está aprobada.")

    vehiculo = session.query(Vehiculo).filter(Vehiculo.id == vehiculo_id).first()
    if not vehiculo or vehiculo.estado_operacional != "Disponible":
        raise AsignacionServiceError("El vehículo no está disponible.")

    conductor = session.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor or conductor.estado_disponibilidad != "Disponible":
        raise AsignacionServiceError("El conductor no está disponible.")

    nueva_asig = asignaciones_queries.crear(session, solicitud_id, vehiculo_id, conductor_id, asignado_por)

    try:
        transition_service.confirmar_asignacion(session, nueva_asig)
    except TransitionError as e:
        raise AsignacionServiceError(str(e))

    return nueva_asig