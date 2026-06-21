"""
Sidebar de navegación de LoncoExpress.
Muestra el logo, menú de módulos y usuario activo.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSpacerItem, QSizePolicy
)   
from PyQt6.QtCore import Qt, pyqtSignal, QSize

import qtawesome as qta

NAV_ITEMS = [
    {
        "section": "PRINCIPAL",
        "items": [
            ("view-dashboard-outline", "Dashboard", 0),
            ("file-document-outline", "Solicitudes", 1),
            ("swap-horizontal", "Asignaciones", 4),
        ]
    },

    {
        "section": "RECURSOS",
        "items": [
            ("truck-outline", "Vehículos", 2),
            ("account-tie-outline", "Conductores", 3),
        ]
    },

    {
        "section": "OPERACIONES",
        "items": [
            ("alert-outline", "Incidentes", 5),
            ("wrench-outline", "Mantenimiento", 6),
            ("file-certificate-outline", "Documentación", 7),
        ]
    },

    {
        "section": "GESTIÓN",
        "items": [
            ("chart-box-outline", "Reportes", 8),
            ("shield-alert-outline", "Contingencia", 9),
        ]
    },
]


class SidebarWidget(QWidget):
    """Barra lateral de navegación principal."""

    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("sidebar")

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setFixedWidth(280)

        self._active_index = 0
        self._buttons: list[QPushButton] = []

        self._build_ui()

    # ──────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        # ── Brand / Logo
        layout.addWidget(self._make_brand())

        # ── Separador
        layout.addWidget(self._make_separator())

        # ── Navegación
        nav_frame = QWidget()
        nav_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(8, 12, 8, 12)
        nav_layout.setSpacing(2)

        button_index = 0

        # ─────────────────────────────────────
        # Construcción dinámica por categorías
        # ─────────────────────────────────────
        for section in NAV_ITEMS:

            # ── Título de sección
            section_label = QLabel(section["section"])
            section_label.setObjectName("nav_section")
            nav_layout.addWidget(section_label)

            # ── Items de sección
            for icon_name, name, page_idx in section["items"]:

                btn = QPushButton(name)

                btn.setObjectName("nav_btn")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setCheckable(False)

                # ── Icono vectorial
                icon = qta.icon(
                    f"mdi.{icon_name}",
                    color="#C7D2E3"
                )

                btn.setIcon(icon)
                btn.setIconSize(QSize(20, 20))

                # ── Estado activo
                btn.setProperty(
                    "active",
                    button_index == self._active_index
                )

                btn.clicked.connect(
                    lambda checked, idx=page_idx, bi=button_index:
                    self._on_nav_clicked(idx, bi)
                )

                self._buttons.append(btn)
                nav_layout.addWidget(btn)

                button_index += 1

            # Espacio entre categorías
            nav_layout.addSpacing(1)

        layout.addWidget(nav_frame)

        # ── Spacer
        layout.addSpacerItem(
            QSpacerItem(
                20,
                40,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Expanding
            )
        )

        # ── Separador
        layout.addWidget(self._make_separator())

        # ── Usuario
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

    # ──────────────────────────────────────────
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

    # ──────────────────────────────────────────
    def _make_separator(self) -> QFrame:
        line = QFrame()

        line.setFrameShape(QFrame.Shape.HLine)

        line.setStyleSheet(
            "background-color: #1A2E50; border: none; max-height: 1px;"
        )

        return line

    # ──────────────────────────────────────────
    def _on_nav_clicked(self, page_idx: int, button_idx: int):
        """Cambia el botón activo y emite señal de cambio de página."""

        # ── Desactivar anterior
        old_btn = self._buttons[self._active_index]

        old_btn.setProperty("active", False)
        old_btn.style().unpolish(old_btn)
        old_btn.style().polish(old_btn)

        # ── Activar nuevo
        self._active_index = button_idx

        new_btn = self._buttons[button_idx]

        new_btn.setProperty("active", True)
        new_btn.style().unpolish(new_btn)
        new_btn.style().polish(new_btn)

        self.page_changed.emit(page_idx)

    # ──────────────────────────────────────────
    def set_active(self, button_idx: int):
        """Activa un botón desde código externo."""

        if 0 <= button_idx < len(self._buttons):
            self._on_nav_clicked(button_idx, button_idx)