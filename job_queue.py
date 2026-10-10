# Kolejka zadań — wykonuje polecenia jedno po drugim z możliwością pauzy i stopu.

import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

from ffmpeg_runner import TIME_RE, _hms_to_seconds


class JobQueueWorker(QThread):
    """Wątek przetwarzający listę zadań sekwencyjnie."""
    job_started = pyqtSignal(int, str)          # (indeks, etykieta)
    job_progress = pyqtSignal(int, float)       # (indeks, procent)
    job_log = pyqtSignal(int, str)              # (indeks, linia logu)
    job_finished = pyqtSignal(int, int)         # (indeks, kod wyjścia)
    queue_finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, jobs: list):
        """jobs: lista słowników {label, cmd, duration}."""
        super().__init__()
        self.jobs = jobs
        self._stop = False
        self._pause = False
        self._proc = None

    def run(self):
        for idx, job in enumerate(self.jobs):
            if self._stop:
                break
            # Obsługa pauzy między zadaniami.
            while self._pause and not self._stop:
                self.msleep(150)
            if self._stop:
                break

            self.job_started.emit(idx, job.get("label", f"Zadanie {idx+1}"))
            cmd = job["cmd"]
            dur = job.get("duration", 0.0) or 0.0
            try:
                self._proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    universal_newlines=True, encoding="utf-8",
                    errors="replace", bufsize=1
                )
                for line in self._proc.stdout:
                    if self._stop:
                        self._proc.terminate()
                        break
                    # Pauza w trakcie zadania.
                    while self._pause and not self._stop:
                        self.msleep(150)
                    self.job_log.emit(idx, line.rstrip())
                    if dur > 0:
                        m = TIME_RE.search(line)
                        if m:
                            cur = _hms_to_seconds(*m.groups())
                            pct = min(100.0, cur / dur * 100.0)
                            self.job_progress.emit(idx, pct)
                self._proc.wait()
                self.job_finished.emit(idx, self._proc.returncode)
            except Exception as e:
                self.error.emit(str(e))
                self.job_finished.emit(idx, -1)
        self.queue_finished.emit()

    def stop(self):
        """Zatrzymuje całą kolejkę."""
        self._stop = True
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()

    def pause(self):
        """Wstrzymuje kolejkę."""
        self._pause = True

    def resume(self):
        """Wznawia kolejkę."""
        self._pause = False