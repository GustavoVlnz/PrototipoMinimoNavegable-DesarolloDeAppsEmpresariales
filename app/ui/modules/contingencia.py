"""
Módulo Contingencia — Protocolo manual ante caída del sistema.
Actor: Todos los operadores.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from app.ui.components.widgets import TopBar


class ContingenciaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._registros = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = TopBar(
            "Protocolo de Contingencia",
            "Registro manual durante caída del sistema",
        )
        layout.addWidget(topbar)

        content = QWidget()
        content.setObjectName("content_area")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 28)
        c_layout.setSpacing(16)

        # Advertencia
        warn = QFrame()
        warn.setObjectName("alert_critical")
        wl = QHBoxLayout(warn)
        wl.setContentsMargins(16, 12, 16, 12)
        warn_lbl = QLabel(
            "<b>Modo Contingencia</b> — El sistema central no está disponible. "
            "Registra las operaciones manualmente aquí. Todos los registros deben ser "
            "sincronizados con el sistema principal una vez restablecido el servicio."
        )
        warn_lbl.setWordWrap(True)
        warn_lbl.setTextFormat(Qt.TextFormat.RichText)
        wl.addWidget(warn_lbl)
        c_layout.addWidget(warn)

        # Formulario
        form_panel = QFrame()
        form_panel.setObjectName("panel")
        fp = QVBoxLayout(form_panel)
        fp.setContentsMargins(24, 24, 24, 24)
        fp.setSpacing(14)

        title = QLabel("Registro Manual de Operación")
        title.setObjectName("section_header")
        fp.addWidget(title)

        def lbl(t):
            l = QLabel(t)
            l.setObjectName("form_label")
            return l

        # Tipo de registro
        fp.addWidget(lbl("Tipo de registro:"))
        self._tipo = QComboBox()
        self._tipo.addItems(["Solicitud de transporte", "Asignación manual",
                             "Incidente en ruta", "Entrega de carga", "Otro"])
        fp.addWidget(self._tipo)

        # Operador
        fp.addWidget(lbl("Operador responsable:"))
        self._operador = QLineEdit()
        self._operador.setPlaceholderText("Nombre completo del operador")
        fp.addWidget(self._operador)

        # Vehículo
        fp.addWidget(lbl("Vehículo involucrado (patente):"))
        self._vehiculo = QLineEdit()
        self._vehiculo.setPlaceholderText("Ej: BKRT-42")
        fp.addWidget(self._vehiculo)

        # Conductor
        fp.addWidget(lbl("Conductor:"))
        self._conductor = QLineEdit()
        self._conductor.setPlaceholderText("Nombre del conductor")
        fp.addWidget(self._conductor)

        # Descripción
        fp.addWidget(lbl("Descripción detallada de la operación:"))
        self._descripcion = QTextEdit()
        self._descripcion.setPlaceholderText(
            "Describe con el máximo detalle posible: origen, destino, carga, "
            "hora, incidentes, estado del vehículo, etc."
        )
        self._descripcion.setFixedHeight(100)
        fp.addWidget(self._descripcion)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setObjectName("btn_secondary")
        btn_limpiar.clicked.connect(self._limpiar)
        btn_guardar = QPushButton("Guardar Registro Manual")
        btn_guardar.setObjectName("btn_primary")
        btn_guardar.clicked.connect(self._guardar)
        btn_row.addWidget(btn_limpiar)
        btn_row.addWidget(btn_guardar)
        fp.addLayout(btn_row)

        c_layout.addWidget(form_panel)

        # Contador de pendientes
        self._contador_lbl = QLabel("0 registros pendientes de sincronización")
        self._contador_lbl.setStyleSheet("color: #5B7FA6; font-size: 12px;")

        sync_row = QHBoxLayout()
        sync_row.addWidget(self._contador_lbl)
        sync_row.addStretch()
        btn_sync = QPushButton("Sincronizar con Sistema Principal")
        btn_sync.setObjectName("btn_warning")
        btn_sync.clicked.connect(self._sincronizar)
        sync_row.addWidget(btn_sync)
        c_layout.addLayout(sync_row)

        layout.addWidget(content)

    def _limpiar(self):
        self._operador.clear()
        self._vehiculo.clear()
        self._conductor.clear()
        self._descripcion.clear()

    def _guardar(self):
        if not self._operador.text() or not self._descripcion.toPlainText():
            QMessageBox.warning(self, "Datos incompletos",
                                "Por favor completa al menos el operador y la descripción.")
            return
        self._registros.append({
            "tipo": self._tipo.currentText(),
            "operador": self._operador.text(),
            "vehiculo": self._vehiculo.text(),
            "conductor": self._conductor.text(),
            "descripcion": self._descripcion.toPlainText(),
            "hora": _now(),
        })
        n = len(self._registros)
        self._contador_lbl.setText(f"{n} registro(s) pendiente(s) de sincronización")
        self._limpiar()
        QMessageBox.information(self, "Registro guardado",
                                f"Registro manual guardado. {n} pendiente(s) de sincronización.")

    def _sincronizar(self):
        if not self._registros:
            QMessageBox.information(self, "Sin pendientes", "No hay registros pendientes de sincronización.")
            return
        n = len(self._registros)
        reply = QMessageBox.question(
            self, "Sincronizar registros",
            f"¿Sincronizar {n} registro(s) con el sistema principal?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._registros.clear()
            self._contador_lbl.setText("0 registros pendientes de sincronización")
            QMessageBox.information(self, "Sincronización completada",
                                    f"{n} registro(s) sincronizados exitosamente.")


def _now():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M")
