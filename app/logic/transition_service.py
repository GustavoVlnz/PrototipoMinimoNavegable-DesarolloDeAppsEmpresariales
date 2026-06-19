"""
transition_service.py
app/logic/transition_service.py

Punto único de entrada para cambiar el estado de Solicitud, Asignacion,
Vehiculo y Conductor.

"""

from __future__ import annotations

from app.data.models import Asignacion, Conductor, Solicitud, Vehiculo


class TransitionError(Exception):
    """Se lanza cuando se intenta una transicion de estado invalida
    o cuando no se cumple una precondicion de negocio."""
    pass


# ═══════════════════════════════════════════════════════════════════════════
# MAPAS DE TRANSICION VALIDA POR ENTIDAD
# ═══════════════════════════════════════════════════════════════════════════

_TRANSICIONES_SOLICITUD: dict[str, set[str]] = {
    "Creada":                  {"En_Evaluacion", "Cancelada"},
    "En_Evaluacion":           {"Aprobada", "Rechazada", "Cancelada"},
    "Aprobada":                {"Pendiente_Reasignacion", "Completada", "Cancelada"},
    "Pendiente_Reasignacion":  {"Aprobada", "Reprogramada", "Cancelada"},
    "Reprogramada":            {"Aprobada", "Cancelada"},
    # Estados terminales: no admiten salida.
    "Rechazada":               set(),
    "Cancelada":                set(),
    "Completada":              set(),
}

_TRANSICIONES_ASIGNACION: dict[str, set[str]] = {

    "Solicitada":               {"Pendiente", "Confirmada", "Fallida"},
    "Pendiente":                {"Confirmada", "Fallida"},
    "Confirmada":               {"En_Ejecucion", "Fallida"},
    "En_Ejecucion":             {"Con_Incidencia", "Completada", "Fallida", "Fallida_Parcial"},
    "Con_Incidencia":           {"En_Ejecucion", "Completada_Con_Incidencia", "Fallida", "Fallida_Parcial"},
    "Completada":               {"Cerrada"},
    "Completada_Con_Incidencia": {"Cerrada"},
    "Fallida":                   {"Cerrada"},
    "Fallida_Parcial":           {"Cerrada"},
    # Estado terminal.
    "Cerrada":                   set(),
}

_TRANSICIONES_VEHICULO: dict[str, set[str]] = {
    "Disponible":        {"Reservado", "Bloqueado", "En_Mantencion", "Fuera_de_Servicio"},
    "Reservado":         {"En_Ruta", "Disponible", "Bloqueado"},
    "En_Ruta":           {"Disponible", "En_Mantencion", "Fuera_de_Servicio"},
    "En_Mantencion":     {"Disponible", "Fuera_de_Servicio", "Bloqueado"},
    "Fuera_de_Servicio": {"Disponible", "En_Mantencion", "Bloqueado"},
    "Bloqueado":         {"Disponible"},
}

_TRANSICIONES_CONDUCTOR: dict[str, set[str]] = {
    "Disponible":    {"Asignado", "En_Descanso", "No_Habilitado"},
    "Asignado":      {"Disponible", "No_Habilitado"},
    "En_Descanso":   {"Disponible", "No_Habilitado"},
    "No_Habilitado": {"Disponible"},
}

_MAPAS_POR_ENTIDAD = {
    Solicitud: _TRANSICIONES_SOLICITUD,
    Asignacion: _TRANSICIONES_ASIGNACION,
    Vehiculo: _TRANSICIONES_VEHICULO,
    Conductor: _TRANSICIONES_CONDUCTOR,
}

_CAMPO_ESTADO = {
    Solicitud: "estado_solicitud",
    Asignacion: "estado_asignacion",
    Vehiculo: "estado_operacional",
    Conductor: "estado_disponibilidad",
}

_NOMBRE_ENTIDAD = {
    Solicitud: "Solicitud",
    Asignacion: "Asignacion",
    Vehiculo: "Vehiculo",
    Conductor: "Conductor",
}


# ═══════════════════════════════════════════════════════════════════════════
# NUCLEO GENERICO
# ═══════════════════════════════════════════════════════════════════════════

def _transicionar(instancia, nuevo_estado: str) -> None:
    """
    Valida y aplica un cambio de estado sobre una instancia ORM, usando el
    mapa de transiciones correspondiente a su clase.

    """
    tipo = type(instancia)
    mapa = _MAPAS_POR_ENTIDAD.get(tipo)
    if mapa is None:
        raise TransitionError(f"Tipo de entidad sin mapa de transiciones: {tipo}")

    campo = _CAMPO_ESTADO[tipo]
    nombre = _NOMBRE_ENTIDAD[tipo]
    estado_actual = getattr(instancia, campo)

    if estado_actual not in mapa:
        raise TransitionError(
            f"{nombre} tiene un estado desconocido '{estado_actual}', "
            f"no se puede validar la transicion."
        )

    if nuevo_estado not in mapa[estado_actual]:
        raise TransitionError(
            f"{nombre}: no se puede pasar de '{estado_actual}' a '{nuevo_estado}'. "
            f"Transiciones permitidas desde '{estado_actual}': "
            f"{sorted(mapa[estado_actual]) or '(ninguna, es estado terminal)'}."
        )

    setattr(instancia, campo, nuevo_estado)


