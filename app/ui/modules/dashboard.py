"""
Módulo Dashboard — Vista principal con KPIs, alertas y actividad reciente.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame,
)

from app.ui.components.widgets import KpiCard, make_table, set_table_item, make_alert_item, TopBar
from app.logic.dashboard_logic import obtener_datos_dashboard


class DashboardView(QWidget):
    """Vista del dashboard principal."""

    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.db_session = db_session
        self._datos = obtener_datos_dashboard(self.db_session)
        self._needs_refresh = False
        self._build_ui()

    # ── Slots ──────────────────────────────────────────────────────────────────

    def _marcar_para_refresh(self):
        """Marca que hay datos nuevos pendientes de mostrar."""
        self._needs_refresh = True

    def showEvent(self, event):
        """Se ejecuta cada vez que el dashboard se vuelve visible."""
        super().showEvent(event)
        if self._needs_refresh:
            self._refresh()

    # ── Recarga interna ───────────────────────────────────────────────────────

    def _refresh(self):
        """Recarga datos desde la DB y reconstruye la UI."""
        self._datos = obtener_datos_dashboard(self.db_session)
        self._needs_refresh = False

        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        self._build_ui()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(TopBar(
            "Dashboard",
            f"Resumen operativo del día — {_today()}",
        ))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setObjectName("content_area")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 28)
        content_layout.setSpacing(20)

        content_layout.addWidget(self._make_kpi_row())

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        bottom_row.addWidget(self._make_actividad_reciente(), stretch=3)
        bottom_row.addWidget(self._make_alertas_panel(), stretch=2)
        content_layout.addLayout(bottom_row)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    # ── Secciones ─────────────────────────────────────────────────────────────

    def _make_kpi_row(self) -> QWidget:
        cards = self._datos["cards"]

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        for card in [
            KpiCard("Vehículos Disponibles",   cards["vehiculos_disponibles"],   color="#16A34A"),
            KpiCard("En Ruta",                  cards["en_ruta"],                 color="#1E5FC3"),
            KpiCard("Bloqueados / F. Servicio", cards["bloqueados_fuera_serv"],   color="#DC2626"),
            KpiCard("En Mantención",            cards["en_mantencion"],           color="#D97706"),
            KpiCard("Alertas Activas",          cards["alertas_activas"],         color="#EA580C"),
            KpiCard("Conductores Disponibles",  cards["conductores_disponibles"], color="#D9CF1D"),
        ]:
            layout.addWidget(card)

        return row

    def _make_actividad_reciente(self) -> QFrame:
        asignaciones = self._datos["asignaciones_hoy"]

        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(_section_header("Asignaciones del Día"))

        cols  = ["ID", "Vehículo", "Conductor", "Origen → Destino", "Estado", "Inicio"]
        table = make_table(cols, row_height=42)
        table.setRowCount(len(asignaciones))

        for r, a in enumerate(asignaciones):
            set_table_item(table, r, 0, a["id"])
            set_table_item(table, r, 1, a["vehiculo_patente"])
            set_table_item(table, r, 2, a["conductor"])
            set_table_item(table, r, 3, f"{a['origen']} → {a['destino']}")
            set_table_item(table, r, 4, a["estado"], badge=True)
            set_table_item(table, r, 5, a["inicio"] or "—")

        table.resizeColumnsToContents()
        layout.addWidget(table)
        return panel

    def _make_alertas_panel(self) -> QFrame:
        alertas = self._datos["alertas"]

        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        layout.addWidget(_section_header(f"Alertas  ({len(alertas)})"))

        for alerta in alertas:
            layout.addWidget(make_alert_item(alerta["nivel"], alerta["mensaje"]))

        layout.addStretch()
        return panel


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _section_header(texto: str) -> QLabel:
    lbl = QLabel(texto)
    lbl.setObjectName("section_header")
    return lbl


def _today() -> str:
    from datetime import date
    d = date.today()
    meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{d.day} de {meses[d.month]} de {d.year}"