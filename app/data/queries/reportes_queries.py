"""
reportes_queries.py
app/data/queries/reportes_queries.py

Consultas para el módulo de Reportes y Trazabilidad.
"""

from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.data.models import (
    Asignacion,
    Conductor,
    DocumentacionVehiculo,
    Incidente,
    Mantenimiento,
    Solicitud,
    Vehiculo,
)
from app.data.queries import asignaciones_queries


# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_ASIGNACION_DISPLAY = {
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

_INCIDENTE_DISPLAY = {
    "Registrado": "Registrado",
    "En_Analisis": "En análisis",
    "En_Gestion": "En gestión",
    "Resuelto": "Resuelto",
    "Cerrado": "Cerrado",
}

_DOCUMENTO_DISPLAY = {
    "Vigente": "Vigente",
    "Por_Vencer": "Por vencer",
    "Vencido": "Vencido",
}

_VEHICULO_DISPLAY = {
    "Disponible": "Disponible",
    "Reservado": "Reservado",
    "En_Ruta": "En ruta",
    "En_Mantencion": "En mantención",
    "Fuera_de_Servicio": "Fuera de servicio",
    "Bloqueado": "Bloqueado",
}

_MANTENIMIENTO_DISPLAY = {
    "Pendiente": "Pendiente",
    "Programada": "Programada",
    "En_Revision": "En revisión",
    "En_Espera_Repuestos": "En espera repuestos",
    "Completada": "Completada",
}


def _estado_display(valor: str | None, mapa: dict | None = None) -> str:
    if not valor:
        return "—"

    if mapa and valor in mapa:
        return mapa[valor]

    return valor.replace("_", " ")


def _nombre_conductor(asignacion: Asignacion | None) -> str:
    if asignacion and asignacion.conductor and asignacion.conductor.usuario:
        return asignacion.conductor.usuario.nombre
    return "—"


def _ruta_asignacion(asignacion: Asignacion | None) -> str:
    if not asignacion or not asignacion.solicitud:
        return "—"

    origen = (
        asignacion.solicitud.sucursal_origen.nombre
        if asignacion.solicitud.sucursal_origen
        else "—"
    )

    destino = (
        asignacion.solicitud.sucursal_destino.nombre
        if asignacion.solicitud.sucursal_destino
        else "—"
    )

    return f"{origen} → {destino}"


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE CONTEO PARA GRÁFICOS
# ─────────────────────────────────────────────────────────────────────────────

def _conteo_por_estado(session, modelo, campo_estado, orden_estados: list[str], mapa_display: dict) -> list[dict]:
    """
    Retorna una lista uniforme para gráficos.

    Ejemplo:
    [
        {"estado_raw": "Disponible", "estado": "Disponible", "total": 3},
        {"estado_raw": "Bloqueado", "estado": "Bloqueado", "total": 1},
    ]
    """
    filas = (
        session.query(campo_estado, func.count(modelo.id))
        .group_by(campo_estado)
        .all()
    )

    conteos = {estado: int(total) for estado, total in filas}

    return [
        {
            "estado_raw": estado,
            "estado": _estado_display(estado, mapa_display),
            "total": conteos.get(estado, 0),
        }
        for estado in orden_estados
    ]


def _filtrar_ceros(datos: list[dict]) -> list[dict]:
    """
    Para que los gráficos no se llenen de estados vacíos.
    Si todos son cero, retorna la lista original.
    """
    con_datos = [d for d in datos if d.get("total", 0) > 0]
    return con_datos if con_datos else datos


# ─────────────────────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────────────────────

