"""Launcher for GF Editor GUI (runs package from src)."""
import sys
from pathlib import Path

if __name__ == '__main__':
    # ensure src is on path so modules in src/ can be imported directly
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
    import gui
    gui.run_gui()
