# Menedżer wtyczek i presetów użytkownika.

import os
import subprocess
import sys
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QPlainTextEdit
)
from PyQt5.QtGui import QFont

from plugins.loader import load_plugin_presets, list_plugins, PLUGINS_USER_DIR


class PluginsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wtyczki i presety")
        self.resize(760, 520)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Zainstalowane wtyczki:"))
        self.list = QListWidget()
        for p in list_plugins():
            QListWidgetItem(str(p), self.list)
        layout.addWidget(self.list, 1)

        row = QHBoxLayout()
        btn_open = QPushButton("Otwórz katalog wtyczek")
        btn_open.clicked.connect(self.open_folder)
        btn_add = QPushButton("Dodaj wtyczkę (.py)…")
        btn_add.clicked.connect(self.add_plugin)
        row.addWidget(btn_open)
        row.addWidget(btn_add)
        row.addStretch()
        layout.addLayout(row)

        layout.addWidget(QLabel("Dostępne presety z wtyczek:"))
        self.info = QPlainTextEdit()
        self.info.setReadOnly(True)
        f = QFont("Consolas")
        f.setStyleHint(QFont.Monospace)
        self.info.setFont(f)
        layout.addWidget(self.info, 1)

        row2 = QHBoxLayout()
        btn_close = QPushButton("Zamknij")
        btn_close.clicked.connect(self.reject)
        row2.addStretch()
        row2.addWidget(btn_close)
        layout.addLayout(row2)

        self.refresh()

    def refresh(self):
        """Odświeża listę presetów z wtyczek."""
        presets = load_plugin_presets()
        lines = []
        for name, data in presets.items():
            label = data.get("label", name)
            ext = data.get("ext", "?")
            lines.append(f"• {label}  (→ .{ext})")
        self.info.setPlainText("\n".join(lines) or "(brak presetów)")

    def open_folder(self):
        """Otwiera katalog wtyczek użytkownika."""
        PLUGINS_USER_DIR.mkdir(parents=True, exist_ok=True)
        path = str(PLUGINS_USER_DIR)
        try:
            if os.name == "nt":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception:
            QMessageBox.information(self, "Katalog wtyczek", path)

    def add_plugin(self):
        """Kopiuje wybrany plik .py do katalogu wtyczek."""
        p, _ = QFileDialog.getOpenFileName(self, "Wybierz plik .py", "", "Python (*.py)")
        if not p:
            return
        dest = PLUGINS_USER_DIR / Path(p).name
        PLUGINS_USER_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(p, "rb") as src, open(dest, "wb") as dst:
                dst.write(src.read())
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się skopiować: {e}")
            return
        QMessageBox.information(self, "Dodano", f"Skopiowano do:\n{dest}")
        self.refresh()