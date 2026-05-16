from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal


class Topbar(QWidget):
    """Barra superior con título de módulo y botón de acción principal."""

    action_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        self._title = QLabel("Dashboard general")
        self._title.setObjectName("topbar-title")
        layout.addWidget(self._title)

        layout.addStretch()

        # Botón de notificaciones (sin texto, solo ícono)
        self._btn_bell = QPushButton("🔔")
        self._btn_bell.setObjectName("btn-icon")
        self._btn_bell.setFixedSize(36, 36)
        self._btn_bell.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self._btn_bell)

        # Botón de acción principal
        self._btn_action = QPushButton("+ Nueva solicitud")
        self._btn_action.setObjectName("btn-primary")
        self._btn_action.setFixedHeight(34)
        self._btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_action.clicked.connect(self.action_clicked)
        layout.addWidget(self._btn_action)

    # ─────────────────────────────────────────────────────────────
    def set_title(self, title: str) -> None:
        self._title.setText(title)

    def set_action_label(self, label: str) -> None:
        self._btn_action.setText(f"+ {label}")

    def hide_action(self) -> None:
        self._btn_action.hide()

    def show_action(self) -> None:
        self._btn_action.show()