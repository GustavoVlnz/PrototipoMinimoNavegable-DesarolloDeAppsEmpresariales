"""
dashboard_logic.py
app/logic/dashboard_logic.py

"""

from datetime import date, datetime

from sqlalchemy.orm import joinedload

from app.data.database import get_session
from app.data.models import (
    Asignacion,
    Conductor,
    DocumentacionVehiculo,
    Incidente,
    Solicitud,
    Vehiculo,
)
from app.data.queries.conductores_queries import obtener_conductores_por_estado
from app.data.queries.vehiculos_queries import obtener_vehiculos_por_estado
from app.data.queries.asignaciones_queries import _asignacion_a_dict


# ─── Nivel visual de cada tipo de alerta ──────
_NIVEL_ALERTA = {
    "mantencion": "critico",     # rojo
    "incidente":  "critico",     # rojo
    "documento_vencido":  "advertencia",  # naranja
    "documento_por_vencer": "advertencia",
    "solicitud":  "info",        # azul
}


# ══════════════════════════════════════════════════════════════════════════════
# TARJETAS
# ══════════════════════════════════════════════════════════════════════════════

def obtener_resumen_cards() -> dict:
    #Conteos para las 6 tarjetas del dashboard.
    return {
        "vehiculos_disponibles":   len(obtener_vehiculos_por_estado("Disponible")),
        "en_ruta":                 len(obtener_vehiculos_por_estado("En_Ruta")),
        "bloqueados_fuera_serv":   (
            len(obtener_vehiculos_por_estado("Bloqueado")) +
            len(obtener_vehiculos_por_estado("Fuera_de_Servicio"))
        ),
        "en_mantencion":           len(obtener_vehiculos_por_estado("En_Mantencion")),
        "conductores_disponibles": len(obtener_conductores_por_estado("Disponible")),
        "alertas_activas":         0,   # se sobreescribe en obtener_datos_dashboard
    }


# ══════════════════════════════════════════════════════════════════════════════
# ASIGNACIONES DEL DÍA
# ══════════════════════════════════════════════════════════════════════════════

def obtener_asignaciones_hoy() -> list[dict]:
    hoy_inicio = datetime.combine(date.today(), datetime.min.time())
    hoy_fin    = datetime.combine(date.today(), datetime.max.time())

    with get_session() as session:
        asignaciones = (
            session.query(Asignacion)
            .options(
                joinedload(Asignacion.solicitud).joinedload(Solicitud.sucursal_origen),
                joinedload(Asignacion.solicitud).joinedload(Solicitud.sucursal_destino),
                joinedload(Asignacion.vehiculo),
                joinedload(Asignacion.conductor).joinedload(Conductor.usuario),
                joinedload(Asignacion.trazabilidad),
            )
            .filter(Asignacion.fecha_asignacion.between(hoy_inicio, hoy_fin))
            .order_by(Asignacion.id.asc())
            .all()
        )
        resultado = [_asignacion_a_dict(a) for a in asignaciones]

    return resultado


# ══════════════════════════════════════════════════════════════════════════════
# ALERTAS
# ══════════════════════════════════════════════════════════════════════════════

