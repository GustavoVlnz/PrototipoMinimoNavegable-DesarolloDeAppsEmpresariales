"""
Módulo Documentación — Control de vigencia documental de vehículos y conductores.
Actor principal: Personal Administrativo.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QDialog, QComboBox, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from app.ui.components.widgets import TopBar, make_table, set_table_item, make_alert_item
from app.data.mock_data import DOCUMENTACION


class DocumentacionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._documentos = list(DOCUMENTACION)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        vencidos = sum(1 for d in self._documentos if d["estado"] == "Vencida")
        por_vencer = sum(1 for d in self._documentos if d["estado"] == "Por vencer")

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

            for d in self._documentos:
                if d["estado"] in ("Vencida", "Por vencer"):
                    tipo = "critica" if d["estado"] == "Vencida" else "advertencia"
                    dias = d["dias_restantes"]
                    if dias < 0:
                        msg = f"{d['vehiculo']} — {d['doc_tipo']}: VENCIDO hace {abs(dias)} días"
                    else:
                        msg = f"{d['vehiculo']} — {d['doc_tipo']}: vence en {dias} días ({d['vencimiento']})"
                    ap_layout.addWidget(make_alert_item(tipo, msg))

            c_layout.addWidget(alert_panel)

        # Tabla completa
        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)
        p_layout.addWidget(_header("Registro Documental Completo"))

        cols = ["Entidad", "Documento", "Vencimiento", "Días Restantes", "Estado"]
        table = make_table(cols)
        table.setRowCount(len(self._documentos))

        for r, d in enumerate(self._documentos):
            dias = d["dias_restantes"]
            dias_str = f"+{dias} días" if dias >= 0 else f"{dias} días"
            set_table_item(table, r, 0, d["vehiculo"])
            set_table_item(table, r, 1, d["doc_tipo"])
            set_table_item(table, r, 2, d["vencimiento"])
            set_table_item(table, r, 3, dias_str)
            set_table_item(table, r, 4, d["estado"], badge=True)

        # Ajustar columnas de texto; la de badge ya fue ajustada por set_table_item
        for col in range(len(cols) - 1):
            table.resizeColumnToContents(col)

        p_layout.addWidget(table)
        c_layout.addWidget(panel)
        layout.addWidget(content)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _refresh_ui(self):
        old_layout = self.layout()
        if old_layout:
            self._clear_layout(old_layout)
            old_layout.deleteLater()
        self._build_ui()

    def _registrar_renovacion(self):
        dlg = RegistrarRenovacionDialog(self._documentos, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            doc, fecha = dlg.get_data()
            doc["vencimiento"] = fecha.toString("yyyy-MM-dd")
            from datetime import date
            dias = (date.fromisoformat(doc["vencimiento"]) - date.today()).days
            doc["dias_restantes"] = dias
            doc["estado"] = "Vigente" if dias >= 0 else "Por vencer"
            self._refresh_ui()
            QMessageBox.information(self, "Renovación registrada",
                                    f"Documento {doc['doc_tipo']} de {doc['vehiculo']} actualizado al {doc['vencimiento']}.")


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