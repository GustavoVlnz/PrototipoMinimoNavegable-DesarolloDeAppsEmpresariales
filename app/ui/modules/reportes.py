"""
Módulo Reportes — Trazabilidad, historial e incumplimientos.

"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from app.ui.components.widgets import TopBar, make_table, set_table_item, KpiCard
from app.data.mock_data import ASIGNACIONES, INCIDENTES, VEHICULOS


class ReportesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = TopBar("Reportes y Trazabilidad", "Historial operativo del día")
        layout.addWidget(topbar)

        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        # KPIs de reporte
        c_layout.addWidget(self._make_resumen())

        # Historial asignaciones
        c_layout.addWidget(self._make_historial())

        layout.addWidget(content)

    def _make_resumen(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        completadas = sum(1 for a in ASIGNACIONES if "Completada" in a["estado"])
        con_incidencia = sum(1 for a in ASIGNACIONES if "incidencia" in a["estado"].lower())
        incumplimientos = 1  # del Caso C
        incidentes_hoy = len(INCIDENTES)

        cards = [
            KpiCard("Asignaciones Completadas", completadas, color="#16A34A"),
            KpiCard("Con Incidencia", con_incidencia, color="#D97706"),
            KpiCard("Incumplimientos de Plazo", incumplimientos, color="#DC2626"),
            KpiCard("Incidentes Registrados Hoy", incidentes_hoy, color="#1E5FC3"),
        ]
        for card in cards:
            layout.addWidget(card)
        layout.addStretch()
        return row

    def _make_historial(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)
        p_layout.setSpacing(10)

        title = QLabel("Historial de Asignaciones")
        title.setObjectName("section_header")
        p_layout.addWidget(title)

        cols = ["ID", "Solicitud", "Vehículo", "Conductor", "Ruta", "Estado", "Inicio", "Fin"]
        table = make_table(cols)
        table.setRowCount(len(ASIGNACIONES))

        for r, a in enumerate(ASIGNACIONES):
            ruta = f"{a['origen']} → {a['destino']}"
            set_table_item(table, r, 0, a["id"])
            set_table_item(table, r, 1, a["solicitud_id"])
            set_table_item(table, r, 2, a["vehiculo_patente"])
            set_table_item(table, r, 3, a["conductor"])
            set_table_item(table, r, 4, ruta)
            set_table_item(table, r, 5, a["estado"], badge=True)
            set_table_item(table, r, 6, a["inicio"] or "—")
            set_table_item(table, r, 7, a["fin"] or "—")

        table.resizeColumnsToContents()
        p_layout.addWidget(table)
        return panel
