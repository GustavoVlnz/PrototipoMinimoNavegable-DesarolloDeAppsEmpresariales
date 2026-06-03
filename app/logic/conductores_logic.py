from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from app.data.mock_data import CONDUCTORES, ASIGNACIONES


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

DIAS_ALERTA_LICENCIA = 30   # Días previos al vencimiento para marcar alerta
ESTADOS_VALIDOS = {"Disponible", "Asignado", "En descanso", "No habilitado", "En espera"}


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
# VALIDACIONES
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


# ─────────────────────────────────────────────────────────────────────────────
# OPERACIONES DE HABILITACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def habilitar_conductor(conductor: dict) -> ResultadoOperacion:
    """
    Habilita a un conductor previamente deshabilitado.

    Reglas:
        - No se puede habilitar si ya está habilitado.
        - No se puede habilitar si la licencia está vencida.
        - Al habilitar pasa a estado 'Disponible'.
    """
    if conductor.get("habilitado"):
        return ResultadoOperacion(False, f"{conductor['nombre']} ya está habilitado.")

    if licencia_vencida(conductor):
        return ResultadoOperacion(
            False,
            f"No se puede habilitar a {conductor['nombre']}: licencia vencida el "
            f"{conductor.get('licencia_vence', '—')}. Actualice la licencia primero."
        )

    conductor["habilitado"] = True
    conductor["estado"] = "Disponible"
    return ResultadoOperacion(
        True,
        f"{conductor['nombre']} habilitado correctamente y marcado como Disponible."
    )


def deshabilitar_conductor(conductor: dict) -> ResultadoOperacion:
    """
    Deshabilita a un conductor.

    Reglas:
        - No se puede deshabilitar si está en una asignación activa (estado 'Asignado').
        - Al deshabilitar pasa a estado 'No habilitado'.
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

    conductor["habilitado"] = False
    conductor["estado"] = "No habilitado"
    return ResultadoOperacion(
        True,
        f"{conductor['nombre']} deshabilitado correctamente."
    )


# ─────────────────────────────────────────────────────────────────────────────
# OPERACIONES DE ESTADO
# ─────────────────────────────────────────────────────────────────────────────

def poner_en_descanso(conductor: dict) -> ResultadoOperacion:
    """
    Marca al conductor como 'En descanso'.

    Reglas:
        - Sólo válido si está Disponible y habilitado.
    """
    if not conductor.get("habilitado"):
        return ResultadoOperacion(False, "El conductor no está habilitado.")
    if conductor.get("estado") != "Disponible":
        return ResultadoOperacion(
            False,
            f"Sólo se puede poner en descanso desde estado 'Disponible'. "
            f"Estado actual: {conductor.get('estado')}."
        )

    conductor["estado"] = "En descanso"
    return ResultadoOperacion(True, f"{conductor['nombre']} marcado en descanso.")


def marcar_disponible(conductor: dict) -> ResultadoOperacion:
    """
    Marca al conductor como 'Disponible'.

    Reglas:
        - El conductor debe estar habilitado.
        - Sólo válido desde 'En descanso' o 'En espera'.
    """
    if not conductor.get("habilitado"):
        return ResultadoOperacion(False, "El conductor no está habilitado.")

    estados_origen = {"En descanso", "En espera"}
    if conductor.get("estado") not in estados_origen:
        return ResultadoOperacion(
            False,
            f"No se puede marcar como Disponible desde estado '{conductor.get('estado')}'."
        )

    conductor["estado"] = "Disponible"
    return ResultadoOperacion(True, f"{conductor['nombre']} marcado como Disponible.")


# ─────────────────────────────────────────────────────────────────────────────
# OPERACIONES DE ASIGNACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def asignar_conductor(conductor: dict, asignacion_id: str) -> ResultadoOperacion:
    """
    Vincula un conductor a una asignación.

    Reglas:
        - El conductor debe estar habilitado.
        - El conductor debe estar en estado 'Disponible'.
        - La licencia no debe estar vencida.
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

    conductor["estado"] = "Asignado"
    conductor["asignacion_activa"] = asignacion_id
    return ResultadoOperacion(
        True,
        f"{conductor['nombre']} asignado a {asignacion_id}."
    )


def liberar_conductor(conductor: dict) -> ResultadoOperacion:
    """
    Libera a un conductor de su asignación activa y lo marca como Disponible.

    Reglas:
        - El conductor debe tener una asignación activa.
    """
    if conductor.get("estado") != "Asignado":
        return ResultadoOperacion(
            False,
            f"{conductor['nombre']} no tiene una asignación activa."
        )

    asig_anterior = conductor.get("asignacion_activa", "—")
    conductor["estado"] = "Disponible"
    conductor["asignacion_activa"] = None
    return ResultadoOperacion(
        True,
        f"{conductor['nombre']} liberado de la asignación {asig_anterior}."
    )


# ─────────────────────────────────────────────────────────────────────────────
# CONSULTAS / HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def conductores_disponibles(conductores: list | None = None) -> list[dict]:
    """Retorna la lista de conductores habilitados y en estado 'Disponible'."""
    fuente = conductores if conductores is not None else CONDUCTORES
    return [
        c for c in fuente
        if c.get("habilitado") and c.get("estado") == "Disponible"
    ]


def conductores_por_sucursal(sucursal: str, conductores: list | None = None) -> list[dict]:
    """Filtra conductores por sucursal."""
    fuente = conductores if conductores is not None else CONDUCTORES
    return [c for c in fuente if c.get("sucursal") == sucursal]


def conductores_con_alerta_licencia(conductores: list | None = None) -> list[dict]:
    """
    Retorna conductores cuya licencia está vencida o vence en los próximos
    DIAS_ALERTA_LICENCIA días.
    """
    fuente = conductores if conductores is not None else CONDUCTORES
    resultado = []
    for c in fuente:
        dias = dias_para_vencimiento_licencia(c)
        if dias is not None and dias <= DIAS_ALERTA_LICENCIA:
            resultado.append(c)
    return resultado


def obtener_asignacion_activa(conductor: dict, asignaciones: list | None = None) -> Optional[dict]:
    """
    Busca y retorna el dict de la asignación activa del conductor, o None.
    """
    if not conductor.get("asignacion_activa"):
        return None
    fuente = asignaciones if asignaciones is not None else ASIGNACIONES
    asig_id = conductor["asignacion_activa"]
    return next((a for a in fuente if a.get("id") == asig_id), None)


def resumen_conductores(conductores: list | None = None) -> dict:
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
    fuente = conductores if conductores is not None else CONDUCTORES
    return {
        "total": len(fuente),
        "disponibles":  sum(1 for c in fuente if c.get("estado") == "Disponible"),
        "asignados":    sum(1 for c in fuente if c.get("estado") == "Asignado"),
        "en_descanso":  sum(1 for c in fuente if c.get("estado") == "En descanso"),
        "no_habilitados": sum(1 for c in fuente if not c.get("habilitado")),
        "con_alerta_licencia": len(conductores_con_alerta_licencia(fuente)),
    }