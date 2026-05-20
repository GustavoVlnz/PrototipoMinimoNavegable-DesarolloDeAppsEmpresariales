"""
Módulo Conductores — Listado y ficha de conductores.
Actor principal: Encargado de Flota.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt

from app.ui.components.widgets import TopBar, make_table, set_table_item, make_badge, KpiCard
from app.data.mock_data import CONDUCTORES


class ConductoresView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._conductores = list(CONDUCTORES)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = TopBar(
            "Gestión de Conductores",
            f"{len(self._conductores)} conductores registrados",
        )
        layout.addWidget(topbar)

        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        # Resumen
        c_layout.addWidget(self._make_resumen())

        # Tabla
        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)

        cols = ["Nombre", "RUT", "Estado", "Licencia", "Vence Licencia", "Sucursal", "Asignación Activa", "Teléfono"]
        table = make_table(cols)
        table.setRowCount(len(self._conductores))

        for r, c in enumerate(self._conductores):
            asig = c["asignacion_activa"] or "—"
            set_table_item(table, r, 0, f"{c['nombre']}")
            set_table_item(table, r, 1, c["rut"])
            set_table_item(table, r, 2, c["estado"], badge=True)
            set_table_item(table, r, 3, c["licencia"])
            lic_vence = c["licencia_vence"]
            set_table_item(table, r, 4, lic_vence)
            set_table_item(table, r, 5, c["sucursal"])
            set_table_item(table, r, 6, asig)
            set_table_item(table, r, 7, c["telefono"])

        table.resizeColumnsToContents()
        p_layout.addWidget(table)

        c_layout.addWidget(panel)
        layout.addWidget(content)

    def _make_resumen(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        disponibles = sum(1 for c in self._conductores if c["estado"] == "Disponible")
        asignados = sum(1 for c in self._conductores if c["estado"] == "Asignado")
        no_hab = sum(1 for c in self._conductores if not c["habilitado"])
        descanso = sum(1 for c in self._conductores if c["estado"] == "En descanso")

        cards = [
            KpiCard("Disponibles",     disponibles, color="#16A34A"),
            KpiCard("Asignados",       asignados,   color="#1E5FC3"),
            KpiCard("En Descanso",     descanso,    color="#D97706"),
            KpiCard("No Habilitados",  no_hab,      color="#DC2626"),
        ]
        for card in cards:
            layout.addWidget(card)
        layout.addStretch()
        return row
