"""
Módulo Solicitudes 
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
    QDialog, QComboBox, QSpinBox,
    QMessageBox,
)

from app.ui.components.widgets import (
    TopBar, make_table, set_table_item,
    make_badge, make_action_button, make_info_frame,
)
from app.data.queries.solicitudes_queries import (
    filtrar_por_estado,
    contar_hoy,
    obtener_por_id,
    obtener_sucursales,
    obtener_encargados_sucursal,
)
from app.logic.solicitudes_service import (
    puede_modificar,
    validar_encargados_disponibles,
    registrar_solicitud,
    ejecutar_reprogramar,
    ejecutar_cancelar,
)


# ─────────────────────────────────────────────────────────────────
class SolicitudesView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("content_area")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._topbar = TopBar(
            "Solicitudes de Transporte",
            self._subtitulo(),
            "＋ Nueva Solicitud",
        )
        self._topbar.action_clicked.connect(self._nueva)
        layout.addWidget(self._topbar)

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
                "Prioridad", "Estado", "Creada", "Encargado", "Acciones"]
        self._table = make_table(cols)
        p_layout.addWidget(self._table)

        c_layout.addWidget(panel)
        layout.addWidget(content)

        self._recargar()

    # ── Helpers ──────────────────────────────────────────────────

    def _subtitulo(self) -> str:
        n = contar_hoy()
        return f"{n} solicitud{'es' if n != 1 else ''} registrada{'s' if n != 1 else ''} hoy"

    def _recargar(self):
        estado = self._filtro.currentText() if hasattr(self, "_filtro") else "Todos"
        self._fill_table(filtrar_por_estado(estado))

    def _fill_table(self, datos: list[dict]):
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

            id_num = s["id_numerico"]
            btn = QPushButton("Gestionar")
            btn.setObjectName("btn_table_action")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=id_num: self._ver_detalle(i))
            self._table.setCellWidget(r, 8, btn)

        self._table.resizeColumnsToContents()

    # ── Slots ─────────────────────────────────────────────────────

    def _filtrar(self, estado: str):
        self._fill_table(filtrar_por_estado(estado))

    def _ver_detalle(self, id_numerico: int):
        datos = obtener_por_id(id_numerico)
        if not datos:
            QMessageBox.warning(self, "Error", "No se encontró la solicitud.")
            return
        dlg = DetalleSolicitudDialog(datos, self)
        if dlg.exec():
            self._recargar()

    def _nueva(self):
        error = validar_encargados_disponibles()
        if error:
            QMessageBox.warning(self, "Sin encargados", error)
            return

        dlg = NuevaSolicitudDialog(obtener_encargados_sucursal(), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            form = dlg.get_data()
            resultado, error = registrar_solicitud(**form)
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                self._recargar()
                QMessageBox.information(
                    self, "Solicitud registrada",
                    f"Solicitud {resultado['id']} registrada correctamente."
                )


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
            ("Ruta",      f"{self._sol['origen']} → {self._sol['destino']}"),
            ("Carga",     f"{self._sol['carga_kg']} kg"),
            ("Prioridad", self._sol["prioridad"]),
            ("Encargado", self._sol["solicitante"]),
            ("Creada",    self._sol["creada"]),
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

        # Acciones — la condición viene del service, no hardcodeada aquí
        if puede_modificar(self._sol["estado"]):
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

        elif self._sol["estado"] == "Confirmada":
            layout.addWidget(make_info_frame(
                "Solicitud con asignación activa. Gestiona desde el módulo Asignaciones."
            ))
        else:
            msg = QLabel(f"Estado «{self._sol['estado']}» — sin acciones disponibles.")
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

    def _reprogramar(self):
        dlg = ReprogramarDialog(self._sol, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            error = ejecutar_reprogramar(self._sol["id_numerico"], dlg.get_prioridad())
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                QMessageBox.information(
                    self, "Reprogramada",
                    f"Solicitud {self._sol['id']} reprogramada correctamente."
                )
                self.accept()

    def _cancelar(self):
        r = QMessageBox.question(
            self, "Cancelar solicitud",
            f"¿Cancelar la solicitud {self._sol['id']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r == QMessageBox.StandardButton.Yes:
            error = ejecutar_cancelar(self._sol["id_numerico"])
            if error:
                QMessageBox.critical(self, "Error", error)
            else:
                QMessageBox.information(
                    self, "Cancelada",
                    f"Solicitud {self._sol['id']} cancelada correctamente."
                )
                self.accept()


# ─────────────────────────────────────────────────────────────────
class ReprogramarDialog(QDialog):

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

    def __init__(self, encargados: list[dict], parent=None):
        super().__init__(parent)
        self._encargados = encargados
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

        sucursales = obtener_sucursales()

        od = QHBoxLayout()
        col1, col2 = QVBoxLayout(), QVBoxLayout()
        col1.addWidget(lbl("Origen:"))
        self._origen = QComboBox()
        self._origen.addItems(sucursales)
        col1.addWidget(self._origen)
        col2.addWidget(lbl("Destino:"))
        self._destino = QComboBox()
        self._destino.addItems(sucursales)
        if len(sucursales) > 1:
            self._destino.setCurrentIndex(1)
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

        layout.addWidget(lbl("Encargado solicitante:"))
        self._encargado = QComboBox()
        for e in self._encargados:
            self._encargado.addItem(e["nombre"], userData=e["id"])
        layout.addWidget(self._encargado)

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
            "origen":        self._origen.currentText(),
            "destino":       self._destino.currentText(),
            "carga_kg":      self._carga.value(),
            "prioridad":     self._prioridad.currentText(),
            "creado_por_id": self._encargado.currentData(),
        }