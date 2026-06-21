from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog, QComboBox,
    QTextEdit, QMessageBox, QCheckBox, QSpinBox,
)
from PyQt6.QtCore import Qt

from app.ui.components.widgets import TopBar, make_table, set_table_item, make_info_frame
from app.data.queries import incidentes_queries
from app.core.events import event_bus


class IncidentesView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._incidentes = []
        self._selected_row = -1

        self._cargar_incidentes()
        self._build_ui()

        event_bus.incidente_actualizado.connect(self._recargar)

    # ── Carga / recarga ───────────────────────────────────────────────────────

    def _cargar_incidentes(self):
        """Carga incidentes desde la base de datos."""
        self._incidentes = incidentes_queries.obtener_todos_incidentes()

    def _recargar(self):
        self._cargar_incidentes()
        self._selected_row = -1
        self._fill_table()
        self._update_action_buttons()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._topbar = TopBar(
            "Gestión de Incidentes",
            f"{len(self._incidentes)} incidentes registrados",
            "Reportar Incidente",
        )
        self._topbar.action_clicked.connect(self._reportar_incidente)
        layout.addWidget(self._topbar)

        content = QWidget()
        content.setObjectName("content_area")

        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        info = QFrame()
        info.setObjectName("alert_info")

        il = QHBoxLayout(info)
        il.setContentsMargins(12, 10, 12, 10)
        il.addWidget(QLabel(
            "Niveles de gravedad: "
            "Incidente menor · Falla operativa · Falla crítica"
        ))

        c_layout.addWidget(info)

        panel = QFrame()
        panel.setObjectName("panel")

        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)

        cols = [
            "ID", "Asignación", "Vehículo", "Conductor",
            "Ruta", "Gravedad", "Estado", "Reportado", "Supervisor",
        ]
        self._table = make_table(cols)
        self._table.cellClicked.connect(self._on_row_clicked)

        self._fill_table()
        p_layout.addWidget(self._table)

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

    def _fill_table(self):
        self._table.setRowCount(len(self._incidentes))

        for r, inc in enumerate(self._incidentes):
            set_table_item(self._table, r, 0, inc["id"])
            set_table_item(self._table, r, 1, inc["asignacion_id"])
            set_table_item(self._table, r, 2, inc["vehiculo_patente"])
            set_table_item(self._table, r, 3, inc["conductor"])
            set_table_item(self._table, r, 4, inc["ruta"])
            set_table_item(self._table, r, 5, inc["gravedad"], badge=True)
            set_table_item(self._table, r, 6, inc["estado"], badge=True)
            set_table_item(self._table, r, 7, inc["hora_reporte"])
            set_table_item(self._table, r, 8, inc["supervisor"])

        self._table.resizeColumnsToContents()

    # ── Selección / acciones ──────────────────────────────────────────────────

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
        estado_raw = inc["estado_raw"]

        self._btn_marcar_gestion.setVisible(estado_raw == "Registrado")
        self._btn_marcar_resuelto.setVisible(estado_raw == "En_Gestion")
        self._btn_cerrar.setVisible(estado_raw == "Resuelto")
        self._btn_cerrar.setEnabled(estado_raw == "Resuelto")

    def _marcar_en_gestion(self):
        if self._selected_row < 0:
            return

        inc = self._incidentes[self._selected_row]
        if inc["estado_raw"] != "Registrado":
            return

        ok = incidentes_queries.actualizar_estado_incidente(
            inc["incidente_id"],
            "En_Gestion",
        )

        if ok:
            event_bus.incidente_actualizado.emit()
            QMessageBox.information(
                self,
                "Incidente en gestión",
                f"Incidente {inc['id']} pasó a 'En gestión'.",
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo actualizar el incidente.",
            )

    def _marcar_resuelto(self):
        if self._selected_row < 0:
            return

        inc = self._incidentes[self._selected_row]
        if inc["estado_raw"] != "En_Gestion":
            return

        ok = incidentes_queries.actualizar_estado_incidente(
            inc["incidente_id"],
            "Resuelto",
        )

        if ok:
            event_bus.incidente_actualizado.emit()
            QMessageBox.information(
                self,
                "Incidente resuelto",
                f"Incidente {inc['id']} marcado como 'Resuelto'.",
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo actualizar el incidente.",
            )

    def _cerrar_incidente(self):
        if self._selected_row < 0:
            return

        inc = self._incidentes[self._selected_row]

        reply = QMessageBox.question(
            self,
            "Cerrar incidente",
            (
                f"¿Cerrar {inc['id']}?\n\n"
                "Esto representa el cierre formal del incidente."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        ok = incidentes_queries.actualizar_estado_incidente(
            inc["incidente_id"],
            "Cerrado",
        )

        if ok:
            event_bus.incidente_actualizado.emit()
            QMessageBox.information(
                self,
                "Incidente cerrado",
                f"Incidente {inc['id']} cerrado formalmente.",
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo cerrar el incidente.",
            )

    # ── Reporte de incidente ──────────────────────────────────────────────────

    def _reportar_incidente(self):
        asignaciones = incidentes_queries.obtener_asignaciones_para_incidente()

        if not asignaciones:
            QMessageBox.warning(
                self,
                "Sin asignaciones activas",
                (
                    "No existen asignaciones en ejecución o con incidencia.\n"
                    "Primero debes tener una asignación en ruta para reportar un incidente."
                ),
            )
            return

        dlg = ReportarIncidenteDialog(asignaciones, self)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        data = dlg.get_data()

        if not data["descripcion"]:
            QMessageBox.warning(
                self,
                "Descripción obligatoria",
                "Debes ingresar una descripción del incidente.",
            )
            return

        ok = incidentes_queries.crear_incidente(
            asignacion_id=data["asignacion_db_id"],
            clasificacion_gravedad=data["gravedad_raw"],
            descripcion_falla=data["descripcion"],
            requiere_asistencia=data["requiere_asistencia"],
            kilometro_ruta=data["kilometro_ruta"],
        )

        if ok:
            event_bus.incidente_actualizado.emit()
            QMessageBox.information(
                self,
                "Incidente registrado",
                "Incidente reportado correctamente.",
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo registrar el incidente.",
            )


# ──────────────────────────────────────────────────────────────────────────────

class ReportarIncidenteDialog(QDialog):

    def __init__(self, asignaciones: list[dict], parent=None):
        super().__init__(parent)

        self._asignaciones = asignaciones

        self.setWindowTitle("Reportar Incidente en Ruta")
        self.setMinimumWidth(520)
        self.setModal(True)

        self._build_ui()
        self._cargar_asignaciones()

        if self._asignacion.count() > 0:
            self._actualizar_info_asignacion()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Reportar Incidente en Ruta")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        layout.addWidget(make_info_frame(
            "Selecciona la asignación afectada. Vehículo, conductor y ruta "
            "se cargan automáticamente desde la asignación real."
        ))

        def lbl(text):
            l = QLabel(text)
            l.setObjectName("form_label")
            return l

        layout.addWidget(lbl("Asignación afectada:"))
        self._asignacion = QComboBox()
        self._asignacion.currentIndexChanged.connect(self._actualizar_info_asignacion)
        layout.addWidget(self._asignacion)

        info_frame = QFrame()
        info_frame.setObjectName("panel")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(14, 12, 14, 12)
        info_layout.setSpacing(6)

        self._lbl_vehiculo = QLabel("Vehículo: —")
        self._lbl_conductor = QLabel("Conductor: —")
        self._lbl_ruta = QLabel("Ruta: —")
        self._lbl_prioridad = QLabel("Prioridad: —")
        self._lbl_estado = QLabel("Estado asignación: —")

        for label in [
            self._lbl_vehiculo,
            self._lbl_conductor,
            self._lbl_ruta,
            self._lbl_prioridad,
            self._lbl_estado,
        ]:
            label.setStyleSheet("color: #E8F0FE;")
            info_layout.addWidget(label)

        layout.addWidget(info_frame)

        layout.addWidget(lbl("Gravedad:"))
        self._gravedad = QComboBox()
        self._gravedad.addItem("Incidente menor", "Incidente_Menor")
        self._gravedad.addItem("Falla operativa", "Falla_Operativa")
        self._gravedad.addItem("Falla crítica", "Falla_Critica")
        layout.addWidget(self._gravedad)

        self._requiere_asistencia = QCheckBox("Requiere asistencia")
        layout.addWidget(self._requiere_asistencia)

        layout.addWidget(lbl("Kilómetro de la ruta:"))
        self._kilometro = QSpinBox()
        self._kilometro.setRange(0, 9999)
        self._kilometro.setSpecialValueText("No informado")
        layout.addWidget(self._kilometro)

        layout.addWidget(lbl("Descripción del incidente:"))
        self._descripcion = QTextEdit()
        self._descripcion.setPlaceholderText("Describe el incidente con detalle...")
        self._descripcion.setFixedHeight(90)
        layout.addWidget(self._descripcion)

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

    def _cargar_asignaciones(self):
        self._asignacion.clear()

        for asig in self._asignaciones:
            texto = f"{asig['id']} · {asig['vehiculo_patente']} · {asig['ruta']}"
            self._asignacion.addItem(texto, asig["asignacion_db_id"])

    def _asignacion_actual(self) -> dict | None:
        asignacion_id = self._asignacion.currentData()

        for asig in self._asignaciones:
            if asig["asignacion_db_id"] == asignacion_id:
                return asig

        return None

    def _actualizar_info_asignacion(self):
        asig = self._asignacion_actual()

        if not asig:
            self._lbl_vehiculo.setText("Vehículo: —")
            self._lbl_conductor.setText("Conductor: —")
            self._lbl_ruta.setText("Ruta: —")
            self._lbl_prioridad.setText("Prioridad: —")
            self._lbl_estado.setText("Estado asignación: —")
            return

        self._lbl_vehiculo.setText(f"Vehículo: {asig['vehiculo_patente']}")
        self._lbl_conductor.setText(f"Conductor: {asig['conductor']}")
        self._lbl_ruta.setText(f"Ruta: {asig['ruta']}")
        self._lbl_prioridad.setText(f"Prioridad: {asig['prioridad']}")
        self._lbl_estado.setText(f"Estado asignación: {asig['estado']}")

    def get_data(self) -> dict:
        kilometro = self._kilometro.value()

        return {
            "asignacion_db_id": self._asignacion.currentData(),
            "gravedad_raw": self._gravedad.currentData(),
            "descripcion": self._descripcion.toPlainText().strip(),
            "requiere_asistencia": self._requiere_asistencia.isChecked(),
            "kilometro_ruta": kilometro if kilometro > 0 else None,
        }