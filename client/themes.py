"""
Theme system untuk light mode dan dark mode.
Menyimpan preferensi tema ke config.json bersama server_url.
"""

# ──────────────────────────────────────────
# COLOR PALETTES
# ──────────────────────────────────────────

LIGHT_THEME = {
    "name": "light",

    # Window / base
    "bg_primary": "#F8F9FA",
    "bg_secondary": "#FFFFFF",
    "bg_tertiary": "#F0F2F5",
    "bg_card": "#FFFFFF",

    # Text
    "text_primary": "#1A1D23",
    "text_secondary": "#5F6368",
    "text_muted": "#9AA0A6",

    # Accents
    "accent_blue": "#1A73E8",
    "accent_blue_hover": "#1565C0",
    "accent_green": "#0D904F",
    "accent_green_hover": "#0B7A42",
    "accent_red": "#D93025",
    "accent_red_hover": "#C5221F",
    "accent_orange": "#E37400",

    # Borders
    "border": "#DADCE0",
    "border_light": "#E8EAED",

    # Table
    "table_header_bg": "#F0F2F5",
    "table_header_fg": "#3C4043",
    "table_row_alt": "#F8F9FA",
    "table_row_hover": "#E8F0FE",
    "table_selection_bg": "#D2E3FC",
    "table_selection_fg": "#1A1D23",
    "table_gridline": "#E8EAED",

    # Input
    "input_bg": "#FFFFFF",
    "input_border": "#DADCE0",
    "input_border_focus": "#1A73E8",

    # Scroll
    "scrollbar_bg": "#F0F2F5",
    "scrollbar_handle": "#BDC1C6",
    "scrollbar_handle_hover": "#9AA0A6",

    # Tab
    "tab_bg": "#F0F2F5",
    "tab_selected_bg": "#FFFFFF",
    "tab_selected_fg": "#1A73E8",
    "tab_fg": "#5F6368",

    # GroupBox
    "groupbox_border": "#DADCE0",
    "groupbox_title": "#1A1D23",

    # Button
    "btn_default_bg": "#F0F2F5",
    "btn_default_fg": "#3C4043",
    "btn_default_hover": "#E8EAED",
    "btn_default_border": "#DADCE0",
}

DARK_THEME = {
    "name": "dark",

    # Window / base
    "bg_primary": "#1A1D23",
    "bg_secondary": "#23272F",
    "bg_tertiary": "#2C313A",
    "bg_card": "#23272F",

    # Text
    "text_primary": "#E8EAED",
    "text_secondary": "#BDC1C6",
    "text_muted": "#9AA0A6",

    # Accents
    "accent_blue": "#8AB4F8",
    "accent_blue_hover": "#AECBFA",
    "accent_green": "#81C995",
    "accent_green_hover": "#A8DAB5",
    "accent_red": "#F28B82",
    "accent_red_hover": "#F6AEA9",
    "accent_orange": "#FDD663",

    # Borders
    "border": "#3C4043",
    "border_light": "#5F6368",

    # Table
    "table_header_bg": "#2C313A",
    "table_header_fg": "#BDC1C6",
    "table_row_alt": "#23272F",
    "table_row_hover": "#303540",
    "table_selection_bg": "#394457",
    "table_selection_fg": "#E8EAED",
    "table_gridline": "#3C4043",

    # Input
    "input_bg": "#2C313A",
    "input_border": "#5F6368",
    "input_border_focus": "#8AB4F8",

    # Scroll
    "scrollbar_bg": "#23272F",
    "scrollbar_handle": "#5F6368",
    "scrollbar_handle_hover": "#9AA0A6",

    # Tab
    "tab_bg": "#2C313A",
    "tab_selected_bg": "#23272F",
    "tab_selected_fg": "#8AB4F8",
    "tab_fg": "#9AA0A6",

    # GroupBox
    "groupbox_border": "#3C4043",
    "groupbox_title": "#E8EAED",

    # Button
    "btn_default_bg": "#2C313A",
    "btn_default_fg": "#E8EAED",
    "btn_default_hover": "#3C4043",
    "btn_default_border": "#5F6368",
}


def get_theme(name: str) -> dict:
    """Return theme dict by name ('light' or 'dark')."""
    return DARK_THEME if name == "dark" else LIGHT_THEME


# ──────────────────────────────────────────
# STYLESHEET GENERATOR
# ──────────────────────────────────────────

