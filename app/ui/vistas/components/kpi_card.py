from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class KpiCard(QFrame):
    """Tarjeta de métrica con etiqueta, valor principal y subtexto opcional.

    Uso:
        card = KpiCard("Vehículos totales", "12", "2 disponibles hoy")
        card = KpiCard("Incidentes activos", "1", color="danger")

    ``color`` acepta: "default" | "success" | "warning" | "danger" | "info"
    """

    def __init__(
        self,
        label: str,
        value: str,
        subtitle: str = "",
        color: str = "default",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("kpi-card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self._label = QLabel(label)
        self._label.setObjectName("kpi-label")
        layout.addWidget(self._label)

        self._value = QLabel(value)
        self._value.setObjectName(f"kpi-value-{color}")
        layout.addWidget(self._value)

        if subtitle:
            self._subtitle = QLabel(subtitle)
            self._subtitle.setObjectName("kpi-subtitle")
            layout.addWidget(self._subtitle)

    # ─────────────────────────────────────────────────────────────
    def set_value(self, value: str) -> None:
        self._value.setText(value)

    def set_label(self, label: str) -> None:
        self._label.setText(label)