def puede_transicionar(instancia, nuevo_estado: str) -> bool:
    tipo = type(instancia)
    mapa = _MAPAS_POR_ENTIDAD.get(tipo)
    if mapa is None:
        return False
    campo = _CAMPO_ESTADO[tipo]
    estado_actual = getattr(instancia, campo)
    return estado_actual in mapa and nuevo_estado in mapa[estado_actual]


# ═══════════════════════════════════════════════════════════════════════════
# SOLICITUD
# ═══════════════════════════════════════════════════════════════════════════

def evaluar_solicitud(session, solicitud: Solicitud) -> None:
    """Creada -> En_Evaluacion. Paso intermedio antes de aprobar/rechazar."""
    _transicionar(solicitud, "En_Evaluacion")
    session.commit()


def aprobar_solicitud(session, solicitud: Solicitud) -> None:
    """En_Evaluacion -> Aprobada. """
    _transicionar(solicitud, "Aprobada")
    session.commit()


def rechazar_solicitud(session, solicitud: Solicitud) -> None:
    _transicionar(solicitud, "Rechazada")
    session.commit()


def reprogramar_solicitud(session, solicitud: Solicitud, nueva_prioridad: str) -> None:
    """
    Aprobada o Pendiente_Reasignacion 
    """
    _transicionar(solicitud, "Reprogramada")
    solicitud.prioridad = nueva_prioridad
    session.commit()


def cancelar_solicitud(session, solicitud: Solicitud) -> None:
    _transicionar(solicitud, "Cancelada")
    session.commit()


def completar_solicitud(session, solicitud: Solicitud) -> None:
    """
    Aprobada -> Completada.
    """
    _transicionar(solicitud, "Completada")
    session.commit()


# ═══════════════════════════════════════════════════════════════════════════
# VEHICULO / CONDUCTOR 
# ═══════════════════════════════════════════════════════════════════════════

def bloquear_vehiculo(session, vehiculo: Vehiculo) -> None:
    """Disponible -> Bloqueado. Bloqueo administrativo manual."""
    _transicionar(vehiculo, "Bloqueado")
    session.commit()


def desbloquear_vehiculo(session, vehiculo: Vehiculo) -> None:
    """Bloqueado -> Disponible."""
    _transicionar(vehiculo, "Disponible")
    session.commit()


def habilitar_conductor(session, conductor: Conductor) -> None:
    """No_Habilitado -> Disponible."""
    _transicionar(conductor, "Disponible")
    session.commit()


def deshabilitar_conductor(session, conductor: Conductor) -> None:
    """
    Disponible o En_Descanso -> No_Habilitado.
    """
    _transicionar(conductor, "No_Habilitado")
    session.commit()


def poner_conductor_en_descanso(session, conductor: Conductor) -> None:
    _transicionar(conductor, "En_Descanso")
    session.commit()


def marcar_conductor_disponible(session, conductor: Conductor) -> None:
    _transicionar(conductor, "Disponible")
    session.commit()


# ═══════════════════════════════════════════════════════════════════════════
# ASIGNACION 
# ═══════════════════════════════════════════════════════════════════════════

def confirmar_asignacion(session, asignacion: Asignacion) -> None:
    """
    Pendiente -> Confirmada. El vehiculo pasa a Reservado y el conductor
    a Asignado.
    """
    _transicionar(asignacion, "Confirmada")
    _transicionar(asignacion.vehiculo, "Reservado")
    _transicionar(asignacion.conductor, "Asignado")
    session.commit()


def iniciar_ruta(session, asignacion: Asignacion) -> None:
    """
    Confirmada -> En_Ejecucion. Vehiculo: Reservado -> En_Ruta.
    """
    _transicionar(asignacion, "En_Ejecucion")
    _transicionar(asignacion.vehiculo, "En_Ruta")
    session.commit()


def registrar_entrega(session, asignacion: Asignacion, fue_conforme: bool) -> None:
    """
    En_Ejecucion -> Completada o Completada_Con_Incidencia.
    Vehiculo: En_Ruta -> Disponible. Conductor: Asignado -> Disponible.

    """
    nuevo_estado = "Completada" if fue_conforme else "Completada_Con_Incidencia"
    _transicionar(asignacion, nuevo_estado)
    _transicionar(asignacion.vehiculo, "Disponible")
    _transicionar(asignacion.conductor, "Disponible")
    session.commit()


def cancelar_asignacion(session, asignacion: Asignacion) -> None:
    """
    Pendiente o Confirmada -> Fallida. Libera vehiculo y conductor, y
    devuelve la solicitud a 'Aprobada' para que pueda reasignarse.
    """
    _transicionar(asignacion, "Fallida")
    _transicionar(asignacion.vehiculo, "Disponible")
    _transicionar(asignacion.conductor, "Disponible")
    if asignacion.solicitud.estado_solicitud != "Aprobada":
        _transicionar(asignacion.solicitud, "Aprobada")

    session.commit()


def cerrar_asignacion(session, asignacion: Asignacion) -> None:
    """
    Completada o Completada_Con_Incidencia o Fallida o Fallida_Parcial -> Cerrada.
    """
    estado_previo = asignacion.estado_asignacion
    _transicionar(asignacion, "Cerrada")

    if estado_previo in ("Completada", "Completada_Con_Incidencia"):
        completar_solicitud(session, asignacion.solicitud)

    session.commit()