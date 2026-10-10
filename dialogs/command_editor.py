# Edytor poleceń FFmpeg — swobodne wpisywanie komend z szablonami.

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QLabel,
    QPushButton, QFileDialog, QMessageBox, QListWidget,
    QListWidgetItem, QSplitter, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ffmpeg_runner import FFmpegWorker


# Gotowe szablony poleceń.
COMMON_TEMPLATES = {
    "Konwersja MP4 → MKV (kopiuj)":
        "ffmpeg -y -i input.mp4 -c copy output.mkv",
    "Konwersja do H.264 CRF 23":
        "ffmpeg -y -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac output.mp4",
    "Wyodrębnij klatki I":
        "ffmpeg -y -i input.mp4 -vf \"select='eq(pict_type,I)'\" -vsync vfr klatka_%05d.png",
    "Wyodrębnij klatki P":
        "ffmpeg -y -i input.mp4 -vf \"select='eq(pict_type,P)'\" -vsync vfr klatka_%05d.png",
    "Wyodrębnij klatki B":
        "ffmpeg -y -i input.mp4 -vf \"select='eq(pict_type,B)'\" -vsync vfr klatka_%05d.png",
    "Co 1 sekundę":
        "ffmpeg -y -i input.mp4 -vf fps=1 klatka_%05d.png",
    "Wizualizacja makrobloków":
        "ffmpeg -y -debug vis_mb_type -i input.mp4 -c:v libx264 -crf 23 out.mp4",
    "Wizualizacja QP":
        "ffmpeg -y -debug vis_qp -i input.mp4 -c:v libx264 -crf 23 out.mp4",
    "Wektory ruchu":
        "ffmpeg -y -flags2 +export_mvs -i input.mp4 -vf codecview=mv=pf+bf+bb out.mp4",
    "Zmiana rozdzielczości do 720p":
        "ffmpeg -y -i input.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 output.mp4",
    "Wyciągnij audio (MP3)":
        "ffmpeg -y -i input.mp4 -vn -c:a libmp3lame -b:a 192k audio.mp3",
    "Wyciągnij audio (bez rekompresji)":
        "ffmpeg -y -i input.mp4 -vn -c:a copy audio.m4a",
    "Przytnij od 00:00:10 do 00:00:30":
        "ffmpeg -y -ss 00:00:10 -to 00:00:30 -i input.mp4 -c copy wycinek.mp4",
    "Łączenie plików (lista.txt)":
        "ffmpeg -y -f concat -safe 0 -i lista.txt -c copy scalone.mp4",
    "GIF z fragmentu":
        "ffmpeg -y -ss 00:00:05 -t 3 -i input.mp4 -vf \"fps=12,scale=480:-1\" anim.gif",
}


class CommandEditorDialog(QDialog):
    def __init__(self, parent=None, ffmpeg_path: str = "ffmpeg",
                 ffprobe_path: str = "ffprobe"):
        super().__init__(parent)
        self.setWindowTitle("Edytor poleceń FFmpeg")
        self.resize(920, 640)
        self.ffmpeg_path = ffmpeg_path or "ffmpeg"
        self.ffprobe_path = ffprobe_path or "ffprobe"
        self.worker = None

        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, 1)

        # --- Lewa: szablony ---
        left = QGroupBox("Szablony")
        lv = QVBoxLayout(left)
        self.list_t = QListWidget()
        for name in COMMON_TEMPLATES:
            QListWidgetItem(name, self.list_t)
        self.list_t.itemDoubleClicked.connect(self.insert_template)
        lv.addWidget(self.list_t, 1)
        btn_ins = QPushButton("Wstaw do edytora")
        btn_ins.clicked.connect(lambda: self.insert_template(self.list_t.currentItem()))
        lv.addWidget(btn_ins)
        splitter.addWidget(left)

        # --- Prawa: edytor + log ---
        right = QGroupBox("Komenda")
        rv = QVBoxLayout(right)
        self.edit = QPlainTextEdit()
        f = QFont("Consolas")
        f.setStyleHint(QFont.Monospace)
        self.edit.setFont(f)
        self.edit.setPlainText(
            f"{self.ffmpeg_path} -y -i input.mp4 -c:v libx264 -crf 23 -c:a aac output.mp4"
        )
        rv.addWidget(self.edit, 1)

        row = QHBoxLayout()
        btn_ff = QPushButton("Wstaw ścieżkę ffmpeg")
        btn_ff.clicked.connect(self.insert_ffmpeg)
        btn_in = QPushButton("Wstaw plik wejściowy…")
        btn_in.clicked.connect(self.insert_input)
        btn_out = QPushButton("Wstaw plik wyjściowy…")
        btn_out.clicked.connect(self.insert_output)
        row.addWidget(btn_ff)
        row.addWidget(btn_in)
        row.addWidget(btn_out)
        row.addStretch()
        rv.addLayout(row)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(f)
        self.log.setMaximumHeight(200)
        rv.addWidget(QLabel("Wyjście FFmpeg:"))
        rv.addWidget(self.log)

        run_row = QHBoxLayout()
        self.btn_run = QPushButton("Uruchom")
        self.btn_run.clicked.connect(self.run_command)
        self.btn_stop = QPushButton("Zatrzymaj")
        self.btn_stop.clicked.connect(self.stop_command)
        self.btn_stop.setEnabled(False)
        btn_close = QPushButton("Zamknij")
        btn_close.clicked.connect(self.reject)
        run_row.addWidget(self.btn_run)
        run_row.addWidget(self.btn_stop)
        run_row.addStretch()
        run_row.addWidget(btn_close)
        rv.addLayout(run_row)

        splitter.addWidget(right)
        splitter.setSizes([260, 660])

    def insert_template(self, item):
        """Wstawia szablon do edytora, podmieniając 'ffmpeg' na ścieżkę."""
        if not item:
            return
        text = COMMON_TEMPLATES[item.text()]
        text = text.replace("ffmpeg", self.ffmpeg_path, 1)
        self.edit.setPlainText(text)

    def insert_ffmpeg(self):
        self.edit.insertPlainText(" " + self.ffmpeg_path + " ")

    def insert_input(self):
        p, _ = QFileDialog.getOpenFileName(self, "Plik wejściowy", "", "Wszystkie (*)")
        if p:
            self.edit.insertPlainText(f' "{p}" ')

    def insert_output(self):
        p, _ = QFileDialog.getSaveFileName(self, "Plik wyjściowy", "", "Wszystkie (*)")
        if p:
            self.edit.insertPlainText(f' "{p}" ')

    def _parse_command(self) -> list:
        """Dzieli tekst na argumenty z obsługą cudzysłowów."""
        import shlex
        text = self.edit.toPlainText().strip().replace("\n", " ")
        try:
            return [c.strip('"') for c in shlex.split(text, posix=False)]
        except ValueError:
            return [c.strip('"') for c in text.split()]

    def run_command(self):
        """Uruchamia polecenie w tle."""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Zajęte", "Poczekaj na zakończenie.")
            return
        cmd = self._parse_command()
        if not cmd:
            QMessageBox.warning(self, "Puste", "Wpisz komendę.")
            return
        self.log.clear()
        self.worker = FFmpegWorker(cmd, total_duration=0.0)
        self.worker.progress.connect(self.log.appendPlainText)
        self.worker.finished_ok.connect(self._done)
        self.worker.error.connect(lambda e: self.log.appendPlainText("BŁĄD: " + e))
        self.worker.start()
        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def stop_command(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log.appendPlainText(">>> Zatrzymano.")

    def _done(self, code):
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log.appendPlainText(f"=== Zakończono (kod {code}) ===")