# Uruchamianie ffplay (odtwarzacz) w osobnym wątku.

import subprocess
from PyQt5.QtCore import QThread, pyqtSignal


class FFplayWorker(QThread):
    """Uruchamia ffplay i przekazuje jego wyjście do logu."""
    output = pyqtSignal(str)
    finished_ok = pyqtSignal(int)

    def __init__(self, command: list):
        super().__init__()
        self.command = command
        self._proc = None

    def run(self):
        try:
            self._proc = subprocess.Popen(
                self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, encoding="utf-8", errors="replace"
            )
            for line in self._proc.stdout:
                self.output.emit(line.rstrip())
            self._proc.wait()
            self.finished_ok.emit(self._proc.returncode)
        except FileNotFoundError:
            self.output.emit("Nie znaleziono ffplay.")
            self.finished_ok.emit(-1)
        except Exception as e:
            self.output.emit(f"Błąd ffplay: {e}")
            self.finished_ok.emit(-1)

    def stop(self):
        """Zatrzymuje odtwarzacz."""
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()