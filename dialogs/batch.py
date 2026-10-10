# Okno przetwarzania wsadowego — wiele plików, jedna operacja.

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QFileDialog, QListWidget, QListWidgetItem,
    QAbstractItemView, QGroupBox, QFormLayout, QSpinBox,
    QLineEdit
)


class BatchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Przetwarzanie wsadowe")
        self.setMinimumWidth(640)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Pliki do przetworzenia:"))
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.list, 1)

        row = QHBoxLayout()
        btn_add = QPushButton("Dodaj pliki…")
        btn_add.clicked.connect(self.add_files)
        btn_del = QPushButton("Usuń zaznaczone")
        btn_del.clicked.connect(self.remove_selected)
        btn_clear = QPushButton("Wyczyść")
        btn_clear.clicked.connect(self.list.clear)
        row.addWidget(btn_add)
        row.addWidget(btn_del)
        row.addWidget(btn_clear)
        row.addStretch()
        layout.addLayout(row)

        box = QGroupBox("Operacja")
        form = QFormLayout(box)
        self.combo_op = QComboBox()
        self.combo_op.addItems([
            "Konwertuj do .mp4",
            "Konwertuj do .mkv",
            "Konwertuj do .webm",
            "Wyodrębnij klatki I",
            "Wyodrębnij klatki P",
            "Wyodrębnij klatki B",
        ])
        form.addRow("Operacja:", self.combo_op)

        self.combo_out = QComboBox()
        self.combo_out.addItems(["PNG", "JPG"])
        form.addRow("Format klatek:", self.combo_out)

        self.spin_parallel = QSpinBox()
        self.spin_parallel.setRange(1, 4)
        form.addRow("Równoległość:", self.spin_parallel)
        layout.addWidget(box)

        row_out = QHBoxLayout()
        self.edit_out = QLineEdit()
        self.edit_out.setReadOnly(True)
        btn_out = QPushButton("Katalog docelowy…")
        btn_out.clicked.connect(self.choose_out)
        row_out.addWidget(QLabel("Wyjście:"))
        row_out.addWidget(self.edit_out, 1)
        row_out.addWidget(btn_out)
        layout.addLayout(row_out)

        btns = QHBoxLayout()
        btn_run = QPushButton("Uruchom")
        btn_run.clicked.connect(self.accept)
        btn_cancel = QPushButton("Anuluj")
        btn_cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(btn_run)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def add_files(self):
        """Dodaje wiele plików do listy."""
        filt = "Wideo (*.mp4 *.mkv *.avi *.mov *.webm *.ts *.flv);;Wszystkie (*)"
        paths, _ = QFileDialog.getOpenFileNames(self, "Wybierz pliki", "", filt)
        for p in paths:
            QListWidgetItem(p, self.list)

    def remove_selected(self):
        """Usuwa zaznaczone pliki."""
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))

    def choose_out(self):
        """Wybór katalogu docelowego."""
        d = QFileDialog.getExistingDirectory(self, "Katalog docelowy")
        if d:
            self.edit_out.setText(d)

    def get_tasks(self):
        """Zwraca (pliki, katalog_wyjściowy, operacja)."""
        files = [self.list.item(i).text() for i in range(self.list.count())]
        return files, self.edit_out.text(), self.combo_op.currentText()