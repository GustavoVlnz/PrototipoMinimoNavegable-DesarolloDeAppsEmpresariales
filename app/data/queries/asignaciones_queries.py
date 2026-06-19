#app/data/queries/asignaciones_queries.py

from datetime import datetime
from sqlalchemy.orm import joinedload
from app.data.models import Asignacion, Solicitud, Vehiculo, Conductor

_ESTADO_DISPLAY = {
    "Solicitada": "Solicitada",
    "Pendiente": "Pendiente",
    "Confirmada": "Confirmada",
    "En_Ejecucion": "En ejecución",
    "Con_Incidencia": "Con incidencia",
    "Completada": "Completada",
    "Completada_Con_Incidencia": "Completada con incidencia",
    "Fallida": "Fallida",
    "Fallida_Parcial": "Fallida parcial",
    "Cerrada": "Cerrada",
}

def _asignacion_a_dict(asig: Asignacion) -> dict:
    if not asig:
        return {}
        
    origen = (
        asig.solicitud.sucursal_origen.nombre
        if asig.solicitud and asig.solicitud.sucursal_origen
        else "—"
    )

    destino = (
        asig.solicitud.sucursal_destino.nombre
        if asig.solicitud and asig.solicitud.sucursal_destino
        else "—"
    )
    
    prioridad = asig.solicitud.prioridad if asig.solicitud else "Media"
    
    nombre_conductor = "—"
    if asig.conductor:
        nombre_conductor = (
            asig.conductor.usuario.nombre 
            if hasattr(asig.conductor, "usuario") and asig.conductor.usuario 
            else getattr(asig.conductor, "nombre", "—")
        )

    return {
        "id": f"AS-{asig.id:03d}",
        "id_numerico": asig.id,
        "solicitud_id": f"SOL-{asig.solicitud_id:03d}" if asig.solicitud_id else "—",
        "solicitud_id_raw": asig.solicitud_id,
        "vehiculo_id": asig.vehiculo_id,
        "vehiculo_patente": asig.vehiculo.patente if asig.vehiculo else "—",
        "conductor_id": asig.conductor_id,
        "conductor": nombre_conductor,
        "origen": origen,
        "destino": destino,
        "prioridad": prioridad,
        "estado": _ESTADO_DISPLAY.get(asig.estado_asignacion, asig.estado_asignacion),
        "estado_raw": asig.estado_asignacion,
        "inicio": asig.fecha_asignacion.strftime("%Y-%m-%d %H:%M") if asig.fecha_asignacion else None,
        "fin": (
            asig.trazabilidad.fecha_hora_arribo_real.strftime("%Y-%m-%d %H:%M")
                if (
                    hasattr(asig, "trazabilidad")
                    and asig.trazabilidad
                    and asig.trazabilidad.fecha_hora_arribo_real) 
                else None),
    }

def obtener_todas(session) -> list:
    asignaciones = (
        session.query(Asignacion)
        .options(
            joinedload(Asignacion.solicitud).joinedload(Solicitud.sucursal_origen),
            joinedload(Asignacion.solicitud).joinedload(Solicitud.sucursal_destino),
            joinedload(Asignacion.vehiculo),
            joinedload(Asignacion.conductor).joinedload(Conductor.usuario),
            joinedload(Asignacion.trazabilidad)
        )
        .order_by(Asignacion.id.desc())
        .all()
    )
    return [_asignacion_a_dict(a) for a in asignaciones]

def obtener_por_id(session, asignacion_id: int) -> dict:
    asig = (
        session.query(Asignacion)
        .options(
            joinedload(Asignacion.solicitud).joinedload(Solicitud.sucursal_origen),
            joinedload(Asignacion.solicitud).joinedload(Solicitud.sucursal_destino),
            joinedload(Asignacion.vehiculo),
            joinedload(Asignacion.conductor).joinedload(Conductor.usuario),
            joinedload(Asignacion.trazabilidad)
        )
        .filter(Asignacion.id == asignacion_id)
        .first()
    )
    return _asignacion_a_dict(asig) if asig else None

def crear(session, solicitud_id: int, vehiculo_id: int, conductor_id: int, asignado_por: int) -> Asignacion:
    """
    Crea la fila de Asignacion en estado 'Solicitada'.

    """
    nueva_asig = Asignacion(
        solicitud_id=solicitud_id,
        vehiculo_id=vehiculo_id,
        conductor_id=conductor_id,
        estado_asignacion="Solicitada",
        fecha_asignacion=datetime.utcnow(),
        asignado_por=asignado_por
    )
    session.add(nueva_asig)
    session.commit()
    session.refresh(nueva_asig)
    return nueva_asig

def obtener_solicitudes_aprobadas(session):
    return session.query(Solicitud).options(
        joinedload(Solicitud.sucursal_origen),
        joinedload(Solicitud.sucursal_destino)
    ).filter(Solicitud.estado_solicitud == "Aprobada").all()

def obtener_vehiculos_disponibles(session):
    return session.query(Vehiculo).filter(Vehiculo.estado_operacional == "Disponible").all()

def obtener_conductores_disponibles(session):
    return (
        session.query(Conductor)
        .options(joinedload(Conductor.usuario))
        .filter(Conductor.estado_disponibilidad == "Disponible")
        .all()
    )