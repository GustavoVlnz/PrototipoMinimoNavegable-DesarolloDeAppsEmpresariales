"""
events.py
app/core/events.py

Bus de eventos centralizado para sincronizar vistas entre si.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    vehiculo_actualizado      = pyqtSignal()
    conductor_actualizado     = pyqtSignal()
    asignacion_actualizada    = pyqtSignal()
    solicitud_actualizada     = pyqtSignal()
    mantenimiento_actualizado = pyqtSignal()
    documento_actualizado     = pyqtSignal()
    incidente_actualizado     = pyqtSignal()


event_bus = EventBus()