def obtener_alertas() -> list[dict]:

    alertas: list[dict] = []
    hoy = date.today()

    with get_session() as session:
        vehiculos_bloqueados = (
            session.query(Vehiculo)
            .filter(Vehiculo.estado_operacional == "Bloqueado")
            .options(joinedload(Vehiculo.mantenimientos))
            .all()
        )
        for v in vehiculos_bloqueados:
            tiene_ot_activa = any(
                m.tipo_mantencion == "Preventiva" and m.estado != "Completada"
                for m in v.mantenimientos
            )
            if not tiene_ot_activa:
                continue

            meses_str = ""
            if v.ultima_mantencion:
                try:
                    ultima = datetime.strptime(v.ultima_mantencion, "%Y-%m-%d").date()
                    meses = (hoy - ultima).days // 30
                    if meses > 0:
                        meses_str = f" (+{meses} meses)"
                except ValueError:
                    pass

            alertas.append({
                "tipo":    "mantencion",
                "nivel":   "critico",
                "folio":   v.patente,
                "mensaje": f"{v.patente} bloqueado — mantención preventiva vencida{meses_str}",
            })

        # ── 2. Incidentes activos con Falla_Critica ───────────────────────────
        # Estados activos: todos menos Resuelto y Cerrado.
        incidentes_criticos = (
            session.query(Incidente)
            .options(
                joinedload(Incidente.asignacion).joinedload(Asignacion.vehiculo)
            )
            .filter(
                Incidente.clasificacion_gravedad == "Falla_Critica",
                Incidente.estado_incidente.notin_(["Resuelto", "Cerrado"]),
            )
            .all()
        )
        for inc in incidentes_criticos:
            patente = (
                inc.asignacion.vehiculo.patente
                if inc.asignacion and inc.asignacion.vehiculo
                else "—"
            )
            desc_corta = (inc.descripcion_falla or "")[:60]
            alertas.append({
                "tipo":    "incidente",
                "nivel":   "critico",
                "folio":   inc.folio(),
                "mensaje": f"{inc.folio()} activo — falla crítica en {patente}: {desc_corta}",
            })

        # ── 3. Documentos vencidos ────────────────────────────────────────────
        docs_vencidos = (
            session.query(DocumentacionVehiculo)
            .options(joinedload(DocumentacionVehiculo.vehiculo))
            .filter(DocumentacionVehiculo.estado_documental == "Vencido")
            .all()
        )
        for doc in docs_vencidos:
            patente      = doc.vehiculo.patente if doc.vehiculo else "—"
            tipo_legible = doc.tipo_documento.replace("_", " ")

            # Días desde el vencimiento (para el mensaje)
            dias_str = ""
            try:
                vence = datetime.strptime(doc.fecha_vencimiento, "%Y-%m-%d").date()
                dias_vencido = (hoy - vence).days
                if dias_vencido > 0:
                    dias_str = f" (vencido hace {dias_vencido} días)"
            except (ValueError, TypeError):
                pass

            alertas.append({
                "tipo":    "documento",
                "nivel":   "advertencia",
                "folio":   patente,
                "mensaje": f"{patente} — {tipo_legible} vencido{dias_str}",
            })

        # ── 4. Documentos por vencer ──────────────────────────────────────────
        docs_por_vencer = (
            session.query(DocumentacionVehiculo)
            .options(joinedload(DocumentacionVehiculo.vehiculo))
            .filter(DocumentacionVehiculo.estado_documental == "Por_Vencer")
            .all()
        )
        for doc in docs_por_vencer:
            patente      = doc.vehiculo.patente if doc.vehiculo else "—"
            tipo_legible = doc.tipo_documento.replace("_", " ")

            dias_str = ""
            try:
                vence = datetime.strptime(doc.fecha_vencimiento, "%Y-%m-%d").date()
                dias_restantes = (vence - hoy).days
                dias_str = f" (vence en {dias_restantes} días — {doc.fecha_vencimiento})"
            except (ValueError, TypeError):
                pass

            alertas.append({
                "tipo":    "documento",
                "nivel":   "advertencia",
                "folio":   patente,
                "mensaje": f"{patente} — {tipo_legible} por vencer{dias_str}",
            })

        # ── 5. Solicitudes pendientes de reasignación ─────────────────────────
        solicitudes_pendientes = (
            session.query(Solicitud)
            .filter(Solicitud.estado_solicitud == "Pendiente_Reasignacion")
            .all()
        )
        for sol in solicitudes_pendientes:
            alertas.append({
                "tipo":    "solicitud",
                "nivel":   "info",
                "folio":   sol.folio(),
                "mensaje": f"{sol.folio()} pendiente de reasignación tras incidente en ruta",
            })

    return alertas


# ══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA ÚNICO
# ══════════════════════════════════════════════════════════════════════════════

def obtener_datos_dashboard() -> dict:
    alertas            = obtener_alertas()
    cards              = obtener_resumen_cards()
    cards["alertas_activas"] = len(alertas)

    return {
        "cards":            cards,
        "asignaciones_hoy": obtener_asignaciones_hoy(),
        "alertas":          alertas,
    }