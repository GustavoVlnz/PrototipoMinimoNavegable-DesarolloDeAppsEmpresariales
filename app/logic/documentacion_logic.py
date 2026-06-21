# app/logic/documentacion_logic.py

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import joinedload

from app.core.events import event_bus
from app.data.models import DocumentacionVehiculo, Vehiculo
from app.logic import transition_service
from app.logic.transition_service import TransitionError


DIAS_ALERTA_POR_VENCER = 30

TIPOS_DOCUMENTO_VEHICULO = [
    "Permiso Circulación",
    "Seguro Obligatorio",
    "Revisión Técnica",
]

TIPOS_DOCUMENTO_CONDUCTOR = [
    "Licencia de Conducir",
]


class ResultadoOperacion:
    def __init__(self, ok: bool, mensaje: str):
        self.ok = ok
        self.mensaje = mensaje

    def __bool__(self) -> bool:
        return self.ok

    def __repr__(self) -> str:
        estado = "OK" if self.ok else "ERROR"
        return f"ResultadoOperacion({estado}: {self.mensaje})"


# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULO DE VIGENCIA
# ─────────────────────────────────────────────────────────────────────────────

def _parse_fecha(fecha_str: str) -> Optional[date]:
    if not fecha_str:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(fecha_str, fmt).date()
        except ValueError:
            continue

    return None


def calcular_dias_restantes(fecha_vencimiento: str) -> Optional[int]:
    fecha = _parse_fecha(fecha_vencimiento)
    if fecha is None:
        return None

    return (fecha - date.today()).days


def calcular_estado_vigencia(dias_restantes: Optional[int]) -> str:
    """
    Estado visible para UI.
    """
    if dias_restantes is None:
        return "Sin datos"
    if dias_restantes < 0:
        return "Vencida"
    if dias_restantes <= DIAS_ALERTA_POR_VENCER:
        return "Por vencer"
    return "Vigente"


def calcular_estado_documental_bd(dias_restantes: Optional[int]) -> str | None:
    """
    Estado real que se guarda en BD.
    """
    if dias_restantes is None:
        return None
    if dias_restantes < 0:
        return "Vencido"
    if dias_restantes <= DIAS_ALERTA_POR_VENCER:
        return "Por_Vencer"
    return "Vigente"


def actualizar_vigencia_documento(doc: dict) -> dict:
    dias = calcular_dias_restantes(doc.get("vencimiento", ""))
    doc["dias_restantes"] = dias if dias is not None else 0
    doc["estado"] = calcular_estado_vigencia(dias)
    return doc


def actualizar_todos_los_documentos(documentos: list | None = None) -> list[dict]:
    """
    Recalcula vigencia sobre una lista ya cargada desde BD.

    Ya no usa DOCUMENTACION porque el proyecto dejó de trabajar con mock data.
    """
    if documentos is None:
        return []

    return [actualizar_vigencia_documento(d) for d in documentos]


# ─────────────────────────────────────────────────────────────────────────────
# SINCRONIZACIÓN REAL CON BD
# ─────────────────────────────────────────────────────────────────────────────

def sincronizar_vencimientos(session, emitir_eventos: bool = True) -> dict:
    """
    Sincroniza el estado_documental real en BD según fecha_vencimiento.

    Reglas:
    - fecha vencida        → Vencido
    - fecha dentro de 30d  → Por_Vencer
    - fecha posterior      → Vigente

    Si un documento queda Vencido, se reevalúa la disponibilidad del vehículo.
    Si un documento vuelve a Vigente, también se reevalúa la disponibilidad.
    """
    documentos = (
        session.query(DocumentacionVehiculo)
        .options(
            joinedload(DocumentacionVehiculo.vehiculo).joinedload(Vehiculo.documentos),
            joinedload(DocumentacionVehiculo.vehiculo).joinedload(Vehiculo.mantenimientos),
        )
        .all()
    )

    docs_actualizados = 0
    vehiculos_afectados = {}

    for doc in documentos:
        dias = calcular_dias_restantes(doc.fecha_vencimiento)
        estado_objetivo = calcular_estado_documental_bd(dias)

        if estado_objetivo is None:
            continue

        if doc.estado_documental != estado_objetivo:
            doc.estado_documental = estado_objetivo
            docs_actualizados += 1

            if doc.vehiculo:
                vehiculos_afectados[doc.vehiculo.id] = doc.vehiculo

    for vehiculo in vehiculos_afectados.values():
        try:
            transition_service.sincronizar_disponibilidad_vehiculo(session, vehiculo)
        except TransitionError:
            pass

    if docs_actualizados:
        session.commit()

        if emitir_eventos:
            event_bus.documento_actualizado.emit()
            event_bus.vehiculo_actualizado.emit()

    return {
        "documentos_actualizados": docs_actualizados,
        "vehiculos_afectados": len(vehiculos_afectados),
    }


