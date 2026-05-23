"""
Módulo Vehículos — PMN.

"""

from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog, QComboBox,
    QSpinBox, QLineEdit, QMessageBox, QStackedWidget,
    QGridLayout
)

from app.ui.components.widgets import (
    TopBar, make_table, set_table_item,
    make_badge, KpiCard, make_action_button, make_info_frame,
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
            "＋ Agregar Vehículo",
        )
        self._topbar.action_clicked.connect(self._agregar)
        layout.addWidget(self._topbar)

        self._stack.addWidget(self._make_lista())
        layout.addWidget(self._stack)

    # ── Lista ─────────────────────────────────────────────────────

    def _make_lista(self) -> QWidget:
        view = QWidget()
        view.setObjectName("content_area")
        layout = QVBoxLayout(view)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        layout.addLayout(self._build_kpis())

        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 12, 16, 16)

        hint = QLabel("Haz clic en «Gestionar» para ver detalle o ejecutar acciones.")
        hint.setObjectName("page_subtitle")
        p_layout.addWidget(hint)

        cols = ["Patente", "Tipo", "Modelo", "Cap. (kg)",
                "Ubicación", "Estado", "Últ. Mantención", "Acciones"]
        self._table = make_table(cols)
        self._table.cellDoubleClicked.connect(lambda r, _: self._ver_detalle(r))
        self._fill_table()
        p_layout.addWidget(self._table)

        layout.addWidget(panel)
        return view

    def _build_kpis(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        color_map = {
            "Disponible": "#16A34A", "En Ruta": "#1E5FC3",
            "Reservado": "#1E5FC3",  "Bloqueado": "#DC2626",
            "Fuera de Servicio": "#DC2626", "En Mantención": "#D97706",
        }
        conteo = {}
        for v in self._vehiculos:
            conteo[v["estado"]] = conteo.get(v["estado"], 0) + 1
        for estado, count in conteo.items():
            row.addWidget(KpiCard(estado, count, color=color_map.get(estado, "#E8F0FE")))
        row.addStretch()
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

            btn = QPushButton("Gestionar")
            btn.setObjectName("btn_table_action")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=r: self._ver_detalle(i))
            self._table.setCellWidget(r, 7, btn)

        self._table.resizeColumnsToContents()

    # ── Detalle ───────────────────────────────────────────────────

    def _ver_detalle(self, row: int):
        v = self._vehiculos[row]
        detail = VehiculoDetalleView(v, on_back=self._volver,
                                     on_toggle=self._toggle_bloqueo)
        if self._stack.count() > 1:
            self._stack.removeWidget(self._stack.widget(1))
        self._stack.addWidget(detail)
        self._stack.setCurrentIndex(1)
        self._topbar.findChild(QLabel, "page_title").setText(f"Vehículo {v['patente']}")

    def _volver(self):
        self._stack.setCurrentIndex(0)
        self._topbar.findChild(QLabel, "page_title").setText("Gestión de Vehículos")
        self._fill_table()

    # ── Acciones ──────────────────────────────────────────────────

    def _toggle_bloqueo(self, patente: str):
        for v in self._vehiculos:
            if v["patente"] == patente:
                if v["estado"] == "Disponible":
                    v["estado"] = "Bloqueado"
                    msg = f"Vehículo {patente} bloqueado."
                elif v["estado"] == "Bloqueado":
                    v["estado"] = "Disponible"
                    msg = f"Vehículo {patente} desbloqueado."
                else:
                    msg = f"No se puede cambiar desde estado «{v['estado']}»."
                QMessageBox.information(self, "Estado actualizado", msg)
                self._fill_table()
                self._volver()
                break

    def _agregar(self):
        dlg = AgregarVehiculoDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            data["estado"]            = "Disponible"
            data["ultima_mantencion"] = "Sin registro"
            data["kilometraje"]       = 0
            data["seguro_vence"]      = "12/2026"
            data["permiso_vence"]     = "12/2026"
            data["revision_tecnica"]  = "12/2026"
            data["observacion"]       = ""
            self._vehiculos.append(data)
            self._fill_table()
            QMessageBox.information(self, "Vehículo agregado",
                                    f"Vehículo {data['patente']} registrado en la flota.")


