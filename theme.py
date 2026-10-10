# Motywy graficzne (QSS) — jasny i ciemny.

LIGHT_QSS = """
QMainWindow, QDialog, QWidget { background: #f5f5f5; color: #202020; }
QTreeWidget, QListWidget, QTextEdit, QPlainTextEdit, QTableWidget {
    background: #ffffff; border: 1px solid #c0c0c0;
}
QTreeWidget::item:selected, QListWidget::item:selected,
QTableWidget::item:selected { background: #3080d0; color: white; }
QPushButton { background: #e6e6e6; border: 1px solid #b0b0b0;
    padding: 5px 10px; border-radius: 3px; }
QPushButton:hover { background: #dcdcdc; }
QPushButton:pressed { background: #c8c8c8; }
QPushButton:disabled { color: #888; background: #eeeeee; }
QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    background: #ffffff; border: 1px solid #b0b0b0; padding: 3px; border-radius: 3px; }
QGroupBox { border: 1px solid #b0b0b0; border-radius: 4px; margin-top: 10px; padding-top: 6px; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
QProgressBar { border: 1px solid #b0b0b0; border-radius: 3px;
    text-align: center; background: #ffffff; }
QProgressBar::chunk { background: #3080d0; }
QTabWidget::pane { border: 1px solid #b0b0b0; }
QTabBar::tab { padding: 6px 12px; background: #e6e6e6; border: 1px solid #b0b0b0; }
QTabBar::tab:selected { background: #ffffff; }
QMenuBar { background: #e6e6e6; }
QMenuBar::item:selected { background: #3080d0; color: white; }
QMenu { background: #ffffff; border: 1px solid #b0b0b0; }
QMenu::item:selected { background: #3080d0; color: white; }
QStatusBar { background: #e6e6e6; }
QHeaderView::section { background: #e6e6e6; border: 1px solid #b0b0b0; padding: 4px; }
"""

DARK_QSS = """
QMainWindow, QDialog, QWidget { background: #1e1e1e; color: #e6e6e6; }
QTreeWidget, QListWidget, QTextEdit, QPlainTextEdit, QTableWidget {
    background: #252526; color: #e6e6e6; border: 1px solid #3c3c3c;
}
QTreeWidget::item:selected, QListWidget::item:selected,
QTableWidget::item:selected { background: #094771; color: white; }
QPushButton { background: #3c3c3c; color: #e6e6e6; border: 1px solid #555;
    padding: 5px 10px; border-radius: 3px; }
QPushButton:hover { background: #4a4a4a; }
QPushButton:pressed { background: #2a2a2a; }
QPushButton:disabled { color: #777; background: #2a2a2a; }
QLineEdit, QComboBox, QSpinBox, QTimeEdit {
    background: #2d2d2d; color: #e6e6e6; border: 1px solid #555;
    padding: 3px; border-radius: 3px; }
QGroupBox { border: 1px solid #555; border-radius: 4px;
    margin-top: 10px; padding-top: 6px; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; color: #e6e6e6; }
QProgressBar { border: 1px solid #555; border-radius: 3px;
    text-align: center; background: #2d2d2d; color: #e6e6e6; }
QProgressBar::chunk { background: #0e639c; }
QTabWidget::pane { border: 1px solid #555; }
QTabBar::tab { padding: 6px 12px; background: #2d2d2d;
    border: 1px solid #555; color: #e6e6e6; }
QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; }
QMenuBar { background: #2d2d2d; color: #e6e6e6; }
QMenuBar::item:selected { background: #094771; color: white; }
QMenu { background: #252526; color: #e6e6e6; border: 1px solid #555; }
QMenu::item:selected { background: #094771; color: white; }
QStatusBar { background: #007acc; color: white; }
QCheckBox, QRadioButton, QLabel { color: inherit; }
QHeaderView::section { background: #2d2d2d; color: #e6e6e6;
    border: 1px solid #555; padding: 4px; }
"""


def apply_theme(app, theme: str):
    """Nakłada wybrany motyw na całą aplikację."""
    app.setStyleSheet(DARK_QSS if theme == "dark" else LIGHT_QSS)