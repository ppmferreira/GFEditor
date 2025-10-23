import sys
from PySide6.QtWidgets import QApplication
sys.path.insert(0,'src')
from gui import MainWindow
app = QApplication([])
w = MainWindow()
print('Discovered modules:', w.modules)
app.quit()
