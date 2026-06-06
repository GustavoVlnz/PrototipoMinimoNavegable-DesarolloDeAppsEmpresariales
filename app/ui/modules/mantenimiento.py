"""
Módulo Mantenimiento — LoncoExpress.
app/ui/modules/mantenimiento.py
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QDialog,
    QComboBox, QTextEdit, QLineEdit,
)

from app.logic import mantenimiento_logic
from app.ui.components.widgets import TopBar, make_table, set_table_item
from app.data.queries import mantenimiento_queries
from app.logic import mantenimiento_logic


class MantenimientoView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ordenes = []
        self._selected_row = -1
        self._cargar_ordenes()
        self._build_ui()

    # ── Carga de datos ────────────────────────────────────────────

    def _cargar_ordenes(self):
        """Carga órdenes de mantenimiento desde la base de datos."""
        self._ordenes = mantenimiento_queries.obtener_todos_mantenimientos()

    # ── Construcción UI ───────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = TopBar(
            "Mantenimiento",
            "Órdenes de mantención y habilitación de vehículos",
            "＋ Nueva Orden",
        )
        topbar.action_clicked.connect(self._nueva_ot)
        layout.addWidget(topbar)

        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        # Info
        info = QFrame()
        info.setObjectName("alert_info")
        il = QHBoxLayout(info)
        il.setContentsMargins(12, 10, 12, 10)
        il.addWidget(QLabel(
            "Un vehículo solo recupera el estado 'Disponible' "
            "tras la aprobación del Técnico de Mantención."
        ))
        c_layout.addWidget(info)

        # Tabla
        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)

        cols = ["ID", "Vehículo", "Tipo", "Descripción",
                "Prioridad", "Estado", "Generado", "Técnico"]
        self._table = make_table(cols)
        self._table.cellClicked.connect(self._on_row_clicked)
        self._fill_table()
        p_layout.addWidget(self._table)

        # Fila de acciones
        action_row = QHBoxLayout()
        action_row.addStretch()

        self._btn_avanzar = QPushButton("Marcar En revisión")
        self._btn_avanzar.setObjectName("btn_primary")
        self._btn_avanzar.setVisible(False)
        self._btn_avanzar.clicked.connect(self._avanzar_estado)
        action_row.addWidget(self._btn_avanzar)

        self._btn_habilitar = QPushButton("Habilitar Vehículo")
        self._btn_habilitar.setObjectName("btn_success")
        self._btn_habilitar.setVisible(False)
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

    # ── Interacción con tabla ─────────────────────────────────────

    def _on_row_clicked(self, row, _col):
        self._selected_row = row
        self._update_action_buttons()

    def _update_action_buttons(self):
        if self._selected_row < 0:
            self._btn_avanzar.setVisible(False)
            self._btn_habilitar.setVisible(False)
            return

        orden = self._ordenes[self._selected_row]
        acciones = mantenimiento_logic.acciones_disponibles(orden)

        # Botón avanzar: visible si hay acción de avance, con label dinámico
        puede_avanzar = "avanzar" in acciones
        self._btn_avanzar.setVisible(puede_avanzar)
        if puede_avanzar:
            self._btn_avanzar.setText(mantenimiento_logic.label_boton_avanzar(orden))

        # Botón habilitar: visible solo desde 'En Revision'
        self._btn_habilitar.setVisible("habilitar" in acciones)

    # ── Acciones ──────────────────────────────────────────────────

    def _avanzar_estado(self):
        if self._selected_row < 0:
            return
        orden = self._ordenes[self._selected_row]

        resultado = mantenimiento_logic.avanzar_estado(orden)
        if not resultado:
            QMessageBox.warning(self, "Acción no permitida", resultado.mensaje)
            return

        nuevo_estado = resultado.mensaje  # avanzar_estado retorna el nuevo estado en .mensaje
        ok = mantenimiento_queries.actualizar_estado_mantenimiento(
            orden["mantenimiento_id"], nuevo_estado
        )
        if ok:
            self._cargar_ordenes()
            self._fill_table()
            self._selected_row = -1
            self._update_action_buttons()
            QMessageBox.information(
                self, "Estado actualizado",
                f"Orden {orden['id']} pasó a '{nuevo_estado}'."
            )
        else:
            QMessageBox.critical(self, "Error", "No se pudo actualizar el estado.")

    def _habilitar_vehiculo(self):
        if self._selected_row < 0:
            return
        orden = self._ordenes[self._selected_row]

        if not mantenimiento_logic.puede_habilitar_vehiculo(orden):
            QMessageBox.warning(
                self, "Acción no permitida",
                "Solo se puede habilitar desde estado 'En Revisión'."
            )
            return

        reply = QMessageBox.question(
            self, "Validación técnica",
            f"¿Confirmar habilitación del vehículo {orden['vehiculo_patente']}?\n\n"
            f"Esto cambiará su estado a 'Disponible' y cerrará la OT {orden['id']}.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok = mantenimiento_queries.habilitar_vehiculo(orden["mantenimiento_id"])
            if ok:
                self._cargar_ordenes()
                self._fill_table()
                self._selected_row = -1
                self._update_action_buttons()
                QMessageBox.information(
                    self, "Vehículo habilitado",
                    f"Vehículo {orden['vehiculo_patente']} habilitado.\n"
                    f"OT {orden['id']} cerrada."
                )
            else:
                QMessageBox.critical(self, "Error", "No se pudo habilitar el vehículo.")

    def _nueva_ot(self):
        patentes = mantenimiento_queries.obtener_patentes_vehiculos()
        dlg = NuevaOTDialog(self, patentes=patentes)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()

            # Validar con lógica de negocio
            resultado = mantenimiento_logic.validar_nueva_ot(
                vehiculo_id=data["vehiculo_id"],
                tipo_mantencion=data["tipo"],
                descripcion=data["descripcion"],
                prioridad=data["prioridad"],
            )
            if not resultado:
                QMessageBox.warning(self, "Datos inválidos", resultado.mensaje)
                return

            ok = mantenimiento_queries.crear_orden_mantenimiento(
                vehiculo_id=data["vehiculo_id"],
                tipo_mantencion=data["tipo"].replace(" ", "_"),
                descripcion=data["descripcion"],
                prioridad=data["prioridad"],
            )
            if ok:
                self._cargar_ordenes()
                self._fill_table()
                QMessageBox.information(
                    self, "OT generada",
                    f"Orden de mantención creada. "
                    f"El vehículo fue marcado como 'En Mantención'."
                )
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar la orden.")


# ─────────────────────────────────────────────────────────────────
class NuevaOTDialog(QDialog):
    """Formulario para generar una nueva Orden de Trabajo de mantención."""

    def __init__(self, parent=None, patentes: list[dict] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Orden de Mantención")
        self.setMinimumWidth(440)
        self.setModal(True)
        self._patentes = patentes or []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Generar Orden de Mantención")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        def lbl(t):
            l = QLabel(t)
            l.setObjectName("form_label")
            return l

        layout.addWidget(lbl("Vehículo:"))
        self._vehiculo = QComboBox()
        for p in self._patentes:
            self._vehiculo.addItem(p["patente"], userData=p["id"])
        layout.addWidget(self._vehiculo)

        layout.addWidget(lbl("Tipo de mantención:"))
        self._tipo = QComboBox()
        self._tipo.addItems(mantenimiento_logic.TIPOS_MANTENCION)
        layout.addWidget(self._tipo)

        layout.addWidget(lbl("Prioridad:"))
        self._prioridad = QComboBox()
        self._prioridad.addItems(mantenimiento_logic.PRIORIDADES)
        self._prioridad.setCurrentText("Media")
        layout.addWidget(self._prioridad)

        layout.addWidget(lbl("Descripción del trabajo:"))
        self._descripcion = QTextEdit()
        self._descripcion.setPlaceholderText("Describe el trabajo a realizar...")
        self._descripcion.setFixedHeight(80)
        layout.addWidget(self._descripcion)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("Generar OT")
        btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_c)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {
            "vehiculo_id":  self._vehiculo.currentData(),
            "tipo":         self._tipo.currentText(),
            "prioridad":    self._prioridad.currentText(),
            "descripcion":  self._descripcion.toPlainText().strip(),
        }