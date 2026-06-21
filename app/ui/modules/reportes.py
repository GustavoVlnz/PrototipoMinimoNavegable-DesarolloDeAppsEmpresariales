"""
Módulo Reportes — Trazabilidad, historial e indicadores operativos.
Actor: Administrador General / Supervisor.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt

from app.ui.components.widgets import TopBar, make_table, set_table_item, KpiCard
from app.data.queries import reportes_queries
from app.logic import documentacion_logic
from app.core.events import event_bus


class ReportesView(QWidget):

    def __init__(self, db_session, parent=None):
        super().__init__(parent)

        self.db_session = db_session

        self._resumen = {}
        self._asignaciones = []
        self._incidentes = []
        self._documentacion = []
        self._mantenimientos = []

        self._build_ui()
        self._conectar_eventos()
        self._recargar()

    # ── Eventos / carga ───────────────────────────────────────────────────────

    def _conectar_eventos(self):
        event_bus.asignacion_actualizada.connect(self._recargar)
        event_bus.incidente_actualizado.connect(self._recargar)
        event_bus.documento_actualizado.connect(self._recargar)
        event_bus.vehiculo_actualizado.connect(self._recargar)
        event_bus.mantenimiento_actualizado.connect(self._recargar)

    def _cargar_datos(self):
        """
        Carga reportes desde BD.
        También sincroniza documentación para que los reportes reflejen
        estados reales de vencimiento.
        """
        self.db_session.expire_all()

        documentacion_logic.sincronizar_vencimientos(
            self.db_session,
            emitir_eventos=False,
        )

        self._resumen = reportes_queries.obtener_resumen_reportes(self.db_session)
        self._asignaciones = reportes_queries.obtener_historial_asignaciones(self.db_session)
        self._incidentes = reportes_queries.obtener_incidentes_reporte(self.db_session)
        self._documentacion = reportes_queries.obtener_documentacion_reporte(self.db_session)
        self._mantenimientos = reportes_queries.obtener_mantenimiento_reporte(self.db_session)

    def _recargar(self):
        self._cargar_datos()
        self._reconstruir_contenido()

    # ── UI base ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._topbar = TopBar(
            "Reportes y Trazabilidad",
            "Resumen operacional conectado a la base de datos",
        )
        root.addWidget(self._topbar)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(self._scroll)

    def _reconstruir_contenido(self):
        content = QWidget()
        content.setObjectName("content_area")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(16)

        layout.addWidget(self._make_resumen())
        layout.addWidget(self._make_historial_asignaciones())
        layout.addWidget(self._make_incidentes())
        layout.addWidget(self._make_documentacion())
        layout.addWidget(self._make_mantenimiento())

        layout.addStretch()

        self._scroll.setWidget(content)

    # ── Paneles ───────────────────────────────────────────────────────────────

    def _make_resumen(self) -> QWidget:
        row = QWidget()

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        cards = [
            KpiCard(
                "Asignaciones Completadas",
                self._resumen.get("asignaciones_completadas", 0),
                color="#16A34A",
            ),
            KpiCard(
                "Con Incidencia",
                self._resumen.get("asignaciones_con_incidencia", 0),
                color="#D97706",
            ),
            KpiCard(
                "Incidentes Activos",
                self._resumen.get("incidentes_activos", 0),
                color="#DC2626",
            ),
            KpiCard(
                "Documentos Críticos",
                self._resumen.get("documentos_criticos", 0),
                color="#D97706",
            ),
            KpiCard(
                "Vehículos Bloqueados",
                self._resumen.get("vehiculos_bloqueados", 0),
                color="#7F1D1D",
            ),
            KpiCard(
                "Mantenciones Abiertas",
                self._resumen.get("mantenciones_abiertas", 0),
                color="#1E5FC3",
            ),
        ]

        for card in cards:
            layout.addWidget(card)

        layout.addStretch()
        return row

    def _make_historial_asignaciones(self) -> QFrame:
        panel = _panel("Historial de Asignaciones")

        cols = [
            "ID", "Solicitud", "Vehículo", "Conductor",
            "Ruta", "Prioridad", "Estado", "Inicio", "Fin",
        ]

        table = make_table(cols)
        table.setRowCount(len(self._asignaciones))

        for r, a in enumerate(self._asignaciones):
            ruta = f"{a.get('origen', '—')} → {a.get('destino', '—')}"

            set_table_item(table, r, 0, a.get("id", "—"))
            set_table_item(table, r, 1, a.get("solicitud_id", "—"))
            set_table_item(table, r, 2, a.get("vehiculo_patente", "—"))
            set_table_item(table, r, 3, a.get("conductor", "—"))
            set_table_item(table, r, 4, ruta)
            set_table_item(table, r, 5, a.get("prioridad", "—"), badge=True)
            set_table_item(table, r, 6, a.get("estado", "—"), badge=True)
            set_table_item(table, r, 7, a.get("inicio") or "—")
            set_table_item(table, r, 8, a.get("fin") or "—")

        table.resizeColumnsToContents()
        _ajustar_altura_tabla(table, len(self._asignaciones), minimo=220, maximo=500)
        panel.layout().addWidget(table)
        return panel

    def _make_incidentes(self) -> QFrame:
        panel = _panel("Reporte de Incidentes")

        cols = [
            "ID", "Asignación", "Vehículo", "Conductor",
            "Ruta", "Gravedad", "Estado", "Reportado",
        ]

        table = make_table(cols)
        table.setRowCount(len(self._incidentes))

        for r, inc in enumerate(self._incidentes):
            set_table_item(table, r, 0, inc.get("id", "—"))
            set_table_item(table, r, 1, inc.get("asignacion", "—"))
            set_table_item(table, r, 2, inc.get("vehiculo", "—"))
            set_table_item(table, r, 3, inc.get("conductor", "—"))
            set_table_item(table, r, 4, inc.get("ruta", "—"))
            set_table_item(table, r, 5, inc.get("gravedad", "—"), badge=True)
            set_table_item(table, r, 6, inc.get("estado", "—"), badge=True)
            set_table_item(table, r, 7, inc.get("reportado", "—"))

        table.resizeColumnsToContents()
        _ajustar_altura_tabla(table, len(self._incidentes), minimo=180, maximo=420)
        panel.layout().addWidget(table)
        return panel

    def _make_documentacion(self) -> QFrame:
        panel = _panel("Reporte Documental Crítico")

        cols = ["Vehículo", "Documento", "Vencimiento", "Días Restantes", "Estado"]

        table = make_table(cols)
        table.setRowCount(len(self._documentacion))

        for r, doc in enumerate(self._documentacion):
            dias = doc.get("dias_restantes", 0)
            dias_str = f"+{dias} días" if dias >= 0 else f"{dias} días"

            set_table_item(table, r, 0, doc.get("vehiculo", "—"))
            set_table_item(table, r, 1, doc.get("documento", "—"))
            set_table_item(table, r, 2, doc.get("vencimiento", "—"))
            set_table_item(table, r, 3, dias_str)
            set_table_item(table, r, 4, doc.get("estado", "—"), badge=True)

        table.resizeColumnsToContents()
        _ajustar_altura_tabla(table, len(self._documentacion), minimo=170, maximo=360)
        panel.layout().addWidget(table)
        return panel

    def _make_mantenimiento(self) -> QFrame:
        panel = _panel("Reporte de Mantenimiento")

        cols = [
            "ID", "Vehículo", "Tipo", "Prioridad",
            "Estado", "Incidente", "Ingreso", "Egreso",
        ]

        table = make_table(cols)
        table.setRowCount(len(self._mantenimientos))

        for r, m in enumerate(self._mantenimientos):
            set_table_item(table, r, 0, m.get("id", "—"))
            set_table_item(table, r, 1, m.get("vehiculo", "—"))
            set_table_item(table, r, 2, m.get("tipo", "—"))
            set_table_item(table, r, 3, m.get("prioridad", "—"), badge=True)
            set_table_item(table, r, 4, m.get("estado", "—"), badge=True)
            set_table_item(table, r, 5, m.get("incidente", "—"))
            set_table_item(table, r, 6, m.get("ingreso", "—"))
            set_table_item(table, r, 7, m.get("egreso", "—"))

        table.resizeColumnsToContents()
        _ajustar_altura_tabla(table, len(self._mantenimientos), minimo=180, maximo=420)
        panel.layout().addWidget(table)
        return panel


# ──────────────────────────────────────────────────────────────────────────────

def _panel(title: str) -> QFrame:
    panel = QFrame()
    panel.setObjectName("panel")

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)

    header = QLabel(title)
    header.setObjectName("section_header")
    layout.addWidget(header)

    return panel

def _ajustar_altura_tabla(table, filas: int, minimo: int = 150, maximo: int = 420):
    """
    Ajusta la altura de una tabla según la cantidad de filas para evitar
    que se vea solo el encabezado.
    """
    alto_header = table.horizontalHeader().height()
    alto_fila = table.verticalHeader().defaultSectionSize()
    alto_scroll = 28

    alto = alto_header + (max(filas, 1) * alto_fila) + alto_scroll + 12
    alto = max(minimo, min(alto, maximo))

    table.setMinimumHeight(alto)