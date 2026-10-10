# Pasek postępu z procentem i etykietą stanu.

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QProgressBar, QLabel
from PyQt5.QtCore import Qt


class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(True)
        self.bar.setFormat("%p%")

        self.lbl = QLabel("Bezczynny")
        self.lbl.setMinimumWidth(180)
        self.lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(self.bar, 1)
        layout.addWidget(self.lbl)

    def reset(self):
        """Resetuje pasek do stanu wyjściowego."""
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.lbl.setText("Bezczynny")

    def set_percent(self, pct: float):
        """Ustawia postęp. Wartość < 0 oznacza tryb nieokreślony."""
        if pct < 0:
            self.bar.setRange(0, 0)
            self.lbl.setText("Przetwarzanie…")
        else:
            self.bar.setRange(0, 100)
            self.bar.setValue(int(pct))
            self.lbl.setText(f"{pct:5.1f}%")

    def set_status(self, text: str):
        """Ustawia tekst etykiety."""
        self.lbl.setText(text)