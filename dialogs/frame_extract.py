# Okna wyodrębniania klatek: według typu, interwału, zakresu, pojedynczej.

import os
from PyQt5.QtWidgets import (
    QFormLayout, QComboBox, QSpinBox, QTimeEdit, QRadioButton,
    QButtonGroup, QCheckBox, QGroupBox
)
from PyQt5.QtCore import QTime
from .base import BaseDialog


class FrameTypeDialog(BaseDialog):
    """Wyodrębnianie klatek I, P lub B."""

    def __init__(self, parent=None, frame_type="I"):
        self.frame_type = frame_type.upper()
        super().__init__(parent, title=f"Wyodrębnij klatki {self.frame_type}",
                         allow_multiple=True)

    def build_specific(self):
        box = QGroupBox("Opcje wyodrębniania")
        form = QFormLayout(box)
        self.combo_fmt = QComboBox()
        self.combo_fmt.addItems(["PNG", "JPG", "BMP"])
        form.addRow("Format obrazu:", self.combo_fmt)

        self.spin_quality = QSpinBox()
        self.spin_quality.setRange(1, 31)
        self.spin_quality.setValue(2)
        form.addRow("Jakość (JPG, 1=najlepsza):", self.spin_quality)

        # Tryb szybki ma sens tylko dla klatek I.
        self.chk_fast = QCheckBox("Tryb szybki (-skip_frame nokey)")
        if self.frame_type == "I":
            form.addRow(self.chk_fast)
        self.layout.addWidget(box)
        self.add_output_dir_row("Katalog docelowy:")
        self.add_run_buttons()

    def _ext(self):
        """Zwraca rozszerzenie pliku wynikowego."""
        return {"PNG": "png", "JPG": "jpg", "BMP": "bmp"}[self.combo_fmt.currentText()]

    def get_command(self, ffmpeg_path: str) -> list:
        in_file = self.input_files[0]
        base = os.path.splitext(os.path.basename(in_file))[0]
        out_dir = os.path.join(self.output_path, base)
        os.makedirs(out_dir, exist_ok=True)
        ext = self._ext()
        pattern = os.path.join(out_dir, f"{base}_{self.frame_type}_%05d.{ext}")

        cmd = [ffmpeg_path, "-y"]
        # Szybki tryb dla klatek I — pomija dekodowanie klatek niekluczowych.
        if self.frame_type == "I" and self.chk_fast.isChecked():
            cmd += ["-skip_frame", "nokey"]
        cmd += ["-i", in_file,
                "-vf", f"select='eq(pict_type,{self.frame_type})'",
                "-vsync", "vfr"]
        if ext in ("jpg", "jpeg"):
            cmd += ["-q:v", str(self.spin_quality.value())]
        cmd.append(pattern)
        return cmd


class IntervalDialog(BaseDialog):
    """Wyodrębnianie co N-tą klatkę lub co N sekund."""

    def __init__(self, parent=None):
        super().__init__(parent, title="Wyodrębnij klatki co N", allow_multiple=True)

    def build_specific(self):
        box = QGroupBox("Tryb interwału")
        form = QFormLayout(box)

        self.radio_frames = QRadioButton("Co N-tą klatkę")
        self.radio_seconds = QRadioButton("Co N sekund")
        self.radio_frames.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self.radio_frames)
        grp.addButton(self.radio_seconds)
        form.addRow(self.radio_frames)
        form.addRow(self.radio_seconds)

        self.spin = QSpinBox()
        self.spin.setRange(1, 100000)
        self.spin.setValue(10)
        form.addRow("Wartość N:", self.spin)

        self.combo_fmt = QComboBox()
        self.combo_fmt.addItems(["PNG", "JPG"])
        form.addRow("Format obrazu:", self.combo_fmt)
        self.layout.addWidget(box)
        self.add_output_dir_row("Katalog docelowy:")
        self.add_run_buttons()

    def get_command(self, ffmpeg_path: str) -> list:
        mode = "frames" if self.radio_frames.isChecked() else "seconds"
        in_file = self.input_files[0]
        base = os.path.splitext(os.path.basename(in_file))[0]
        out_dir = os.path.join(self.output_path, base)
        os.makedirs(out_dir, exist_ok=True)
        ext = "png" if self.combo_fmt.currentText() == "PNG" else "jpg"
        pattern = os.path.join(out_dir, f"{base}_%05d.{ext}")
        vf = (f"select='not(mod(n\\,{self.spin.value()}))'"
              if mode == "frames" else f"fps=1/{self.spin.value()}")
        return [ffmpeg_path, "-y", "-i", in_file, "-vf", vf,
                "-vsync", "vfr", pattern]


