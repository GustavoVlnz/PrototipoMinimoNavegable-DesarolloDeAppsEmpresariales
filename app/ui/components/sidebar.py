"""
Sidebar de navegación de LoncoExpress.
Muestra el logo, menú de módulos y usuario activo.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


# Definición de módulos: (nombre, emoji_icon, page_index)
NAV_ITEMS = [
    ("Dashboard",       "⬛ ", 0),
    ("Solicitudes",     "📋 ", 1),
    ("Vehículos",       "🚛 ", 2),
    ("Conductores",     "👤 ", 3),
    ("Asignaciones",    "🔗 ", 4),
    ("Incidentes",      "⚠️  ", 5),
    ("Mantenimiento",   "🔧 ", 6),
    ("Documentación",   "📄 ", 7),
    ("Reportes",        "📊 ", 8),
    ("Contingencia",    "🛡️  ", 9),
]


class SidebarWidget(QWidget):
    """Barra lateral de navegación principal."""

    page_changed = pyqtSignal(int)  # emite el índice de página seleccionada

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(230)
        self._active_index = 0
        self._buttons: list[QPushButton] = []
        self._build_ui()

    # ──────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Brand / Logo
        layout.addWidget(self._make_brand())

        # ── Separador
        layout.addWidget(self._make_separator())

        # ── Sección de navegación
        nav_label = QLabel("NAVEGACIÓN")
        nav_label.setObjectName("nav_section")
        layout.addWidget(nav_label)

        # ── Botones de navegación
        nav_frame = QWidget()
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 4, 0, 4)
        nav_layout.setSpacing(2)

        for i, (name, icon, page_idx) in enumerate(NAV_ITEMS):
            btn = QPushButton(f"{icon}{name}")
            btn.setObjectName("nav_btn")
            btn.setCheckable(False)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("active", i == self._active_index)
            btn.clicked.connect(lambda checked, idx=page_idx, bi=i: self._on_nav_clicked(idx, bi))
            self._buttons.append(btn)
            nav_layout.addWidget(btn)

        layout.addWidget(nav_frame)

        # ── Spacer para empujar usuario al fondo
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ── Separador
        layout.addWidget(self._make_separator())

        # ── Info del usuario
        layout.addWidget(self._make_user_panel())

    # ──────────────────────────────────────────
    def _make_brand(self) -> QWidget:
        brand = QWidget()
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(20, 24, 20, 16)
        brand_layout.setSpacing(2)

        logo = QLabel("LoncoExpress")
        logo.setObjectName("brand_logo")

        sub = QLabel("GESTIÓN DE FLOTA")
        sub.setObjectName("brand_sub")

        brand_layout.addWidget(logo)
        brand_layout.addWidget(sub)
        return brand

    def _make_user_panel(self) -> QWidget:
        user_widget = QWidget()
        layout = QHBoxLayout(user_widget)
        layout.setContentsMargins(16, 12, 16, 20)
        layout.setSpacing(10)

        avatar = QLabel("RF")
        avatar.setObjectName("user_avatar")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info = QWidget()
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(0)

        name_label = QLabel("Roberto Fuentes")
        name_label.setObjectName("user_name")

        role_label = QLabel("Enc. Flota Vehicular")
        role_label.setObjectName("user_role")

        info_layout.addWidget(name_label)
        info_layout.addWidget(role_label)

        layout.addWidget(avatar)
        layout.addWidget(info)
        return user_widget

    def _make_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #1A2E50; border: none; max-height: 1px;")
        return line

    # ──────────────────────────────────────────
    def _on_nav_clicked(self, page_idx: int, button_idx: int):
        """Cambia el botón activo y emite señal de cambio de página."""
        # Desactivar botón anterior
        old_btn = self._buttons[self._active_index]
        old_btn.setProperty("active", False)
        old_btn.style().unpolish(old_btn)
        old_btn.style().polish(old_btn)

        # Activar nuevo botón
        self._active_index = button_idx
        new_btn = self._buttons[button_idx]
        new_btn.setProperty("active", True)
        new_btn.style().unpolish(new_btn)
        new_btn.style().polish(new_btn)

        self.page_changed.emit(page_idx)

    def set_active(self, button_idx: int):
        """Activa un botón desde código externo."""
        if 0 <= button_idx < len(self._buttons):
            self._on_nav_clicked(button_idx, button_idx)
