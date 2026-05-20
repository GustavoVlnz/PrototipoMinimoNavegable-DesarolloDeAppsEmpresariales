"""
Módulo Mantenimiento — Órdenes de mantención y habilitación de vehículos.
Actor principal: Técnico de Mantención, Encargado de Flota.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox
)
from app.ui.components.widgets import TopBar, make_table, set_table_item
from app.data.mock_data import MANTENIMIENTO


class MantenimientoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ordenes = list(MANTENIMIENTO)
        self._selected_row = -1
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = TopBar(
            "Mantenimiento",
            "Órdenes de mantención y habilitación de vehículos",
        )
        layout.addWidget(topbar)

        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        info = QFrame()
        info.setObjectName("alert_info")
        il = QHBoxLayout(info)
        il.setContentsMargins(12, 10, 12, 10)
        il.addWidget(QLabel("ℹ️  Un vehículo solo recupera el estado 'Disponible' "
                            "tras la aprobación del Técnico de Mantención."))
        c_layout.addWidget(info)

        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)

        cols = ["ID", "Vehículo", "Tipo", "Descripción", "Prioridad", "Estado", "Generado", "Técnico"]
        self._table = make_table(cols)
        self._table.cellClicked.connect(self._on_row_clicked)
        self._fill_table()
        p_layout.addWidget(self._table)

        action_row = QHBoxLayout()
        action_row.addStretch()
        self._btn_habilitar = QPushButton("✅ Habilitar Vehículo (validación técnica)")
        self._btn_habilitar.setObjectName("btn_success")
        self._btn_habilitar.setEnabled(False)
        self._btn_habilitar.clicked.connect(self._habilitar_vehiculo)
        action_row.addWidget(self._btn_habilitar)
        p_layout.addLayout(action_row)

        c_layout.addWidget(panel)
        layout.addWidget(content)

    def _fill_table(self):
        self._table.setRowCount(len(self._ordenes))
        for r, m in enumerate(self._ordenes):
            desc = m["descripcion"]
            set_table_item(self._table, r, 0, m["id"])
            set_table_item(self._table, r, 1, m["vehiculo_patente"])
            set_table_item(self._table, r, 2, m["tipo"])
            set_table_item(self._table, r, 3, desc[:55] + "…" if len(desc) > 55 else desc)
            set_table_item(self._table, r, 4, m["prioridad"], badge=True)
            set_table_item(self._table, r, 5, m["estado"], badge=True)
            set_table_item(self._table, r, 6, m["generado"])
            set_table_item(self._table, r, 7, m["tecnico"])
        self._table.resizeColumnsToContents()

    def _on_row_clicked(self, row, _col):
        self._selected_row = row
        orden = self._ordenes[row]
        puede = orden["estado"] in ("En proceso",)
        self._btn_habilitar.setEnabled(puede)

    def _habilitar_vehiculo(self):
        if self._selected_row < 0:
            return
        orden = self._ordenes[self._selected_row]
        reply = QMessageBox.question(
            self, "Validación técnica",
            f"¿Confirmar habilitación del vehículo {orden['vehiculo_patente']}?\n\n"
            f"Esto cambiará su estado a 'Disponible' y cerrará la orden.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            orden["estado"] = "Completada"
            self._fill_table()
            QMessageBox.information(self, "Vehículo habilitado",
                                    f"Vehículo {orden['vehiculo_patente']} habilitado.\n"
                                    f"Orden {orden['id']} cerrada.")
