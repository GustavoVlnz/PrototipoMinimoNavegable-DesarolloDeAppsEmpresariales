from __future__ import annotations

from datetime import datetime
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

TIPOS_INCIDENTE = [
    "Accidente",
    "Daño vehículo",
    "Infracción",
    "Retraso",
    "Cliente",
    "Otro",
]

GRAVEDADES = [
    "Menor",
    "Operativa",
    "Crítica",
]

# Mapa de transiciones válidas: estado_actual → [estados_destino_válidos]
TRANSICIONES_VALIDAS = {
    "Registrado": ["En gestión", "En Análisis"],
    "En Análisis": ["En gestión", "Registrado"],
    "En gestión": ["Resuelto"],
    "Resuelto": ["Cerrado"],
    "Cerrado": [],
}


# ─────────────────────────────────────────────────────────────────────────────
# RESULTADO TIPADO
# ─────────────────────────────────────────────────────────────────────────────

class ResultadoOperacion:
    """Encapsula el resultado (éxito/fallo) de una operación sobre un incidente."""

    def __init__(self, ok: bool, mensaje: str):
        self.ok = ok
        self.mensaje = mensaje

    def __bool__(self) -> bool:
        return self.ok

    def __repr__(self) -> str:
        estado = "OK" if self.ok else "ERROR"
        return f"ResultadoOperacion({estado}: {self.mensaje})"


# ─────────────────────────────────────────────────────────────────────────────
# OPERACIONES DE CREACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def reportar_incidente(
    asignacion_id: str,
    vehiculo_patente: str,
    conductor: str,
    tipo: str,
    gravedad: str,
    descripcion: str,
    incidentes: list[dict],
) -> ResultadoOperacion:
    """
    Registra un nuevo incidente en la lista.

    Reglas:
        - La descripción es obligatoria.
        - Si gravedad es 'Crítica', pasa directamente a 'En gestión' (escalado automático).
        - Incidentes normales comienzan en estado 'Registrado'.

    Parámetros:
        asignacion_id:     ID de la asignación afectada.
        vehiculo_patente:  Patente del vehículo.
        conductor:         Nombre del conductor.
        tipo:              Tipo de incidente (debe estar en TIPOS_INCIDENTE).
        gravedad:          Nivel de gravedad (debe estar en GRAVEDADES).
        descripcion:       Descripción detallada del incidente.
        incidentes:        Lista de incidentes (usa INCIDENTES por defecto).

    Retorna:
        ResultadoOperacion con los datos del nuevo incidente.
    """
    if not descripcion or not descripcion.strip():
        return ResultadoOperacion(False, "La descripción del incidente es obligatoria.")

    if tipo not in TIPOS_INCIDENTE:
        return ResultadoOperacion(False, f"Tipo de incidente inválido: {tipo}")

    if gravedad not in GRAVEDADES:
        return ResultadoOperacion(False, f"Gravedad inválida: {gravedad}")

    # Generar ID único
    max_num = 0
    for inc in incidentes:
        try:
            num = int(inc.get("id", "INC-0").replace("INC-", ""))
            max_num = max(max_num, num)
        except (ValueError, AttributeError):
            pass
    nuevo_id = f"INC-{max_num + 1:03d}"

    # Determinar estado inicial según gravedad
    estado_inicial = "En gestión" if gravedad == "Crítica" else "Registrado"

    nuevo_incidente = {
        "id": nuevo_id,
        "asignacion_id": asignacion_id,
        "vehiculo_patente": vehiculo_patente,
        "conductor": conductor,
        "tipo": tipo,
        "gravedad": gravedad,
        "estado": estado_inicial,
        "descripcion": descripcion,
        "resolucion": None,
        "hora_reporte": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "supervisor": None,
    }

    incidentes.append(nuevo_incidente)

    msg = f"Incidente {nuevo_id} reportado correctamente."
    if gravedad == "Crítica":
        msg += " (Escalado automático a 'En gestión' por gravedad crítica)"

    return ResultadoOperacion(True, msg)


# ─────────────────────────────────────────────────────────────────────────────
# OPERACIONES DE ESTADO
# ─────────────────────────────────────────────────────────────────────────────

def marcar_en_gestion(incidente: dict) -> ResultadoOperacion:
    """
    Marca el incidente como 'En gestión'.

    Reglas:
        - Válido desde estado 'Registrado' o 'En Análisis'.
        - La transición debe ser válida según TRANSICIONES_VALIDAS.
    """
    estado_actual = incidente.get("estado")

    if estado_actual not in TRANSICIONES_VALIDAS:
        return ResultadoOperacion(
            False,
            f"Estado desconocido: {estado_actual}"
        )

    if "En gestión" not in TRANSICIONES_VALIDAS.get(estado_actual, []):
        return ResultadoOperacion(
            False,
            f"No se puede marcar como 'En gestión' desde estado '{estado_actual}'."
        )

    incidente["estado"] = "En gestión"
    return ResultadoOperacion(
        True,
        f"Incidente {incidente['id']} marcado como 'En gestión'."
    )


