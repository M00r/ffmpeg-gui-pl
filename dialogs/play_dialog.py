# Okno odtwarzacza ffplay z opcjami debug.

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QCheckBox, QSpinBox, QFormLayout,
    QGroupBox, QPlainTextEdit
)
from PyQt5.QtGui import QFont

from ffplay_runner import FFplayWorker


class PlayDialog(QDialog):
    def __init__(self, parent=None, ffplay_path: str = "ffplay"):
        super().__init__(parent)
        self.setWindowTitle("Odtwarzacz FFplay")
        self.resize(720, 520)
        self.ffplay_path = ffplay_path or "ffplay"
        self.worker = None

        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        self.edit_file = QLineEdit()
        btn_file = QPushButton("Wybierz plik…")
        btn_file.clicked.connect(self.pick_file)
        row.addWidget(QLabel("Plik:"))
        row.addWidget(self.edit_file, 1)
        row.addWidget(btn_file)
        layout.addLayout(row)

        box = QGroupBox("Opcje odtwarzania")
        form = QFormLayout(box)
        self.chk_fullscreen = QCheckBox("Pełny ekran")
        form.addRow(self.chk_fullscreen)

        self.chk_noborder = QCheckBox("Bez ramki okna")
        form.addRow(self.chk_noborder)

        self.spin_ss = QSpinBox()
        self.spin_ss.setRange(0, 36000)
        self.spin_ss.setSuffix(" s")
        form.addRow("Start od (sekundy):", self.spin_ss)

        self.edit_filter = QLineEdit()
        self.edit_filter.setPlaceholderText("np. scale=1280:720 lub codecview=mv=pf+bf+bb")
        form.addRow("Filtr wideo (-vf):", self.edit_filter)

        self.edit_flags2 = QLineEdit()
        self.edit_flags2.setPlaceholderText("np. +export_mvs")
        form.addRow("-flags2:", self.edit_flags2)

        self.edit_debug = QLineEdit()
        self.edit_debug.setPlaceholderText("np. vis_mb_type lub vis_qp")
        form.addRow("-debug:", self.edit_debug)
        layout.addWidget(box)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        f = QFont("Consolas")
        f.setStyleHint(QFont.Monospace)
        self.log.setFont(f)
        layout.addWidget(QLabel("Log FFplay:"))
        layout.addWidget(self.log, 1)

        row2 = QHBoxLayout()
        self.btn_play = QPushButton("Odtwórz")
        self.btn_play.clicked.connect(self.play)
        self.btn_stop = QPushButton("Zatrzymaj")
        self.btn_stop.clicked.connect(self.stop)
        self.btn_stop.setEnabled(False)
        btn_close = QPushButton("Zamknij")
        btn_close.clicked.connect(self.reject)
        row2.addWidget(self.btn_play)
        row2.addWidget(self.btn_stop)
        row2.addStretch()
        row2.addWidget(btn_close)
        layout.addLayout(row2)

    def pick_file(self):
        p, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "", "Wszystkie (*)")
        if p:
            self.edit_file.setText(p)

    def _build_cmd(self) -> list:
        """Buduje polecenie ffplay z wybranych opcji."""
        cmd = [self.ffplay_path, "-autoexit"]
        if self.chk_fullscreen.isChecked():
            cmd.append("-fs")
        if self.chk_noborder.isChecked():
            cmd.append("-noborder")
        if self.spin_ss.value() > 0:
            cmd += ["-ss", str(self.spin_ss.value())]
        if self.edit_flags2.text().strip():
            cmd += ["-flags2", self.edit_flags2.text().strip()]
        if self.edit_debug.text().strip():
            cmd += ["-debug", self.edit_debug.text().strip()]
        if self.edit_filter.text().strip():
            cmd += ["-vf", self.edit_filter.text().strip()]
        cmd.append(self.edit_file.text())
        return cmd

    def play(self):
        if not self.edit_file.text().strip():
            return
        if self.worker and self.worker.isRunning():
            return
        cmd = self._build_cmd()
        self.log.clear()
        self.log.appendPlainText("$ " + " ".join(cmd))
        self.worker = FFplayWorker(cmd)
        self.worker.output.connect(self.log.appendPlainText)
        self.worker.finished_ok.connect(self._done)
        self.worker.start()
        self.btn_play.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def stop(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()

    def _done(self, code):
        self.btn_play.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log.appendPlainText(f"=== FFplay zakończony (kod {code}) ===")