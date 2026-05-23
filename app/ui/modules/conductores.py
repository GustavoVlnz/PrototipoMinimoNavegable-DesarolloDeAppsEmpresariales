"""
Módulo Conductores.

"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog, QComboBox,
    QLineEdit, QMessageBox, QGridLayout
)

from app.ui.components.widgets import (
    TopBar, make_table, set_table_item,
    make_badge, KpiCard, make_action_button, make_info_frame,
)
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
            "＋ Agregar Conductor",
        )
        topbar.action_clicked.connect(self._agregar)
        layout.addWidget(topbar)

        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        c_layout.addLayout(self._build_kpis())

        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 12, 16, 16)

        hint = QLabel("Haz clic en «Gestionar» para ver detalle o cambiar estado.")
        hint.setObjectName("page_subtitle")
        p_layout.addWidget(hint)

        cols = ["Nombre", "RUT", "Estado", "Licencia",
                "Vence Licencia", "Sucursal", "Asignación Activa", "Acciones"]
        self._table = make_table(cols)
        self._fill_table()
        p_layout.addWidget(self._table)

        c_layout.addWidget(panel)
        layout.addWidget(content)

    # ── KPIs ─────────────────────────────────────────────────────

    def _build_kpis(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        disp    = sum(1 for c in self._conductores if c["estado"] == "Disponible")
        asig    = sum(1 for c in self._conductores if c["estado"] == "Asignado")
        desc    = sum(1 for c in self._conductores if c["estado"] == "En descanso")
        no_hab  = sum(1 for c in self._conductores if not c["habilitado"])
        row.addWidget(KpiCard("Disponibles",    disp,   color="#16A34A"))
        row.addWidget(KpiCard("Asignados",      asig,   color="#1E5FC3"))
        row.addWidget(KpiCard("En descanso",    desc,   color="#D97706"))
        row.addWidget(KpiCard("No habilitados", no_hab, color="#DC2626"))
        row.addStretch()
        return row

    # ── Tabla ─────────────────────────────────────────────────────

    def _fill_table(self):
        self._table.setRowCount(len(self._conductores))
        for r, c in enumerate(self._conductores):
            set_table_item(self._table, r, 0, c["nombre"])
            set_table_item(self._table, r, 1, c["rut"])
            set_table_item(self._table, r, 2, c["estado"], badge=True)
            set_table_item(self._table, r, 3, c["licencia"])
            set_table_item(self._table, r, 4, c["licencia_vence"])
            set_table_item(self._table, r, 5, c["sucursal"])
            set_table_item(self._table, r, 6, c["asignacion_activa"] or "—")

            btn = QPushButton("Gestionar")
            btn.setObjectName("btn_table_action")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=r: self._ver_detalle(i))
            self._table.setCellWidget(r, 7, btn)

        self._table.resizeColumnsToContents()

    # ── Detalle ───────────────────────────────────────────────────

    def _ver_detalle(self, idx: int):
        dlg = DetalleConductorDialog(self._conductores[idx], self)
        if dlg.exec():
            self._fill_table()

    # ── Agregar ───────────────────────────────────────────────────

    def _agregar(self):
        dlg = AgregarConductorDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            data["estado"]           = "Disponible"
            data["habilitado"]       = True
            data["asignacion_activa"] = None
            self._conductores.append(data)
            self._fill_table()
            QMessageBox.information(self, "Conductor agregado",
                                    f"{data['nombre']} registrado correctamente.")


# ─────────────────────────────────────────────────────────────────
class DetalleConductorDialog(QDialog):

    def __init__(self, conductor: dict, parent=None):
        super().__init__(parent)
        self._c = conductor
        self.setWindowTitle(conductor["nombre"])
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(14)

        # Encabezado
        h = QHBoxLayout()
        title = QLabel(self._c["nombre"])
        title.setObjectName("dialog_title")
        h.addWidget(title)
        h.addStretch()
        h.addWidget(make_badge(self._c["estado"]))
        layout.addLayout(h)

        # Info
        frame = QFrame()
        frame.setObjectName("panel")
        grid = QGridLayout(frame)
        grid.setContentsMargins(16, 14, 16, 14)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(8)
        fields = [
            ("RUT",             self._c["rut"]),
            ("Licencia",        self._c["licencia"]),
            ("Vence licencia",  self._c["licencia_vence"]),
            ("Sucursal",        self._c["sucursal"]),
            ("Teléfono",        self._c.get("telefono", "—")),
            ("Habilitado",      "Sí" if self._c["habilitado"] else "No"),
            ("Asignación",      self._c["asignacion_activa"] or "Sin asignación activa"),
        ]
        for i, (k, v) in enumerate(fields):
            lbl_k = QLabel(k + ":")
            lbl_k.setObjectName("form_label")
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet("color: #E8F0FE;")
            grid.addWidget(lbl_k, i, 0)
            grid.addWidget(lbl_v, i, 1)
        layout.addWidget(frame)

        # Acciones
        habilitado = self._c["habilitado"]
        estado     = self._c["estado"]

        if estado == "Asignado":
            layout.addWidget(make_info_frame(
                f"Conductor en asignación activa: {self._c['asignacion_activa']}. "
                "No se puede cambiar el estado en este momento."
            ))
        else:
            sec = QLabel("Acciones disponibles")
            sec.setObjectName("section_header")
            layout.addWidget(sec)

            btn_row = QHBoxLayout()
            if habilitado:
                btn_row.addWidget(make_action_button(
                    "Deshabilitar conductor", "btn_danger",
                    self._deshabilitar
                ))
            else:
                btn_row.addWidget(make_action_button(
                    "Habilitar conductor", "btn_success",
                    self._habilitar
                ))

            if estado == "Disponible":
                btn_row.addStretch()
                btn_row.addWidget(make_action_button(
                    "Poner en descanso", "btn_warning",
                    self._descanso
                ))
            elif estado == "En descanso":
                btn_row.addStretch()
                btn_row.addWidget(make_action_button(
                    "Marcar disponible", "btn_success",
                    self._disponible
                ))
            layout.addLayout(btn_row)

        # Cerrar
        close_row = QHBoxLayout()
        close_row.addStretch()
        btn_close = QPushButton("Cerrar")
        btn_close.setObjectName("btn_secondary")
        btn_close.clicked.connect(self.accept)
        close_row.addWidget(btn_close)
        layout.addLayout(close_row)

    # ── Acciones simuladas ────────────────────────────────────────

    def _habilitar(self):
        self._c["habilitado"] = True
        self._c["estado"]     = "Disponible"
        QMessageBox.information(self, "Conductor habilitado",
                                f"{self._c['nombre']} habilitado y disponible.")
        self.accept()

    def _deshabilitar(self):
        r = QMessageBox.question(self, "Deshabilitar conductor",
                                 f"¿Deshabilitar a {self._c['nombre']}?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            self._c["habilitado"] = False
            self._c["estado"]     = "No habilitado"
            QMessageBox.information(self, "Conductor deshabilitado",
                                    f"{self._c['nombre']} deshabilitado.")
            self.accept()

    def _descanso(self):
        self._c["estado"] = "En descanso"
        QMessageBox.information(self, "Estado actualizado",
                                f"{self._c['nombre']} marcado en descanso.")
        self.accept()

    def _disponible(self):
        self._c["estado"] = "Disponible"
        QMessageBox.information(self, "Estado actualizado",
                                f"{self._c['nombre']} disponible.")
        self.accept()


# ─────────────────────────────────────────────────────────────────
class AgregarConductorDialog(QDialog):
    """Formulario para registrar un nuevo conductor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Conductor")
        self.setMinimumWidth(400)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Registrar Nuevo Conductor")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        def lbl(t):
            l = QLabel(t)
            l.setObjectName("form_label")
            return l

        layout.addWidget(lbl("Nombre completo:"))
        self._nombre = QLineEdit()
        self._nombre.setPlaceholderText("Ej: Juan Pérez García")
        layout.addWidget(self._nombre)

        layout.addWidget(lbl("RUT:"))
        self._rut = QLineEdit()
        self._rut.setPlaceholderText("Ej: 12.345.678-9")
        layout.addWidget(self._rut)

        layout.addWidget(lbl("Tipo de licencia:"))
        self._licencia = QComboBox()
        self._licencia.addItems(["Clase B", "Clase B · A2", "Clase C", "Clase D"])
        layout.addWidget(self._licencia)

        layout.addWidget(lbl("Sucursal:"))
        self._sucursal = QComboBox()
        self._sucursal.addItems(["Temuco", "Santiago", "Concepción", "Los Ángeles", "Valparaíso"])
        layout.addWidget(self._sucursal)

        layout.addWidget(lbl("Teléfono:"))
        self._telefono = QLineEdit()
        self._telefono.setPlaceholderText("Ej: +56 9 1234 5678")
        layout.addWidget(self._telefono)

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
            "nombre":         self._nombre.text() or "Nuevo Conductor",
            "rut":            self._rut.text()    or "00.000.000-0",
            "licencia":       self._licencia.currentText(),
            "licencia_vence": "12/2027",
            "sucursal":       self._sucursal.currentText(),
            "telefono":       self._telefono.text() or "—",
        }