class RangeDialog(BaseDialog):
    """Wyodrębnianie klatek z zakresu czasu."""

    def __init__(self, parent=None):
        super().__init__(parent, title="Wyodrębnij klatki z zakresu czasu")

    def build_specific(self):
        box = QGroupBox("Zakres i częstotliwość")
        form = QFormLayout(box)
        self.time_start = QTimeEdit()
        self.time_start.setDisplayFormat("HH:mm:ss")
        self.time_start.setTime(QTime(0, 0, 0))
        form.addRow("Start:", self.time_start)

        self.time_end = QTimeEdit()
        self.time_end.setDisplayFormat("HH:mm:ss")
        self.time_end.setTime(QTime(0, 0, 30))
        form.addRow("Koniec:", self.time_end)

        self.spin_fps = QSpinBox()
        self.spin_fps.setRange(1, 60)
        self.spin_fps.setValue(1)
        form.addRow("Klatek na sekundę:", self.spin_fps)

        self.combo_fmt = QComboBox()
        self.combo_fmt.addItems(["PNG", "JPG"])
        form.addRow("Format obrazu:", self.combo_fmt)
        self.layout.addWidget(box)
        self.add_output_dir_row("Katalog docelowy:")
        self.add_run_buttons()

    def get_command(self, ffmpeg_path: str) -> list:
        in_file = self.input_files[0]
        base = os.path.splitext(os.path.basename(in_file))[0]
        out_dir = os.path.join(self.output_path, base)
        os.makedirs(out_dir, exist_ok=True)
        ext = "png" if self.combo_fmt.currentText() == "PNG" else "jpg"
        pattern = os.path.join(out_dir, f"{base}_%05d.{ext}")
        start = self.time_start.time().toString("HH:mm:ss")
        end = self.time_end.time().toString("HH:mm:ss")
        return [ffmpeg_path, "-y", "-ss", start, "-to", end, "-i", in_file,
                "-vf", f"fps={self.spin_fps.value()}", pattern]


class SingleFrameDialog(BaseDialog):
    """Wyodrębnianie jednej klatki — według czasu lub numeru."""

    def __init__(self, parent=None):
        super().__init__(parent, title="Wyodrębnij pojedynczą klatkę")

    def build_specific(self):
        box = QGroupBox("Tryb wyboru")
        form = QFormLayout(box)

        self.radio_time = QRadioButton("Według czasu")
        self.radio_num = QRadioButton("Według numeru klatki")
        self.radio_time.setChecked(True)
        grp = QButtonGroup(self)
        grp.addButton(self.radio_time)
        grp.addButton(self.radio_num)
        form.addRow(self.radio_time)
        form.addRow(self.radio_num)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss.zzz")
        form.addRow("Czas:", self.time_edit)

        self.spin_num = QSpinBox()
        self.spin_num.setMaximum(10_000_000)
        form.addRow("Numer klatki:", self.spin_num)
        self.layout.addWidget(box)
        self.add_output_file_row("Plik wyjściowy:", "PNG (*.png);;JPG (*.jpg)")
        self.add_run_buttons()

    def get_command(self, ffmpeg_path: str) -> list:
        out = self.output_path
        if not out.lower().endswith((".png", ".jpg")):
            out += ".png"
        if self.radio_time.isChecked():
            t = self.time_edit.time().toString("HH:mm:ss.zzz")
            return [ffmpeg_path, "-y", "-ss", t, "-i", self.input_files[0],
                    "-frames:v", "1", out]
        n = self.spin_num.value()
        return [ffmpeg_path, "-y", "-i", self.input_files[0],
                "-vf", f"select='eq(n\\,{n})'",
                "-vsync", "vfr", "-frames:v", "1", out]