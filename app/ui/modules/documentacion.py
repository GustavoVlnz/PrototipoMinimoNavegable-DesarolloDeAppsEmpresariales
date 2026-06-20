from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QDialog, QComboBox, QDateEdit, QMessageBox
)
from PyQt6.QtCore import QDate

from app.ui.components.widgets import TopBar, make_table, set_table_item, make_alert_item
from app.data.queries import documentacion_queries
from app.logic import documentacion_logic


class DocumentacionView(QWidget):
    def __init__(self, db_session, parent=None):
        super().__init__(parent)
        self.db_session = db_session
        self._documentos = []
        self._table = None  # Referencia a la tabla para actualizaciones
        self._cargar_documentos()
        self._build_ui()

    def _cargar_documentos(self):
        """Carga documentos desde la base de datos y calcula vigencia."""
        documentos_bd = documentacion_queries.obtener_todos_documentos(self.db_session)
        for d in documentos_bd:
            dias = documentacion_logic.calcular_dias_restantes(d["vencimiento"])
            d["dias_restantes"] = dias if dias is not None else 0
            d["estado"] = documentacion_logic.calcular_estado_vigencia(dias)
        self._documentos = documentos_bd

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        resumen = documentacion_logic.resumen_documentacion(self._documentos)
        vencidos = resumen["vencidos"]
        por_vencer = resumen["por_vencer"]

        topbar = TopBar(
            "Documentación Legal",
            f"{vencidos} documentos vencidos · {por_vencer} por vencer",
        )
        layout.addWidget(topbar)

        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        action_row = QHBoxLayout()
        action_row.addStretch()
        self._btn_renovar = QPushButton("Registrar renovación")
        self._btn_renovar.setObjectName("btn_primary")
        self._btn_renovar.clicked.connect(self._registrar_renovacion)
        action_row.addWidget(self._btn_renovar)
        c_layout.addLayout(action_row)

        # Alertas críticas
        if vencidos > 0 or por_vencer > 0:
            alert_panel = QFrame()
            alert_panel.setObjectName("panel")
            ap_layout = QVBoxLayout(alert_panel)
            ap_layout.setContentsMargins(16, 16, 16, 16)
            ap_layout.setSpacing(6)
            ap_layout.addWidget(_header("Alertas Prioritarias"))

            documentos_criticos = documentacion_logic.documentos_criticos(self._documentos)
            for d in documentos_criticos:
                tipo = documentacion_logic.tipo_alerta(d)
                msg = documentacion_logic.mensaje_alerta(d)
                ap_layout.addWidget(make_alert_item(tipo, msg))

            c_layout.addWidget(alert_panel)

        # Tabla completa
        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)
        p_layout.addWidget(_header("Registro Documental Completo"))

        cols = ["Entidad", "Documento", "Vencimiento", "Días Restantes", "Estado"]
        self._table = make_table(cols)
        self._table.setRowCount(len(self._documentos))

        for r, d in enumerate(self._documentos):
            dias = d["dias_restantes"]
            dias_str = f"+{dias} días" if dias >= 0 else f"{dias} días"
            set_table_item(self._table, r, 0, d["vehiculo"])
            set_table_item(self._table, r, 1, d["doc_tipo"])
            set_table_item(self._table, r, 2, d["vencimiento"])
            set_table_item(self._table, r, 3, dias_str)
            set_table_item(self._table, r, 4, d["estado"], badge=True)

        for col in range(len(cols) - 1):
            self._table.resizeColumnToContents(col)

        p_layout.addWidget(self._table)
        c_layout.addWidget(panel)
        layout.addWidget(content)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _actualizar_tabla(self):
        """Actualiza solo el contenido de la tabla sin reconstruir la UI."""
        if self._table is None:
            return

        self._table.setRowCount(len(self._documentos))
        for r, d in enumerate(self._documentos):
            dias = d["dias_restantes"]
            dias_str = f"+{dias} días" if dias >= 0 else f"{dias} días"
            set_table_item(self._table, r, 0, d["vehiculo"])
            set_table_item(self._table, r, 1, d["doc_tipo"])
            set_table_item(self._table, r, 2, d["vencimiento"])
            set_table_item(self._table, r, 3, dias_str)
            set_table_item(self._table, r, 4, d["estado"], badge=True)

    def _refresh_ui(self):
        old_layout = self.layout()
        if old_layout:
            self._clear_layout(old_layout)
            old_layout.deleteLater()
        self._cargar_documentos()
        self._build_ui()

    def _registrar_renovacion(self):
        dlg = RegistrarRenovacionDialog(self._documentos, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            doc, fecha = dlg.get_data()
            nueva_fecha_str = fecha.toString("yyyy-MM-dd")

            documento_id = doc.get("documento_id")
            ok, error = documentacion_queries.renovar(
                self.db_session, documento_id, nueva_fecha_str
            )

            if ok:
                self._cargar_documentos()
                self._actualizar_tabla()
                QMessageBox.information(
                    self, "Renovación registrada",
                    f"Documento {doc['doc_tipo']} de {doc['vehiculo']} actualizado al "
                    f"{nueva_fecha_str}. Si el vehículo no tiene otros impedimentos, "
                    f"su disponibilidad fue re-evaluada automáticamente."
                )
            else:
                QMessageBox.warning(
                    self, "Error",
                    error or "No se pudo registrar la renovación. Intente nuevamente."
                )


class RegistrarRenovacionDialog(QDialog):
    def __init__(self, documentos, parent=None):
        super().__init__(parent)
        self._documentos = documentos
        self.setWindowTitle("Registrar renovación de documento")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Registrar renovación")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        layout.addWidget(QLabel("Documento a renovar:"))
        self._documento = QComboBox()
        for doc in self._documentos:
            self._documento.addItem(f"{doc['vehiculo']} — {doc['doc_tipo']} ({doc['vencimiento']})", doc)
        layout.addWidget(self._documento)

        layout.addWidget(QLabel("Nueva fecha de vencimiento:"))
        self._fecha = QDateEdit()
        self._fecha.setCalendarPopup(True)
        self._fecha.setDate(QDate.currentDate())
        layout.addWidget(self._fecha)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Registrar")
        btn_ok.setObjectName("btn_success")
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_data(self):
        return self._documento.currentData(), self._fecha.date()


def _header(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("section_header")
    return lbl