def obtener_resumen_reportes(session) -> dict:
    """
    Retorna KPIs generales para el módulo de reportes.
    """

    asignaciones_completadas = (
        session.query(Asignacion)
        .filter(Asignacion.estado_asignacion.in_([
            "Completada",
            "Completada_Con_Incidencia",
            "Cerrada",
        ]))
        .count()
    )

    asignaciones_con_incidencia = (
        session.query(Asignacion)
        .filter(Asignacion.estado_asignacion.in_([
            "Con_Incidencia",
            "Completada_Con_Incidencia",
        ]))
        .count()
    )

    incidentes_activos = (
        session.query(Incidente)
        .filter(Incidente.estado_incidente.notin_(["Resuelto", "Cerrado"]))
        .count()
    )

    documentos_criticos = (
        session.query(DocumentacionVehiculo)
        .filter(DocumentacionVehiculo.estado_documental.in_(["Vencido", "Por_Vencer"]))
        .count()
    )

    vehiculos_bloqueados = (
        session.query(Vehiculo)
        .filter(Vehiculo.estado_operacional == "Bloqueado")
        .count()
    )

    mantenciones_abiertas = (
        session.query(Mantenimiento)
        .filter(Mantenimiento.estado != "Completada")
        .count()
    )

    return {
        "asignaciones_completadas": asignaciones_completadas,
        "asignaciones_con_incidencia": asignaciones_con_incidencia,
        "incidentes_activos": incidentes_activos,
        "documentos_criticos": documentos_criticos,
        "vehiculos_bloqueados": vehiculos_bloqueados,
        "mantenciones_abiertas": mantenciones_abiertas,
    }


# ─────────────────────────────────────────────────────────────────────────────
# DATOS PARA GRÁFICOS
# ─────────────────────────────────────────────────────────────────────────────

def obtener_asignaciones_por_estado(session) -> list[dict]:
    datos = _conteo_por_estado(
        session,
        Asignacion,
        Asignacion.estado_asignacion,
        [
            "Solicitada",
            "Pendiente",
            "Confirmada",
            "En_Ejecucion",
            "Con_Incidencia",
            "Completada",
            "Completada_Con_Incidencia",
            "Fallida",
            "Fallida_Parcial",
            "Cerrada",
        ],
        _ASIGNACION_DISPLAY,
    )
    return _filtrar_ceros(datos)


def obtener_incidentes_por_estado(session) -> list[dict]:
    datos = _conteo_por_estado(
        session,
        Incidente,
        Incidente.estado_incidente,
        [
            "Registrado",
            "En_Analisis",
            "En_Gestion",
            "Resuelto",
            "Cerrado",
        ],
        _INCIDENTE_DISPLAY,
    )
    return _filtrar_ceros(datos)


def obtener_documentos_por_estado(session) -> list[dict]:
    datos = _conteo_por_estado(
        session,
        DocumentacionVehiculo,
        DocumentacionVehiculo.estado_documental,
        [
            "Vigente",
            "Por_Vencer",
            "Vencido",
        ],
        _DOCUMENTO_DISPLAY,
    )
    return _filtrar_ceros(datos)


def obtener_vehiculos_por_estado(session) -> list[dict]:
    datos = _conteo_por_estado(
        session,
        Vehiculo,
        Vehiculo.estado_operacional,
        [
            "Disponible",
            "Reservado",
            "En_Ruta",
            "En_Mantencion",
            "Fuera_de_Servicio",
            "Bloqueado",
        ],
        _VEHICULO_DISPLAY,
    )
    return _filtrar_ceros(datos)


def obtener_mantenimientos_por_estado(session) -> list[dict]:
    datos = _conteo_por_estado(
        session,
        Mantenimiento,
        Mantenimiento.estado,
        [
            "Pendiente",
            "Programada",
            "En_Revision",
            "En_Espera_Repuestos",
            "Completada",
        ],
        _MANTENIMIENTO_DISPLAY,
    )
    return _filtrar_ceros(datos)


# ─────────────────────────────────────────────────────────────────────────────
# HISTORIAL DE ASIGNACIONES
# ─────────────────────────────────────────────────────────────────────────────

def obtener_historial_asignaciones(session) -> list[dict]:
    """
    Retorna historial completo de asignaciones usando la query existente.
    """
    return asignaciones_queries.obtener_todas(session)


