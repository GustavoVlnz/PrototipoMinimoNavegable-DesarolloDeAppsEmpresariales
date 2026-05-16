from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt

from app.ui.components.kpi_card import KpiCard
from app.ui.components.status_badge import StatusBadge


class DashboardView(QScrollArea):
    """Vista principal — Dashboard general.

    Muestra KPIs, solicitudes recientes, alertas del sistema
    y estado de flota.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("module-view")
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("module-content")
        self.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(18)

        layout.addLayout(self._build_kpis())
        layout.addLayout(self._build_middle_row())
        layout.addWidget(self._build_fleet_table())
        layout.addStretch()

    # ─── KPIs ────────────────────────────────────────────────────
    def _build_kpis(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        kpis = [
            ("Vehículos totales",  "12", "2 disponibles hoy",    "default"),
            ("En ruta ahora",       "4",  "Km activos: ~890",     "info"),
            ("Solicitudes hoy",     "7",  "3 pendientes",         "warning"),
            ("Incidentes activos",  "1",  "Falla crítica activa", "danger"),
        ]
        for label, value, sub, color in kpis:
            card = KpiCard(label, value, sub, color)
            row.addWidget(card)

        return row

    # ─── Fila media: solicitudes + alertas ───────────────────────
    def _build_middle_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(14)
        row.addWidget(self._build_recent_requests(), stretch=1)
        row.addWidget(self._build_alerts(), stretch=1)
        return row

    def _build_recent_requests(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("Solicitudes recientes")
        header.setObjectName("panel-header")
        layout.addWidget(header)

        table = QTableWidget(4, 4)
        table.setObjectName("data-table")
        table.setHorizontalHeaderLabels(["ID", "Destino", "Prioridad", "Estado"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        rows = [
            ("#0041", "Concepción", "Alta",   "En ejecución"),
            ("#0042", "Los Ángeles","Media",  "Pendiente"),
            ("#0043", "Santiago",   "Media",  "Creada"),
            ("#0040", "Temuco",     "Normal", "Completada"),
        ]
        for r, (id_, dest, prio, estado) in enumerate(rows):
            table.setItem(r, 0, QTableWidgetItem(id_))
            table.setItem(r, 1, QTableWidgetItem(dest))
            # Prioridad como badge en celda
            prio_badge = StatusBadge(prio)
            table.setCellWidget(r, 2, prio_badge)
            estado_badge = StatusBadge(estado)
            table.setCellWidget(r, 3, estado_badge)

        layout.addWidget(table)
        return frame

    def _build_alerts(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(0)

        header = QLabel("Alertas del sistema")
        header.setObjectName("panel-header-padded")
        layout.addWidget(header)

        alerts = [
            ("🔴", "Falla crítica en ruta — BKRT-42",         "Km 112, Ruta 5 Sur · 10:33 AM"),
            ("🟡", "Permiso circulación vence en 3 días",      "Furgón GKRS-91"),
            ("🟡", "Mantención vencida — BKRT-42",             "Supera 6 meses desde última revisión"),
            ("🔵", "Solicitud #0042 sin asignar",              "Salida programada 11:00 AM"),
        ]
        for icon, title, subtitle in alerts:
            row = QHBoxLayout()
            row.setSpacing(10)

            icon_lbl = QLabel(icon)
            icon_lbl.setFixedWidth(22)
            row.addWidget(icon_lbl)

            col = QVBoxLayout()
            col.setSpacing(1)
            t = QLabel(title)
            t.setObjectName("alert-title")
            s = QLabel(subtitle)
            s.setObjectName("alert-sub")
            col.addWidget(t)
            col.addWidget(s)
            row.addLayout(col)
            row.addStretch()

            wrapper = QWidget()
            wrapper.setObjectName("alert-row")
            wrapper.setLayout(row)
            layout.addWidget(wrapper)

        layout.addStretch()
        return frame

    # ─── Tabla flota ─────────────────────────────────────────────
    def _build_fleet_table(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("Estado de flota")
        header.setObjectName("panel-header")
        layout.addWidget(header)

        table = QTableWidget(4, 6)
        table.setObjectName("data-table")
        table.setHorizontalHeaderLabels(
            ["Vehículo", "Tipo", "Conductor", "Destino", "Estado", "Capacidad"]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        rows = [
            ("BKRT-42", "Toyota Hilux",      "Carlos Moya", "Concepción", "Fuera de servicio", "1.200 kg"),
            ("GKRS-91", "Peugeot Boxer",     "Marco Díaz",  "—",          "Disponible",        "900 kg"),
            ("KLMP-77", "Mercedes Sprinter", "Ana Torres",  "Santiago",   "En Ruta",           "1.500 kg"),
            ("TRFN-88", "Ford Transit",      "—",           "—",          "Bloqueado",         "800 kg"),
        ]
        for r, (patente, tipo, conductor, destino, estado, cap) in enumerate(rows):
            table.setItem(r, 0, QTableWidgetItem(patente))
            table.setItem(r, 1, QTableWidgetItem(tipo))
            table.setItem(r, 2, QTableWidgetItem(conductor))
            table.setItem(r, 3, QTableWidgetItem(destino))
            table.setCellWidget(r, 4, StatusBadge(estado))
            table.setItem(r, 5, QTableWidgetItem(cap))

        layout.addWidget(table)
        return frame