"""
transition_service.py
app/logic/transition_service.py

Punto único de entrada para cambiar el estado de Solicitud, Asignacion,
Vehiculo y Conductor.
"""

from __future__ import annotations

from datetime import datetime

from app.data.models import (
    Asignacion,
    Conductor,
    DocumentacionVehiculo,
    Mantenimiento,
    Solicitud,
    Vehiculo,
)
from app.core.events import event_bus


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
    "Cerrada":                   set(),
}

_TRANSICIONES_VEHICULO: dict[str, set[str]] = {
    "Disponible":        {"Reservado", "Bloqueado", "En_Mantencion", "Fuera_de_Servicio"},
    "Reservado":         {"En_Ruta", "Disponible", "Bloqueado"},
    "En_Ruta":           {"Disponible", "En_Mantencion", "Fuera_de_Servicio", "Bloqueado"},
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

_TRANSICIONES_MANTENIMIENTO: dict[str, set[str]] = {
    "Pendiente":            {"En_Revision", "Programada"},
    "Programada":           {"En_Revision"},
    "En_Revision":          {"En_Espera_Repuestos", "Completada"},
    "En_Espera_Repuestos":  {"En_Revision", "Completada"},
    "Completada":           set(),
}

_TRANSICIONES_DOCUMENTO: dict[str, set[str]] = {
    "Vigente":     {"Por_Vencer", "Vencido"},
    "Por_Vencer":  {"Vigente", "Vencido"},
    "Vencido":     {"Vigente"},
}

_MAPAS_POR_ENTIDAD = {
    Solicitud: _TRANSICIONES_SOLICITUD,
    Asignacion: _TRANSICIONES_ASIGNACION,
    Vehiculo: _TRANSICIONES_VEHICULO,
    Conductor: _TRANSICIONES_CONDUCTOR,
    Mantenimiento: _TRANSICIONES_MANTENIMIENTO,
    DocumentacionVehiculo: _TRANSICIONES_DOCUMENTO,
}

_CAMPO_ESTADO = {
    Solicitud: "estado_solicitud",
    Asignacion: "estado_asignacion",
    Vehiculo: "estado_operacional",
    Conductor: "estado_disponibilidad",
    Mantenimiento: "estado",
    DocumentacionVehiculo: "estado_documental",
}

_NOMBRE_ENTIDAD = {
    Solicitud: "Solicitud",
    Asignacion: "Asignacion",
    Vehiculo: "Vehiculo",
    Conductor: "Conductor",
    Mantenimiento: "Mantenimiento",
    DocumentacionVehiculo: "DocumentacionVehiculo",
}


# ═══════════════════════════════════════════════════════════════════════════
# NUCLEO GENERICO (privado -- no se llama directo desde fuera de este archivo)
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
# DISPONIBILIDAD UNIFICADA DE VEHICULO
# ═══════════════════════════════════════════════════════════════════════════

def _tiene_mantencion_abierta(vehiculo: Vehiculo) -> bool:
    """True si el vehiculo tiene alguna orden de mantenimiento que no
    esta en estado terminal (Completada)."""
    return any(m.estado != "Completada" for m in vehiculo.mantenimientos)


def _tiene_documentacion_vencida(vehiculo: Vehiculo) -> bool:
    """True si el vehiculo tiene al menos un documento en estado Vencido."""
    return any(d.estado_documental == "Vencido" for d in vehiculo.documentos)


def estado_objetivo_vehiculo(vehiculo: Vehiculo) -> str:
    if _tiene_documentacion_vencida(vehiculo):
        return "Bloqueado"
    if _tiene_mantencion_abierta(vehiculo):
        return "En_Mantencion"
    return "Disponible"


def sincronizar_disponibilidad_vehiculo(session, vehiculo: Vehiculo) -> None:
    """
    Re-evalua y aplica el estado del vehiculo segun
    estado_objetivo_vehiculo(), EXCEPTO si el vehiculo esta En_Ruta
    """
    if vehiculo.estado_operacional == "En_Ruta":
        return

    objetivo = estado_objetivo_vehiculo(vehiculo)
    if vehiculo.estado_operacional != objetivo:
        _transicionar(vehiculo, objetivo)


def puede_asignarse_vehiculo(vehiculo: Vehiculo) -> bool:
    return vehiculo.estado_operacional == "Disponible"


def vehiculos_bloqueados_por_documentacion(vehiculos: list[Vehiculo]) -> list[Vehiculo]:
    """
    Filtra, de una lista de vehiculos, los que estan Bloqueados
    especificamente por documentacion vencida (no por mantencion).
    """
    return [
        v for v in vehiculos
        if v.estado_operacional == "Bloqueado" and _tiene_documentacion_vencida(v)
    ]


def vehiculos_en_mantencion_abierta(vehiculos: list[Vehiculo]) -> list[Vehiculo]:
    """
    Filtra, de una lista de vehiculos, los que tienen una orden de
    mantenimiento sin completar (sin importar el estado_operacional
    actual
    """
    return [v for v in vehiculos if _tiene_mantencion_abierta(v)]


# ═══════════════════════════════════════════════════════════════════════════
# SOLICITUD
# ═══════════════════════════════════════════════════════════════════════════

def evaluar_solicitud(session, solicitud: Solicitud) -> None:
    """Creada -> En_Evaluacion. Paso intermedio antes de aprobar/rechazar."""
    _transicionar(solicitud, "En_Evaluacion")
    session.commit()
    event_bus.solicitud_actualizada.emit()


def aprobar_solicitud(session, solicitud: Solicitud) -> None:
    """En_Evaluacion -> Aprobada. Habilita la solicitud para ser tomada
    desde el formulario de Nueva Asignacion."""
    _transicionar(solicitud, "Aprobada")
    session.commit()
    event_bus.solicitud_actualizada.emit()


def rechazar_solicitud(session, solicitud: Solicitud) -> None:
    _transicionar(solicitud, "Rechazada")
    session.commit()
    event_bus.solicitud_actualizada.emit()


def reprogramar_solicitud(session, solicitud: Solicitud, nueva_prioridad: str) -> None:
    """
    Aprobada o Pendiente_Reasignacion -> Reprogramada, con cambio de
    prioridad. Mantiene el mismo comportamiento que ya tenian en
    solicitudes_queries.reprogramar, pero ahora validado contra el mapa.
    """
    _transicionar(solicitud, "Reprogramada")
    solicitud.prioridad = nueva_prioridad
    session.commit()
    event_bus.solicitud_actualizada.emit()


def cancelar_solicitud(session, solicitud: Solicitud) -> None:
    _transicionar(solicitud, "Cancelada")
    session.commit()
    event_bus.solicitud_actualizada.emit()


def completar_solicitud(session, solicitud: Solicitud) -> None:
    """
    Aprobada -> Completada.
    """
    _transicionar(solicitud, "Completada")
    session.commit()


# ═══════════════════════════════════════════════════════════════════════════
# VEHICULO / CONDUCTOR -- transiciones simples sin efectos cruzados
# ═══════════════════════════════════════════════════════════════════════════

def bloquear_vehiculo(session, vehiculo: Vehiculo) -> None:
    """Disponible -> Bloqueado. Bloqueo administrativo manual."""
    _transicionar(vehiculo, "Bloqueado")
    session.commit()
    event_bus.vehiculo_actualizado.emit()


def desbloquear_vehiculo(session, vehiculo: Vehiculo) -> None:
    """Bloqueado -> Disponible."""
    _transicionar(vehiculo, "Disponible")
    session.commit()
    event_bus.vehiculo_actualizado.emit()


def habilitar_conductor(session, conductor: Conductor) -> None:
    """No_Habilitado -> Disponible."""
    _transicionar(conductor, "Disponible")
    session.commit()
    event_bus.conductor_actualizado.emit()


def deshabilitar_conductor(session, conductor: Conductor) -> None:
    """
    Disponible o En_Descanso -> No_Habilitado.
    """
    _transicionar(conductor, "No_Habilitado")
    session.commit()
    event_bus.conductor_actualizado.emit()


def poner_conductor_en_descanso(session, conductor: Conductor) -> None:
    _transicionar(conductor, "En_Descanso")
    session.commit()
    event_bus.conductor_actualizado.emit()


def marcar_conductor_disponible(session, conductor: Conductor) -> None:
    _transicionar(conductor, "Disponible")
    session.commit()
    event_bus.conductor_actualizado.emit()


# ═══════════════════════════════════════════════════════════════════════════
# ASIGNACION -- aqui viven los efectos cruzados (vehiculo + conductor + solicitud)
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
    event_bus.asignacion_actualizada.emit()
    event_bus.vehiculo_actualizado.emit()
    event_bus.conductor_actualizado.emit()


def iniciar_ruta(session, asignacion: Asignacion) -> None:
    """
    Confirmada -> En_Ejecucion. Vehiculo: Reservado -> En_Ruta.
    Equivalente al Paso 7 del documento (check-out exitoso -> salida).
    """
    _transicionar(asignacion, "En_Ejecucion")
    _transicionar(asignacion.vehiculo, "En_Ruta")
    session.commit()
    event_bus.asignacion_actualizada.emit()
    event_bus.vehiculo_actualizado.emit()


def registrar_entrega(session, asignacion: Asignacion, fue_conforme: bool) -> None:
    """
    En_Ejecucion -> Completada o Completada_Con_Incidencia.
    Conductor: Asignado -> Disponible.

    """
    nuevo_estado = "Completada" if fue_conforme else "Completada_Con_Incidencia"
    _transicionar(asignacion, nuevo_estado)

    objetivo = estado_objetivo_vehiculo(asignacion.vehiculo)
    _transicionar(asignacion.vehiculo, objetivo)

    _transicionar(asignacion.conductor, "Disponible")
    session.commit()
    event_bus.asignacion_actualizada.emit()
    event_bus.vehiculo_actualizado.emit()
    event_bus.conductor_actualizado.emit()


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
    event_bus.asignacion_actualizada.emit()
    event_bus.vehiculo_actualizado.emit()
    event_bus.conductor_actualizado.emit()
    event_bus.solicitud_actualizada.emit()


def cerrar_asignacion(session, asignacion: Asignacion) -> None:
    """
    Completada o Completada_Con_Incidencia o Fallida o Fallida_Parcial -> Cerrada.
    """
    estado_previo = asignacion.estado_asignacion
    _transicionar(asignacion, "Cerrada")

    if estado_previo in ("Completada", "Completada_Con_Incidencia"):
        completar_solicitud(session, asignacion.solicitud)

    session.commit()
    event_bus.asignacion_actualizada.emit()
    event_bus.solicitud_actualizada.emit()


# ═══════════════════════════════════════════════════════════════════════════
# MANTENIMIENTO -- efectos cruzados sobre Vehiculo
# ═══════════════════════════════════════════════════════════════════════════

def abrir_mantenimiento(session, mantenimiento: Mantenimiento) -> None:
    """
    Vehiculo -> En_Mantencion. Se llama justo despues de crear la fila
    de Mantenimiento (que ya nace en 'Pendiente' por default del
    modelo).
    """
    _transicionar(mantenimiento.vehiculo, "En_Mantencion")
    session.commit()
    event_bus.mantenimiento_actualizado.emit()
    event_bus.vehiculo_actualizado.emit()


def avanzar_mantenimiento(session, mantenimiento: Mantenimiento, nuevo_estado: str) -> None:
    _transicionar(mantenimiento, nuevo_estado)
    session.commit()
    event_bus.mantenimiento_actualizado.emit()


def completar_mantenimiento(session, mantenimiento: Mantenimiento, tecnico_id: int | None = None) -> None:
    """
    En_Revision o En_Espera_Repuestos -> Completada.

    """
    _transicionar(mantenimiento, "Completada")
    mantenimiento.fecha_egreso_real = datetime.utcnow()
    if tecnico_id:
        mantenimiento.validado_por_tecnico = tecnico_id

    sincronizar_disponibilidad_vehiculo(session, mantenimiento.vehiculo)
    session.commit()
    event_bus.mantenimiento_actualizado.emit()
    event_bus.vehiculo_actualizado.emit()


# ═══════════════════════════════════════════════════════════════════════════
# DOCUMENTACION -- efectos cruzados sobre Vehiculo
# ═══════════════════════════════════════════════════════════════════════════

def marcar_documento_vencido(session, documento: DocumentacionVehiculo) -> None:
    """
    Vigente o Por_Vencer -> Vencido.
    """
    _transicionar(documento, "Vencido")
    sincronizar_disponibilidad_vehiculo(session, documento.vehiculo)
    session.commit()
    event_bus.documento_actualizado.emit()
    event_bus.vehiculo_actualizado.emit()


def renovar_documento(session, documento: DocumentacionVehiculo, nueva_fecha: str) -> None:
    """
    Vencido o Por_Vencer -> Vigente, con actualizacion de fecha.


    """
    estado_actual = documento.estado_documental
    if estado_actual == "Vigente":

        documento.fecha_vencimiento = nueva_fecha
    else:
        _transicionar(documento, "Vigente")
        documento.fecha_vencimiento = nueva_fecha

    sincronizar_disponibilidad_vehiculo(session, documento.vehiculo)
    session.commit()
    event_bus.documento_actualizado.emit()
    event_bus.vehiculo_actualizado.emit()