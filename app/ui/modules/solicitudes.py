"""
Módulo Solicitudes — Listado y creación de solicitudes logísticas.
Actor principal: Encargado de Sucursal.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QDialogButtonBox,
    QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt

from app.ui.components.widgets import TopBar, make_table, set_table_item
from app.data.mock_data import SOLICITUDES


class SolicitudesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._solicitudes = list(SOLICITUDES)
        self._build_ui()
        self.setObjectName("content_area")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = TopBar(
            "Solicitudes de Transporte",
            f"{len(self._solicitudes)} solicitudes registradas hoy",
            "＋ Nueva Solicitud",
        )
        topbar.action_clicked.connect(self._abrir_nueva_solicitud)
        layout.addWidget(topbar)

        # Contenido
        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        # Filtros rápidos
        c_layout.addWidget(self._make_filtros())

        # Tabla
        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 16, 16, 16)

        cols = ["ID", "Origen", "Destino", "Carga (kg)", "Prioridad", "Estado", "Creada", "Solicitante"]
        self._table = make_table(cols)
        self._fill_table(self._solicitudes)
        p_layout.addWidget(self._table)

        c_layout.addWidget(panel)
        layout.addWidget(content)

    def _make_filtros(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        estados = ["Todos", "Creada", "En evaluación", "Confirmada", "Pendiente", "Completada", "Cancelada", "Reprogramada"]
        combo = QComboBox()
        combo.addItems(estados)
        combo.setFixedWidth(200)
        combo.currentTextChanged.connect(self._filtrar_por_estado)

        layout.addWidget(QLabel("Filtrar por estado:"))
        layout.addWidget(combo)
        layout.addStretch()
        return row

    def _fill_table(self, datos: list):
        self._table.setRowCount(len(datos))
        for r, s in enumerate(datos):
            set_table_item(self._table, r, 0, s["id"])
            set_table_item(self._table, r, 1, s["origen"])
            set_table_item(self._table, r, 2, s["destino"])
            set_table_item(self._table, r, 3, str(s["carga_kg"]))
            set_table_item(self._table, r, 4, s["prioridad"], badge=True)
            set_table_item(self._table, r, 5, s["estado"], badge=True)
            set_table_item(self._table, r, 6, s["creada"])
            set_table_item(self._table, r, 7, s["solicitante"])
        self._table.resizeColumnsToContents()

    def _filtrar_por_estado(self, estado: str):
        if estado == "Todos":
            self._fill_table(self._solicitudes)
        else:
            filtrados = [s for s in self._solicitudes if s["estado"] == estado]
            self._fill_table(filtrados)

    def _abrir_nueva_solicitud(self):
        dlg = NuevaSolicitudDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            nueva = dlg.get_data()
            nueva["id"] = f"SOL-{len(self._solicitudes) + 1:03d}"
            nueva["estado"] = "Creada"
            nueva["creada"] = _now()
            self._solicitudes.append(nueva)
            self._fill_table(self._solicitudes)
            QMessageBox.information(self, "Solicitud registrada",
                                    f"Solicitud {nueva['id']} registrada exitosamente.")


# ─────────────────────────────────────────────
class NuevaSolicitudDialog(QDialog):
    """Formulario para registrar una nueva solicitud logística."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Solicitud de Transporte")
        self.setMinimumWidth(440)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Registrar Solicitud Logística")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._origen = QComboBox()
        self._origen.addItems(["Temuco", "Santiago", "Concepción", "Los Ángeles", "Valparaíso", "Osorno"])

        self._destino = QComboBox()
        self._destino.addItems(["Concepción", "Santiago", "Temuco", "Valparaíso", "Los Ángeles", "Chillán"])

        self._carga = QSpinBox()
        self._carga.setRange(1, 5000)
        self._carga.setSuffix(" kg")
        self._carga.setValue(500)

        self._prioridad = QComboBox()
        self._prioridad.addItems(["Alta", "Media", "Baja"])

        self._solicitante = QLineEdit()
        self._solicitante.setPlaceholderText("Nombre del encargado de sucursal")

        def make_label(text):
            lbl = QLabel(text)
            lbl.setObjectName("form_label")
            return lbl

        form.addRow(make_label("Origen:"), self._origen)
        form.addRow(make_label("Destino:"), self._destino)
        form.addRow(make_label("Carga (kg):"), self._carga)
        form.addRow(make_label("Prioridad:"), self._prioridad)
        form.addRow(make_label("Solicitante:"), self._solicitante)

        layout.addLayout(form)

        # Botones
        buttons = QDialogButtonBox()
        btn_ok = QPushButton("Registrar Solicitud")
        btn_ok.setObjectName("btn_primary")
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {
            "origen": self._origen.currentText(),
            "destino": self._destino.currentText(),
            "carga_kg": self._carga.value(),
            "prioridad": self._prioridad.currentText(),
            "solicitante": self._solicitante.text() or "Sin especificar",
            "sucursal_origen": self._origen.currentText(),
        }


def _now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")
