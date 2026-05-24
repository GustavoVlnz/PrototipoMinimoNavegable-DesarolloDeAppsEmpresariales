"""
Tema visual de LoncoExpress.
"""

APP_STYLESHEET = """
/* ───────────────────────────────────────────────
   GLOBAL
─────────────────────────────────────────────── */
* {
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: #E8F0FE;
    outline: none;
}

QMainWindow,
QWidget#central,
QStackedWidget,
QFrame#content_area {
    background-color: #132238;
}

QScrollArea {
    border: none;
    background-color: #0D1B2E;
}
/* El widget interior del viewport también necesita fondo oscuro */
QScrollArea > QWidget > QWidget {
    background-color: #0D1B2E;
}

QScrollBar:vertical {
    background: #0D1B2E;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2A4A72;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ───────────────────────────────────────────────
   SIDEBAR
─────────────────────────────────────────────── */
QWidget#sidebar {
    background-color: #071120;
    border-right: 1px solid #132238;
}

QWidget#sidebar QWidget {
    background: transparent;
}

QLabel#brand_logo {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 1px;
    padding: 0px 0px 2px 0px;
}

QLabel#brand_sub {
    color: #4A6A94;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

QLabel#nav_section {
    color: #2E4D72;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    padding: 8px 20px 4px 20px;
}

QPushButton#nav_btn {
    color: #FFFFFF;
    background: transparent;
    border: none;

    text-align: left;

    padding: 10px 16px 8px 18px;
    min-height: 38px;

    font-size: 14px;
    font-weight: 600;

    border-radius: 10px;

    margin: 1px 3px;

    qproperty-iconSize: 20px 20px;
}

QPushButton#nav_btn:hover {
    background-color: rgba(255,255,255,0.10);
    color: #FFFFFF;
}

QPushButton#nav_btn[active="true"] {
    background-color: #1E5FC3;
    color: #FFFFFF;
    font-weight: 700;
}

QLabel#user_name {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 700;
}
QLabel#user_role {
    color: #4A6A94;
    font-size: 11px;
}
QLabel#user_avatar {
    background-color: #1E5FC3;
    color: #FFFFFF;
    border-radius: 16px;
    font-size: 13px;
    font-weight: 800;
}

QStackedWidget#content_stack {
    background-color: #132238;
}

/* ───────────────────────────────────────────────
   TOPBAR
─────────────────────────────────────────────── */
QWidget#topbar {
    background-color: #111F35;
    border-bottom: 1px solid #1A3055;
}
QLabel#page_title {
    font-size: 20px;
    font-weight: 700;
    color: #FFFFFF;
}
QLabel#page_subtitle {
    font-size: 12px;
    color: #6B8EB8;
}
QPushButton#topbar_action {
    background-color: #1E5FC3;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#topbar_action:hover {
    background-color: #1749A3;
}
QPushButton#topbar_action:pressed {
    background-color: #133A8A;
}

/* ───────────────────────────────────────────────
   KPI CARDS
─────────────────────────────────────────────── */
QFrame#kpi_card {
    background-color: #1A2F4D;
    border: 1px solid #23456D;
    border-radius: 12px;
}
QLabel#kpi_value {
    font-size: 36px;
    font-weight: 700;
    color: #E8F0FE;
}
QLabel#kpi_label {
    font-size: 12px;
    color: #7BA5CC;
    font-weight: 500;
}
QLabel#kpi_delta {
    font-size: 11px;
    color: #16A34A;
}
QLabel#kpi_icon {
    font-size: 24px;
}

/* ───────────────────────────────────────────────
   TABLES
─────────────────────────────────────────────── */
QTableWidget {
    background-color: #1A2F4D;
    border: 1px solid #23456D;
    border-radius: 10px;
    gridline-color: #1E3A5C;
    selection-background-color: #1E5FC3;
    selection-color: #FFFFFF;
    alternate-background-color: #1A3050;
    color: #E8F0FE;
}
QTableWidget::item {
    padding: 10px 12px;
    border: none;
    color: #E8F0FE;
}
QTableWidget::item:selected {
    background-color: #1E5FC3;
    color: #FFFFFF;
}
QHeaderView::section {
    background-color: #1E3558;
    color: #A8C4E0;
    font-weight: 600;
    font-size: 12px;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #1E3A5C;
    letter-spacing: 0.5px;
}
QHeaderView {
    background: transparent;
}

/* ───────────────────────────────────────────────
   FORMS / INPUTS
─────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #172B42;
    border: 1px solid #1E3A5C;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #E8F0FE;
}
QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #1E5FC3;
    background-color: #172B42;
}
QComboBox {
    background-color: #172B42;
    border: 1px solid #1E3A5C;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #E8F0FE;
}
QComboBox:focus {
    border: 2px solid #1E5FC3;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background: #172B42;
    border: 1px solid #1E3A5C;
    border-radius: 8px;
    selection-background-color: #1E5FC3;
    color: #E8F0FE;
}
QSpinBox, QDoubleSpinBox {
    background-color: #172B42;
    border: 1px solid #1E3A5C;
    border-radius: 8px;
    padding: 8px 12px;
    color: #E8F0FE;
}
QSpinBox:focus {
    border: 2px solid #1E5FC3;
}
QLabel#form_label {
    font-size: 12px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 2px;
}

/* ───────────────────────────────────────────────
   BUTTONS
─────────────────────────────────────────────── */
QPushButton#btn_primary {
    background-color: #1E5FC3;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#btn_primary:hover { background-color: #1749A3; }
QPushButton#btn_primary:pressed { background-color: #133A8A; }

QPushButton#btn_secondary {
    background-color: rgba(255,255,255,0.08);
    color: #FFFFFF;
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#btn_secondary:hover { background-color: rgba(255,255,255,0.15); }

QPushButton#btn_danger {
    background-color: #DC2626;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#btn_danger:hover { background-color: #B91C1C; }

QPushButton#btn_warning {
    background-color: #D97706;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#btn_success {
    background-color: #16A34A;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#btn_table_action {
    background-color: #1B365D;
    border: 1px solid #2F5B91;
    border-radius: 8px;
    padding: 6px 12px;
    color: #E8F0FE;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#btn_table_action:hover {
    background-color: #244975;
    border: 1px solid #4A78B0;
}

QPushButton#btn_table_action:pressed {
    background-color: #16324C;
}

QPushButton#btn_table_action {
    background-color: transparent;
    color: #60A5FA;
    border: 1px solid #1E3A5C;
    border-radius: 6px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#btn_table_action:hover 
    { background-color: rgba(30,95,195,0.25); }
/* ───────────────────────────────────────────────
   STATUS BADGES 
─────────────────────────────────────────────── */
QLabel#badge_green {
    background: transparent;
    color: #34D399;
    font-size: 12px;
    font-weight: 700;
}
QLabel#badge_red {
    background: transparent;
    color: #F87171;
    font-size: 12px;
    font-weight: 700;
}
QLabel#badge_blue {
    background: transparent;
    color: #60A5FA;
    font-size: 12px;
    font-weight: 700;
}
QLabel#badge_yellow {
    background: transparent;
    color: #FCD34D;
    font-size: 12px;
    font-weight: 700;
}
QLabel#badge_orange {
    background: transparent;
    color: #FB923C;
    font-size: 12px;
    font-weight: 700;
}
QLabel#badge_gray {
    background: transparent;
    color: #94A3B8;
    font-size: 12px;
    font-weight: 700;
}

/* ───────────────────────────────────────────────
   DIALOGS
─────────────────────────────────────────────── */
QDialog {
    background-color: #172B42;
}
QLabel#dialog_title {
    font-size: 17px;
    font-weight: 700;
    color: #FFFFFF;
}
QLabel#section_header {
    font-size: 13px;
    font-weight: 700;
    color: #FFFFFF;
    border-bottom: 2px solid #1E3A5C;
    padding-bottom: 4px;
}

QDialog QPushButton {
    background-color: #1E5FC3;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    min-width: 80px;
    font-size: 13px;
    font-weight: 600;
}

QDialog QPushButton:hover {
    background-color: #1749A3;
}

QDialog QPushButton:pressed {
    background-color: #133A8A;
}

QMessageBox QPushButton {
    background-color: #1E5FC3;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    min-width: 80px;
    font-size: 13px;
    font-weight: 600;
}

QMessageBox QPushButton:hover {
    background-color: #1749A3;
}

QMessageBox QPushButton:pressed {
    background-color: #133A8A;
}
/* ───────────────────────────────────────────────
   ALERT PANEL
─────────────────────────────────────────────── */
QFrame#alert_critical {
    background-color: rgba(127, 29, 29, 0.35);
    border: 1px solid #DC2626;
    border-radius: 10px;
}

QFrame#alert_item {
    background-color: rgba(146, 64, 14, 0.35);
    border: 1px solid #F59E0B;
    border-radius: 10px;
}

QFrame#alert_info {
    background-color: rgba(29, 78, 216, 0.25);
    border: 1px solid #3B82F6;
    border-radius: 10px;
}
QFrame#alert_item QLabel,
QFrame#alert_item QPushButton,
QFrame#alert_critical QLabel,
QFrame#alert_critical QPushButton,
QFrame#alert_info QLabel,
QFrame#alert_info QPushButton {
    color: #E8F0FE;
    background: transparent;
}

/* ───────────────────────────────────────────────
   CONTENT PANELS
─────────────────────────────────────────────── */
QFrame#panel {
    background-color: #1A2F4D;
    border: 1px solid #23456D;
    border-radius: 12px;
}

QWidget#content_area {
    background-color: #0D1B2E;
}
"""
# Color constants for use in Python code
COLORS = {
    # Backgrounds oscuros 
    "navy":           "#050E1C",   # sidebar (más oscuro)
    "bg_main":        "#0D1B2E",   # fondo general de vistas
    "bg_topbar":      "#111F35",   # topbar
    "bg_component":   "#172B42",   # tarjetas, tablas, inputs, paneles, dialogs
    "bg_alt_row":     "#1A3050",   # fila alternada en tablas
    "bg_header_row":  "#1E3558",   # cabecera de tabla

    # Blues de acción
    "blue_dark":      "#1749A3",
    "blue_mid":       "#1E5FC3",

    # Bordes
    "border":         "#1E3A5C",   # borde universal sobre fondos oscuros

    # Texto
    "text_on_dark":   "#E8F0FE",   # texto principal sobre fondos oscuros
    "text_muted_dark":"#7BA5CC",   # texto secundario/muted sobre fondos oscuros
    "text_header":    "#A8C4E0",   # texto en cabeceras de tabla
    "text_white":     "#FFFFFF",   # texto de énfasis máximo

    # Status colors
    "green":          "#16A34A",
    "green_bg":       "#DCFCE7",
    "red":            "#B91C1C",
    "red_bg":         "#FEE2E2",
    "blue_status":    "#1D4ED8",
    "blue_status_bg": "#DBEAFE",
    "yellow":         "#92400E",
    "yellow_bg":      "#FEF3C7",
    "orange":         "#9A3412",
    "orange_bg":      "#FFEDD5",
    "gray":           "#374151",
    "gray_bg":        "#F3F4F6",
}