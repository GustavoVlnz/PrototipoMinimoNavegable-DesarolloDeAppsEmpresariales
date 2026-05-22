"""
Componentes reutilizables de la UI de LoncoExpress.
- TopBar: barra superior con título y botón de acción
- StatusBadge: etiqueta de color para estados
- KpiCard: tarjeta de indicador clave
- make_table: helper para crear QTableWidget estilizado
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


# ─────────────────────────────────────────────
# STATUS BADGE
# ─────────────────────────────────────────────

STATUS_BADGE_MAP = {
    # Vehículos
    "Disponible":                  "badge_green",
    "Reservado":                   "badge_blue",
    "En Ruta":                     "badge_blue",
    "En Mantención":               "badge_orange",
    "Fuera de Servicio":           "badge_red",
    "Bloqueado":                   "badge_red",
    # Solicitudes / Asignaciones
    "Creada":                      "badge_gray",
    "En evaluación":               "badge_blue",
    "Confirmada":                  "badge_blue",
    "En ejecución":                "badge_blue",
    "Pendiente":                   "badge_yellow",
    "Pendiente de Reasignación":   "badge_yellow",
    "Reprogramada":                "badge_yellow",
    "Completada":                  "badge_green",
    "Completada con incidencia":   "badge_orange",
    "Fallida":                     "badge_red",
    "Cancelada":                   "badge_gray",
    # Conductores
    "Asignado":                    "badge_blue",
    "No habilitado":               "badge_red",
    "En descanso":                 "badge_gray",
    "En espera":                   "badge_yellow",
    # Incidentes
    "Registrado":                  "badge_yellow",
    "En Análisis":                 "badge_blue",
    "En gestión":                  "badge_orange",
    "Resuelto":                    "badge_green",
    "Cerrado":                     "badge_gray",
    # Docs
    "Vigente":                     "badge_green",
    "Por vencer":                  "badge_yellow",
    "Vencida":                     "badge_red",
    # Mantenimiento
    "Programada":                  "badge_blue",
    "En proceso":                  "badge_orange",
    "En espera de repuestos":      "badge_yellow",
    # Prioridad
    "Alta":                        "badge_red",
    "Media":                       "badge_yellow",
    "Baja":                        "badge_green",
    # Gravedad incidentes
    "Crítica":                     "badge_red",
    "Operativa":                   "badge_orange",
    "Menor":                       "badge_green",
}


def make_badge(text: str) -> QLabel:
    """Crea un QLabel con estilo de badge según el texto de estado."""
    badge = QLabel(text)
    badge.setObjectName(STATUS_BADGE_MAP.get(text, "badge_gray"))
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    badge.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    # Solo política de tamaño — sin max/min fijo para no interferir con el layout
    badge.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    return badge


# ─────────────────────────────────────────────
# TOP BAR
# ─────────────────────────────────────────────

class TopBar(QWidget):
    """Barra superior con título de módulo y botón de acción opcional."""

    action_clicked = pyqtSignal()

    def __init__(self, title: str, subtitle: str = "", action_label: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(83)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 8, 28, 8)

        title_container = QVBoxLayout()
        title_container.setSpacing(0)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("page_title")
        title_container.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("page_subtitle")
            title_container.addWidget(sub_lbl)

        layout.addLayout(title_container)
        layout.addStretch()

        if action_label:
            self.action_btn = QPushButton(action_label)
            self.action_btn.setObjectName("topbar_action")
            self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.action_btn.clicked.connect(self.action_clicked.emit)
            layout.addWidget(self.action_btn)


# ─────────────────────────────────────────────
# KPI CARD
# ─────────────────────────────────────────────

class KpiCard(QFrame):
    """Tarjeta de indicador clave de desempeño."""

    def __init__(self, label: str, value: str | int,
                 delta: str = "", color: str = "#0B1E3D", parent=None):
        super().__init__(parent)
        self.setObjectName("kpi_card")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        val_lbl = QLabel(str(value))
        val_lbl.setObjectName("kpi_value")
        val_lbl.setStyleSheet(f"color: {color};")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(label)
        lbl.setObjectName("kpi_label")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_layout.addWidget(val_lbl)
        text_layout.addWidget(lbl)

        if delta:
            delta_lbl = QLabel(delta)
            delta_lbl.setObjectName("kpi_delta")
            text_layout.addWidget(delta_lbl)
            delta_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(text_layout)


def _lighten_color(hex_color: str) -> str:
    color_map = {
        "#16A34A": "#DCFCE7",
        "#1E5FC3": "#DBEAFE",
        "#DC2626": "#FEE2E2",
        "#D97706": "#FEF3C7",
        "#EA580C": "#FFEDD5",
        "#0B1E3D": "#EBF2FF",
    }
    return color_map.get(hex_color, "#EBF2FF")


# ─────────────────────────────────────────────
# TABLE HELPER
# ─────────────────────────────────────────────

def make_table(columns: list[str], row_height: int = 44) -> QTableWidget:
    """
    Crea y configura un QTableWidget con estilo LoncoExpress.
    Retorna la tabla lista para rellenar con datos.
    """
    table = QTableWidget()
    table.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setMinimumSectionSize(row_height)
    table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    # Interactive: permite que set_table_item ajuste anchos de columnas con badges
    # sin ser sobreescrito por ResizeToContents que ignora setCellWidget
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    table.horizontalHeader().setStretchLastSection(True)

    table.setShowGrid(False)
    table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    table.resizeColumnsToContents()
    table.resizeRowsToContents()
    return table


def set_table_item(table: QTableWidget, row: int, col: int,
                   text: str, badge: bool = False, align_center: bool = False):
    """Inserta un ítem en la tabla, con opción de badge de estado."""
    if badge:
        badge_lbl = make_badge(text)

        # Calcular ancho mínimo real basado en el texto + padding del badge
        text_w = badge_lbl.fontMetrics().horizontalAdvance(text)
        needed_w = text_w + 42
        container_w = needed_w + 24

        container = QWidget()
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(badge_lbl)

        table.setCellWidget(row, col, container)

        # Ajustar ancho de columna si el badge necesita más espacio del actual
        current_w = table.columnWidth(col)
        if current_w < container_w:
            table.setColumnWidth(col, container_w)

    else:
        item = QTableWidgetItem(text)
        if align_center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, col, item)


# ─────────────────────────────────────────────
# ALERT ITEM
# ─────────────────────────────────────────────

def make_alert_item(tipo: str, mensaje: str) -> QFrame:
    """Crea un ítem de alerta para el panel del dashboard."""

    frame_id = {
        "critica":     "alert_critical",
        "advertencia": "alert_item",
        "info":        "alert_info",
    }.get(tipo, "alert_info")

    frame = QFrame()
    frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    frame.setObjectName(frame_id)

    layout = QHBoxLayout(frame)
    layout.setContentsMargins(12, 8, 12, 8)
    layout.setSpacing(8)

    msg_lbl = QLabel(mensaje)
    msg_lbl.setWordWrap(True)

    layout.addWidget(msg_lbl)

    return frame

# ─────────────────────────────────────────────────────────────
# Helpers reutilizables
# ─────────────────────────────────────────────────────────────

def make_action_button(text, style, slot, icon=None):
    btn = QPushButton(f"{icon}  {text}" if icon else text)
    btn.setObjectName(style)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.clicked.connect(slot)
    return btn


def make_info_frame(text: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("alert_info")
    frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    layout = QHBoxLayout(frame)
    layout.setContentsMargins(12, 10, 12, 10)

    lbl = QLabel(text)
    lbl.setWordWrap(True)

    layout.addWidget(lbl)
    return frame