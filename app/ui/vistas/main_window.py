from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt

from app.ui.components.sidebar import Sidebar
from app.ui.components.topbar import Topbar

from app.ui.modules.dashboard.dashboard_view import DashboardView
from app.ui.modules.solicitudes.solicitudes_view import SolicitudesView
from app.ui.modules.asignaciones.asignaciones_view import AsignacionesView
from app.ui.modules.vehiculos.vehiculos_view import VehiculosView
from app.ui.modules.conductores.conductores_view import ConductoresView
from app.ui.modules.incidentes.incidentes_view import IncidentesView
from app.ui.modules.mantenimiento.mantenimiento_view import MantenimientoView
from app.ui.modules.documentos.documentos_view import DocumentosView
from app.ui.modules.reportes.reportes_view import ReportesView


# Títulos para cada módulo
MODULE_TITLES = {
    "dashboard":     "Dashboard general",
    "solicitudes":   "Solicitudes de transporte",
    "asignaciones":  "Asignaciones",
    "vehiculos":     "Gestión de vehículos",
    "conductores":   "Conductores",
    "incidentes":    "Incidentes en ruta",
    "mantenimiento": "Mantenimiento",
    "documentos":    "Documentación legal",
    "reportes":      "Reportes y trazabilidad",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LoncoExpress — Gestión de Flota Vehicular")
        self.setMinimumSize(1100, 680)
        self.resize(1280, 760)

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────
        self.sidebar = Sidebar()
        root_layout.addWidget(self.sidebar)

        # ── Zona derecha: topbar + contenido ─────────────────────
        right_widget = QWidget()
        right_widget.setObjectName("right-pane")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.topbar = Topbar()
        right_layout.addWidget(self.topbar)

        # QStackedWidget: una vista por módulo
        self.stack = QStackedWidget()
        self.stack.setObjectName("stack")
        right_layout.addWidget(self.stack)

        root_layout.addWidget(right_widget)

        # ── Registrar vistas ─────────────────────────────────────
        self.views: dict[str, QWidget] = {
            "dashboard":     DashboardView(),
            "solicitudes":   SolicitudesView(),
            "asignaciones":  AsignacionesView(),
            "vehiculos":     VehiculosView(),
            "conductores":   ConductoresView(),
            "incidentes":    IncidentesView(),
            "mantenimiento": MantenimientoView(),
            "documentos":    DocumentosView(),
            "reportes":      ReportesView(),
        }
        for view in self.views.values():
            self.stack.addWidget(view)

        # ── Conectar navegación ───────────────────────────────────
        self.sidebar.nav_changed.connect(self._on_nav_changed)

        # Vista inicial
        self._on_nav_changed("dashboard")

    # ──────────────────────────────────────────────────────────────
    def _on_nav_changed(self, module_id: str) -> None:
        """Cambia la vista activa y actualiza el título del topbar."""
        if module_id in self.views:
            self.stack.setCurrentWidget(self.views[module_id])
            title = MODULE_TITLES.get(module_id, module_id.capitalize())
            self.topbar.set_title(title)