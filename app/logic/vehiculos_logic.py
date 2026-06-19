"""
vehiculos_logic.py
app/logic/vehiculos_logic.py
"""

from __future__ import annotations

from datetime import date, datetime

TIPOS_VEHICULO = ["Camioneta", "Furgon", "Camion Liviano"]

ESTADOS_VEHICULO = [
    "Disponible",
    "Reservado",
    "En Ruta",
    "En Mantencion",
    "Fuera de Servicio",
    "Bloqueado",
]

ESTADOS_NO_ASIGNABLES = ["Bloqueado", "En Mantencion", "Fuera de Servicio", "En Ruta"]


class ResultadoOperacion:
    """Encapsula el resultado (éxito/fallo) de una operación sobre un vehículo."""

    def __init__(self, ok: bool, mensaje: str):
        self.ok = ok
        self.mensaje = mensaje

    def __bool__(self) -> bool:
        return self.ok

    def __repr__(self) -> str:
        estado = "OK" if self.ok else "ERROR"
        return f"ResultadoOperacion({estado}: {self.mensaje})"


# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIONES DE REGISTRO
# ─────────────────────────────────────────────────────────────────────────────

def validar_patente(patente: str) -> ResultadoOperacion:
    """
    Valida el formato de una patente chilena.
    Acepta formato antiguo (XX-NNNN) y nuevo (XXNN-NN).
    También acepta el formato interno del proyecto (XXXX-NN).
    """
    if not patente or not patente.strip():
        return ResultadoOperacion(False, "La patente es obligatoria.")
    patente = patente.strip().upper()
    if len(patente) < 5 or len(patente) > 10:
        return ResultadoOperacion(False, f"Patente '{patente}' tiene formato inválido.")
    return ResultadoOperacion(True, f"Patente '{patente}' válida.")


def validar_nuevo_vehiculo(
    patente: str,
    tipo: str,
    capacidad_kg: int,
    vehiculos_existentes: list[dict],
) -> ResultadoOperacion:
    resultado_patente = validar_patente(patente)
    if not resultado_patente:
        return resultado_patente

    patente_upper = patente.strip().upper()
    patentes_actuales = {v["patente"].upper() for v in vehiculos_existentes}
    if patente_upper in patentes_actuales:
        return ResultadoOperacion(False, f"Ya existe un vehículo con patente '{patente_upper}'.")

    tipo_normalizado = tipo.replace("_", " ")
    tipos_validos = [t.replace("_", " ") for t in TIPOS_VEHICULO]
    if tipo_normalizado not in tipos_validos:
        return ResultadoOperacion(False, f"Tipo de vehículo inválido: '{tipo}'.")

    if capacidad_kg <= 0:
        return ResultadoOperacion(False, "La capacidad debe ser mayor a 0 kg.")

    return ResultadoOperacion(True, f"Vehículo {patente_upper} listo para registrar.")


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTAS DE ELEGIBILIDAD 
# ─────────────────────────────────────────────────────────────────────────────

def puede_asignarse(vehiculo: dict) -> bool:
    """Retorna True si el vehículo está en condiciones de ser asignado."""
    estado = vehiculo.get("estado", "").replace("_", " ")
    return estado not in ESTADOS_NO_ASIGNABLES


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTAS Y ANÁLISIS
# ─────────────────────────────────────────────────────────────────────────────

def resumen_flota(vehiculos: list[dict]) -> dict:

    def count(estado: str) -> int:
        return sum(1 for v in vehiculos if v.get("estado", "").replace("_", " ") == estado)

    return {
        "disponibles":    count("Disponible"),
        "reservados":     count("Reservado"),
        "en_ruta":        count("En Ruta"),
        "en_mantencion":  count("En Mantencion"),
        "bloqueados":     count("Bloqueado"),
        "fuera_servicio": count("Fuera de Servicio"),
        "total":          len(vehiculos),
    }


def _parse_fecha(fecha_str: str) -> date | None:
    """Intenta parsear una fecha en formato ISO (YYYY-MM-DD)."""
    if not fecha_str or fecha_str == "—":
        return None
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def vehiculos_con_documentacion_vencida(vehiculos: list[dict]) -> list[dict]:
    """
    Retorna los vehiculos que tienen al menos un documento
    (seguro_vence, permiso_vence, revision_tecnica) con fecha pasada.

    """
    hoy = date.today()
    alertas = []
    for v in vehiculos:
        campos = ["seguro_vence", "permiso_vence", "revision_tecnica"]
        for campo in campos:
            fecha = _parse_fecha(v.get(campo, ""))
            if fecha is not None and fecha < hoy:
                alertas.append(v)
                break
    return alertas