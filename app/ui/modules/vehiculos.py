"""
Módulo Vehículos — LoncoExpress.
Refactorizado para usar vehiculos_queries y vehiculos_logic (sin mock_data).
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog, QComboBox,
    QSpinBox, QLineEdit, QMessageBox, QStackedWidget,
    QGridLayout,
)

from app.logic import vehiculos_logic
from app.ui.components.widgets import (
    TopBar, make_table, set_table_item,
    make_badge, KpiCard, make_action_button, make_info_frame,
)
from app.data.queries import vehiculos_queries
from app.logic import vehiculos_logic


class VehiculosView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._vehiculos = []
        self._cargar_vehiculos()
        self._stack = QStackedWidget()
        self._build_ui()

    # ── Carga de datos ────────────────────────────────────────────

    def _cargar_vehiculos(self):
        """Carga vehículos desde la base de datos."""
        self._vehiculos = vehiculos_queries.obtener_todos_vehiculos()

    # ── Construcción UI ───────────────────────────────────────────

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

    # ── Vista Lista ───────────────────────────────────────────────

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
        resumen = vehiculos_logic.resumen_flota(self._vehiculos)
        color_map = {
            "disponibles":    "#16A34A",
            "en_ruta":        "#1E5FC3",
            "reservados":     "#1E5FC3",
            "bloqueados":     "#DC2626",
            "fuera_servicio": "#DC2626",
            "en_mantencion":  "#D97706",
        }
        labels = {
            "disponibles":    "Disponible",
            "reservados":     "Reservado",
            "en_ruta":        "En Ruta",
            "en_mantencion":  "En Mantención",
            "bloqueados":     "Bloqueado",
            "fuera_servicio": "Fuera de Servicio",
        }
        row = QHBoxLayout()
        row.setSpacing(12)
        for key, label in labels.items():
            count = resumen.get(key, 0)
            if count > 0:
                row.addWidget(KpiCard(label, count, color=color_map.get(key, "#E8F0FE")))
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

    # ── Vista Detalle ─────────────────────────────────────────────

    def _ver_detalle(self, row: int):
        v = self._vehiculos[row]
        detail = VehiculoDetalleView(
            v,
            on_back=self._volver,
            on_toggle=self._toggle_bloqueo,
        )
        if self._stack.count() > 1:
            self._stack.removeWidget(self._stack.widget(1))
        self._stack.addWidget(detail)
        self._stack.setCurrentIndex(1)
        self._topbar.findChild(QLabel, "page_title").setText(f"Vehículo {v['patente']}")

    def _volver(self):
        self._cargar_vehiculos()
        self._fill_table()
        self._stack.setCurrentIndex(0)
        self._topbar.findChild(QLabel, "page_title").setText("Gestión de Vehículos")

    # ── Acciones ──────────────────────────────────────────────────

    def _toggle_bloqueo(self, vehiculo: dict):
        resultado = vehiculos_logic.toggle_bloqueo(vehiculo)
        if not resultado:
            QMessageBox.warning(self, "Acción no permitida", resultado.mensaje)
            return

        nuevo_estado = vehiculos_logic.nuevo_estado_tras_toggle(vehiculo["estado"])
        ok = vehiculos_queries.actualizar_estado_vehiculo(
            vehiculo["vehiculo_id"], nuevo_estado
        )
        if ok:
            QMessageBox.information(self, "Estado actualizado", resultado.mensaje)
            self._volver()
        else:
            QMessageBox.critical(self, "Error", "No se pudo actualizar el estado en la base de datos.")

    def _agregar(self):
            sucursales = vehiculos_queries.obtener_sucursales()
            if not sucursales:
                QMessageBox.warning(self, "Sin sucursales",
                                    "No hay sucursales registradas en la base de datos.")
                return

            dlg = AgregarVehiculoDialog(self, sucursales=sucursales)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                data = dlg.get_data()

                resultado = vehiculos_logic.validar_nuevo_vehiculo(
                    patente=data["patente"],
                    tipo=data["tipo"],
                    capacidad_kg=data["capacidad_kg"],
                    vehiculos_existentes=self._vehiculos,
                )
                if not resultado:
                    QMessageBox.warning(self, "Datos inválidos", resultado.mensaje)
                    return

                ok = vehiculos_queries.crear_vehiculo(
                    patente=data["patente"],
                    tipo=data["tipo"].replace(" ", "_"),
                    marca_modelo=data["modelo"],
                    capacidad_kg=data["capacidad_kg"],
                    sucursal_nombre=data["ubicacion"],
                )
                if ok:
                    self._cargar_vehiculos()
                    self._fill_table()
                    QMessageBox.information(
                        self, "Vehículo agregado",
                        f"Vehículo {data['patente']} registrado en la flota."
                    )
                else:
                    QMessageBox.critical(self, "Error", "No se pudo registrar el vehículo.")


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

        # Botón volver
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
            ("Tipo",            self._v["tipo"]),
            ("Capacidad",       f"{self._v['capacidad_kg']:,} kg"),
            ("Kilometraje",     f"{self._v.get('kilometraje', 0):,} km"),
            ("Ubicación",       self._v["ubicacion"]),
            ("Últ. mantención", self._v["ultima_mantencion"]),
            ("Seguro vence",    self._v.get("seguro_vence", "—")),
            ("Permiso circ.",   self._v.get("permiso_vence", "—")),
            ("Rev. técnica",    self._v.get("revision_tecnica", "—")),
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

        # Observación
        if self._v.get("observacion"):
            p.addWidget(make_info_frame(f"⚠ {self._v['observacion']}"))

        # Botón contextual
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        estado = self._v["estado"]

        if estado == "Disponible":
            p.addWidget(make_info_frame("Vehículo operativo y disponible para asignación."))
            btn = QPushButton("Bloquear Vehículo")
            btn.setObjectName("btn_danger")
            btn.clicked.connect(lambda: self._on_toggle(self._v))
            btn_row.addWidget(btn)
        elif estado == "Bloqueado":
            p.addWidget(make_info_frame("Vehículo bloqueado administrativamente."))
            btn = QPushButton("Desbloquear Vehículo")
            btn.setObjectName("btn_success")
            btn.clicked.connect(lambda: self._on_toggle(self._v))
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

    def __init__(self, parent=None, sucursales: list[str] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Vehículo")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._sucursales = sucursales or []
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
        self._tipo.addItems(vehiculos_logic.TIPOS_VEHICULO)
        layout.addWidget(self._tipo)

        layout.addWidget(lbl("Modelo:"))
        self._modelo = QLineEdit()
        self._modelo.setPlaceholderText("Ej: Toyota Hilux")
        layout.addWidget(self._modelo)

        layout.addWidget(lbl("Capacidad (kg):"))
        self._cap = QSpinBox()
        self._cap.setRange(100, 20000)
        self._cap.setSuffix(" kg")
        self._cap.setValue(1000)
        layout.addWidget(self._cap)

        layout.addWidget(lbl("Sucursal:"))
        self._ubic = QComboBox()
        self._ubic.addItems(self._sucursales)
        if not self._sucursales:
            self._ubic.setEnabled(False)
            self._ubic.setPlaceholderText("Sin sucursales disponibles")
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
            "patente":      self._patente.text().strip().upper() or "NUEVA-01",
            "tipo":         self._tipo.currentText(),
            "modelo":       self._modelo.text().strip() or "Sin especificar",
            "capacidad_kg": self._cap.value(),
            "ubicacion":    self._ubic.currentText(),
        }