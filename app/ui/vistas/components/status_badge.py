from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


# Mapeo de estado → object name para QSS
STATUS_STYLES: dict[str, str] = {
    # Vehículos
    "disponible":        "badge-green",
    "reservado":         "badge-amber",
    "en ruta":           "badge-blue",
    "en mantención":     "badge-orange",
    "fuera de servicio": "badge-orange",
    "bloqueado":         "badge-red",
    # Asignaciones / solicitudes
    "creada":            "badge-gray",
    "en evaluación":     "badge-blue",
    "confirmada":        "badge-blue",
    "en ejecución":      "badge-blue",
    "pendiente":         "badge-amber",
    "completada":        "badge-green",
    "completada con incidencia": "badge-orange",
    "fallida":           "badge-red",
    "cancelada":         "badge-gray",
    "reprogramada":      "badge-amber",
    "con incidencia":    "badge-orange",
    # Conductores
    "asignado":          "badge-blue",
    "no habilitado":     "badge-red",
    "en descanso":       "badge-gray",
    # Prioridad
    "alta":              "badge-red",
    "media":             "badge-amber",
    "normal":            "badge-green",
    # Incidentes
    "crítico":           "badge-red",
    "operativo":         "badge-amber",
    "menor":             "badge-gray",
    "en gestión":        "badge-amber",
    "resuelto":          "badge-green",
    "cerrado":           "badge-green",
}


class StatusBadge(QLabel):
    """Etiqueta de estado con color según el valor pasado.

    Uso:
        badge = StatusBadge("Disponible")
        badge = StatusBadge("En Ruta")
    """

    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.set_status(status)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_status(self, status: str) -> None:
        self.setText(status)
        key = status.lower().strip()
        style_name = STATUS_STYLES.get(key, "badge-gray")
        self.setObjectName(style_name)
        # Refrescar estilos QSS
        self.style().unpolish(self)
        self.style().polish(self)