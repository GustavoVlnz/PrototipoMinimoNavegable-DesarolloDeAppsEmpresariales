"""
Módulo Dashboard — Vista principal con KPIs, alertas y actividad reciente.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt

from app.ui.components.widgets import KpiCard, make_table, set_table_item, make_alert_item, TopBar
from app.data.mock_data import get_kpis, ASIGNACIONES, ALERTAS


class DashboardView(QWidget):
    """Vista del dashboard principal."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Topbar
        topbar = TopBar(
            "Dashboard",
            f"Resumen operativo del día — {_today()}",
        )
        layout.addWidget(topbar)

        # Área scrollable de contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setObjectName("content_area")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 28)
        content_layout.setSpacing(20)

        # ── KPI Cards
        content_layout.addWidget(self._make_kpi_row())

        # ── Fila inferior: tabla + alertas
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        bottom_row.addWidget(self._make_actividad_reciente(), stretch=3)
        bottom_row.addWidget(self._make_alertas_panel(), stretch=2)
        content_layout.addLayout(bottom_row)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    # ──────────────────────────────────────────
    def _make_kpi_row(self) -> QWidget:
        kpis = get_kpis()
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        cards = [
            KpiCard("Vehículos Disponibles",  kpis["disponibles"],         color="#16A34A"),
            KpiCard("En Ruta",                 kpis["en_ruta"],             color="#1E5FC3"),
            KpiCard("Bloqueados / F. Servicio",kpis["bloqueados"],          color="#DC2626"),
            KpiCard("En Mantención",           kpis["en_mantencion"],       color="#D97706"),
            KpiCard("Alertas Activas",          kpis["alertas_doc"],         color="#EA580C"),
            KpiCard("Conductores Disponibles", kpis["conductores_disponibles"], color="#D9CF1D"),
        ]
        for card in cards:
            layout.addWidget(card)
        return row

    def _make_actividad_reciente(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Asignaciones del Día")
        title.setObjectName("section_header")
        layout.addWidget(title)

        cols = ["ID", "Vehículo", "Conductor", "Origen → Destino", "Estado", "Inicio"]
        table = make_table(cols, row_height=42)
        table.setRowCount(len(ASIGNACIONES))

        for r, a in enumerate(ASIGNACIONES):
            ruta = f"{a['origen']} → {a['destino']}"
            inicio = a["inicio"] or "—"
            set_table_item(table, r, 0, a["id"])
            set_table_item(table, r, 1, a["vehiculo_patente"])
            set_table_item(table, r, 2, a["conductor"])
            set_table_item(table, r, 3, ruta)
            set_table_item(table, r, 4, a["estado"], badge=True)
            set_table_item(table, r, 5, inicio)

        table.resizeColumnsToContents()
        layout.addWidget(table)
        return panel

    def _make_alertas_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title = QLabel(f"Alertas  ({len(ALERTAS)})")
        title.setObjectName("section_header")
        layout.addWidget(title)

        for alerta in ALERTAS:
            layout.addWidget(make_alert_item(alerta["tipo"], alerta["mensaje"]))

        layout.addStretch()
        return panel


def _today() -> str:
    from datetime import date
    d = date.today()
    meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{d.day} de {meses[d.month]} de {d.year}"
