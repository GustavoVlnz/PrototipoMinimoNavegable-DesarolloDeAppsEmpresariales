#app/ui/modules/asignaciones.py

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QDialog, QComboBox, QMessageBox, QGridLayout
)
from app.ui.components.widgets import (
    TopBar, make_table, set_table_item, make_badge, KpiCard,
    make_action_button, make_info_frame
)
from app.data.queries import asignaciones_queries
from app.logic import asignaciones_service
from app.logic import transition_service
from app.core.events import event_bus


class AsignacionesView(QWidget):

    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.db_session = db_session
        self._asignaciones = []
        self._build_ui()
        self.cargar_datos()
        event_bus.asignacion_actualizada.connect(self.cargar_datos)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.topbar = TopBar(
            "Asignaciones",
            "Gestión de asignaciones vehículo + conductor",
            "＋ Nueva Asignación",
        )
        self.topbar.action_clicked.connect(self._nueva_asignacion)
        layout.addWidget(self.topbar)

        content = QWidget()
        content.setObjectName("content_area")
        self.c_layout = QVBoxLayout(content)
        self.c_layout.setContentsMargins(28, 24, 28, 28)
        self.c_layout.setSpacing(16)

        self.kpi_widget = QWidget()
        self.kpi_layout = QHBoxLayout(self.kpi_widget)
        self.kpi_layout.setContentsMargins(0, 0, 0, 0)
        self.c_layout.addWidget(self.kpi_widget)

        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 12, 16, 16)

        hint = QLabel("Haz clic en «Gestionar» para ejecutar acciones sobre una asignación.")
        hint.setObjectName("page_subtitle")
        p_layout.addWidget(hint)

        cols = ["ID", "Solicitud", "Vehículo", "Conductor", "Ruta", "Prioridad", "Estado", "Inicio", "Fin", "Acciones"]
        self._table = make_table(cols)
        p_layout.addWidget(self._table)
        self.c_layout.addWidget(panel)
        layout.addWidget(content)

    def cargar_datos(self):
        self._asignaciones = asignaciones_queries.obtener_todas(self.db_session)
        self._actualizar_kpis()
        self._fill_table()

    def _actualizar_kpis(self):
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        estados = [a["estado"] for a in self._asignaciones]
        self.kpi_layout.addWidget(KpiCard("Confirmadas", str(sum(1 for e in estados if e == "Confirmada")), color="#1E5FC3"))
        self.kpi_layout.addWidget(KpiCard("En ejecución", str(sum(1 for e in estados if e == "En ejecución")), color="#D97706"))
        self.kpi_layout.addWidget(KpiCard("Completadas", str(sum(1 for e in estados if "Completada" in e)), color="#16A34A"))
        self.kpi_layout.addWidget(KpiCard("Total", str(len(self._asignaciones)), color="#E8F0FE"))

    def _fill_table(self):
        self._table.setRowCount(len(self._asignaciones))
        for r, a in enumerate(self._asignaciones):
            values = [
                a["id"], a["solicitud_id"], a["vehiculo_patente"], a["conductor"],
                f"{a['origen']} → {a['destino']}", a["prioridad"], a["estado"],
                a["inicio"] or "—", a["fin"] or "—"
            ]

            for c, value in enumerate(values):
                set_table_item(self._table, r, c, value, badge=c in (5, 6))

            btn = QPushButton("Gestionar")
            btn.setObjectName("btn_table_action")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, aid=a["id_numerico"]: self._ver_detalle(aid))
            self._table.setCellWidget(r, 9, btn)

        self._table.resizeColumnsToContents()

    def _ver_detalle(self, asignacion_id: int):
        dlg = DetalleAsignacionDialog(asignacion_id, self.db_session, self)
        if dlg.exec():
            self.cargar_datos()

    def _nueva_asignacion(self):
        solicitudes = asignaciones_queries.obtener_solicitudes_aprobadas(self.db_session)
        if not solicitudes:
            QMessageBox.warning(self, "Sin solicitudes", "No existen solicitudes aprobadas.")
            return

        vehiculos = asignaciones_queries.obtener_vehiculos_disponibles(self.db_session)
        if not vehiculos:
            QMessageBox.warning(self, "Sin vehículos", "No hay vehículos disponibles en este momento.")
            return

        conductores = asignaciones_queries.obtener_conductores_disponibles(self.db_session)
        if not conductores:
            QMessageBox.warning(self, "Sin conductores", "No hay conductores disponibles en este momento.")
            return

        dlg = NuevaAsignacionDialog(self.db_session, self, solicitudes, vehiculos, conductores)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            try:
                asignaciones_service.registrar_asignacion(
                    self.db_session,
                    solicitud_id=data["solicitud_id"],
                    vehiculo_id=data["vehiculo_id"],
                    conductor_id=data["conductor_id"],
                    asignado_por=1  # TODO: reemplazar con ID del usuario autenticado
                )
                self.cargar_datos()
                QMessageBox.information(self, "Asignación creada", "Asignación creada exitosamente en BD.")
            except asignaciones_service.AsignacionServiceError as e:
                QMessageBox.critical(self, "Error de validación", str(e))


