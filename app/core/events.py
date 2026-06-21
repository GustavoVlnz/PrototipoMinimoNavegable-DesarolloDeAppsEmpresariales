"""
events.py
app/core/events.py

Bus de eventos centralizado para sincronizar vistas entre si.

"""

from PyQt6.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    """
    Cada senal representa "esta entidad cambio en la BD". No lleva
    parametros (ej. no dice CUAL vehiculo cambio) a proposito: como la
    politica acordada es recarga completa de tabla, a las vistas les
    basta saber "algo de esta entidad cambio", no el detalle de que.
    """

    vehiculo_actualizado      = pyqtSignal()
    conductor_actualizado     = pyqtSignal()
    asignacion_actualizada    = pyqtSignal()
    solicitud_actualizada     = pyqtSignal()
    mantenimiento_actualizado = pyqtSignal()
    documento_actualizado     = pyqtSignal()


event_bus = EventBus()