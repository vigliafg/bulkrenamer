"""Catppuccin Mocha QSS Theme for Bulk File Renamer."""

C = dict(
    base     = "#1e1e2e",
    mantle   = "#181825",
    surface0 = "#313244",
    surface1 = "#45475a",
    overlay1 = "#7f849c",
    text     = "#cdd6f4",
    subtext  = "#a6adc8",
    blue     = "#89b4fa",
    green    = "#a6e3a1",
    red      = "#f38ba8",
    yellow   = "#f9e2af",
    teal     = "#94e2d5",
    mauve    = "#cba6f7",
    peach    = "#fab387",
)

QSS = f"""
/* ── Global ─────────────────────────────────────── */
QWidget {{
    background-color: {C['base']};
    color: {C['text']};
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
}}
QMainWindow {{
    background-color: {C['base']};
}}
QMenuBar {{
    background-color: {C['mantle']};
    color: {C['text']};
    border: none;
    padding: 2px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 4px 10px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background-color: {C['surface1']};
    color: {C['blue']};
}}
QMenu {{
    background-color: {C['mantle']};
    color: {C['text']};
    border: 1px solid {C['surface1']};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 28px 6px 16px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {C['surface1']};
    color: {C['blue']};
}}
QMenu::separator {{
    height: 1px;
    background: {C['surface1']};
    margin: 4px 8px;
}}

/* ── Toolbar ─────────────────────────────────────── */
QToolBar {{
    background-color: {C['mantle']};
    border: none;
    spacing: 4px;
    padding: 4px;
}}
QToolBar::separator {{
    width: 2px;
    background: {C['surface1']};
    margin: 4px 6px;
}}

/* ── PushButton ──────────────────────────────────── */
QPushButton {{
    background-color: {C['surface1']};
    color: {C['text']};
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 12px;
    min-height: 28px;
}}
QPushButton:hover {{
    background-color: {C['surface0']};
}}
QPushButton:pressed {{
    background-color: {C['overlay1']};
}}
QPushButton[accent="true"] {{
    background-color: {C['blue']};
    color: {C['base']};
    font-weight: bold;
    font-size: 13px;
}}
QPushButton[accent="true"]:hover {{
    background-color: {C['mauve']};
}}
QPushButton[accent="true"]:pressed {{
    background-color: {C['teal']};
}}
QPushButton[danger="true"] {{
    background-color: {C['red']};
    color: {C['base']};
    font-weight: bold;
}}
QPushButton[danger="true"]:hover {{
    background-color: #cc6a80;
}}
QPushButton[success="true"] {{
    background-color: {C['green']};
    color: {C['base']};
    font-weight: bold;
}}
QPushButton[success="true"]:hover {{
    background-color: #8bc48a;
}}
QPushButton[info="true"] {{
    background-color: {C['teal']};
    color: {C['base']};
    font-weight: bold;
}}
QPushButton[info="true"]:hover {{
    background-color: #7ecfc2;
}}

/* ── QSplitter ───────────────────────────────────── */
QSplitter::handle {{
    background-color: {C['surface1']};
    width: 4px;
    margin: 0;
}}
QSplitter::handle:hover {{
    background-color: {C['blue']};
}}

/* ── QTableWidget / QTableView ───────────────────── */
QTableWidget, QTableView {{
    background-color: {C['surface0']};
    color: {C['text']};
    border: 1px solid {C['surface1']};
    border-radius: 6px;
    gridline-color: {C['surface1']};
    selection-background-color: {C['surface1']};
    selection-color: {C['text']};
    font-size: 11px;
}}
QHeaderView::section {{
    background-color: {C['mantle']};
    color: {C['blue']};
    border: none;
    border-right: 1px solid {C['surface1']};
    border-bottom: 1px solid {C['surface1']};
    padding: 6px 8px;
    font-weight: bold;
    font-size: 11px;
}}
QScrollBar:vertical {{
    background: {C['mantle']};
    width: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {C['surface1']};
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C['overlay1']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ── QLineEdit ───────────────────────────────────── */
QLineEdit {{
    background-color: {C['surface0']};
    color: {C['text']};
    border: 1px solid {C['surface1']};
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 12px;
}}
QLineEdit:focus {{
    border-color: {C['blue']};
}}

/* ── QComboBox ───────────────────────────────────── */
QComboBox {{
    background-color: {C['surface0']};
    color: {C['text']};
    border: 1px solid {C['surface1']};
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 12px;
}}
QComboBox:hover {{
    border-color: {C['blue']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {C['surface0']};
    color: {C['text']};
    border: 1px solid {C['surface1']};
    selection-background-color: {C['surface1']};
}}

/* ── QCheckBox ───────────────────────────────────── */
QCheckBox {{
    color: {C['subtext']};
    spacing: 8px;
    font-size: 12px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {C['surface1']};
    border-radius: 4px;
    background: {C['surface0']};
}}
QCheckBox::indicator:checked {{
    background: {C['blue']};
    border-color: {C['blue']};
}}

/* ── QRadioButton ────────────────────────────────── */
QRadioButton {{
    color: {C['subtext']};
    spacing: 6px;
    font-size: 12px;
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {C['surface1']};
    border-radius: 8px;
    background: {C['surface0']};
}}
QRadioButton::indicator:checked {{
    background: {C['blue']};
    border-color: {C['blue']};
}}

/* ── QSpinBox ────────────────────────────────────── */
QSpinBox {{
    background-color: {C['surface0']};
    color: {C['text']};
    border: 1px solid {C['surface1']};
    border-radius: 6px;
    padding: 4px 6px;
    font-size: 12px;
}}
QSpinBox:focus {{
    border-color: {C['blue']};
}}

/* ── QGroupBox ───────────────────────────────────── */
QGroupBox {{
    border: 1px solid {C['surface1']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 14px;
    font-size: 12px;
    font-weight: bold;
    color: {C['blue']};
    background-color: {C['mantle']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {C['blue']};
}}

/* ── QLabel ──────────────────────────────────────── */
QLabel[heading="true"] {{
    font-size: 14px;
    font-weight: bold;
    color: {C['blue']};
}}
QLabel[conflict="true"] {{
    color: {C['red']};
    font-weight: bold;
}}
QLabel[subtext="true"] {{
    color: {C['subtext']};
    font-size: 10px;
}}

/* ── QTabWidget ──────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {C['surface1']};
    border-radius: 6px;
    background: {C['mantle']};
}}
QTabBar::tab {{
    background: {C['surface1']};
    color: {C['text']};
    padding: 6px 16px;
    border-radius: 6px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {C['blue']};
    color: {C['base']};
}}
QTabBar::tab:hover:!selected {{
    background: {C['surface0']};
}}

/* ── QStatusBar ──────────────────────────────────── */
QStatusBar {{
    background-color: {C['mantle']};
    color: {C['blue']};
    border: none;
    font-size: 11px;
}}

/* ── QDialog / QMessageBox ───────────────────────── */
QDialog {{
    background-color: {C['base']};
}}
QLabel[tooltip="true"] {{
    color: {C['overlay1']};
    font-size: 10px;
    font-style: italic;
}}
"""
