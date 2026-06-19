#app/logic/conductores_logic.py

from __future__ import annotations

from datetime import date, datetime
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

DIAS_ALERTA_LICENCIA = 30   # Días previos al vencimiento para marcar alerta
ESTADOS_VALIDOS = {"Disponible", "Asignado", "En descanso", "No habilitado"}


# ─────────────────────────────────────────────────────────────────────────────
# RESULTADOS TIPADOS
# ─────────────────────────────────────────────────────────────────────────────

class ResultadoOperacion:
    """Encapsula el resultado (éxito/fallo) de una operación sobre un conductor."""

    def __init__(self, ok: bool, mensaje: str):
        self.ok = ok
        self.mensaje = mensaje

    def __bool__(self) -> bool:
        return self.ok

    def __repr__(self) -> str:
        estado = "OK" if self.ok else "ERROR"
        return f"ResultadoOperacion({estado}: {self.mensaje})"


# ─────────────────────────────────────────────────────────────────────────────
# VALIDACIONES (solo lectura, no mutan nada)
# ─────────────────────────────────────────────────────────────────────────────

def _parse_fecha(fecha_str: str) -> Optional[date]:
    """Intenta parsear una fecha en formato ISO (YYYY-MM-DD) o MM/YYYY."""
    for fmt in ("%Y-%m-%d", "%m/%Y"):
        try:
            return datetime.strptime(fecha_str, fmt).date()
        except ValueError:
            continue
    return None


def licencia_vencida(conductor: dict) -> bool:
    """Devuelve True si la licencia del conductor está vencida."""
    fecha = _parse_fecha(conductor.get("licencia_vence", ""))
    if fecha is None:
        return False
    return date.today() > fecha


def dias_para_vencimiento_licencia(conductor: dict) -> Optional[int]:
    """
    Retorna cuántos días faltan para que venza la licencia.
    Negativo si ya está vencida. None si la fecha no es parseable.
    """
    fecha = _parse_fecha(conductor.get("licencia_vence", ""))
    if fecha is None:
        return None
    return (fecha - date.today()).days


def alerta_licencia(conductor: dict) -> Optional[str]:
    """
    Devuelve una cadena de alerta si la licencia está vencida o próxima a vencer.
    Devuelve None si está vigente y sin riesgo inmediato.
    """
    dias = dias_para_vencimiento_licencia(conductor)
    if dias is None:
        return None
    if dias < 0:
        return f"Licencia vencida hace {abs(dias)} días"
    if dias <= DIAS_ALERTA_LICENCIA:
        return f"Licencia vence en {dias} días ({conductor['licencia_vence']})"
    return None


def puede_habilitarse(conductor: dict) -> ResultadoOperacion:
    """
    Verifica si un conductor puede pasar a habilitado, SIN mutar nada.
    La mutacion real la hace transition_service.habilitar_conductor().
    """
    if conductor.get("habilitado"):
        return ResultadoOperacion(False, f"{conductor['nombre']} ya está habilitado.")
    if licencia_vencida(conductor):
        return ResultadoOperacion(
            False,
            f"No se puede habilitar a {conductor['nombre']}: licencia vencida el "
            f"{conductor.get('licencia_vence', '—')}. Actualice la licencia primero."
        )
    return ResultadoOperacion(True, f"{conductor['nombre']} puede habilitarse.")


def puede_deshabilitarse(conductor: dict) -> ResultadoOperacion:
    """
    Verifica si un conductor puede deshabilitarse, SIN mutar nada.
    La mutacion real la hace transition_service.deshabilitar_conductor().
    """
    if not conductor.get("habilitado"):
        return ResultadoOperacion(False, f"{conductor['nombre']} ya está deshabilitado.")
    if conductor.get("estado") == "Asignado":
        asig = conductor.get("asignacion_activa", "desconocida")
        return ResultadoOperacion(
            False,
            f"No se puede deshabilitar a {conductor['nombre']}: "
            f"tiene una asignación activa ({asig}). Libere la asignación primero."
        )
    return ResultadoOperacion(True, f"{conductor['nombre']} puede deshabilitarse.")


def puede_asignarse(conductor: dict) -> ResultadoOperacion:
    """
    Verifica si un conductor puede ser asignado, SIN mutar nada.
    La mutacion real (vincularlo a una asignacion) ocurre en
    asignaciones_service.registrar_asignacion(), via transition_service.
    """
    if not conductor.get("habilitado"):
        return ResultadoOperacion(
            False,
            f"{conductor['nombre']} no está habilitado y no puede ser asignado."
        )
    if conductor.get("estado") != "Disponible":
        return ResultadoOperacion(
            False,
            f"{conductor['nombre']} no está disponible "
            f"(estado actual: {conductor.get('estado')})."
        )
    if licencia_vencida(conductor):
        return ResultadoOperacion(
            False,
            f"La licencia de {conductor['nombre']} está vencida. No se puede asignar."
        )
    return ResultadoOperacion(True, f"{conductor['nombre']} puede asignarse.")


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTAS / HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def conductores_disponibles(conductores: list[dict]) -> list[dict]:
    """Retorna la lista de conductores habilitados y en estado 'Disponible'."""
    return [
        c for c in conductores
        if c.get("habilitado") and c.get("estado") == "Disponible"
    ]


def conductores_por_sucursal(sucursal: str, conductores: list[dict]) -> list[dict]:
    """Filtra conductores por sucursal."""
    return [c for c in conductores if c.get("sucursal") == sucursal]


def conductores_con_alerta_licencia(conductores: list[dict]) -> list[dict]:
    """
    Retorna conductores cuya licencia está vencida o vence en los próximos
    DIAS_ALERTA_LICENCIA días.
    """
    resultado = []
    for c in conductores:
        dias = dias_para_vencimiento_licencia(c)
        if dias is not None and dias <= DIAS_ALERTA_LICENCIA:
            resultado.append(c)
    return resultado


def obtener_asignacion_activa(conductor: dict, asignaciones: list[dict]) -> Optional[dict]:
    """
    Busca y retorna el dict de la asignación activa del conductor, o None.
    """
    if not conductor.get("asignacion_activa"):
        return None
    asig_id = conductor["asignacion_activa"]
    return next((a for a in asignaciones if a.get("id") == asig_id), None)


def resumen_conductores(conductores: list[dict]) -> dict:
    """
    Retorna un dict con conteos rápidos para los KPIs del módulo.

    Ejemplo de retorno:
        {
            "total": 6,
            "disponibles": 2,
            "asignados": 1,
            "en_descanso": 1,
            "no_habilitados": 1,
            "con_alerta_licencia": 2,
        }
    """
    return {
        "total": len(conductores),
        "disponibles":  sum(1 for c in conductores if c.get("estado") == "Disponible"),
        "asignados":    sum(1 for c in conductores if c.get("estado") == "Asignado"),
        "en_descanso":  sum(1 for c in conductores if c.get("estado") == "En descanso"),
        "no_habilitados": sum(1 for c in conductores if not c.get("habilitado")),
        "con_alerta_licencia": len(conductores_con_alerta_licencia(conductores)),
    }