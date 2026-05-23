"""
Módulo Solicitudes.

"""

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
    QDialog, QComboBox, QSpinBox,
    QLineEdit, QMessageBox
)

from app.ui.components.widgets import (
    TopBar, make_table, set_table_item,
    make_badge, make_action_button, make_info_frame,
)
from app.data.mock_data import SOLICITUDES


_ESTADOS_ACTIVOS = ("Creada", "En evaluación", "Pendiente", "Reprogramada")


# ─────────────────────────────────────────────────────────────────
class SolicitudesView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._solicitudes = list(SOLICITUDES)
        self.setObjectName("content_area")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = TopBar(
            "Solicitudes de Transporte",
            f"{len(self._solicitudes)} solicitudes registradas hoy",
            "＋ Nueva Solicitud",
        )
        topbar.action_clicked.connect(self._nueva)
        layout.addWidget(topbar)

        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        # Filtro rápido
        filtro_row = QHBoxLayout()
        lbl_f = QLabel("Filtrar por estado:")
        lbl_f.setObjectName("form_label")
        self._filtro = QComboBox()
        self._filtro.addItems([
            "Todos", "Creada", "En evaluación", "Confirmada",
            "Pendiente", "Reprogramada", "Completada", "Cancelada",
        ])
        self._filtro.setFixedWidth(200)
        self._filtro.currentTextChanged.connect(self._filtrar)
        filtro_row.addWidget(lbl_f)
        filtro_row.addWidget(self._filtro)
        filtro_row.addStretch()
        c_layout.addLayout(filtro_row)

        panel = QFrame()
        panel.setObjectName("panel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 12, 16, 16)

        hint = QLabel("Haz clic en «Gestionar» para ver detalle o ejecutar acciones.")
        hint.setObjectName("page_subtitle")
        p_layout.addWidget(hint)

        cols = ["ID", "Origen", "Destino", "Carga (kg)",
                "Prioridad", "Estado", "Creada", "Solicitante", "Acciones"]
        self._table = make_table(cols)
        self._fill_table(self._solicitudes)
        p_layout.addWidget(self._table)

        c_layout.addWidget(panel)
        layout.addWidget(content)

    def _fill_table(self, datos: list):
        self._table.setRowCount(len(datos))
        for r, s in enumerate(datos):
            set_table_item(self._table, r, 0, s["id"])
            set_table_item(self._table, r, 1, s["origen"])
            set_table_item(self._table, r, 2, s["destino"])
            set_table_item(self._table, r, 3, str(s["carga_kg"]))
            set_table_item(self._table, r, 4, s["prioridad"], badge=True)
            set_table_item(self._table, r, 5, s["estado"],    badge=True)
            set_table_item(self._table, r, 6, s["creada"])
            set_table_item(self._table, r, 7, s["solicitante"])

            idx_real = self._solicitudes.index(s)
            btn = QPushButton("Gestionar")
            btn.setObjectName("btn_table_action")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx_real: self._ver_detalle(i))
            self._table.setCellWidget(r, 8, btn)

        self._table.resizeColumnsToContents()

    def _filtrar(self, estado: str):
        datos = (self._solicitudes if estado == "Todos"
                 else [s for s in self._solicitudes if s["estado"] == estado])
        self._fill_table(datos)

    def _ver_detalle(self, idx: int):
        dlg = DetalleSolicitudDialog(self._solicitudes[idx], self)
        if dlg.exec():
            self._fill_table(self._solicitudes)

    def _nueva(self):
        dlg = NuevaSolicitudDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            data["id"]     = f"SOL-{len(self._solicitudes) + 1:03d}"
            data["estado"] = "Creada"
            data["creada"] = _now()
            self._solicitudes.append(data)
            self._fill_table(self._solicitudes)
            QMessageBox.information(self, "Solicitud registrada",
                                    f"Solicitud {data['id']} registrada.")


