# Podgląd miniatury wyodrębnionych klatek z katalogu.

import os
import subprocess
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize


class FramePreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self.lbl_dir = QLabel("Katalog: (nie wybrano)")
        btn_dir = QPushButton("Wybierz katalog…")
        btn_dir.clicked.connect(self.choose_dir)
        btn_refresh = QPushButton("Odśwież")
        btn_refresh.clicked.connect(self.reload)
        top.addWidget(self.lbl_dir, 1)
        top.addWidget(btn_dir)
        top.addWidget(btn_refresh)
        layout.addLayout(top)

        self.list = QListWidget()
        self.list.setViewMode(QListWidget.IconMode)
        self.list.setIconSize(QSize(160, 90))
        self.list.setResizeMode(QListWidget.Adjust)
        self.list.setSpacing(6)
        self.list.itemDoubleClicked.connect(self.open_external)
        layout.addWidget(self.list, 1)

        self._dir = ""

    def choose_dir(self):
        """Wybór katalogu z klatkami."""
        d = QFileDialog.getExistingDirectory(self, "Wybierz katalog z klatkami")
        if d:
            self.set_dir(d)

    def set_dir(self, d: str):
        """Ustawia katalog i ładuje miniatury."""
        self._dir = d
        self.lbl_dir.setText(f"Katalog: {d}")
        self.reload()

    def reload(self):
        """Wczytuje miniatury z bieżącego katalogu."""
        self.list.clear()
        if not self._dir or not os.path.isdir(self._dir):
            return
        files = sorted(
            f for f in os.listdir(self._dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))
        )
        for name in files[:500]:  # limit dla wydajności
            path = os.path.join(self._dir, name)
            pix = QPixmap(path)
            if pix.isNull():
                continue
            thumb = pix.scaled(160, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            item = QListWidgetItem(QIcon(thumb), name)
            item.setData(Qt.UserRole, path)
            self.list.addItem(item)

    def open_external(self, item):
        """Otwiera plik w domyślnej aplikacji systemowej."""
        path = item.data(Qt.UserRole)
        if path and os.path.exists(path):
            try:
                if os.name == "nt":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["xdg-open", path])
            except Exception:
                pass