# ─────────────────────────────────────────────────────────────────
class VehiculoDetalleView(QWidget):

    def __init__(self, v: dict, on_back, on_toggle, parent=None):
        super().__init__(parent)
        self._v = v
        self._on_back   = on_back
        self._on_toggle = on_toggle
        self.setObjectName("content_area")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        # Volver
        back_row = QHBoxLayout()
        btn_back = QPushButton("← Volver al listado")
        btn_back.setObjectName("btn_secondary")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self._on_back)
        back_row.addWidget(btn_back)
        back_row.addStretch()
        layout.addLayout(back_row)

        panel = QFrame()
        panel.setObjectName("panel")
        p = QVBoxLayout(panel)
        p.setContentsMargins(24, 20, 24, 20)
        p.setSpacing(16)

        # Encabezado
        h = QHBoxLayout()
        title = QLabel(f"{self._v['modelo']}  —  {self._v['patente']}")
        title.setObjectName("dialog_title")
        h.addWidget(title)
        h.addStretch()
        h.addWidget(make_badge(self._v["estado"]))
        p.addLayout(h)

        # Grid de datos
        grid = QGridLayout()
        grid.setSpacing(10)
        fields = [
            ("Tipo",             self._v["tipo"]),
            ("Capacidad",        f"{self._v['capacidad_kg']:,} kg"),
            ("Kilometraje",      f"{self._v.get('kilometraje', 0):,} km"),
            ("Ubicación",        self._v["ubicacion"]),
            ("Últ. mantención",  self._v["ultima_mantencion"]),
            ("Seguro vence",     self._v.get("seguro_vence", "—")),
            ("Permiso circ.",    self._v.get("permiso_vence", "—")),
            ("Rev. técnica",     self._v.get("revision_tecnica", "—")),
        ]
        for i, (k, val) in enumerate(fields):
            row, col = divmod(i, 2)
            lbl_k = QLabel(k + ":")
            lbl_k.setObjectName("form_label")
            lbl_v = QLabel(str(val))
            lbl_v.setStyleSheet("color: #E8F0FE;")
            grid.addWidget(lbl_k, row, col * 2)
            grid.addWidget(lbl_v, row, col * 2 + 1)
        p.addLayout(grid)

        # Observación si existe
        if self._v.get("observacion"):
            p.addWidget(make_info_frame(f"⚠ {self._v['observacion']}"))

        # Botón contextual
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        estado = self._v["estado"]
        if estado == "Disponible":
            p.addWidget(make_info_frame("Vehículo operativo y disponible para asignación."))
            btn = QPushButton("  Bloquear Vehículo")
            btn.setObjectName("btn_danger")
            btn.clicked.connect(lambda: self._on_toggle(self._v["patente"]))
            btn_row.addWidget(btn)
        elif estado == "Bloqueado":
            p.addWidget(make_info_frame("Vehículo bloqueado administrativamente."))
            btn = QPushButton("  Desbloquear Vehículo")
            btn.setObjectName("btn_success")
            btn.clicked.connect(lambda: self._on_toggle(self._v["patente"]))
            btn_row.addWidget(btn)
        else:
            p.addWidget(make_info_frame(
                f"Estado «{estado}» — sin acciones manuales disponibles."
            ))

        p.addLayout(btn_row)
        layout.addWidget(panel)
        layout.addStretch()


# ─────────────────────────────────────────────────────────────────
class AgregarVehiculoDialog(QDialog):
    """Formulario para registrar un nuevo vehículo. """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Vehículo")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Registrar Nuevo Vehículo")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        def lbl(t):
            l = QLabel(t)
            l.setObjectName("form_label")
            return l

        layout.addWidget(lbl("Patente:"))
        self._patente = QLineEdit()
        self._patente.setPlaceholderText("Ej: XKRT-99")
        layout.addWidget(self._patente)

        layout.addWidget(lbl("Tipo:"))
        self._tipo = QComboBox()
        self._tipo.addItems(["Camioneta", "Furgón", "Camión liviano", "Sprinter"])
        layout.addWidget(self._tipo)

        layout.addWidget(lbl("Modelo:"))
        self._modelo = QLineEdit()
        self._modelo.setPlaceholderText("Ej: Toyota Hilux")
        layout.addWidget(self._modelo)

        layout.addWidget(lbl("Capacidad (kg):"))
        self._cap = QSpinBox()
        self._cap.setRange(100, 10000)
        self._cap.setSuffix(" kg")
        self._cap.setValue(1000)
        layout.addWidget(self._cap)

        layout.addWidget(lbl("Ubicación:"))
        self._ubic = QComboBox()
        self._ubic.addItems(["Temuco", "Santiago", "Concepción", "Los Ángeles", "Valparaíso"])
        layout.addWidget(self._ubic)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("Agregar")
        btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_c)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {
            "patente":      self._patente.text().upper() or "NUEVA-01",
            "tipo":         self._tipo.currentText(),
            "modelo":       self._modelo.text() or "Sin especificar",
            "capacidad_kg": self._cap.value(),
            "ubicacion":    self._ubic.currentText(),
        }