# ─────────────────────────────────────────────────────────────────────────────
# INCIDENTES
# ─────────────────────────────────────────────────────────────────────────────

def obtener_incidentes_reporte(session) -> list[dict]:
    """
    Retorna incidentes para tabla de reportes.
    """

    incidentes = (
        session.query(Incidente)
        .options(
            joinedload(Incidente.asignacion)
            .joinedload(Asignacion.solicitud)
            .joinedload(Solicitud.sucursal_origen),

            joinedload(Incidente.asignacion)
            .joinedload(Asignacion.solicitud)
            .joinedload(Solicitud.sucursal_destino),

            joinedload(Incidente.asignacion)
            .joinedload(Asignacion.vehiculo),

            joinedload(Incidente.asignacion)
            .joinedload(Asignacion.conductor)
            .joinedload(Conductor.usuario),
        )
        .order_by(Incidente.id.desc())
        .all()
    )

    resultado = []

    for inc in incidentes:
        asig = inc.asignacion

        resultado.append({
            "id": inc.folio(),
            "asignacion": asig.folio() if asig else "—",
            "vehiculo": asig.vehiculo.patente if asig and asig.vehiculo else "—",
            "conductor": _nombre_conductor(asig),
            "ruta": _ruta_asignacion(asig),
            "gravedad": _estado_display(inc.clasificacion_gravedad),
            "estado": _estado_display(inc.estado_incidente, _INCIDENTE_DISPLAY),
            "reportado": (
                inc.fecha_hora_reporte.strftime("%Y-%m-%d %H:%M")
                if inc.fecha_hora_reporte
                else "—"
            ),
        })

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENTACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def obtener_documentacion_reporte(session) -> list[dict]:
    """
    Retorna documentos vencidos o por vencer.
    """

    documentos = (
        session.query(DocumentacionVehiculo)
        .options(joinedload(DocumentacionVehiculo.vehiculo))
        .filter(DocumentacionVehiculo.estado_documental.in_(["Vencido", "Por_Vencer"]))
        .order_by(DocumentacionVehiculo.estado_documental.asc())
        .all()
    )

    hoy = date.today()
    resultado = []

    for doc in documentos:
        dias = 0

        try:
            vence = datetime.strptime(doc.fecha_vencimiento, "%Y-%m-%d").date()
            dias = (vence - hoy).days
        except (ValueError, TypeError):
            pass

        resultado.append({
            "vehiculo": doc.vehiculo.patente if doc.vehiculo else "—",
            "documento": _estado_display(doc.tipo_documento),
            "vencimiento": doc.fecha_vencimiento or "—",
            "dias_restantes": dias,
            "estado": _estado_display(doc.estado_documental, _DOCUMENTO_DISPLAY),
        })

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# MANTENIMIENTO
# Se mantiene por compatibilidad si después quieres tabla de detalle.
# ─────────────────────────────────────────────────────────────────────────────

def obtener_mantenimiento_reporte(session) -> list[dict]:
    """
    Retorna órdenes de mantenimiento para reportes.
    """

    mantenimientos = (
        session.query(Mantenimiento)
        .options(
            joinedload(Mantenimiento.vehiculo),
            joinedload(Mantenimiento.incidente),
        )
        .order_by(Mantenimiento.id.desc())
        .all()
    )

    resultado = []

    for m in mantenimientos:
        resultado.append({
            "id": m.folio(),
            "vehiculo": m.vehiculo.patente if m.vehiculo else "—",
            "tipo": _estado_display(m.tipo_mantencion),
            "prioridad": m.prioridad or "—",
            "estado": _estado_display(m.estado, _MANTENIMIENTO_DISPLAY),
            "incidente": m.incidente.folio() if m.incidente else "—",
            "ingreso": (
                m.fecha_ingreso.strftime("%Y-%m-%d")
                if m.fecha_ingreso
                else "—"
            ),
            "egreso": (
                m.fecha_egreso_real.strftime("%Y-%m-%d")
                if m.fecha_egreso_real
                else "—"
            ),
        })

    return resultado