from pathlib import Path
from typing import List

def list_entries(lib_path: Path) -> List[str]:
    data_dir = lib_path / 'data' / 'db'
    if not data_dir.exists():
        return []
    return [p.name for p in data_dir.glob('*Shop*.ini')]


def panel_widget(parent):
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
    w = QWidget(parent)
    l = QVBoxLayout()
    l.addWidget(QLabel('Shops module - placeholder'))
    w.setLayout(l)
    return w
