"""
Ventana principal de LoncoExpress.
Ensambla el sidebar + topbar + stack de módulos.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget

from app.ui.components.sidebar import SidebarWidget
from app.data.database import _SessionFactory  # ← sesión de larga vida para la UI

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
from app.logic import documentacion_logic


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._db_session = _SessionFactory()
        documentacion_logic.sincronizar_vencimientos(
            self._db_session,
            emitir_eventos=False,
        )
        self._build_ui()

    def closeEvent(self, event):
        """Cierra la sesión limpiamente al cerrar la ventana."""
        self._db_session.close()
        super().closeEvent(event)

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

        self._pages = [
            DashboardView(self._db_session),
            SolicitudesView(self._db_session),   
            VehiculosView(self._db_session),
            ConductoresView(self._db_session),
            AsignacionesView(self._db_session), 
            IncidentesView(),
            MantenimientoView(self._db_session),
            DocumentacionView(self._db_session),
            ReportesView(self._db_session),
            ContingenciaView(),
        ]
        for page in self._pages:
            self._stack.addWidget(page)

        self._stack.setCurrentIndex(0)

    def _cambiar_pagina(self, index: int):
        if 0 <= index < self._stack.count():
            self._stack.setCurrentIndex(index)