"""
Módulo Asignaciones — Prototipo navegable.
Actor principal: Encargado de Flota.

Flujo:
Confirmada → En ejecución → Completada → Cerrada
"""

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
    QDialog, QComboBox, QMessageBox,
    QGridLayout
)

from app.ui.components.widgets import (
    TopBar,
    make_table,
    set_table_item,
    make_badge,
    KpiCard,
    make_action_button,
    make_info_frame,
)

from app.data.mock_data import (
    ASIGNACIONES,
    VEHICULOS,
    CONDUCTORES,
    SOLICITUDES,
)


# ─────────────────────────────────────────────────────────────
# Vista principal
# ─────────────────────────────────────────────────────────────

class AsignacionesView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._asignaciones = list(ASIGNACIONES)

        self._build_ui()

    # ─────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = TopBar(
            "Asignaciones",
            "Gestión de asignaciones vehículo + conductor",
            "＋ Nueva Asignación",
        )

        topbar.action_clicked.connect(self._nueva_asignacion)

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

        hint = QLabel(
            "Haz clic en «Gestionar» para ejecutar acciones sobre una asignación."
        )
        hint.setObjectName("page_subtitle")

        p_layout.addWidget(hint)

        cols = [
            "ID",
            "Solicitud",
            "Vehículo",
            "Conductor",
            "Ruta",
            "Prioridad",
            "Estado",
            "Inicio",
            "Fin",
            "Acciones",
        ]

        self._table = make_table(cols)

        self._fill_table()

        p_layout.addWidget(self._table)

        c_layout.addWidget(panel)

        layout.addWidget(content)

    # ─────────────────────────────────────────

    def _build_kpis(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        estados = [a["estado"] for a in self._asignaciones]

        row.addWidget(
            KpiCard(
                "Confirmadas",
                str(sum(1 for e in estados if e == "Confirmada")),
                color="#1E5FC3"
            )
        )

        row.addWidget(
            KpiCard(
                "En ejecución",
                str(sum(1 for e in estados if e == "En ejecución")),
                color="#D97706"
            )
        )

        row.addWidget(
            KpiCard(
                "Completadas",
                str(sum(1 for e in estados if "Completada" in e)),
                color="#16A34A"
            )
        )

        row.addWidget(
            KpiCard(
                "Total",
                str(len(self._asignaciones)),
                color="#E8F0FE"
            )
        )

        return row

    # ─────────────────────────────────────────

    def _fill_table(self):
        self._table.setRowCount(len(self._asignaciones))

        for r, a in enumerate(self._asignaciones):

            values = [
                a["id"],
                a["solicitud_id"],
                a["vehiculo_patente"],
                a["conductor"],
                f"{a['origen']} → {a['destino']}",
                a["prioridad"],
                a["estado"],
                a["inicio"] or "—",
                a["fin"] or "—",
            ]

            for c, value in enumerate(values):
                set_table_item(
                    self._table,
                    r,
                    c,
                    value,
                    badge=c in (5, 6)
                )

            btn = QPushButton("Gestionar")
            btn.setObjectName("btn_table_action")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            btn.clicked.connect(
                lambda _, idx=r: self._ver_detalle(idx)
            )

            self._table.setCellWidget(r, 9, btn)

        self._table.resizeColumnsToContents()

    # ─────────────────────────────────────────

    def _ver_detalle(self, row):
        dlg = DetalleAsignacionDialog(
            self._asignaciones[row],
            self
        )

        if dlg.exec():
            self._fill_table()

    # ─────────────────────────────────────────

    def _nueva_asignacion(self):
        dlg = NuevaAsignacionDialog(self)

        if dlg.exec() == QDialog.DialogCode.Accepted:

            data = dlg.get_data()

            nueva = {
                "id": f"AS-{len(self._asignaciones) + 1:03d}",
                "solicitud_id": data["solicitud_id"],
                "vehiculo_patente": data["vehiculo_patente"],
                "conductor": data["conductor"],
                "origen": data["origen"],
                "destino": data["destino"],
                "estado": "Confirmada",
                "inicio": None,
                "fin": None,
                "prioridad": data["prioridad"],
            }

            self._asignaciones.append(nueva)

            self._fill_table()

            QMessageBox.information(
                self,
                "Asignación creada",
                "Asignación creada exitosamente."
            )


# ─────────────────────────────────────────────────────────────
# Detalle asignación
# ─────────────────────────────────────────────────────────────

class DetalleAsignacionDialog(QDialog):

    def __init__(self, asig, parent=None):
        super().__init__(parent)

        self._asig = asig

        self.setWindowTitle(f"Asignación {asig['id']}")
        self.setMinimumWidth(520)

        self._build_ui()

    # ─────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)

        self._build_header(layout)
        self._build_info(layout)
        self._build_actions(layout)

    # ─────────────────────────────────────────

    def _build_header(self, layout):
        row = QHBoxLayout()

        title = QLabel(f"Asignación {self._asig['id']}")
        title.setObjectName("dialog_title")

        badge = make_badge(self._asig["estado"])

        row.addWidget(title)
        row.addStretch()
        row.addWidget(badge)

        layout.addLayout(row)
        layout.addSpacing(20)

    # ─────────────────────────────────────────

    def _build_info(self, layout):
        frame = QFrame()
        frame.setObjectName("panel")

        grid = QGridLayout(frame)

        fields = [
            ("Solicitud", self._asig["solicitud_id"]),
            ("Vehículo", self._asig["vehiculo_patente"]),
            ("Conductor", self._asig["conductor"]),
            ("Ruta", f"{self._asig['origen']} → {self._asig['destino']}"),
            ("Prioridad", self._asig["prioridad"]),
            ("Inicio", self._asig["inicio"] or "Pendiente"),
            ("Fin", self._asig["fin"] or "Pendiente"),
        ]

        for i, (label, value) in enumerate(fields):

            lbl = QLabel(label + ":")
            lbl.setObjectName("form_label")

            val = QLabel(value)
            val.setStyleSheet("color: #E8F0FE;")

            grid.addWidget(lbl, i, 0)
            grid.addWidget(val, i, 1)

        layout.addWidget(frame)
        layout.addSpacing(18)

    # ─────────────────────────────────────────

    def _build_actions(self, layout):
        estado = self._asig["estado"]

        if estado == "Confirmada":
            self._acciones_confirmada(layout)

        elif estado == "En ejecución":
            self._acciones_ruta(layout)

        elif estado in ("Completada", "Completada con incidencia"):
            self._acciones_completada(layout)

        else:
            lbl = QLabel(
                "No hay acciones disponibles para esta asignación."
            )

            lbl.setObjectName("page_subtitle")

            layout.addWidget(lbl)

    # ─────────────────────────────────────────

    def _acciones_confirmada(self, layout):

        layout.addWidget(
            make_info_frame(
                "El conductor debe revisar el vehículo antes de salir."
            )
        )

        layout.addSpacing(10)

        row = QHBoxLayout()

        row.addWidget(
            make_action_button(
                "Confirmar Check-out",
                "btn_success",
                self._checkout,
                "✓"
            )
        )

        row.addStretch()

        row.addWidget(
            make_action_button(
                "Cancelar",
                "btn_danger",
                self._cancelar,
                "✕"
            )
        )

        layout.addLayout(row)

    # ─────────────────────────────────────────

    def _acciones_ruta(self, layout):

        layout.addWidget(
            make_info_frame(
                "La asignación se encuentra actualmente en ruta."
            )
        )

        layout.addSpacing(10)

        row = QHBoxLayout()

        row.addWidget(
            make_action_button(
                "Registrar Entrega",
                "btn_success",
                self._entrega,
                ""
            )
        )

        row.addStretch()

        row.addWidget(
            make_action_button(
                "Reportar Incidente",
                "btn_warning",
                self._incidente,
                ""
            )
        )

        layout.addLayout(row)

    # ─────────────────────────────────────────

    def _acciones_completada(self, layout):

        layout.addWidget(
            make_info_frame(
                "La entrega fue registrada correctamente."
            )
        )

        layout.addSpacing(10)

        row = QHBoxLayout()
        row.addStretch()

        row.addWidget(
            make_action_button(
                "Cerrar Asignación",
                "btn_primary",
                self._cerrar,
                ""
            )
        )

        layout.addLayout(row)

    # ─────────────────────────────────────────
    # Acciones simples de maqueta
    # ─────────────────────────────────────────

    def _checkout(self):
        self._asig["estado"] = "En ejecución"
        self._asig["inicio"] = _now()

        QMessageBox.information(
            self,
            "Check-out",
            "Vehículo enviado a ruta."
        )

        self.accept()

    # ─────────────────────────────────────────

    def _entrega(self):

        resp = QMessageBox.question(
            self,
            "Entrega",
            "¿La entrega fue conforme?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        self._asig["fin"] = _now()

        self._asig["estado"] = (
            "Completada"
            if resp == QMessageBox.StandardButton.Yes
            else "Completada con incidencia"
        )

        QMessageBox.information(
            self,
            "Entrega",
            "Entrega registrada."
        )

        self.accept()

    # ─────────────────────────────────────────

    def _cerrar(self):
        self._asig["estado"] = "Cerrada"

        QMessageBox.information(
            self,
            "Asignación",
            "Asignación cerrada."
        )

        self.accept()

    # ─────────────────────────────────────────

    def _cancelar(self):
        self._asig["estado"] = "Cancelada"

        QMessageBox.warning(
            self,
            "Asignación",
            "Asignación cancelada."
        )

        self.accept()

    # ─────────────────────────────────────────

    def _incidente(self):
        QMessageBox.information(
            self,
            "Incidente",
            "Para registrar el incidente, ve al módulo Incidentes y vincula esta asignación."
        )


# ─────────────────────────────────────────────────────────────
# Nueva asignación
# ─────────────────────────────────────────────────────────────

class NuevaAsignacionDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Nueva Asignación")
        self.setMinimumWidth(460)

        self._build_ui()

    # ─────────────────────────────────────────

    def _build_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Crear Asignación")
        title.setObjectName("dialog_title")

        layout.addWidget(title)

        layout.addWidget(
            make_info_frame(
                "Selecciona vehículo, conductor y ruta."
            )
        )

        def lbl(text):
            l = QLabel(text)
            l.setObjectName("form_label")
            return l

        form = QVBoxLayout()

        # solicitud
        form.addWidget(lbl("Solicitud vinculada:"))

        self._solicitud = QComboBox()

        self._solicitud.addItems(
            [s["id"] for s in SOLICITUDES]
        )

        form.addWidget(self._solicitud)

        # vehículo
        form.addWidget(lbl("Vehículo:"))

        self._vehiculo = QComboBox()

        self._vehiculo.addItems(
            [v["patente"] for v in VEHICULOS]
        )

        form.addWidget(self._vehiculo)

        # conductor
        form.addWidget(lbl("Conductor:"))

        self._conductor = QComboBox()

        self._conductor.addItems(
            [c["nombre"] for c in CONDUCTORES]
        )

        form.addWidget(self._conductor)

        # origen / destino
        row = QHBoxLayout()

        col1 = QVBoxLayout()
        col2 = QVBoxLayout()

        col1.addWidget(lbl("Origen:"))
        col2.addWidget(lbl("Destino:"))

        self._origen = QComboBox()
        self._destino = QComboBox()

        ciudades = [
            "Temuco",
            "Santiago",
            "Concepción",
            "Valparaíso",
            "Los Ángeles",
        ]

        self._origen.addItems(ciudades)
        self._destino.addItems(ciudades)

        col1.addWidget(self._origen)
        col2.addWidget(self._destino)

        row.addLayout(col1)
        row.addLayout(col2)

        form.addLayout(row)

        # prioridad
        form.addWidget(lbl("Prioridad:"))

        self._prioridad = QComboBox()
        self._prioridad.addItems(["Alta", "Media", "Baja"])

        form.addWidget(self._prioridad)

        layout.addLayout(form)

        # botones
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Crear")
        btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)

        layout.addLayout(btn_row)

    # ─────────────────────────────────────────

    def get_data(self):

        return {
            "solicitud_id": self._solicitud.currentText(),
            "vehiculo_patente": self._vehiculo.currentText(),
            "conductor": self._conductor.currentText(),
            "origen": self._origen.currentText(),
            "destino": self._destino.currentText(),
            "prioridad": self._prioridad.currentText(),
        }


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")