class DetalleAsignacionDialog(QDialog):

    def __init__(self, asignacion_id: int, db_session, parent=None):
        super().__init__(parent)
        self.db_session = db_session
        self._asignacion_id = asignacion_id
        self._asig = asignaciones_queries.obtener_orm_por_id(db_session, asignacion_id)

        if not self._asig:
            self.setWindowTitle("Asignación no encontrada")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("No se encontró la asignación solicitada."))
            btn = QPushButton("Cerrar")
            btn.clicked.connect(self.reject)
            layout.addWidget(btn)
            return

        self.setWindowTitle(f"Asignación {self._asig.folio()}")
        self.setMinimumWidth(520)
        self._build_ui()

    def _build_ui(self):
        asig = self._asig

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        estado_display = asignaciones_queries.estado_display(asig.estado_asignacion)

        row = QHBoxLayout()
        title = QLabel(f"Asignación {asig.folio()}")
        title.setObjectName("dialog_title")
        badge = make_badge(estado_display)
        row.addWidget(title)
        row.addStretch()
        row.addWidget(badge)
        layout.addLayout(row)
        layout.addSpacing(20)

        frame = QFrame()
        frame.setObjectName("panel")
        grid = QGridLayout(frame)

        origen = asig.solicitud.sucursal_origen.nombre if asig.solicitud and asig.solicitud.sucursal_origen else "—"
        destino = asig.solicitud.sucursal_destino.nombre if asig.solicitud and asig.solicitud.sucursal_destino else "—"
        nombre_conductor = "—"
        if asig.conductor and asig.conductor.usuario:
            nombre_conductor = asig.conductor.usuario.nombre

        fields = [
            ("Solicitud", asig.solicitud.folio() if asig.solicitud else "—"),
            ("Vehículo", asig.vehiculo.patente if asig.vehiculo else "—"),
            ("Conductor", nombre_conductor),
            ("Ruta", f"{origen} → {destino}"),
            ("Prioridad", asig.solicitud.prioridad if asig.solicitud else "—"),
            ("Inicio", asig.fecha_asignacion.strftime("%Y-%m-%d %H:%M") if asig.fecha_asignacion else "Pendiente"),
            ("Fin", (
                asig.trazabilidad.fecha_hora_arribo_real.strftime("%Y-%m-%d %H:%M")
                if asig.trazabilidad and asig.trazabilidad.fecha_hora_arribo_real
                else "Pendiente"
            )),
        ]
        for i, (label, value) in enumerate(fields):
            lbl = QLabel(label + ":")
            lbl.setObjectName("form_label")
            val = QLabel(str(value))
            val.setStyleSheet("color: #E8F0FE;")
            grid.addWidget(lbl, i, 0)
            grid.addWidget(val, i, 1)

        layout.addWidget(frame)
        layout.addSpacing(18)
        acciones_mostradas = False

        if asig.estado_asignacion == "Confirmada" and transition_service.puede_transicionar(asig, "En_Ejecucion"):
            acciones_mostradas = True
            layout.addWidget(make_info_frame("El conductor debe revisar el vehículo antes de salir."))
            layout.addSpacing(10)
            r_box = QHBoxLayout()
            r_box.addWidget(make_action_button("Confirmar Check-out", "btn_success", self._checkout, "✓"))
            r_box.addStretch()
            r_box.addWidget(make_action_button("Cancelar", "btn_danger", self._cancelar, "✕"))
            layout.addLayout(r_box)

        elif (
            transition_service.puede_transicionar(asig, "Completada")
            or transition_service.puede_transicionar(asig, "Completada_Con_Incidencia")
        ):
            acciones_mostradas = True
            layout.addWidget(make_info_frame("La asignación se encuentra actualmente en ruta."))
            layout.addSpacing(10)
            r_box = QHBoxLayout()
            if transition_service.tiene_incidentes_activos(asig):
                layout.addWidget(make_info_frame(
                    "La asignación tiene incidentes activos. Primero deben quedar Resueltos "
                    "o Cerrados antes de registrar la entrega."
                ))
            else:
                r_box.addWidget(make_action_button("Registrar Entrega", "btn_success", self._entrega, ""))

            r_box.addStretch()
            r_box.addWidget(make_action_button("Reportar Incidente", "btn_warning", self._incidente, ""))
            layout.addLayout(r_box)

        elif transition_service.puede_transicionar(asig, "Cerrada"):
            acciones_mostradas = True
            layout.addWidget(make_info_frame("La entrega fue registrada correctamente."))
            layout.addSpacing(10)
            r_box = QHBoxLayout()
            r_box.addStretch()
            r_box.addWidget(make_action_button("Cerrar Asignación", "btn_primary", self._cerrar, ""))
            layout.addLayout(r_box)

        if not acciones_mostradas:
            lbl = QLabel("No hay acciones disponibles para esta asignación.")
            lbl.setObjectName("page_subtitle")
            layout.addWidget(lbl)
            r_box = QHBoxLayout()
            r_box.addStretch()
            r_box.addWidget(make_action_button("Cerrar", "btn_secondary", self.reject, ""))
            layout.addLayout(r_box)

    # ─── Acciones. ──────────────

    def _obtener_asignacion_actual(self):
        asig = asignaciones_queries.obtener_orm_por_id(
            self.db_session,
            self._asignacion_id,
        )
        if not asig:
            QMessageBox.warning(self, "Error", "No se encontró la asignación.")
            return None
        return asig

    def _ejecutar_transicion(self, accion, *args):
        asig = self._obtener_asignacion_actual()
        if not asig:
            return

        try:
            accion(self.db_session, asig, *args)
            self.accept()
        except transition_service.TransitionError as e:
            self.db_session.rollback()
            QMessageBox.critical(self, "Error", str(e))

    def _checkout(self):
        self._ejecutar_transicion(transition_service.iniciar_ruta)

    def _entrega(self):
        resp = QMessageBox.question(
            self, "Entrega", "¿La entrega fue conforme?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        conforme = (resp == QMessageBox.StandardButton.Yes)
        self._ejecutar_transicion(transition_service.registrar_entrega, conforme)

    def _cerrar(self):
        self._ejecutar_transicion(transition_service.cerrar_asignacion)

    def _cancelar(self):
        self._ejecutar_transicion(transition_service.cancelar_asignacion)

    def _incidente(self):
        QMessageBox.information(self, "Incidente", "Diríjase al módulo de Incidentes vinculando esta ID de asignación.")


class NuevaAsignacionDialog(QDialog):

    def __init__(self, db_session, parent, solicitudes, vehiculos, conductores):
        super().__init__(parent)
        self.db_session = db_session
        self.solicitudes = solicitudes
        self.vehiculos = vehiculos
        self.conductores = conductores

        self.setWindowTitle("Nueva Asignación")
        self.setMinimumWidth(460)

        self._solicitudes_map = {}
        self._vehiculos_map = {}
        self._conductores_map = {}

        self._build_ui()
        self._cargar_combos_desde_listas()
        if self._solicitud_cb.count() > 0:
            self._on_solicitud_cambiada()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Crear Asignación")
        title.setObjectName("dialog_title")
        layout.addWidget(title)
        layout.addWidget(make_info_frame("Selecciona los recursos para la orden de transporte."))

        def lbl(text):
            l = QLabel(text)
            l.setObjectName("form_label")
            return l

        form = QVBoxLayout()

        form.addWidget(lbl("Solicitud vinculada Aprobada:"))
        self._solicitud_cb = QComboBox()
        self._solicitud_cb.currentIndexChanged.connect(self._on_solicitud_cambiada)
        form.addWidget(self._solicitud_cb)

        info_ruta_frame = QFrame()
        info_ruta_frame.setStyleSheet("background-color: #1E1E2E; border-radius: 6px;")
        grid_info = QGridLayout(info_ruta_frame)

        grid_info.addWidget(lbl("Ruta Solicitada:"), 0, 0)
        self.lbl_ruta_dinamica = QLabel("—")
        self.lbl_ruta_dinamica.setStyleSheet("color: #E8F0FE; font-weight: bold;")
        grid_info.addWidget(self.lbl_ruta_dinamica, 0, 1)

        grid_info.addWidget(lbl("Prioridad:"), 1, 0)
        self.lbl_prioridad_dinamica = QLabel("—")
        self.lbl_prioridad_dinamica.setStyleSheet("color: #E8F0FE;")
        grid_info.addWidget(self.lbl_prioridad_dinamica, 1, 1)

        form.addWidget(info_ruta_frame)

        form.addWidget(lbl("Vehículo Disponible:"))
        self._vehiculo_cb = QComboBox()
        form.addWidget(self._vehiculo_cb)

        form.addWidget(lbl("Conductor Disponible:"))
        self._conductor_cb = QComboBox()
        form.addWidget(self._conductor_cb)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("Crear Asignación")
        btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self.accept)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _cargar_combos_desde_listas(self):
        for s in self.solicitudes:
            origen = s.sucursal_origen.nombre if s.sucursal_origen else "—"
            destino = s.sucursal_destino.nombre if s.sucursal_destino else "—"
            label = f"SOL-{s.id:03d} ({origen} → {destino})"

            self._solicitudes_map[label] = {
                "id": s.id, "origen": origen, "destino": destino, "prioridad": s.prioridad
            }
            self._solicitud_cb.addItem(label)

        for v in self.vehiculos:
            label = f"{v.patente} - {v.marca_modelo}"
            self._vehiculos_map[label] = v.id
            self._vehiculo_cb.addItem(label)

        for c in self.conductores:
            nombre = c.usuario.nombre if hasattr(c, 'usuario') and c.usuario else f"Conductor ID: {c.id}"
            label = f"{nombre} (Licencia: {c.tipo_licencia})"
            self._conductores_map[label] = c.id
            self._conductor_cb.addItem(label)

    def _on_solicitud_cambiada(self):
        texto = self._solicitud_cb.currentText()
        if texto in self._solicitudes_map:
            meta = self._solicitudes_map[texto]
            self.lbl_ruta_dinamica.setText(f"{meta['origen']} → {meta['destino']}")
            self.lbl_prioridad_dinamica.setText(meta["prioridad"])

    def get_data(self) -> dict:
        sol_text = self._solicitud_cb.currentText()
        veh_text = self._vehiculo_cb.currentText()
        cond_text = self._conductor_cb.currentText()

        return {
            "solicitud_id": self._solicitudes_map[sol_text]["id"],
            "vehiculo_id": self._vehiculos_map[veh_text],
            "conductor_id": self._conductores_map[cond_text],
        }