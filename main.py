"""
LoncoExpress - Sistema de Gestión de Flota Vehicular
Punto de entrada principal de la aplicación.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.ui.main_window import MainWindow
from app.styles.theme import APP_STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LoncoExpress - Gestión de Flota")
    app.setOrganizationName("LoncoExpress")
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.setWindowTitle("LoncoExpress — Gestión de Flota Vehicular")
    window.setMinimumSize(1780, 850)
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
