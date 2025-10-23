from pathlib import Path
from typing import List

from PySide6.QtWidgets import QLabel


def list_entries(lib_path: Path) -> List[str]:
    data_dir = lib_path / 'data' / 'serverdb'
    if not data_dir.exists():
        return []
    return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


def panel_widget(parent):
    # Minimal clean panel used while we reimplement the full editor.
    return QLabel('Items panel (clean)')