# ─────────────────────────────────────────────────────────────────
class DetalleSolicitudDialog(QDialog):

    def __init__(self, sol: dict, parent=None):
        super().__init__(parent)
        self._sol = sol
        self.setWindowTitle(f"Solicitud {sol['id']}")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(14)

        # Encabezado
        row = QHBoxLayout()
        title = QLabel(f"Solicitud  {self._sol['id']}")
        title.setObjectName("dialog_title")
        row.addWidget(title)
        row.addStretch()
        row.addWidget(make_badge(self._sol["estado"]))
        layout.addLayout(row)

        # Info
        frame = QFrame()
        frame.setObjectName("panel")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(6)
        for lbl_txt, val_txt in [
            ("Ruta",        f"{self._sol['origen']} → {self._sol['destino']}"),
            ("Carga",       f"{self._sol['carga_kg']} kg"),
            ("Prioridad",   self._sol["prioridad"]),
            ("Solicitante", self._sol["solicitante"]),
            ("Creada",      self._sol["creada"]),
        ]:
            r = QHBoxLayout()
            l = QLabel(lbl_txt + ":")
            l.setObjectName("form_label")
            l.setFixedWidth(90)
            v = QLabel(val_txt)
            v.setStyleSheet("color: #E8F0FE;")
            r.addWidget(l)
            r.addWidget(v)
            r.addStretch()
            fl.addLayout(r)
        layout.addWidget(frame)

        # Acciones contextuales
        estado = self._sol["estado"]
        if estado in _ESTADOS_ACTIVOS:
            layout.addWidget(QLabel("Acciones disponibles")).setObjectName if False else None
            sec = QLabel("Acciones disponibles")
            sec.setObjectName("section_header")
            layout.addWidget(sec)

            btn_row = QHBoxLayout()
            btn_row.addWidget(
                make_action_button("Reprogramar", "btn_warning", self._reprogramar, "✎")
            )
            btn_row.addStretch()
            btn_row.addWidget(
                make_action_button("Cancelar solicitud", "btn_danger", self._cancelar, "✕")
            )
            layout.addLayout(btn_row)

        elif estado == "Confirmada":
            layout.addWidget(make_info_frame(
                "Solicitud con asignación activa. Gestiona desde el módulo Asignaciones."
            ))
        else:
            msg = QLabel(f"Estado «{estado}» — sin acciones disponibles.")
            msg.setObjectName("page_subtitle")
            layout.addWidget(msg)

        # Cerrar
        close_row = QHBoxLayout()
        close_row.addStretch()
        btn_close = QPushButton("Cerrar")
        btn_close.setObjectName("btn_secondary")
        btn_close.clicked.connect(self.accept)
        close_row.addWidget(btn_close)
        layout.addLayout(close_row)

    # ── Acciones simuladas ────────────────────────────────────────

    def _reprogramar(self):
        dlg = ReprogramarDialog(self._sol, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._sol["prioridad"] = dlg.get_prioridad()
            self._sol["estado"]    = "Reprogramada"
            QMessageBox.information(self, "Reprogramada",
                                    f"Solicitud {self._sol['id']} reprogramada.")
            self.accept()

    def _cancelar(self):
        r = QMessageBox.question(self, "Cancelar solicitud",
                                 f"¿Cancelar la solicitud {self._sol['id']}?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            self._sol["estado"] = "Cancelada"
            QMessageBox.information(self, "Cancelada",
                                    f"Solicitud {self._sol['id']} cancelada.")
            self.accept()


# ─────────────────────────────────────────────────────────────────
class ReprogramarDialog(QDialog):
    """Solo cambia prioridad — simulado para PMN."""

    def __init__(self, sol: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reprogramar")
        self.setMinimumWidth(360)
        self.setModal(True)
        self._build_ui(sol)

    def _build_ui(self, sol: dict):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Reprogramar Solicitud")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        layout.addWidget(make_info_frame(
            f"Solicitud {sol['id']}  ·  {sol['origen']} → {sol['destino']}"
        ))

        lbl = QLabel("Nueva prioridad:")
        lbl.setObjectName("form_label")
        layout.addWidget(lbl)

        self._prioridad = QComboBox()
        self._prioridad.addItems(["Alta", "Media", "Baja"])
        idx = self._prioridad.findText(sol.get("prioridad", "Media"))
        self._prioridad.setCurrentIndex(idx if idx >= 0 else 0)
        layout.addWidget(self._prioridad)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Confirmar")
        btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_prioridad(self) -> str:
        return self._prioridad.currentText()


# ─────────────────────────────────────────────────────────────────
class NuevaSolicitudDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Solicitud")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Registrar Solicitud")
        title.setObjectName("dialog_title")
        layout.addWidget(title)

        def lbl(t):
            l = QLabel(t)
            l.setObjectName("form_label")
            return l

        # Origen / Destino
        od = QHBoxLayout()
        col1, col2 = QVBoxLayout(), QVBoxLayout()
        col1.addWidget(lbl("Origen:"))
        self._origen = QComboBox()
        self._origen.addItems(["Temuco", "Santiago", "Concepción", "Los Ángeles", "Valparaíso"])
        col1.addWidget(self._origen)
        col2.addWidget(lbl("Destino:"))
        self._destino = QComboBox()
        self._destino.addItems(["Concepción", "Santiago", "Temuco", "Valparaíso", "Los Ángeles"])
        col2.addWidget(self._destino)
        od.addLayout(col1)
        od.addLayout(col2)
        layout.addLayout(od)

        layout.addWidget(lbl("Carga (kg):"))
        self._carga = QSpinBox()
        self._carga.setRange(1, 5000)
        self._carga.setSuffix(" kg")
        self._carga.setValue(500)
        layout.addWidget(self._carga)

        layout.addWidget(lbl("Prioridad:"))
        self._prioridad = QComboBox()
        self._prioridad.addItems(["Alta", "Media", "Baja"])
        layout.addWidget(self._prioridad)

        layout.addWidget(lbl("Solicitante:"))
        self._solicitante = QLineEdit()
        self._solicitante.setPlaceholderText("Nombre del encargado")
        layout.addWidget(self._solicitante)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject)
        btn_ok = QPushButton("Registrar")
        btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_c)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {
            "origen":      self._origen.currentText(),
            "destino":     self._destino.currentText(),
            "carga_kg":    self._carga.value(),
            "prioridad":   self._prioridad.currentText(),
            "solicitante": self._solicitante.text() or "Sin especificar",
        }


# ─────────────────────────────────────────────────────────────────
def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")