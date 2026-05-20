"""
Módulo Vehículos — Listado de flota, detalle y acciones de bloqueo.
Actor principal: Encargado de Flota.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog, QScrollArea,
    QMessageBox, QStackedWidget, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt

from app.ui.components.widgets import (
    TopBar, make_table, set_table_item, make_badge, KpiCard
)
from app.data.mock_data import VEHICULOS


class VehiculosView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._vehiculos = list(VEHICULOS)
        self._stack = QStackedWidget()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._topbar = TopBar(
            "Gestión de Vehículos",
            f"{len(self._vehiculos)} unidades en flota",
        )
        layout.addWidget(self._topbar)

        # Vistas: 0 = listado, 1 = detalle
        self._stack.addWidget(self._make_lista_view())
        layout.addWidget(self._stack)

    # ──────────────────────────────────────────
    def _make_lista_view(self) -> QWidget:
        view = QWidget()
        view.setObjectName("content_area")
        layout = QVBoxLayout(view)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        # Resumen de estados
        layout.addWidget(self._make_resumen())

        # Tabla
        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)
        p_layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.addWidget(_section_label("Flota Completa"))
        header_row.addStretch()
        tip = QLabel("Haz clic en una fila para ver el detalle")
        tip.setStyleSheet("color: #5B7FA6; font-size: 11px;")
        header_row.addWidget(tip)
        p_layout.addLayout(header_row)

        cols = ["Patente", "Tipo", "Modelo", "Cap. (kg)", "Ubicación", "Estado", "Últ. Mantención", "Observación"]
        self._table = make_table(cols)
        self._table.cellClicked.connect(self._on_row_clicked)
        self._fill_table()
        p_layout.addWidget(self._table)

        layout.addWidget(panel)
        return view

    def _make_resumen(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        estados = {}
        for v in self._vehiculos:
            estados[v["estado"]] = estados.get(v["estado"], 0) + 1

        color_map = {
            "Disponible": "#16A34A",
            "En Ruta": "#1E5FC3",
            "Reservado": "#1E5FC3",
            "Bloqueado": "#DC2626",
            "Fuera de Servicio": "#DC2626",
            "En Mantención": "#D97706",
        }

        for estado, count in estados.items():
            card = KpiCard(
                estado, count,
                color=color_map.get(estado, "#0B1E3D")
            )
            layout.addWidget(card)

        layout.addStretch()
        return row

    def _fill_table(self):
        self._table.setRowCount(len(self._vehiculos))
        for r, v in enumerate(self._vehiculos):
            set_table_item(self._table, r, 0, v["patente"])
            set_table_item(self._table, r, 1, v["tipo"])
            set_table_item(self._table, r, 2, v["modelo"])
            set_table_item(self._table, r, 3, f"{v['capacidad_kg']:,}")
            set_table_item(self._table, r, 4, v["ubicacion"])
            set_table_item(self._table, r, 5, v["estado"], badge=True)
            set_table_item(self._table, r, 6, v["ultima_mantencion"])
            obs = v.get("observacion", "")
            set_table_item(self._table, r, 7, obs[:50] + "…" if len(obs) > 50 else obs)
        self._table.resizeColumnsToContents()

    def _on_row_clicked(self, row: int, _col: int):
        vehiculo = self._vehiculos[row]
        detail = VehiculoDetailView(vehiculo, on_back=self._back_to_lista,
                                    on_action=self._toggle_bloqueo)
        # Reemplazar vista de detalle si existe
        if self._stack.count() > 1:
            old = self._stack.widget(1)
            self._stack.removeWidget(old)
        self._stack.addWidget(detail)
        self._stack.setCurrentIndex(1)
        self._topbar.findChild(QLabel, "page_title").setText(f"Vehículo {vehiculo['patente']}")

    def _back_to_lista(self):
        self._stack.setCurrentIndex(0)
        self._topbar.findChild(QLabel, "page_title").setText("Gestión de Vehículos")

    def _toggle_bloqueo(self, patente: str):
        for v in self._vehiculos:
            if v["patente"] == patente:
                if v["estado"] == "Disponible":
                    v["estado"] = "Bloqueado"
                    msg = f"Vehículo {patente} bloqueado correctamente."
                elif v["estado"] == "Bloqueado":
                    v["estado"] = "Disponible"
                    msg = f"Vehículo {patente} desbloqueado. Ahora disponible."
                else:
                    msg = f"No se puede cambiar el estado desde '{v['estado']}'."
                QMessageBox.information(self, "Estado actualizado", msg)
                self._fill_table()
                self._back_to_lista()
                break


# ─────────────────────────────────────────────
class VehiculoDetailView(QWidget):
    """Vista de detalle de un vehículo específico."""

    def __init__(self, vehiculo: dict, on_back, on_action, parent=None):
        super().__init__(parent)
        self._v = vehiculo
        self._on_back = on_back
        self._on_action = on_action
        self.setObjectName("content_area")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        # Botón volver
        back_row = QHBoxLayout()
        back_btn = QPushButton("← Volver al listado")
        back_btn.setObjectName("btn_secondary")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self._on_back)
        back_row.addWidget(back_btn)
        back_row.addStretch()
        layout.addLayout(back_row)

        # Panel principal
        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(24, 24, 24, 24)
        p_layout.setSpacing(20)

        # Encabezado
        header = QHBoxLayout()
        title = QLabel(f"{self._v['modelo']} — {self._v['patente']}")
        title.setObjectName("dialog_title")
        header.addWidget(title)
        header.addStretch()

        badge = make_badge(self._v["estado"])
        badge.setFixedWidth(140)
        header.addWidget(badge)
        p_layout.addLayout(header)

        # Grid de datos
        grid = QGridLayout()
        grid.setSpacing(12)
        datos = [
            ("Tipo", self._v["tipo"]),
            ("Capacidad", f"{self._v['capacidad_kg']:,} kg"),
            ("Kilometraje", f"{self._v['kilometraje']:,} km"),
            ("Ubicación actual", self._v["ubicacion"]),
            ("Última mantención", self._v["ultima_mantencion"]),
            ("Seguro vence", self._v["seguro_vence"]),
            ("Permiso circulación", self._v["permiso_vence"]),
            ("Revisión técnica", self._v["revision_tecnica"]),
        ]
        for i, (k, val) in enumerate(datos):
            row, col = divmod(i, 2)
            lbl_k = QLabel(k + ":")
            lbl_k.setObjectName("form_label")
            lbl_v = QLabel(str(val))
            lbl_v.setStyleSheet("font-weight: 500;")
            grid.addWidget(lbl_k, row, col * 2)
            grid.addWidget(lbl_v, row, col * 2 + 1)
        p_layout.addLayout(grid)

        # Observación
        if self._v.get("observacion"):
            obs_frame = QFrame()
            obs_frame.setObjectName("alert_item")
            obs_layout = QHBoxLayout(obs_frame)
            obs_layout.setContentsMargins(12, 8, 12, 8)
            obs_layout.addWidget(QLabel("⚠️"))
            obs_layout.addWidget(QLabel(self._v["observacion"]))
            p_layout.addWidget(obs_frame)

        # Botones de acción
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        estado = self._v["estado"]
        if estado == "Disponible":
            btn = QPushButton("🔒 Bloquear Vehículo")
            btn.setObjectName("btn_danger")
            btn.clicked.connect(lambda: self._on_action(self._v["patente"]))
            btn_row.addWidget(btn)
        elif estado == "Bloqueado":
            btn = QPushButton("🔓 Desbloquear Vehículo")
            btn.setObjectName("btn_success")
            btn.clicked.connect(lambda: self._on_action(self._v["patente"]))
            btn_row.addWidget(btn)

        p_layout.addLayout(btn_row)
        layout.addWidget(panel)
        layout.addStretch()


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("section_header")
    return lbl
