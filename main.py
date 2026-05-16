import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LoncoExpress")
    app.setOrganizationName("LoncoExpress")

    # Fuente base de la app
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Cargar hoja de estilos QSS
    qss_path = os.path.join(os.path.dirname(__file__), "app", "assets", "styles", "main.qss")
    with open(qss_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()