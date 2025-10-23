"""Minimal GUI for GF Editor using PySide6.

This provides: open file, show first lines in a table, save (writes back raw pipe-delimited).
"""
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
)
import sys
from pathlib import Path
from .gfio import read_pipe_file, write_pipe_file


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GF Editor - Prototype')
        self.table = QTableWidget()
        open_btn = QPushButton('Open')
        save_btn = QPushButton('Save')
        open_btn.clicked.connect(self.open_file)
        save_btn.clicked.connect(self.save_file)
        btns = QHBoxLayout()
        btns.addWidget(open_btn)
        btns.addWidget(save_btn)
        layout = QVBoxLayout()
        layout.addLayout(btns)
        layout.addWidget(self.table)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.current_path = None
        self.rows = []

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open file', str(Path.cwd() / 'Lib'))
        if not path:
            return
        # ask encoding
        encoding = 'big5'  # for now, assume big5 for data files
        self.rows = read_pipe_file(path, encoding=encoding, limit=1000)
        self.current_path = path
        self.populate_table()

    def populate_table(self):
        if not self.rows:
            self.table.clear()
            return
        max_cols = max(len(r) for r in self.rows)
        self.table.setColumnCount(max_cols)
        self.table.setRowCount(len(self.rows))
        for i, row in enumerate(self.rows):
            for j in range(max_cols):
                val = row[j] if j < len(row) else ''
                self.table.setItem(i, j, QTableWidgetItem(val))

    def save_file(self):
        if not self.current_path:
            QMessageBox.warning(self, 'No file', 'No file opened')
            return
        # collect rows from table
        rows = []
        for i in range(self.table.rowCount()):
            row = []
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                row.append(item.text() if item else '')
            rows.append(row)
        # make backup
        Path(self.current_path + '.bak').write_text('backup', encoding='utf-8')
        write_pipe_file(self.current_path, rows, encoding='big5')
        QMessageBox.information(self, 'Saved', 'File saved (backup created)')


def run_gui():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(1000, 600)
    w.show()
    return app.exec()
