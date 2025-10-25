from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path

# Make src/ available on sys.path similar to launch_gfeditor_gui.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
import gui

# Create app and main window, process events briefly and exit.
# This is a lightweight sanity check to ensure QSplitter warnings are gone.
app = QApplication([])
win = gui.MainWindow()
app.processEvents()
print('GUI init OK')
win.close()
app.quit()