def escalar_incidente(incidente: dict, motivo: str = "") -> ResultadoOperacion:
    """
    Escala el incidente a 'En Análisis' para revisión supervisada.

    Reglas:
        - Válido desde estado 'Registrado'.
        - El motivo es opcional pero registrable para auditoría.
    """
    estado_actual = incidente.get("estado")

    if estado_actual != "Registrado":
        return ResultadoOperacion(
            False,
            f"Solo se puede escalar desde 'Registrado'. Estado actual: {estado_actual}."
        )

    incidente["estado"] = "En Análisis"
    if motivo and motivo.strip():
        # Registrar motivo en descripción extendida (en BD se usaría campo separado)
        if incidente.get("descripcion"):
            incidente["descripcion"] += f"\n[Motivo escalado: {motivo}]"

    return ResultadoOperacion(
        True,
        f"Incidente {incidente['id']} escalado a 'En Análisis'."
    )


def marcar_resuelto(incidente: dict, resolucion: str) -> ResultadoOperacion:
    """
    Marca el incidente como 'Resuelto' registrando la descripción de la resolución.

    Reglas:
        - Válido solo desde estado 'En gestión'.
        - La descripción de resolución es obligatoria.
    """
    if not resolucion or not resolucion.strip():
        return ResultadoOperacion(False, "La descripción de la resolución es obligatoria.")

    estado_actual = incidente.get("estado")

    if estado_actual != "En gestión":
        return ResultadoOperacion(
            False,
            f"Solo se puede marcar como 'Resuelto' desde 'En gestión'. "
            f"Estado actual: {estado_actual}."
        )

    incidente["estado"] = "Resuelto"
    incidente["resolucion"] = resolucion
    return ResultadoOperacion(
        True,
        f"Incidente {incidente['id']} marcado como 'Resuelto'."
    )


def cerrar_incidente(incidente: dict) -> ResultadoOperacion:
    """
    Cierra formalmente el incidente.

    Reglas:
        - Válido solo desde estado 'Resuelto'.
        - Esta acción es definitiva y no reversible.
    """
    estado_actual = incidente.get("estado")

    if estado_actual != "Resuelto":
        return ResultadoOperacion(
            False,
            f"Solo se puede cerrar desde 'Resuelto'. Estado actual: {estado_actual}."
        )

    incidente["estado"] = "Cerrado"
    return ResultadoOperacion(
        True,
        f"Incidente {incidente['id']} cerrado formalmente."
    )


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTAS Y ANÁLISIS
# ─────────────────────────────────────────────────────────────────────────────

def acciones_disponibles(incidente: dict) -> list[str]:
    """
    Retorna lista de acciones válidas para el incidente según su estado actual.

    Posibles acciones:
        - "escalar":    Escalar a En Análisis (solo desde Registrado)
        - "en_gestion": Marcar En gestión (desde Registrado o En Análisis)
        - "resolver":   Registrar resolución (solo desde En gestión)
        - "cerrar":     Cerrar (solo desde Resuelto)
    """
    estado = incidente.get("estado")
    acciones = []

    if estado == "Registrado":
        acciones.append("escalar")
        acciones.append("en_gestion")
    elif estado == "En Análisis":
        acciones.append("en_gestion")
    elif estado == "En gestión":
        acciones.append("resolver")
    elif estado == "Resuelto":
        acciones.append("cerrar")
    # "Cerrado" → sin acciones

    return acciones


def incidentes_criticos(incidentes: list[dict]) -> list[dict]:
    """Retorna incidentes con gravedad 'Crítica' que estén activos (no cerrados)."""
    return [
        inc for inc in incidentes
        if inc.get("gravedad") == "Crítica" and inc.get("estado") != "Cerrado"
    ]


def resumen_incidentes(incidentes: list[dict]) -> dict:
    """
    Retorna un diccionario con conteos desglosados por estado.

    Clave del resumen:
        - registrados:    Count de estado 'Registrado'
        - en_analisis:    Count de estado 'En Análisis'
        - en_gestion:     Count de estado 'En gestión'
        - resueltos:      Count de estado 'Resuelto'
        - cerrados:       Count de estado 'Cerrado'
        - criticos_activos: Count de gravedad 'Crítica' y estado != 'Cerrado'
    """
    resumen = {
        "registrados": sum(1 for i in incidentes if i.get("estado") == "Registrado"),
        "en_analisis": sum(1 for i in incidentes if i.get("estado") == "En Análisis"),
        "en_gestion": sum(1 for i in incidentes if i.get("estado") == "En gestión"),
        "resueltos": sum(1 for i in incidentes if i.get("estado") == "Resuelto"),
        "cerrados": sum(1 for i in incidentes if i.get("estado") == "Cerrado"),
    }

    resumen["criticos_activos"] = len(incidentes_criticos(incidentes))

    return resumen