def build_stylesheet(theme: dict) -> str:
    """Generate a full Qt stylesheet from the given theme palette."""
    t = theme  # shorthand
    return f"""
    /* ── Base ── */
    QWidget {{
        background-color: {t['bg_primary']};
        color: {t['text_primary']};
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 13px;
    }}

    /* ── QMainWindow ── */
    QMainWindow {{
        background-color: {t['bg_primary']};
    }}

    /* ── Labels ── */
    QLabel {{
        background: transparent;
        color: {t['text_primary']};
    }}

    /* ── Inputs ── */
    QLineEdit, QDoubleSpinBox, QSpinBox, QDateEdit {{
        background-color: {t['input_bg']};
        color: {t['text_primary']};
        border: 1px solid {t['input_border']};
        border-radius: 6px;
        padding: 6px 10px;
        selection-background-color: {t['accent_blue']};
    }}
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QDateEdit:focus {{
        border: 2px solid {t['input_border_focus']};
        padding: 5px 9px;
    }}

    /* ── Buttons ── */
    QPushButton {{
        background-color: {t['btn_default_bg']};
        color: {t['btn_default_fg']};
        border: 1px solid {t['btn_default_border']};
        border-radius: 6px;
        padding: 7px 16px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {t['btn_default_hover']};
    }}
    QPushButton:pressed {{
        background-color: {t['border']};
    }}

    /* Named button classes via objectName */
    QPushButton#btn_primary {{
        background-color: {t['accent_blue']};
        color: white;
        border: none;
        font-weight: bold;
    }}
    QPushButton#btn_primary:hover {{
        background-color: {t['accent_blue_hover']};
    }}

    QPushButton#btn_success {{
        background-color: {t['accent_green']};
        color: white;
        border: none;
        font-weight: bold;
    }}
    QPushButton#btn_success:hover {{
        background-color: {t['accent_green_hover']};
    }}

    QPushButton#btn_danger {{
        background-color: {t['accent_red']};
        color: white;
        border: none;
        font-weight: bold;
    }}
    QPushButton#btn_danger:hover {{
        background-color: {t['accent_red_hover']};
    }}

    /* ── Tables ── */
    QTableWidget {{
        background-color: {t['bg_secondary']};
        alternate-background-color: {t['table_row_alt']};
        color: {t['text_primary']};
        gridline-color: {t['table_gridline']};
        border: 1px solid {t['border']};
        border-radius: 8px;
        selection-background-color: {t['table_selection_bg']};
        selection-color: {t['table_selection_fg']};
    }}
    QTableWidget::item:hover {{
        background-color: {t['table_row_hover']};
    }}
    QHeaderView::section {{
        background-color: {t['table_header_bg']};
        color: {t['table_header_fg']};
        border: none;
        border-bottom: 2px solid {t['border']};
        padding: 8px 12px;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
    }}
    QHeaderView::section:first {{
        border-top-left-radius: 8px;
    }}
    QHeaderView::section:last {{
        border-top-right-radius: 8px;
    }}

    /* ── TabWidget ── */
    QTabWidget::pane {{
        border: 1px solid {t['border']};
        border-radius: 8px;
        background-color: {t['bg_secondary']};
        top: -1px;
    }}
    QTabBar::tab {{
        background-color: {t['tab_bg']};
        color: {t['tab_fg']};
        border: 1px solid {t['border']};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 8px 20px;
        margin-right: 2px;
        font-weight: 500;
    }}
    QTabBar::tab:selected {{
        background-color: {t['tab_selected_bg']};
        color: {t['tab_selected_fg']};
        font-weight: 600;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {t['btn_default_hover']};
    }}

    /* ── GroupBox ── */
    QGroupBox {{
        background-color: {t['bg_card']};
        border: 1px solid {t['groupbox_border']};
        border-radius: 10px;
        margin-top: 16px;
        padding-top: 20px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 12px;
        color: {t['groupbox_title']};
    }}

    /* ── Frame line separator ── */
    QFrame[frameShape="4"] {{
        color: {t['border']};
    }}

    /* ── Scrollbar ── */
    QScrollBar:vertical {{
        background: {t['scrollbar_bg']};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: {t['scrollbar_handle']};
        min-height: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {t['scrollbar_handle_hover']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {t['scrollbar_bg']};
        height: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal {{
        background: {t['scrollbar_handle']};
        min-width: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {t['scrollbar_handle_hover']};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ── TextEdit (receipt) ── */
    QTextEdit {{
        background-color: {t['bg_secondary']};
        color: {t['text_primary']};
        border: 1px solid {t['border']};
        border-radius: 8px;
        padding: 8px;
    }}

    /* ── Dialog ── */
    QDialog {{
        background-color: {t['bg_primary']};
    }}

    /* ── MessageBox ── */
    QMessageBox {{
        background-color: {t['bg_primary']};
    }}
    QMessageBox QLabel {{
        color: {t['text_primary']};
    }}

    /* ── Calendar ── */
    QCalendarWidget {{
        background-color: {t['bg_secondary']};
    }}
    QCalendarWidget QToolButton {{
        color: {t['text_primary']};
        background-color: {t['btn_default_bg']};
        border-radius: 4px;
        padding: 4px;
    }}
    QCalendarWidget QMenu {{
        background-color: {t['bg_secondary']};
        color: {t['text_primary']};
    }}
    QCalendarWidget QAbstractItemView:enabled {{
        color: {t['text_primary']};
        background-color: {t['bg_secondary']};
        selection-background-color: {t['accent_blue']};
        selection-color: white;
    }}
    """
