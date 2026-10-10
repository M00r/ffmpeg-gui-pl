# Okno ustawień — ścieżki do ffmpeg/ffprobe/ffplay, motyw, aktualizacje.

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QFileDialog, QDialogButtonBox, QCheckBox,
    QComboBox, QLabel, QMessageBox
)
from config import load_config, save_config, resolve_ffmpeg, resolve_ffprobe, resolve_ffplay


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ustawienia")
        self.setMinimumWidth(600)
        self.cfg = load_config()

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Ścieżki do narzędzi FFmpeg.
        self.edit_ff = self._path_row(form, "Ścieżka do ffmpeg:", "ffmpeg_path")
        self.edit_fp = self._path_row(form, "Ścieżka do ffprobe:", "ffprobe_path")
        self.edit_fplay = self._path_row(form, "Ścieżka do ffplay:", "ffplay_path")

        # Motyw.
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["light", "dark"])
        self.combo_theme.setCurrentText(self.cfg.get("theme", "light"))
        form.addRow("Motyw:", self.combo_theme)

        # Kanał aktualizacji.
        self.combo_channel = QComboBox()
        self.combo_channel.addItems(["stable", "beta"])
        self.combo_channel.setCurrentText(self.cfg.get("update_channel", "stable"))
        form.addRow("Kanał aktualizacji:", self.combo_channel)

        # Przełączniki.
        self.chk_auto_update = QCheckBox("Sprawdzaj aktualizacje przy starcie")
        self.chk_auto_update.setChecked(self.cfg.get("auto_check_updates", True))
        form.addRow(self.chk_auto_update)

        self.chk_verify = QCheckBox("Weryfikuj SHA-256 pobranej aktualizacji")
        self.chk_verify.setChecked(self.cfg.get("verify_sha256", True))
        form.addRow(self.chk_verify)

        self.chk_checksums = QCheckBox("Generuj sumy SHA-256 po operacji")
        self.chk_checksums.setChecked(self.cfg.get("generate_checksums", True))
        form.addRow(self.chk_checksums)

        self.chk_confirm = QCheckBox("Potwierdzaj nadpisanie plików")
        self.chk_confirm.setChecked(self.cfg.get("confirm_overwrite", True))
        form.addRow(self.chk_confirm)

        self.chk_keep = QCheckBox("Zachowuj log po zamknięciu")
        self.chk_keep.setChecked(self.cfg.get("keep_log", True))
        form.addRow(self.chk_keep)

        layout.addLayout(form)

        # Informacje diagnostyczne.
        info = QLabel()
        info.setWordWrap(True)
        info.setText(
            f"<i>Wykryty ffmpeg: {resolve_ffmpeg(self.cfg) or '<brak>'}<br>"
            f"Wykryty ffprobe: {resolve_ffprobe(self.cfg) or '<brak>'}<br>"
            f"Wykryty ffplay: {resolve_ffplay(self.cfg) or '<brak>'}</i>"
        )
        layout.addWidget(info)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _path_row(self, form, label, key):
        """Tworzy wiersz z polem tekstowym i przyciskiem wyboru pliku."""
        row = QHBoxLayout()
        edit = QLineEdit(self.cfg.get(key, ""))
        btn = QPushButton("Wybierz…")
        btn.clicked.connect(lambda: self._pick(edit))
        row.addWidget(edit)
        row.addWidget(btn)
        form.addRow(label, row)
        return edit

    def _pick(self, edit):
        """Otwiera okno wyboru pliku wykonywalnego."""
        filt = "Pliki wykonywalne (*.exe);;Wszystkie (*)" if os.name == "nt" else "Wszystkie (*)"
        p, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "", filt)
        if p:
            edit.setText(p)

    def save(self):
        """Zapisuje ustawienia i zamyka okno."""
        self.cfg["ffmpeg_path"] = self.edit_ff.text().strip()
        self.cfg["ffprobe_path"] = self.edit_fp.text().strip()
        self.cfg["ffplay_path"] = self.edit_fplay.text().strip()
        self.cfg["theme"] = self.combo_theme.currentText()
        self.cfg["update_channel"] = self.combo_channel.currentText()
        self.cfg["auto_check_updates"] = self.chk_auto_update.isChecked()
        self.cfg["verify_sha256"] = self.chk_verify.isChecked()
        self.cfg["generate_checksums"] = self.chk_checksums.isChecked()
        self.cfg["confirm_overwrite"] = self.chk_confirm.isChecked()
        self.cfg["keep_log"] = self.chk_keep.isChecked()
        save_config(self.cfg)
        QMessageBox.information(self, "Zapisano", "Ustawienia zapisane.")
        self.accept()