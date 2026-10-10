# Okno konwersji kontenerów z presetami jakości i kodekami.

import os
from PyQt5.QtWidgets import (
    QFormLayout, QComboBox, QCheckBox, QGroupBox, QVBoxLayout
)
from .base import BaseDialog
from presets import (
    QUALITY_PRESETS, RESOLUTION_PRESETS, FPS_PRESETS,
    VIDEO_CODECS, AUDIO_CODECS, AUDIO_BITRATES
)


class ConvertDialog(BaseDialog):
    # Mapowanie formatu docelowego: (rozszerzenie, kodek wideo, kodek audio).
    FORMATS = {
        "mp4":  ("mp4",  "libx264",   "aac"),
        "avi":  ("avi",  "libx264",   "aac"),
        "mov":  ("mov",  "libx264",   "aac"),
        "mkv":  ("mkv",  "libx264",   "aac"),
        "webm": ("webm", "libvpx-vp9","libopus"),
        "ts":   ("ts",   "libx264",   "aac"),
        "flv":  ("flv",  "flv",       "mp3"),
        "wmv":  ("wmv",  "wmv2",      "wmav2"),
        "gif":  ("gif",  "gif",       None),
    }

    def __init__(self, parent=None, target_format="mp4"):
        self.target_format = target_format
        super().__init__(parent, title=f"Konwersja do .{target_format}", allow_multiple=True)

    def build_specific(self):
        # --- Grupa: kodeki ---
        box_codec = QGroupBox("Kodeki")
        fc = QFormLayout(box_codec)

        self.combo_vcodec = QComboBox()
        for name in VIDEO_CODECS:
            self.combo_vcodec.addItem(name)
        default_v = self.FORMATS[self.target_format][1]
        for i, c in enumerate(VIDEO_CODECS.values()):
            if c == default_v:
                self.combo_vcodec.setCurrentIndex(i)
                break
        fc.addRow("Kodek wideo:", self.combo_vcodec)

        self.combo_acodec = QComboBox()
        for name in AUDIO_CODECS:
            self.combo_acodec.addItem(name)
        default_a = self.FORMATS[self.target_format][2]
        for i, c in enumerate(AUDIO_CODECS.values()):
            if c == default_a:
                self.combo_acodec.setCurrentIndex(i)
                break
        fc.addRow("Kodek audio:", self.combo_acodec)

        self.combo_abitrate = QComboBox()
        for name in AUDIO_BITRATES:
            self.combo_abitrate.addItem(name)
        self.combo_abitrate.setCurrentIndex(2)  # 128k
        fc.addRow("Bitrate audio:", self.combo_abitrate)

        self.layout.addWidget(box_codec)

        # --- Grupa: jakość ---
        box_q = QGroupBox("Jakość obrazu")
        fq = QFormLayout(box_q)

        self.combo_quality = QComboBox()
        for name in QUALITY_PRESETS:
            self.combo_quality.addItem(name)
        self.combo_quality.setCurrentIndex(3)  # Standardowa CRF 23
        fq.addRow("Preset jakości:", self.combo_quality)

        self.combo_res = QComboBox()
        for name in RESOLUTION_PRESETS:
            self.combo_res.addItem(name)
        fq.addRow("Rozdzielczość:", self.combo_res)

        self.combo_fps = QComboBox()
        for name in FPS_PRESETS:
            self.combo_fps.addItem(name)
        fq.addRow("Klatki na sekundę:", self.combo_fps)
        self.layout.addWidget(box_q)

        # --- Grupa: opcje dodatkowe ---
        box_e = QGroupBox("Opcje dodatkowe")
        ve = QVBoxLayout(box_e)
        self.chk_copy = QCheckBox("Kopiuj strumienie bez rekompresji (-c copy)")
        ve.addWidget(self.chk_copy)
        self.chk_faststart = QCheckBox("MP4: szybki start (faststart)")
        self.chk_faststart.setChecked(self.target_format == "mp4")
        ve.addWidget(self.chk_faststart)
        self.chk_noaudio = QCheckBox("Usuń ścieżkę audio (-an)")
        ve.addWidget(self.chk_noaudio)
        self.chk_novideo = QCheckBox("Usuń ścieżkę wideo (-vn)")
        ve.addWidget(self.chk_novideo)
        self.chk_overwrite = QCheckBox("Nadpisz istniejące pliki (-y)")
        self.chk_overwrite.setChecked(True)
        ve.addWidget(self.chk_overwrite)
        self.layout.addWidget(box_e)

        self.add_output_dir_row("Katalog docelowy:")
        self.add_run_buttons()

    def _make_output_name(self, input_file: str, ext: str) -> str:
        """Buduje ścieżkę pliku wyjściowego w katalogu docelowym."""
        base = os.path.splitext(os.path.basename(input_file))[0]
        out = self.output_path
        if out.lower().endswith("." + ext):
            return out
        if not os.path.exists(out):
            os.makedirs(out, exist_ok=True)
        return os.path.join(out, f"{base}.{ext}")

    def get_command(self, ffmpeg_path: str) -> list:
        """Buduje polecenie ffmpeg dla pierwszego pliku wejściowego."""
        ext = self.FORMATS[self.target_format][0]
        in_file = self.input_files[0]
        out_file = self._make_output_name(in_file, ext)

        cmd = [ffmpeg_path]
        cmd.append("-y" if self.chk_overwrite.isChecked() else "-n")
        cmd += ["-i", in_file]

        if self.chk_copy.isChecked():
            cmd += ["-c", "copy"]
        else:
            # Wideo
            if self.chk_novideo.isChecked():
                cmd += ["-vn"]
            else:
                vcodec = VIDEO_CODECS[self.combo_vcodec.currentText()]
                cmd += ["-c:v", vcodec]
                q = QUALITY_PRESETS[self.combo_quality.currentText()]
                if vcodec not in ("copy", "gif"):
                    cmd += ["-crf", q["crf"], "-preset", q["preset"]]
                res = RESOLUTION_PRESETS[self.combo_res.currentText()]
                if res:
                    cmd += ["-vf", f"scale={res}"]
                fps = FPS_PRESETS[self.combo_fps.currentText()]
                if fps:
                    cmd += ["-r", str(fps)]

            # Audio
            if self.chk_noaudio.isChecked():
                cmd += ["-an"]
            else:
                acodec = AUDIO_CODECS[self.combo_acodec.currentText()]
                if acodec is None:
                    cmd += ["-an"]
                elif acodec == "copy":
                    cmd += ["-c:a", "copy"]
                else:
                    cmd += ["-c:a", acodec]
                    ab = AUDIO_BITRATES[self.combo_abitrate.currentText()]
                    if ab:
                        cmd += ["-b:a", ab]

        if self.target_format == "mp4" and self.chk_faststart.isChecked():
            cmd += ["-movflags", "+faststart"]

        cmd.append(out_file)
        return cmd