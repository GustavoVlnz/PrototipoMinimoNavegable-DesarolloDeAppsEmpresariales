"""
Ventana principal de LoncoExpress.
Ensambla el sidebar + topbar + stack de módulos.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt

from app.ui.components.sidebar import SidebarWidget   # nombre correcto de la clase

# Módulos
from app.ui.modules.dashboard      import DashboardView
from app.ui.modules.solicitudes    import SolicitudesView
from app.ui.modules.vehiculos      import VehiculosView
from app.ui.modules.conductores    import ConductoresView
from app.ui.modules.asignaciones   import AsignacionesView
from app.ui.modules.incidentes     import IncidentesView
from app.ui.modules.mantenimiento  import MantenimientoView
from app.ui.modules.documentacion  import DocumentacionView
from app.ui.modules.reportes       import ReportesView
from app.ui.modules.contingencia   import ContingenciaView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._build_ui()

    # ──────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar
        self._sidebar = SidebarWidget()
        self._sidebar.page_changed.connect(self._cambiar_pagina)
        root.addWidget(self._sidebar)

        # ── Stack de páginas
        self._stack = QStackedWidget()
        self._stack.setObjectName("content_stack")
        root.addWidget(self._stack)

        # Registrar módulos (mismo orden que NAV_ITEMS en sidebar.py)
        self._pages = [
            DashboardView(),
            SolicitudesView(),
            VehiculosView(),
            ConductoresView(),
            AsignacionesView(),
            IncidentesView(),
            MantenimientoView(),
            DocumentacionView(),
            ReportesView(),
            ContingenciaView(),
        ]
        for page in self._pages:
            self._stack.addWidget(page)

        self._stack.setCurrentIndex(0)

    # ──────────────────────────────────────────
    def _cambiar_pagina(self, index: int):
        if 0 <= index < self._stack.count():
            self._stack.setCurrentIndex(index)
