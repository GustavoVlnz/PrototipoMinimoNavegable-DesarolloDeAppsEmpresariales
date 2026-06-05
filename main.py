import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.styles.theme import APP_STYLESHEET
from app.data.database import init_db
from app.data.seed import run_seed  

def main():
    init_db()
    run_seed() 
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