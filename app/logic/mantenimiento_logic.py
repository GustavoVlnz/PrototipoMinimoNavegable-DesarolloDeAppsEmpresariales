"""
mantenimiento_logic.py
app/logic/mantenimiento_logic.py
"""

from __future__ import annotations


TIPOS_MANTENCION = ["Preventiva", "Correctiva"]

PRIORIDADES = ["Alta", "Media", "Baja"]


# ─────────────────────────────────────────────────────────────────────────────
# RESULTADO TIPADO
# ─────────────────────────────────────────────────────────────────────────────

class ResultadoOperacion:
    """Encapsula el resultado (éxito/fallo) de una operación sobre una OT."""

    def __init__(self, ok: bool, mensaje: str):
        self.ok = ok
        self.mensaje = mensaje

    def __bool__(self) -> bool:
        return self.ok

    def __repr__(self) -> str:
        estado = "OK" if self.ok else "ERROR"
        return f"ResultadoOperacion({estado}: {self.mensaje})"


# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIONES DE CREACIÓN DE OT
# ─────────────────────────────────────────────────────────────────────────────

def validar_nueva_ot(
    vehiculo_id: int | None,
    tipo_mantencion: str,
    descripcion: str,
    prioridad: str,
) -> ResultadoOperacion:
    if not vehiculo_id:
        return ResultadoOperacion(False, "Debe seleccionar un vehículo.")

    if tipo_mantencion not in TIPOS_MANTENCION:
        return ResultadoOperacion(False, f"Tipo de mantención inválido: '{tipo_mantencion}'.")

    if not descripcion or not descripcion.strip():
        return ResultadoOperacion(False, "La descripción del trabajo es obligatoria.")

    if prioridad not in PRIORIDADES:
        return ResultadoOperacion(False, f"Prioridad inválida: '{prioridad}'.")

    return ResultadoOperacion(True, "OT lista para registrar.")


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTAS Y ANÁLISIS
# ─────────────────────────────────────────────────────────────────────────────

def resumen_mantenimientos(ordenes: list[dict]) -> dict:

    def count(estado: str) -> int:
        return sum(
            1 for o in ordenes
            if o.get("estado", "").replace("_", " ") == estado
        )

    activas_criticas = sum(
        1 for o in ordenes
        if o.get("prioridad") == "Alta"
        and o.get("estado", "").replace("_", " ") != "Completada"
    )

    return {
        "pendientes":       count("Pendiente"),
        "programadas":      count("Programada"),
        "en_revision":      count("En Revision"),
        "en_espera":        count("En Espera Repuestos"),
        "completadas":      count("Completada"),
        "criticas_activas": activas_criticas,
        "total":            len(ordenes),
    }


def ordenes_activas(ordenes: list[dict]) -> list[dict]:
    """Retorna OTs que no están en estado 'Completada'."""
    return [
        o for o in ordenes
        if o.get("estado", "").replace("_", " ") != "Completada"
    ]