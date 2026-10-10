# Uruchamianie ffmpeg w osobnym wątku z raportowaniem postępu.

import subprocess
import re
from PyQt5.QtCore import QThread, pyqtSignal


# Wzorce do parsowania postępu i czasu trwania pliku.
TIME_RE = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)")


def _hms_to_seconds(h, m, s):
    """Zamienia godziny:minuty:sekundy na sekundy."""
    return int(h) * 3600 + int(m) * 60 + float(s)


def get_duration(ffprobe: str, input_file: str) -> float:
    """Zwraca czas trwania pliku w sekundach (0 jeśli nieznany)."""
    if not ffprobe:
        return 0.0
    try:
        r = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", input_file],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        return float(r.stdout.strip()) if r.stdout.strip() else 0.0
    except Exception:
        return 0.0


def probe_video_info(ffprobe_path: str, input_file: str) -> str:
    """Zwraca pełne informacje o pliku (ffprobe -show_format -show_streams)."""
    if not ffprobe_path:
        return "ffprobe niedostępny."
    try:
        r = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_format", "-show_streams", input_file],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        return r.stdout
    except Exception as e:
        return f"Błąd ffprobe: {e}"


def build_frame_type_filter(frame_type: str) -> str:
    """Buduje filtr select dla klatek I/P/B."""
    return f"select='eq(pict_type,{frame_type.upper()})'"


def build_interval_filter(mode: str, value: int) -> str:
    """Buduje filtr interwału — 'frames' lub 'seconds'."""
    if mode == "frames":
        return f"select='not(mod(n\\,{value}))'"
    return f"fps=1/{value}"


class FFmpegWorker(QThread):
    """Wątek uruchamiający pojedyncze polecenie ffmpeg."""
    progress = pyqtSignal(str)          # surowa linia logu
    percent = pyqtSignal(float)         # postęp 0..100 lub -1
    finished_ok = pyqtSignal(int)       # kod wyjścia
    error = pyqtSignal(str)             # komunikat błędu

    def __init__(self, command: list, total_duration: float = 0.0):
        super().__init__()
        self.command = command
        self.total_duration = total_duration
        self._stop = False

    def run(self):
        try:
            self.progress.emit("$ " + " ".join(self.command))
            p = subprocess.Popen(
                self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, encoding="utf-8",
                errors="replace", bufsize=1
            )
            for line in p.stdout:
                if self._stop:
                    p.terminate()
                    break
                self.progress.emit(line.rstrip())
                if self.total_duration > 0:
                    m = TIME_RE.search(line)
                    if m:
                        cur = _hms_to_seconds(*m.groups())
                        pct = min(100.0, cur / self.total_duration * 100.0)
                        self.percent.emit(pct)
            p.wait()
            self.finished_ok.emit(p.returncode)
        except FileNotFoundError:
            self.error.emit("Nie znaleziono ffmpeg.")
        except Exception as e:
            self.error.emit(f"Błąd: {e}")

    def stop(self):
        """Zgłasza żądanie zatrzymania procesu."""
        self._stop = True