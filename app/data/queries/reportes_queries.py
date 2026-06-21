"""
reportes_queries.py
app/data/queries/reportes_queries.py

Consultas para el módulo de Reportes y Trazabilidad.
"""

from datetime import date, datetime

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


def _estado_display(valor: str | None) -> str:
    if not valor:
        return "—"
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
            "estado": _estado_display(inc.estado_incidente),
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
            "estado": _estado_display(doc.estado_documental),
        })

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# MANTENIMIENTO
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
            "estado": _estado_display(m.estado),
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