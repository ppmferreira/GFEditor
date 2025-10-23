from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QSplitter, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QFileDialog, QMessageBox
)

import gfio as _gfio


def list_entries(lib_path: Path) -> List[str]:
    data_dir = lib_path / 'data' / 'serverdb'
    if not data_dir.exists():
        return []
    return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


def panel_widget(parent):
    lib_path = Path.cwd() / 'Lib'

    container = QWidget(parent)
    splitter = QSplitter(container)

    left = QVBoxLayout()
    list_w = QListWidget()
    for name in list_entries(lib_path):
        list_w.addItem(name)

    left_container = QWidget()
    left_container.setObjectName('itemsLeftPanel')
    left_layout = QVBoxLayout()
    left_layout.addWidget(list_w)
    left_container.setLayout(left_layout)

    table = QTableWidget()

    open_btn = QPushButton('Open')
    save_btn = QPushButton('Save')

    def open_selected():
        item = list_w.currentItem()
        if not item:
            return
        path = lib_path / 'data' / 'serverdb' / item.text()
        rows = _gfio.read_pipe_file(path, encoding='big5', limit=2000)
        table.clear()
        if not rows:
            return
        max_cols = max(len(r) for r in rows)
        table.setColumnCount(max_cols)
        table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            for j in range(max_cols):
                val = r[j] if j < len(r) else ''
                table.setItem(i, j, QTableWidgetItem(val))

    def save_table():
        item = list_w.currentItem()
        if not item:
            QMessageBox.warning(container, 'No file', 'No file selected')
            return
        path = lib_path / 'data' / 'serverdb' / item.text()
        rows = []
        for i in range(table.rowCount()):
            row = []
            for j in range(table.columnCount()):
                it = table.item(i, j)
                row.append(it.text() if it else '')
            rows.append(row)
        Path(str(path) + '.bak').write_text('backup', encoding='utf-8')
        _gfio.write_pipe_file(path, rows, encoding='big5')
        QMessageBox.information(container, 'Saved', f'{item.text()} saved')

    open_btn.clicked.connect(open_selected)
    save_btn.clicked.connect(save_table)

    right_container = QWidget()
    right_container.setObjectName('itemsRightPanel')
    right_layout = QVBoxLayout()
    btns = QHBoxLayout()
    btns.addWidget(open_btn)
    btns.addWidget(save_btn)
    right_layout.addLayout(btns)
    right_layout.addWidget(table)
    right_container.setLayout(right_layout)

    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    main_layout = QVBoxLayout()
    main_layout.addWidget(splitter)
    container.setLayout(main_layout)
    return container
