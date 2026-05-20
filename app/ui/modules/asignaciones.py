"""
Módulo Asignaciones — Listado, creación y validación de asignaciones.
Actor principal: Encargado de Flota.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog, QComboBox,
    QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt

from app.ui.components.widgets import TopBar, make_table, set_table_item
from app.data.mock_data import ASIGNACIONES, VEHICULOS, CONDUCTORES, SOLICITUDES


class AsignacionesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._asignaciones = list(ASIGNACIONES)
        self._build_ui()

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

        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)

        cols = ["ID", "Solicitud", "Vehículo", "Conductor", "Origen → Destino", "Prioridad", "Estado", "Inicio", "Fin"]
        self._table = make_table(cols)
        self._fill_table()
        p_layout.addWidget(self._table)

        c_layout.addWidget(panel)
        layout.addWidget(content)

    def _fill_table(self):
        self._table.setRowCount(len(self._asignaciones))
        for r, a in enumerate(self._asignaciones):
            ruta = f"{a['origen']} → {a['destino']}"
            set_table_item(self._table, r, 0, a["id"])
            set_table_item(self._table, r, 1, a["solicitud_id"])
            set_table_item(self._table, r, 2, a["vehiculo_patente"])
            set_table_item(self._table, r, 3, a["conductor"])
            set_table_item(self._table, r, 4, ruta)
            set_table_item(self._table, r, 5, a["prioridad"], badge=True)
            set_table_item(self._table, r, 6, a["estado"], badge=True)
            set_table_item(self._table, r, 7, a["inicio"] or "—")
            set_table_item(self._table, r, 8, a["fin"] or "—")
        self._table.resizeColumnsToContents()

    def _nueva_asignacion(self):
        dlg = NuevaAsignacionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            # Validación básica
            vehiculo = next((v for v in VEHICULOS if v["patente"] == data["vehiculo_patente"]), None)
            conductor = next((c for c in CONDUCTORES if c["nombre"] == data["conductor"]), None)

            errores = []
            if vehiculo and vehiculo["estado"] not in ("Disponible", "Reservado"):
                errores.append(f"Vehículo {data['vehiculo_patente']} no está disponible (estado: {vehiculo['estado']}).")
            if conductor and not conductor["habilitado"]:
                errores.append(f"Conductor {data['conductor']} no está habilitado.")

            if errores:
                QMessageBox.warning(self, "Validación fallida",
                                    "No se puede crear la asignación:\n\n• " + "\n• ".join(errores))
                return

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
            QMessageBox.information(self, "Asignación creada",
                                    f"Asignación {nueva['id']} confirmada exitosamente.")


# ─────────────────────────────────────────────
class NuevaAsignacionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Asignación")
        self.setMinimumWidth(460)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Crear Asignación Vehículo + Conductor")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        # Info sobre validación automática
        info = QFrame()
        info.setObjectName("alert_info")
        info_layout = QHBoxLayout(info)
        info_layout.setContentsMargins(12, 8, 12, 8)
        info_layout.addWidget(QLabel("El sistema validará aptitud técnica, documental y disponibilidad."))
        layout.addWidget(info)

        def lbl(text):
            l = QLabel(text)
            l.setObjectName("form_label")
            return l

        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)

        # Solicitud
        form_layout.addWidget(lbl("Solicitud vinculada:"))
        self._solicitud = QComboBox()
        sol_disponibles = [s for s in SOLICITUDES if s["estado"] in ("Creada", "En evaluación", "Pendiente")]
        self._solicitud.addItems([s["id"] for s in sol_disponibles] or ["SOL-005"])
        form_layout.addWidget(self._solicitud)

        # Vehículo
        form_layout.addWidget(lbl("Vehículo (solo disponibles):"))
        self._vehiculo = QComboBox()
        disponibles = [v["patente"] for v in VEHICULOS if v["estado"] == "Disponible"]
        self._vehiculo.addItems(disponibles or ["Sin vehículos disponibles"])
        form_layout.addWidget(self._vehiculo)

        # Conductor
        form_layout.addWidget(lbl("Conductor (solo habilitados):"))
        self._conductor = QComboBox()
        conductores_ok = [c["nombre"] for c in CONDUCTORES if c["habilitado"] and c["estado"] == "Disponible"]
        self._conductor.addItems(conductores_ok or ["Sin conductores disponibles"])
        form_layout.addWidget(self._conductor)

        # Origen / Destino
        row = QHBoxLayout()
        origen_col = QVBoxLayout()
        origen_col.addWidget(lbl("Origen:"))
        self._origen = QComboBox()
        self._origen.addItems(["Temuco", "Santiago", "Concepción", "Los Ángeles", "Valparaíso"])
        origen_col.addWidget(self._origen)
        row.addLayout(origen_col)

        dest_col = QVBoxLayout()
        dest_col.addWidget(lbl("Destino:"))
        self._destino = QComboBox()
        self._destino.addItems(["Concepción", "Santiago", "Temuco", "Valparaíso", "Los Ángeles"])
        dest_col.addWidget(self._destino)
        row.addLayout(dest_col)
        form_layout.addLayout(row)

        # Prioridad
        form_layout.addWidget(lbl("Prioridad:"))
        self._prioridad = QComboBox()
        self._prioridad.addItems(["Alta", "Media", "Baja"])
        form_layout.addWidget(self._prioridad)

        layout.addLayout(form_layout)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Confirmar Asignación")
        btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {
            "solicitud_id": self._solicitud.currentText(),
            "vehiculo_patente": self._vehiculo.currentText(),
            "conductor": self._conductor.currentText(),
            "origen": self._origen.currentText(),
            "destino": self._destino.currentText(),
            "prioridad": self._prioridad.currentText(),
        }


def _now():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")
