"""
Módulo Incidentes — Reporte y gestión de incidencias en ruta.
Actores: Conductor, Supervisor Operacional.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog, QComboBox,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

from app.ui.components.widgets import TopBar, make_table, set_table_item
from app.data.mock_data import INCIDENTES, ASIGNACIONES


class IncidentesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._incidentes = list(INCIDENTES)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = TopBar(
            "Gestión de Incidentes",
            f"{len(self._incidentes)} incidentes registrados",
            "Reportar Incidente",
        )
        topbar.action_clicked.connect(self._reportar_incidente)
        layout.addWidget(topbar)

        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        # Info de clasificación
        info = QFrame()
        info.setObjectName("alert_info")
        il = QHBoxLayout(info)
        il.setContentsMargins(12, 10, 12, 10)
        il.addWidget(QLabel("Niveles de gravedad: "
                            "Menor (sin interrupción) · "
                            "Operativa (continúa con monitoreo) · "
                            "Crítica (inmovilización obligatoria)"))
        c_layout.addWidget(info)

        # Tabla
        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)

        cols = ["ID", "Asignación", "Vehículo", "Conductor", "Tipo", "Gravedad", "Estado", "Reportado", "Supervisor"]
        self._table = make_table(cols)
        self._fill_table()

        # Botón cerrar incidente al seleccionar
        self._table.cellClicked.connect(self._on_row_clicked)

        p_layout.addWidget(self._table)

        # Panel de acciones
        action_row = QHBoxLayout()
        action_row.addStretch()

        self._btn_marcar_gestion = QPushButton("Marcar En gestión")
        self._btn_marcar_gestion.setObjectName("btn_primary")
        self._btn_marcar_gestion.setVisible(False)
        self._btn_marcar_gestion.clicked.connect(self._marcar_en_gestion)
        action_row.addWidget(self._btn_marcar_gestion)

        self._btn_marcar_resuelto = QPushButton("Marcar Resuelto")
        self._btn_marcar_resuelto.setObjectName("btn_warning")
        self._btn_marcar_resuelto.setVisible(False)
        self._btn_marcar_resuelto.clicked.connect(self._marcar_resuelto)
        action_row.addWidget(self._btn_marcar_resuelto)

        self._btn_cerrar = QPushButton("Cerrar Incidente Seleccionado")
        self._btn_cerrar.setObjectName("btn_success")
        self._btn_cerrar.setVisible(False)
        self._btn_cerrar.clicked.connect(self._cerrar_incidente)
        action_row.addWidget(self._btn_cerrar)

        p_layout.addLayout(action_row)

        c_layout.addWidget(panel)
        layout.addWidget(content)

        self._selected_row = -1

    def _fill_table(self):
        self._table.setRowCount(len(self._incidentes))
        for r, inc in enumerate(self._incidentes):
            set_table_item(self._table, r, 0, inc["id"])
            set_table_item(self._table, r, 1, inc["asignacion_id"])
            set_table_item(self._table, r, 2, inc["vehiculo_patente"])
            set_table_item(self._table, r, 3, inc["conductor"])
            set_table_item(self._table, r, 4, inc["tipo"])
            set_table_item(self._table, r, 5, inc["gravedad"], badge=True)
            set_table_item(self._table, r, 6, inc["estado"], badge=True)
            set_table_item(self._table, r, 7, inc["hora_reporte"])
            set_table_item(self._table, r, 8, inc["supervisor"])
        self._table.resizeColumnsToContents()

    def _on_row_clicked(self, row, _col):
        self._selected_row = row
        self._update_action_buttons()

    def _update_action_buttons(self):
        if self._selected_row < 0:
            self._btn_marcar_gestion.setVisible(False)
            self._btn_marcar_resuelto.setVisible(False)
            self._btn_cerrar.setVisible(False)
            return

        inc = self._incidentes[self._selected_row]
        estado = inc["estado"]
        self._btn_marcar_gestion.setVisible(estado == "Registrado")
        self._btn_marcar_resuelto.setVisible(estado == "En gestión")
        self._btn_cerrar.setVisible(estado == "Resuelto")
        self._btn_cerrar.setEnabled(estado == "Resuelto")

    def _marcar_en_gestion(self):
        if self._selected_row < 0:
            return
        inc = self._incidentes[self._selected_row]
        if inc["estado"] != "Registrado":
            return
        inc["estado"] = "En gestión"
        self._fill_table()
        self._update_action_buttons()
        QMessageBox.information(self, "Incidente en gestión",
                                f"Incidente {inc['id']} pasó a 'En gestión'.")

    def _marcar_resuelto(self):
        if self._selected_row < 0:
            return
        inc = self._incidentes[self._selected_row]
        if inc["estado"] != "En gestión":
            return
        inc["estado"] = "Resuelto"
        self._fill_table()
        self._update_action_buttons()
        QMessageBox.information(self, "Incidente resuelto",
                                f"Incidente {inc['id']} marcado como 'Resuelto'.")

    def _cerrar_incidente(self):
        if self._selected_row < 0:
            return
        inc = self._incidentes[self._selected_row]
        reply = QMessageBox.question(
            self, "Cerrar incidente",
            f"¿Cerrar {inc['id']}?\n\nEsto requiere aprobación técnica y administrativa.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            inc["estado"] = "Cerrado"
            self._fill_table()
            self._btn_cerrar.setEnabled(False)
            QMessageBox.information(self, "Incidente cerrado",
                                    f"Incidente {inc['id']} cerrado formalmente.")

    def _reportar_incidente(self):
        dlg = ReportarIncidenteDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            nuevo = {
                "id": f"INC-{len(self._incidentes) + 1:03d}",
                "asignacion_id": data["asignacion_id"],
                "vehiculo_patente": data["vehiculo_patente"],
                "conductor": data["conductor"],
                "tipo": data["tipo"],
                "descripcion": data["descripcion"],
                "gravedad": data["gravedad"],
                "estado": "Registrado",
                "hora_reporte": _now(),
                "supervisor": "Felipe Rivas",
                "resolucion": "",
            }
            self._incidentes.append(nuevo)
            self._fill_table()
            QMessageBox.information(self, "Incidente registrado",
                                    f"Incidente {nuevo['id']} reportado. El supervisor ha sido notificado.")


# ─────────────────────────────────────────────
class ReportarIncidenteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reportar Incidente en Ruta")
        self.setMinimumWidth(460)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Reportar Incidente en Ruta")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        def lbl(t):
            l = QLabel(t)
            l.setObjectName("form_label")
            return l

        layout.addWidget(lbl("Asignación afectada:"))
        self._asignacion = QComboBox()
        activas = [a["id"] for a in ASIGNACIONES if a["estado"] == "En ejecución"]
        self._asignacion.addItems(activas or ["AS-003"])
        layout.addWidget(self._asignacion)

        layout.addWidget(lbl("Vehículo:"))
        self._vehiculo = QComboBox()
        self._vehiculo.addItems(["BKRT-42", "GKRS-91", "FLRT-15", "MRTS-34"])
        layout.addWidget(self._vehiculo)

        layout.addWidget(lbl("Conductor:"))
        self._conductor = QComboBox()
        self._conductor.addItems(["Carlos Moya", "Marco Díaz", "Rodrigo Pérez", "Andrea Fuentes"])
        layout.addWidget(self._conductor)

        layout.addWidget(lbl("Tipo de incidente:"))
        self._tipo = QComboBox()
        self._tipo.addItems(["Falla mecánica", "Accidente", "Demora", "Problema de carga", "Otro"])
        layout.addWidget(self._tipo)

        layout.addWidget(lbl("Gravedad:"))
        self._gravedad = QComboBox()
        self._gravedad.addItems(["Menor", "Operativa", "Crítica"])
        layout.addWidget(self._gravedad)

        layout.addWidget(lbl("Descripción del incidente:"))
        self._descripcion = QTextEdit()
        self._descripcion.setPlaceholderText("Describe el incidente con detalle...")
        self._descripcion.setFixedHeight(80)
        layout.addWidget(self._descripcion)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Reportar Incidente")
        btn_ok.setObjectName("btn_danger")
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {
            "asignacion_id": self._asignacion.currentText(),
            "vehiculo_patente": self._vehiculo.currentText(),
            "conductor": self._conductor.currentText(),
            "tipo": self._tipo.currentText(),
            "gravedad": self._gravedad.currentText(),
            "descripcion": self._descripcion.toPlainText(),
        }


def _now():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")
