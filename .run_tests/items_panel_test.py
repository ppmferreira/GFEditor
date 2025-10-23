import sys
from PySide6.QtWidgets import QApplication
sys.path.insert(0, 'src')
from modules.items import panel_widget, list_entries
app = QApplication([])
print('entries sample:', list_entries(__import__('pathlib').Path.cwd() / 'Lib')[:10])
w = panel_widget(None)
print('panel created:', type(w))
app.quit()
