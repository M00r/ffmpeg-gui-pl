# Widżet kolejki zadań z możliwością pauzy, stopu i zmiany kolejności.

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QProgressBar,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from job_queue import JobQueueWorker


class JobQueueWidget(QWidget):
    log_line = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["#", "Zadanie", "Postęp", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table, 1)

        row = QHBoxLayout()
        btn_up = QPushButton("▲ W górę")
        btn_up.clicked.connect(lambda: self._move(-1))
        btn_down = QPushButton("▼ W dół")
        btn_down.clicked.connect(lambda: self._move(1))
        btn_del = QPushButton("Usuń")
        btn_del.clicked.connect(self._remove)
        btn_clear = QPushButton("Wyczyść")
        btn_clear.clicked.connect(self.clear)
        row.addWidget(btn_up)
        row.addWidget(btn_down)
        row.addWidget(btn_del)
        row.addWidget(btn_clear)
        row.addStretch()

        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start_queue)
        self.btn_pause = QPushButton("Pauza")
        self.btn_pause.clicked.connect(self.pause_queue)
        self.btn_pause.setEnabled(False)
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_queue)
        self.btn_stop.setEnabled(False)
        row.addWidget(self.btn_start)
        row.addWidget(self.btn_pause)
        row.addWidget(self.btn_stop)
        layout.addLayout(row)

        self.worker = None

    def add_job(self, label: str, cmd: list, duration: float = 0.0):
        """Dodaje nowe zadanie do kolejki."""
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(str(r + 1)))
        it = QTableWidgetItem(label)
        it.setData(Qt.UserRole, {"cmd": cmd, "duration": duration})
        self.table.setItem(r, 1, it)
        bar = QProgressBar()
        bar.setRange(0, 100)
        self.table.setCellWidget(r, 2, bar)
        self.table.setItem(r, 3, QTableWidgetItem("Oczekuje"))

    def _renumber(self):
        for r in range(self.table.rowCount()):
            self.table.item(r, 0).setText(str(r + 1))

    def _row_data(self, row: int) -> dict:
        item = self.table.item(row, 1)
        return {
            "label": item.text(),
            "payload": item.data(Qt.UserRole),
            "status": self.table.item(row, 3).text(),
        }

    def _set_row_data(self, row: int, data: dict):
        self.table.item(row, 1).setText(data["label"])
        self.table.item(row, 1).setData(Qt.UserRole, data["payload"])
        self.table.item(row, 3).setText(data["status"])

    def _move(self, delta: int):
        """Przesuwa zaznaczone zadanie w górę/w dół."""
        r = self.table.currentRow()
        if r < 0:
            return
        nr = r + delta
        if nr < 0 or nr >= self.table.rowCount():
            return
        a = self._row_data(r)
        b = self._row_data(nr)
        self._set_row_data(r, b)
        self._set_row_data(nr, a)
        self.table.setCurrentCell(nr, 1)
        self._renumber()

    def _remove(self):
        """Usuwa zaznaczone zadania."""
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)
        self._renumber()

    def clear(self):
        """Czyści całą kolejkę (jeśli nie jest uruchomiona)."""
        if self._is_running():
            QMessageBox.warning(self, "Zajęte", "Zatrzymaj kolejkę przed czyszczeniem.")
            return
        self.table.setRowCount(0)

    def _is_running(self):
        return self.worker is not None and self.worker.isRunning()

    def _collect_jobs(self) -> list:
        jobs = []
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 1)
            payload = it.data(Qt.UserRole) or {}
            jobs.append({
                "label": it.text(),
                "cmd": payload.get("cmd", []),
                "duration": payload.get("duration", 0.0),
            })
        return jobs

    def start_queue(self):
        """Uruchamia przetwarzanie kolejki."""
        jobs = self._collect_jobs()
        if not jobs or self._is_running():
            return
        for r in range(self.table.rowCount()):
            self.table.item(r, 3).setText("Oczekuje")
            w = self.table.cellWidget(r, 2)
            if isinstance(w, QProgressBar):
                w.setValue(0)

        self.worker = JobQueueWorker(jobs)
        self.worker.job_started.connect(self._on_start)
        self.worker.job_progress.connect(self._on_progress)
        self.worker.job_log.connect(self._on_log)
        self.worker.job_finished.connect(self._on_finished)
        self.worker.queue_finished.connect(self._on_all_done)
        self.worker.error.connect(lambda e: self.log_line.emit("BŁĄD: " + e))
        self.worker.start()
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)

    def pause_queue(self):
        """Wstrzymuje lub wznawia kolejkę."""
        if self.worker and self.worker.isRunning():
            if self.btn_pause.text() == "Pauza":
                self.worker.pause()
                self.btn_pause.setText("Wznów")
            else:
                self.worker.resume()
                self.btn_pause.setText("Pauza")

    def stop_queue(self):
        """Zatrzymuje całą kolejkę."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()

    def _on_start(self, idx, label):
        self.table.item(idx, 3).setText("W toku")
        self.table.item(idx, 3).setForeground(QColor("#0e639c"))
        self.log_line.emit(f">>> [{idx+1}] {label}")

    def _on_progress(self, idx, pct):
        w = self.table.cellWidget(idx, 2)
        if isinstance(w, QProgressBar):
            w.setValue(int(pct))

    def _on_log(self, idx, line):
        self.log_line.emit(f"[{idx+1}] {line}")

    def _on_finished(self, idx, code):
        it = self.table.item(idx, 3)
        if code == 0:
            it.setText("OK")
            it.setForeground(QColor("#2e7d32"))
            w = self.table.cellWidget(idx, 2)
            if isinstance(w, QProgressBar):
                w.setValue(100)
        else:
            it.setText(f"Błąd ({code})")
            it.setForeground(QColor("#c62828"))
        self.log_line.emit(f"<<< [{idx+1}] kod {code}")

    def _on_all_done(self):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("Pauza")
        self.btn_stop.setEnabled(False)
        self.log_line.emit("=== Kolejka zakończona ===")