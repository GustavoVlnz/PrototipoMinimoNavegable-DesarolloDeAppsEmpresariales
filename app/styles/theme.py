"""
Tema visual de LoncoExpress.
Paleta en escala de azules, estilo empresarial minimalista.
"""

APP_STYLESHEET = """
/* ───────────────────────────────────────────────
   GLOBAL
─────────────────────────────────────────────── */
* {
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: #1E2D40;
    outline: none;
}

QMainWindow, QWidget#central {
    background-color: #EBF2FF;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: #EBF2FF;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #93BAE8;
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
    background-color: #0B1E3D;
}

QLabel#brand_logo {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 0px 0px 2px 0px;
}

QLabel#brand_sub {
    color: #5B7FA6;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

QLabel#nav_section {
    color: #3D5978;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 8px 20px 4px 20px;
}

QPushButton#nav_btn {
    color: #94B4D9;
    background: transparent;
    border: none;
    text-align: left;
    padding: 10px 16px 10px 20px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 8px;
    margin: 1px 10px;
}
QPushButton#nav_btn:hover {
    background-color: rgba(255,255,255,0.07);
    color: #D6E8FF;
}

QPushButton#nav_btn[active="true"] {
    background-color: #1E5FC3;
    color: #FFFFFF;
    font-weight: 600;
}

QLabel#user_name {
    color: #D6E8FF;
    font-size: 13px;
    font-weight: 600;
}
QLabel#user_role {
    color: #5B7FA6;
    font-size: 11px;
}
QLabel#user_avatar {
    background-color: #1E5FC3;
    color: white;
    border-radius: 16px;
    font-size: 13px;
    font-weight: 700;
}

/* ───────────────────────────────────────────────
   TOPBAR
─────────────────────────────────────────────── */
QWidget#topbar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #D6E4F7;
}
QLabel#page_title {
    font-size: 20px;
    font-weight: 700;
    color: #0B1E3D;
}
QLabel#page_subtitle {
    font-size: 12px;
    color: #5B7FA6;
}
QPushButton#topbar_action {
    background-color: #1E5FC3;
    color: white;
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
    background-color: #FFFFFF;
    border: 1px solid #D6E4F7;
    border-radius: 12px;
}
QLabel#kpi_value {
    font-size: 36px;
    font-weight: 700;
    color: #0B1E3D;
}
QLabel#kpi_label {
    font-size: 12px;
    color: #5B7FA6;
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
    background-color: #FFFFFF;
    border: 1px solid #D6E4F7;
    border-radius: 10px;
    gridline-color: #EBF2FF;
    selection-background-color: #DBEAFE;
    selection-color: #0B1E3D;
    alternate-background-color: #F5F8FF;
}
QTableWidget::item {
    padding: 10px 12px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #DBEAFE;
    color: #0B1E3D;
}
QHeaderView::section {
    background-color: #F0F6FF;
    color: #374151;
    font-weight: 600;
    font-size: 12px;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #D6E4F7;
    letter-spacing: 0.5px;
}
QHeaderView {
    background: transparent;
}

/* ───────────────────────────────────────────────
   FORMS / INPUTS
─────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #F5F8FF;
    border: 1px solid #C3D9F5;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #1E2D40;
}
QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #1E5FC3;
    background-color: #FFFFFF;
}
QComboBox {
    background-color: #F5F8FF;
    border: 1px solid #C3D9F5;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}
QComboBox:focus {
    border: 2px solid #1E5FC3;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background: white;
    border: 1px solid #C3D9F5;
    border-radius: 8px;
    selection-background-color: #DBEAFE;
}
QSpinBox, QDoubleSpinBox {
    background-color: #F5F8FF;
    border: 1px solid #C3D9F5;
    border-radius: 8px;
    padding: 8px 12px;
}
QSpinBox:focus {
    border: 2px solid #1E5FC3;
}
QLabel#form_label {
    font-size: 12px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 2px;
}

/* ───────────────────────────────────────────────
   BUTTONS
─────────────────────────────────────────────── */
QPushButton#btn_primary {
    background-color: #1E5FC3;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#btn_primary:hover { background-color: #1749A3; }
QPushButton#btn_primary:pressed { background-color: #133A8A; }

QPushButton#btn_secondary {
    background-color: #EBF2FF;
    color: #1E5FC3;
    border: 1px solid #C3D9F5;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#btn_secondary:hover { background-color: #DBEAFE; }

QPushButton#btn_danger {
    background-color: #DC2626;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#btn_danger:hover { background-color: #B91C1C; }

QPushButton#btn_warning {
    background-color: #D97706;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#btn_success {
    background-color: #16A34A;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 13px;
    font-weight: 600;
}

/* ───────────────────────────────────────────────
   STATUS BADGES (inline QLabel)
─────────────────────────────────────────────── */
QLabel#badge_green {
    background-color: #DCFCE7;
    color: #15803D;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#badge_red {
    background-color: #FEE2E2;
    color: #B91C1C;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#badge_blue {
    background-color: #DBEAFE;
    color: #1D4ED8;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#badge_yellow {
    background-color: #FEF3C7;
    color: #92400E;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#badge_orange {
    background-color: #FFEDD5;
    color: #9A3412;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#badge_gray {
    background-color: #F3F4F6;
    color: #374151;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}

/* ───────────────────────────────────────────────
   DIALOGS
─────────────────────────────────────────────── */
QDialog {
    background-color: #FFFFFF;
}
QLabel#dialog_title {
    font-size: 17px;
    font-weight: 700;
    color: #0B1E3D;
}
QLabel#section_header {
    font-size: 13px;
    font-weight: 700;
    color: #0B1E3D;
    border-bottom: 2px solid #EBF2FF;
    padding-bottom: 4px;
}

/* ───────────────────────────────────────────────
   ALERT PANEL
─────────────────────────────────────────────── */
QFrame#alert_item {
    background-color: #FEF3C7;
    border: 1px solid #FDE68A;
    border-radius: 8px;
    margin: 2px 0;
}
QFrame#alert_critical {
    background-color: #FEE2E2;
    border: 1px solid #FECACA;
    border-radius: 8px;
    margin: 2px 0;
}
QFrame#alert_info {
    background-color: #DBEAFE;
    border: 1px solid #BFDBFE;
    border-radius: 8px;
    margin: 2px 0;
}

/* ───────────────────────────────────────────────
   CONTENT PANELS
─────────────────────────────────────────────── */
QFrame#panel {
    background-color: #FFFFFF;
    border: 1px solid #D6E4F7;
    border-radius: 12px;
}
QFrame#content_area {
    background-color: #EBF2FF;
}
"""

# Color constants for use in Python code
COLORS = {
    "navy": "#0B1E3D",
    "blue_dark": "#1749A3",
    "blue_mid": "#1E5FC3",
    "blue_light": "#EBF2FF",
    "blue_pale": "#F5F8FF",
    "white": "#FFFFFF",
    "border": "#D6E4F7",
    "text_primary": "#1E2D40",
    "text_muted": "#5B7FA6",
    # Status colors
    "green": "#16A34A",
    "green_bg": "#DCFCE7",
    "red": "#B91C1C",
    "red_bg": "#FEE2E2",
    "blue_status": "#1D4ED8",
    "blue_status_bg": "#DBEAFE",
    "yellow": "#92400E",
    "yellow_bg": "#FEF3C7",
    "orange": "#9A3412",
    "orange_bg": "#FFEDD5",
    "gray": "#374151",
    "gray_bg": "#F3F4F6",
}
