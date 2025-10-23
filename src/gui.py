"""Minimal GUI for GF Editor using PySide6.

This provides: open file, show first lines in a table, save (writes back raw pipe-delimited).
"""
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox,
    QListWidget, QSplitter
)
import sys
from pathlib import Path
import gfio as _gfio


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GF Editor - Prototype')
        # detect Lib folder
        self.lib_path = self.find_lib()

        # modules list and main area: discover subpackages in src/modules
        self.modules = []
        try:
            modules_dir = Path(__file__).parent / 'modules'
            if modules_dir.exists():
                for p in sorted(modules_dir.iterdir()):
                    if p.is_dir() and (p / '__init__.py').exists():
                        name = p.name
                        display = name.capitalize()
                        self.modules.append((display, f'modules.{name}'))
        except Exception:
            # fallback to default list if discovery fails
            self.modules = [
                ('Items', 'modules.items'),
                ('Monsters', 'modules.monsters'),
                ('NPCs', 'modules.npcs'),
                ('Shops', 'modules.shops'),
            ]
        # sidebar with modules
        self.module_list = QListWidget()
        for name, _ in self.modules:
            self.module_list.addItem(name)
        self.module_list.currentRowChanged.connect(self.on_module_changed)

        # main table and buttons
        self.table = QTableWidget()
        open_btn = QPushButton('Open')
        save_btn = QPushButton('Save')
        open_btn.clicked.connect(self.open_file)
        save_btn.clicked.connect(self.save_file)

        btns = QHBoxLayout()
        btns.addWidget(open_btn)
        btns.addWidget(save_btn)

        right_layout = QVBoxLayout()
        right_layout.addLayout(btns)
        right_layout.addWidget(self.table)
        right_container = QWidget()
        right_container.setLayout(right_layout)

        splitter = QSplitter()
        splitter.addWidget(self.module_list)
        splitter.addWidget(right_container)
        splitter.setSizes([150, 800])

        self.setCentralWidget(splitter)

        self.current_path = None
        self.rows = []

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open file', str(Path.cwd() / 'Lib'))
        if not path:
            return
        # ask encoding
        encoding = 'big5'  # for now, assume big5 for data files
        # try to detect a client/server pair (C_/S_ files under Lib/data/db and Lib/data/serverdb)
        p = Path(path)
        self.pair_paths = None
        try:
            parts = p.parts
        except Exception:
            parts = []

        # default: single file
        self.current_path = path

        # if the selected file looks like a client or server db file, attempt to find its mirror
        try:
            name = p.name
            parent = p.parent
            # detect common layout: Lib/data/db/C_*.ini or Lib/data/serverdb/S_*.ini (or .txt)
            str_path = str(p)
            if 'Lib{}data{}db'.format(Path.sep, Path.sep) in str_path.replace('/', Path.sep):
                # selected is client file under Lib/data/db
                if name.startswith('C_') or name.startswith('c_'):
                    counterpart_name = name.replace('C_', 'S_', 1)
                    counterpart = Path(str(p).replace(str(Path('Lib') / 'data' / 'db'), str(Path('Lib') / 'data' / 'serverdb'))).with_name(counterpart_name)
                    if counterpart.exists():
                        self.pair_paths = (str(p), str(counterpart))
                        # prefer to load client file rows
                        self.current_path = str(p)
                elif name.startswith('S_') or name.startswith('s_'):
                    counterpart_name = name.replace('S_', 'C_', 1)
                    counterpart = Path(str(p).replace(str(Path('Lib') / 'data' / 'serverdb'), str(Path('Lib') / 'data' / 'db'))).with_name(counterpart_name)
                    if counterpart.exists():
                        self.pair_paths = (str(counterpart), str(p))
                        self.current_path = str(counterpart)
        except Exception:
            self.pair_paths = None

        # load entire file (no 1000-line limit) and assemble logical records
        # using the expected 93 fields so multiline Tip fields are handled
        self.rows = _gfio.read_pipe_file(self.current_path, encoding=encoding, expected_fields=93)
        self.populate_table()

    def find_lib(self):
        p = Path.cwd()
        for _ in range(10):
            candidate = p / 'Lib'
            if candidate.exists():
                return candidate
            if p.parent == p:
                break
            p = p.parent
        return Path.cwd() / 'Lib'  # fallback

    def on_module_changed(self, row: int):
        if row < 0 or row >= len(self.modules):
            return
        module_path = self.modules[row][1]
        try:
            mod = __import__(module_path, fromlist=['panel_widget'])
        except Exception:
            QMessageBox.warning(self, 'Module load error', f'Failed to load {module_path}')
            return
        # remove right widget and replace with module panel
        panel = mod.panel_widget(self)
        # assume right widget is index 1 in splitter
        splitter = self.centralWidget()
        # replace widget at index 1
        old = splitter.widget(1)
        splitter.insertWidget(1, panel)
        old.setParent(None)

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
        # make backup for primary (client) path
        Path(self.current_path + '.bak').write_text('backup', encoding='utf-8')

        # if pair_paths present, write both client and server copies
        try:
            if getattr(self, 'pair_paths', None):
                client_path, server_path = self.pair_paths
                _gfio.write_pipe_file(client_path, rows, encoding='big5')
                _gfio.write_pipe_file(server_path, rows, encoding='big5')
                QMessageBox.information(self, 'Saved', f'Saved pair:\nClient: {client_path}\nServer: {server_path}')
            else:
                _gfio.write_pipe_file(self.current_path, rows, encoding='big5')
                QMessageBox.information(self, 'Saved', 'File saved (backup created)')
        except Exception as exc:
            QMessageBox.critical(self, 'Save error', f'Failed to save: {exc}')


def run_gui():
    app = QApplication(sys.argv)
    # try to load global stylesheet from src/style/style.qss
    try:
        style_path = Path(__file__).parent / 'style' / 'style.qss'
        if style_path.exists():
            app.setStyleSheet(style_path.read_text(encoding='utf-8'))
    except Exception:
        pass
    w = MainWindow()
    w.resize(1000, 600)
    w.show()
    return app.exec()
