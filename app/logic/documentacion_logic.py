from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from app.data.mock_data import DOCUMENTACION, CONDUCTORES, VEHICULOS


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

DIAS_ALERTA_POR_VENCER = 30   # Umbral para clasificar como "Por vencer"
TIPOS_DOCUMENTO_VEHICULO = [
    "Permiso Circulación",
    "Seguro Obligatorio",
    "Revisión Técnica",
]
TIPOS_DOCUMENTO_CONDUCTOR = [
    "Licencia de Conducir",
]


# ─────────────────────────────────────────────────────────────────────────────
# RESULTADO TIPADO
# ─────────────────────────────────────────────────────────────────────────────

class ResultadoOperacion:
    """Encapsula el resultado de una operación de renovación."""

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
    """Parsea fechas en formatos ISO (YYYY-MM-DD) o DD/MM/YYYY."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(fecha_str, fmt).date()
        except ValueError:
            continue
    return None


def calcular_dias_restantes(fecha_vencimiento: str) -> Optional[int]:
    """
    Retorna cuántos días faltan para la fecha de vencimiento.
    Negativo si ya venció. None si la fecha no es parseable.
    """
    fecha = _parse_fecha(fecha_vencimiento)
    if fecha is None:
        return None
    return (fecha - date.today()).days


def calcular_estado_vigencia(dias_restantes: Optional[int]) -> str:
    """
    Retorna el estado de vigencia según los días restantes:
        - 'Vencida'    → días < 0
        - 'Por vencer' → 0 <= días <= DIAS_ALERTA_POR_VENCER
        - 'Vigente'    → días > DIAS_ALERTA_POR_VENCER
        - 'Sin datos'  → None
    """
    if dias_restantes is None:
        return "Sin datos"
    if dias_restantes < 0:
        return "Vencida"
    if dias_restantes <= DIAS_ALERTA_POR_VENCER:
        return "Por vencer"
    return "Vigente"


def actualizar_vigencia_documento(doc: dict) -> dict:
    """
    Recalcula y actualiza `dias_restantes` y `estado` de un documento
    según la fecha de vencimiento almacenada.
    Modifica el dict in-place y lo retorna.
    """
    dias = calcular_dias_restantes(doc.get("vencimiento", ""))
    doc["dias_restantes"] = dias if dias is not None else 0
    doc["estado"] = calcular_estado_vigencia(dias)
    return doc


def actualizar_todos_los_documentos(documentos: list | None = None) -> list[dict]:
    """
    Recalcula la vigencia de todos los documentos y retorna la lista actualizada.
    Útil para sincronizar el estado al iniciar la app o al cambiar de fecha.
    """
    fuente = documentos if documentos is not None else DOCUMENTACION
    return [actualizar_vigencia_documento(d) for d in fuente]


# ─────────────────────────────────────────────────────────────────────────────
# OPERACIONES DE RENOVACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def renovar_documento(doc: dict, nueva_fecha_vencimiento: str) -> ResultadoOperacion:
    """
    Registra la renovación de un documento actualizando su fecha de vencimiento.

    Parámetros:
        doc:                      El dict del documento a renovar.
        nueva_fecha_vencimiento:  Fecha en formato 'YYYY-MM-DD' o 'DD/MM/YYYY'.

    Reglas de validación:
        - La nueva fecha debe ser parseable.
        - La nueva fecha debe ser posterior a hoy (no se puede renovar hacia atrás).
    """
    nueva_fecha = _parse_fecha(nueva_fecha_vencimiento)
    if nueva_fecha is None:
        return ResultadoOperacion(
            False,
            f"Fecha inválida: '{nueva_fecha_vencimiento}'. "
            "Use formato YYYY-MM-DD o DD/MM/YYYY."
        )

    if nueva_fecha <= date.today():
        return ResultadoOperacion(
            False,
            f"La nueva fecha de vencimiento ({nueva_fecha_vencimiento}) "
            "debe ser posterior a hoy."
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

def documentos_vencidos(documentos: list | None = None) -> list[dict]:
    """Retorna documentos en estado 'Vencida'."""
    fuente = documentos if documentos is not None else DOCUMENTACION
    return [d for d in fuente if d.get("estado") == "Vencida"]


def documentos_por_vencer(documentos: list | None = None) -> list[dict]:
    """Retorna documentos en estado 'Por vencer'."""
    fuente = documentos if documentos is not None else DOCUMENTACION
    return [d for d in fuente if d.get("estado") == "Por vencer"]


def documentos_criticos(documentos: list | None = None) -> list[dict]:
    """Retorna vencidos + por vencer, ordenados por urgencia (días asc)."""
    fuente = documentos if documentos is not None else DOCUMENTACION
    criticos = [
        d for d in fuente
        if d.get("estado") in ("Vencida", "Por vencer")
    ]
    return sorted(criticos, key=lambda d: d.get("dias_restantes", 0))


def mensaje_alerta(doc: dict) -> str:
    """Genera el texto de alerta para un documento crítico."""
    dias = doc.get("dias_restantes", 0)
    entidad = doc.get("vehiculo", "—")
    tipo = doc.get("doc_tipo", "Documento")
    vencimiento = doc.get("vencimiento", "—")

    if dias < 0:
        return f"{entidad} — {tipo}: VENCIDO hace {abs(dias)} días"
    return f"{entidad} — {tipo}: vence en {dias} días ({vencimiento})"


def tipo_alerta(doc: dict) -> str:
    """Retorna 'critica' o 'advertencia' según el estado del documento."""
    return "critica" if doc.get("estado") == "Vencida" else "advertencia"


def resumen_documentacion(documentos: list | None = None) -> dict:
    """
    Retorna un dict con conteos rápidos para KPIs del módulo y del dashboard.

    Ejemplo de retorno:
        {
            "total": 6,
            "vigentes": 1,
            "por_vencer": 3,
            "vencidos": 2,
            "criticos": 5,
        }
    """
    fuente = documentos if documentos is not None else DOCUMENTACION
    return {
        "total":      len(fuente),
        "vigentes":   sum(1 for d in fuente if d.get("estado") == "Vigente"),
        "por_vencer": sum(1 for d in fuente if d.get("estado") == "Por vencer"),
        "vencidos":   sum(1 for d in fuente if d.get("estado") == "Vencida"),
        "criticos":   sum(1 for d in fuente if d.get("estado") in ("Vencida", "Por vencer")),
    }


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRACIÓN: ALERTAS DE LICENCIAS DE CONDUCTORES
# ─────────────────────────────────────────────────────────────────────────────

def generar_documentos_conductores(conductores: list | None = None) -> list[dict]:
    """
    Genera entradas de documentación para las licencias de conductores,
    en el mismo formato que DOCUMENTACION, para poder incluirlas en el módulo.

    Útil cuando se quiere mostrar licencias de conductores junto con
    los documentos de vehículos en una vista unificada.
    """
    fuente = conductores if conductores is not None else CONDUCTORES
    docs = []
    for c in fuente:
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
    documentos: list | None = None,
    conductores: list | None = None,
    incluir_conductores: bool = True
) -> list[dict]:
    """
    Retorna la lista combinada de documentos de vehículos y (opcionalmente)
    de licencias de conductores, todo en el mismo formato.
    """
    base = list(documentos if documentos is not None else DOCUMENTACION)
    if incluir_conductores:
        base += generar_documentos_conductores(conductores)
    return base