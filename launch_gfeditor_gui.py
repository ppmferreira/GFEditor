"""Launcher for GF Editor GUI (runs package from src)."""
import sys
from pathlib import Path

if __name__ == '__main__':
    # ensure src is on path so package imports work
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
    from gfeditor.gui import run_gui
    run_gui()
