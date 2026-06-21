"""
Módulo Reportes — Trazabilidad e indicadores visuales.
Actor: Administrador General / Supervisor.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from app.ui.components.widgets import TopBar, KpiCard
from app.data.queries import reportes_queries
from app.logic import documentacion_logic
from app.core.events import event_bus


class ReportesView(QWidget):

    def __init__(self, db_session, parent=None):
        super().__init__(parent)

        self.db_session = db_session

        self._resumen = {}
        self._asignaciones_estado = []
        self._incidentes_estado = []
        self._documentos_estado = []
        self._vehiculos_estado = []
        self._mantenimientos_estado = []

        self._build_ui()
        self._conectar_eventos()
        self._recargar()

    # ── Eventos / carga ───────────────────────────────────────────────────────

    def _conectar_eventos(self):
        event_bus.asignacion_actualizada.connect(self._recargar)
        event_bus.incidente_actualizado.connect(self._recargar)
        event_bus.documento_actualizado.connect(self._recargar)
        event_bus.vehiculo_actualizado.connect(self._recargar)
        event_bus.mantenimiento_actualizado.connect(self._recargar)

    def _cargar_datos(self):
        """
        Carga reportes desde BD.
        También sincroniza documentación para que los reportes reflejen
        estados reales de vencimiento.
        """
        self.db_session.expire_all()

        documentacion_logic.sincronizar_vencimientos(
            self.db_session,
            emitir_eventos=False,
        )

        self._resumen = reportes_queries.obtener_resumen_reportes(self.db_session)
        self._asignaciones_estado = reportes_queries.obtener_asignaciones_por_estado(self.db_session)
        self._incidentes_estado = reportes_queries.obtener_incidentes_por_estado(self.db_session)
        self._documentos_estado = reportes_queries.obtener_documentos_por_estado(self.db_session)
        self._vehiculos_estado = reportes_queries.obtener_vehiculos_por_estado(self.db_session)
        self._mantenimientos_estado = reportes_queries.obtener_mantenimientos_por_estado(self.db_session)

    def _recargar(self):
        self._cargar_datos()
        self._reconstruir_contenido()

    # ── UI base ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._topbar = TopBar(
            "Reportes y Trazabilidad",
            "Indicadores visuales del estado operativo de la flota",
        )
        root.addWidget(self._topbar)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(self._scroll)

    def _reconstruir_contenido(self):
        content = QWidget()
        content.setObjectName("content_area")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(18)

        layout.addWidget(self._make_resumen())

        layout.addLayout(self._make_chart_row([
            ChartCard(
                "Asignaciones por estado",
                "Distribución del flujo operacional de transporte.",
                self._asignaciones_estado,
                accent="#2F80ED",
            ),
            ChartCard(
                "Vehículos por estado",
                "Disponibilidad actual del parque vehicular.",
                self._vehiculos_estado,
                accent="#16A34A",
            ),
        ]))

        layout.addLayout(self._make_chart_row([
            ChartCard(
                "Incidentes por estado",
                "Seguimiento de incidentes registrados y su avance.",
                self._incidentes_estado,
                accent="#DC2626",
            ),
            ChartCard(
                "Documentación por estado",
                "Control de documentos vigentes, por vencer y vencidos.",
                self._documentos_estado,
                accent="#D97706",
            ),
        ]))

        layout.addLayout(self._make_chart_row([
            ChartCard(
                "Mantenimiento por estado",
                "Estado de las órdenes de mantenimiento registradas.",
                self._mantenimientos_estado,
                accent="#7C3AED",
            ),
            SummaryCard(
                "Lectura operacional",
                self._generar_lectura_operacional(),
            ),
        ]))

        layout.addStretch()
        self._scroll.setWidget(content)

    # ── Secciones ─────────────────────────────────────────────────────────────

    def _make_resumen(self) -> QWidget:
        row = QWidget()

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        cards = [
            KpiCard(
                "Asignaciones Completadas",
                self._resumen.get("asignaciones_completadas", 0),
                color="#16A34A",
            ),
            KpiCard(
                "Con Incidencia",
                self._resumen.get("asignaciones_con_incidencia", 0),
                color="#D97706",
            ),
            KpiCard(
                "Incidentes Activos",
                self._resumen.get("incidentes_activos", 0),
                color="#DC2626",
            ),
            KpiCard(
                "Documentos Críticos",
                self._resumen.get("documentos_criticos", 0),
                color="#D97706",
            ),
            KpiCard(
                "Vehículos Bloqueados",
                self._resumen.get("vehiculos_bloqueados", 0),
                color="#7F1D1D",
            ),
            KpiCard(
                "Mantenciones Abiertas",
                self._resumen.get("mantenciones_abiertas", 0),
                color="#1E5FC3",
            ),
        ]

        for card in cards:
            layout.addWidget(card)

        layout.addStretch()
        return row


    def _make_chart_row(self, cards: list[QWidget]) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        for card in cards:
            row.addWidget(card)

        return row

    def _generar_lectura_operacional(self) -> list[str]:
        asignaciones_completadas = self._resumen.get("asignaciones_completadas", 0)
        asignaciones_con_incidencia = self._resumen.get("asignaciones_con_incidencia", 0)
        incidentes_activos = self._resumen.get("incidentes_activos", 0)
        documentos_criticos = self._resumen.get("documentos_criticos", 0)
        vehiculos_bloqueados = self._resumen.get("vehiculos_bloqueados", 0)
        mantenciones_abiertas = self._resumen.get("mantenciones_abiertas", 0)

        lineas = [
            f"• {asignaciones_completadas} asignaciones se encuentran completadas o cerradas.",
            f"• {asignaciones_con_incidencia} asignaciones registran historial de incidencia.",
            f"• {incidentes_activos} incidentes siguen activos y requieren seguimiento.",
            f"• {documentos_criticos} documentos están vencidos o próximos a vencer.",
            f"• {vehiculos_bloqueados} vehículos se encuentran bloqueados operacionalmente.",
            f"• {mantenciones_abiertas} órdenes de mantenimiento permanecen abiertas.",
        ]

        if incidentes_activos > 0 or documentos_criticos > 0 or vehiculos_bloqueados > 0:
            lineas.append("• La operación presenta alertas activas que deben priorizarse.")
        else:
            lineas.append("• No se observan alertas críticas activas en la operación.")

        return lineas


# ══════════════════════════════════════════════════════════════════════════════
# WIDGETS DE GRÁFICOS
# ══════════════════════════════════════════════════════════════════════════════

class ChartCard(QFrame):

    def __init__(
        self,
        title: str,
        subtitle: str,
        data: list[dict],
        accent: str = "#2F80ED",
        parent=None,
    ):
        super().__init__(parent)

        self.setObjectName("panel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("section_header")
        layout.addWidget(title_lbl)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setWordWrap(True)
        sub_lbl.setStyleSheet("color: #8EA8C8; font-size: 12px;")
        layout.addWidget(sub_lbl)

        chart = HorizontalBarChart(data, accent=accent)
        layout.addWidget(chart)


class HorizontalBarChart(QWidget):

    def __init__(self, data: list[dict], accent: str = "#2F80ED", parent=None):
        super().__init__(parent)

        self._data = data or []
        self._accent = QColor(accent)

        rows = max(len(self._data), 3)
        self.setMinimumHeight(70 + rows * 34)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(4, 8, -4, -8)

        if not self._data:
            self._draw_empty(painter, rect)
            return

        max_value = max((item.get("total", 0) for item in self._data), default=0)
        total_general = sum(item.get("total", 0) for item in self._data)

        if max_value <= 0:
            self._draw_empty(painter, rect)
            return

        label_width = min(190, max(130, int(rect.width() * 0.34)))
        value_width = 48
        gap = 12

        chart_left = rect.left() + label_width + gap
        chart_right = rect.right() - value_width
        chart_width = max(40, chart_right - chart_left)

        row_height = max(30, int(rect.height() / max(len(self._data), 1)))
        bar_height = 15

        font_label = QFont()
        font_label.setPointSize(9)

        font_value = QFont()
        font_value.setPointSize(9)
        font_value.setBold(True)

        for i, item in enumerate(self._data):
            label = item.get("estado", "—")
            value = int(item.get("total", 0))
            porcentaje = int(round((value / total_general) * 100)) if total_general > 0 else 0

            row_top = rect.top() + i * row_height
            center_y = row_top + row_height // 2

            painter.setFont(font_label)
            painter.setPen(QColor("#B8C7E0"))
            painter.drawText(
                rect.left(),
                row_top,
                label_width,
                row_height,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                label,
            )

            bg_rect = QRectF(
                chart_left,
                center_y - bar_height / 2,
                chart_width,
                bar_height,
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#132A46"))
            painter.drawRoundedRect(bg_rect, 7, 7)

            fill_width = chart_width * (value / max_value)

            fill_rect = QRectF(
                chart_left,
                center_y - bar_height / 2,
                max(3, fill_width) if value > 0 else 0,
                bar_height,
            )

            painter.setBrush(self._accent)
            painter.drawRoundedRect(fill_rect, 7, 7)

            painter.setFont(font_value)
            painter.setPen(QColor("#E8F0FE"))
            painter.drawText(
                chart_right + 8,
                row_top,
                value_width,
                row_height,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                f"{value} ({porcentaje}%)",
            )

    def _draw_empty(self, painter: QPainter, rect):
        painter.setPen(QPen(QColor("#8EA8C8")))
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            "Sin datos disponibles",
        )


class SummaryCard(QFrame):

    def __init__(self, title: str, lines: list[str], parent=None):
        super().__init__(parent)

        self.setObjectName("panel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("section_header")
        layout.addWidget(title_lbl)

        for line in lines:
            lbl = QLabel(line)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #B8C7E0; font-size: 13px;")
            layout.addWidget(lbl)

        layout.addStretch()