# ─────────────────────────────────────────────────────────────────────────────
# OPERACIONES DE RENOVACIÓN EN MEMORIA
# ─────────────────────────────────────────────────────────────────────────────

def renovar_documento(doc: dict, nueva_fecha_vencimiento: str) -> ResultadoOperacion:
    nueva_fecha = _parse_fecha(nueva_fecha_vencimiento)

    if nueva_fecha is None:
        return ResultadoOperacion(
            False,
            f"Fecha inválida: '{nueva_fecha_vencimiento}'. Use formato YYYY-MM-DD o DD/MM/YYYY."
        )

    if nueva_fecha <= date.today():
        return ResultadoOperacion(
            False,
            f"La nueva fecha de vencimiento ({nueva_fecha_vencimiento}) debe ser posterior a hoy."
        )

    fecha_anterior = doc.get("vencimiento", "—")
    doc["vencimiento"] = nueva_fecha.strftime("%Y-%m-%d")
    actualizar_vigencia_documento(doc)

    return ResultadoOperacion(
        True,
        f"Documento '{doc.get('doc_tipo')}' de '{doc.get('vehiculo')}' renovado. "
        f"Vencimiento actualizado: {fecha_anterior} → {doc['vencimiento']}."
    )


# ─────────────────────────────────────────────────────────────────────────────
# ALERTAS Y CONSULTAS
# ─────────────────────────────────────────────────────────────────────────────

def documentos_vencidos(documentos: list[dict]) -> list[dict]:
    return [d for d in documentos if d.get("estado") == "Vencida"]


def documentos_por_vencer(documentos: list[dict]) -> list[dict]:
    return [d for d in documentos if d.get("estado") == "Por vencer"]


def documentos_criticos(documentos: list[dict]) -> list[dict]:
    criticos = [
        d for d in documentos
        if d.get("estado") in ("Vencida", "Por vencer")
    ]

    return sorted(criticos, key=lambda d: d.get("dias_restantes", 0))


def mensaje_alerta(doc: dict) -> str:
    dias = doc.get("dias_restantes", 0)
    entidad = doc.get("vehiculo", "—")
    tipo = doc.get("doc_tipo", "Documento")
    vencimiento = doc.get("vencimiento", "—")

    if dias < 0:
        return f"{entidad} — {tipo}: VENCIDO hace {abs(dias)} días"

    return f"{entidad} — {tipo}: vence en {dias} días ({vencimiento})"


def tipo_alerta(doc: dict) -> str:
    return "critica" if doc.get("estado") == "Vencida" else "advertencia"


def resumen_documentacion(documentos: list[dict]) -> dict:
    return {
        "total":      len(documentos),
        "vigentes":   sum(1 for d in documentos if d.get("estado") == "Vigente"),
        "por_vencer": sum(1 for d in documentos if d.get("estado") == "Por vencer"),
        "vencidos":   sum(1 for d in documentos if d.get("estado") == "Vencida"),
        "criticos":   sum(1 for d in documentos if d.get("estado") in ("Vencida", "Por vencer")),
    }


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRACIÓN: ALERTAS DE LICENCIAS DE CONDUCTORES
# ─────────────────────────────────────────────────────────────────────────────

def generar_documentos_conductores(conductores: list[dict]) -> list[dict]:
    docs = []

    for c in conductores:
        vencimiento = c.get("licencia_vence", "")
        dias = calcular_dias_restantes(vencimiento)

        docs.append({
            "vehiculo":       f"{c['nombre']} (conductor)",
            "doc_tipo":       "Licencia de Conducir",
            "vencimiento":    vencimiento,
            "dias_restantes": dias if dias is not None else 0,
            "estado":         calcular_estado_vigencia(dias),
            "_ref_conductor_id": c.get("id"),
        })

    return docs


def documentos_completos(
    documentos: list[dict],
    conductores: list[dict],
    incluir_conductores: bool = True,
) -> list[dict]:
    base = list(documentos)

    if incluir_conductores:
        base += generar_documentos_conductores(conductores)

    return base