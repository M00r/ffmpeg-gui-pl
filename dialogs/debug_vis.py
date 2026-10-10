# Wizualizacja debugowa: QP (jeśli obsługiwane) oraz wektory ruchu.
# Uwaga: FFmpeg 7.1.1 nie obsługuje już -debug vis_mb_type.
# Wizualizacja QP dla H.264 wymaga FFmpeg z czerwca 2025 (nightly).
# Wektory ruchu działają stabilnie we wszystkich wersjach 6.x/7.x.

import os
from PyQt5.QtWidgets import (
    QFormLayout, QComboBox, QCheckBox, QGroupBox, QSpinBox,
    QLabel, QVBoxLayout
)
from .base import BaseDialog


class DebugVisDialog(BaseDialog):
    """
    Tryby:
    - 'qp' : wizualizacja QP (codecview=qp=1 + export_side_data)
    - 'mv' : wektory ruchu (codecview=mv=pf+bf+bb)
    """

    def __init__(self, parent=None, mode="mv"):
        self.mode = mode
        titles = {
            "qp": "Wizualizacja wartości QP",
            "mv": "Wektory ruchu (codecview)",
        }
        super().__init__(parent, title=titles.get(mode, "Debug"))

    def build_specific(self):
        if self.mode == "qp":
            self._build_qp()
        else:
            self._build_mv()

        self.add_output_file_row(
            "Plik wyjściowy:",
            "Wideo (*.mp4 *.mkv *.avi);;Wszystkie (*)"
        )
        self.add_run_buttons()

    # ------------------------------------------------------------------
    # Tryb QP
    # ------------------------------------------------------------------
    def _build_qp(self):
        box = QGroupBox("Opcje wizualizacji QP")
        form = QFormLayout(box)

        self.combo_outcodec = QComboBox()
        self.combo_outcodec.addItems(["libx264", "mpeg4", "libx265"])
        form.addRow("Kodek wyjściowy:", self.combo_outcodec)

        self.spin_crf = QSpinBox()
        self.spin_crf.setRange(0, 51)
        self.spin_crf.setValue(23)
        form.addRow("CRF:", self.spin_crf)

        info = QLabel(
            "<i>Wizualizacja QP dla H.264 wymaga FFmpeg zawierającego "
            "poprawkę z czerwca 2025. W standardowym FFmpeg 7.1.1 "
            "nakładka QP może się nie pojawić.</i>"
        )
        info.setWordWrap(True)
        form.addRow(info)

        self.layout.addWidget(box)

    def _command_qp(self, ffmpeg_path: str, in_file: str, out_file: str) -> list:
        """Buduje polecenie dla trybu QP."""
        return [
            ffmpeg_path, "-y",
            "-export_side_data", "4",   # eksport tabeli QP
            "-i", in_file,
            "-vf", "codecview=qp=1",
            "-c:v", self.combo_outcodec.currentText(),
            "-crf", str(self.spin_crf.value()),
            out_file,
        ]

    # ------------------------------------------------------------------
    # Tryb MV (wektory ruchu)
    # ------------------------------------------------------------------
    def _build_mv(self):
        box = QGroupBox("Wektory ruchu")
        form = QFormLayout(box)

        self.chk_pf = QCheckBox("P-klatki: predykcja w przód (pf)")
        self.chk_bf = QCheckBox("B-klatki: predykcja w przód (bf)")
        self.chk_bb = QCheckBox("B-klatki: predykcja w tył (bb)")
        self.chk_pf.setChecked(True)
        self.chk_bf.setChecked(True)
        self.chk_bb.setChecked(True)

        form.addRow(self.chk_pf)
        form.addRow(self.chk_bf)
        form.addRow(self.chk_bb)

        info = QLabel(
            "<i>Działa tylko z kodekami eksportującymi MVS. "
            "H.264 zazwyczaj to obsługuje.</i>"
        )
        info.setWordWrap(True)
        form.addRow(info)

        self.layout.addWidget(box)

    def _command_mv(self, ffmpeg_path: str, in_file: str, out_file: str) -> list:
        """Buduje polecenie dla trybu wektorów ruchu."""
        opts = []
        if self.chk_pf.isChecked():
            opts.append("pf")
        if self.chk_bf.isChecked():
            opts.append("bf")
        if self.chk_bb.isChecked():
            opts.append("bb")
        mv = "+".join(opts) if opts else "pf"

        return [
            ffmpeg_path, "-y",
            "-flags2", "+export_mvs",
            "-i", in_file,
            "-vf", f"codecview=mv={mv}",
            out_file,
        ]

    # ------------------------------------------------------------------
    # Wspólne
    # ------------------------------------------------------------------
    def get_command(self, ffmpeg_path: str) -> list:
        in_file = self.input_files[0]
        out_file = self.output_path
        if not os.path.splitext(out_file)[1]:
            out_file += ".mp4"

        if self.mode == "qp":
            return self._command_qp(ffmpeg_path, in_file, out_file)
        return self._command_mv(ffmpeg_path, in_file, out_file)