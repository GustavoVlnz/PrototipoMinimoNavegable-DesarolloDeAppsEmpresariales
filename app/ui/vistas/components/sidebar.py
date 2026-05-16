# Sidebar component for LoncoExpress UI
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


# ─────────────────────────────────────────────────────────────────
# Ítem de navegación individual
# ─────────────────────────────────────────────────────────────────
class NavItem(QPushButton):
    """Botón de navegación lateral. Checkable para marcar activo."""

    def __init__(self, label: str, module_id: str, badge: str = "", parent=None):
        super().__init__(parent)
        self.module_id = module_id
        self.setCheckable(True)
        self.setObjectName("nav-item")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(8)

        self.label_widget = QLabel(label)
        self.label_widget.setObjectName("nav-item-label")
        layout.addWidget(self.label_widget)

        layout.addStretch()

        if badge:
            badge_lbl = QLabel(badge)
            badge_lbl.setObjectName("nav-badge")
            badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(badge_lbl)

        self.setFixedHeight(36)
        # Necesario para que el layout interno funcione con QPushButton
        self.setLayout(layout)


# ─────────────────────────────────────────────────────────────────
# Sidebar principal
# ─────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    """Panel de navegación lateral.

    Emite ``nav_changed(module_id: str)`` al hacer clic en un ítem.
    """

    nav_changed = pyqtSignal(str)

    # Estructura de navegación: (sección, [(label, module_id, badge?), ...])
    NAV_STRUCTURE = [
        ("PRINCIPAL", [
            ("Dashboard",    "dashboard",     ""),
            ("Solicitudes",  "solicitudes",   "3"),
            ("Asignaciones", "asignaciones",  ""),
        ]),
        ("RECURSOS", [
            ("Vehículos",   "vehiculos",   ""),
            ("Conductores", "conductores", ""),
        ]),
        ("OPERACIONES", [
            ("Incidentes",    "incidentes",    "1"),
            ("Mantenimiento", "mantenimiento", ""),
            ("Documentación", "documentos",   ""),
        ]),
        ("GESTIÓN", [
            ("Reportes", "reportes", ""),
        ]),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(210)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Logo ─────────────────────────────────────────────────
        layout.addWidget(self._build_logo())

        # ── Ítems de navegación ───────────────────────────────────
        self._nav_items: list[NavItem] = []

        for section_title, items in self.NAV_STRUCTURE:
            section_lbl = QLabel(section_title)
            section_lbl.setObjectName("nav-section")
            layout.addWidget(section_lbl)

            for label, module_id, badge in items:
                item = NavItem(label, module_id, badge)
                item.clicked.connect(
                    lambda _checked, mid=module_id: self._activate(mid)
                )
                layout.addWidget(item)
                self._nav_items.append(item)

        layout.addStretch()

        # ── Footer con usuario activo ─────────────────────────────
        layout.addWidget(self._build_footer())

        # Activar primer ítem
        if self._nav_items:
            self._activate(self._nav_items[0].module_id)

    # ── Helpers ──────────────────────────────────────────────────

    def _activate(self, module_id: str) -> None:
        for item in self._nav_items:
            item.setChecked(item.module_id == module_id)
        self.nav_changed.emit(module_id)

    def _build_logo(self) -> QWidget:
        container = QFrame()
        container.setObjectName("sidebar-logo")
        container.setFixedHeight(64)

        h = QHBoxLayout(container)
        h.setContentsMargins(16, 0, 16, 0)
        h.setSpacing(10)

        icon_box = QLabel("🚚")
        icon_box.setObjectName("logo-icon")
        icon_box.setFixedSize(32, 32)
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(icon_box)

        text_col = QVBoxLayout()
        text_col.setSpacing(1)

        name_lbl = QLabel("LoncoExpress")
        name_lbl.setObjectName("logo-name")

        sub_lbl = QLabel("GESTIÓN DE FLOTA")
        sub_lbl.setObjectName("logo-sub")

        text_col.addWidget(name_lbl)
        text_col.addWidget(sub_lbl)
        h.addLayout(text_col)
        h.addStretch()

        return container

    def _build_footer(self) -> QWidget:
        container = QFrame()
        container.setObjectName("sidebar-footer")
        container.setFixedHeight(56)

        h = QHBoxLayout(container)
        h.setContentsMargins(14, 0, 14, 0)
        h.setSpacing(10)

        avatar = QLabel("RF")
        avatar.setObjectName("user-avatar")
        avatar.setFixedSize(28, 28)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(avatar)

        text_col = QVBoxLayout()
        text_col.setSpacing(0)

        name_lbl = QLabel("Roberto F.")
        name_lbl.setObjectName("user-name")

        role_lbl = QLabel("Enc. de Flota")
        role_lbl.setObjectName("user-role")

        text_col.addWidget(name_lbl)
        text_col.addWidget(role_lbl)
        h.addLayout(text_col)
        h.addStretch()

        return container