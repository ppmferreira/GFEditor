"""Minimal GUI for GF Editor using PySide6.

This provides: open file, show first lines in a table, save (writes back raw pipe-delimited).
"""
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox,
    QListWidget, QSplitter, QLabel, QTextEdit
)
from PySide6.QtCore import Qt
import sys
from pathlib import Path
from typing import Optional
import gfio as _gfio


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('GF Editor - Prototype')

        # detect Lib folder
        self.lib_path = self.find_lib()

        # discover available modules in src/modules
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
            # fallback
            self.modules = [
                ('Items', 'modules.items'),
                ('Monsters', 'modules.monsters'),
                ('NPCs', 'modules.npcs'),
                ('Shops', 'modules.shops'),
            ]

        # module list widget
        self.module_list = QListWidget()
        for name, _ in self.modules:
            self.module_list.addItem(name)
        self.module_list.currentRowChanged.connect(self.on_module_changed)

        # left panel: Home button above module list (user requested)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        home_btn = QPushButton('Home')
        home_btn.clicked.connect(self.show_intro)
        left_layout.addWidget(home_btn)
        left_layout.addWidget(self.module_list)
        left_layout.addStretch()
        left_panel.setLayout(left_layout)

        # main table (used when a file is opened)
        self.table = QTableWidget()

        # create intro panel shown initially on the right
        self.intro_panel = self.create_intro_panel()

        # splitter: left panel (with Home+modules) and right content (intro/table)
        splitter = QSplitter()
        splitter.addWidget(left_panel)
        splitter.addWidget(self.intro_panel)
        splitter.setSizes([150, 800])

        # central layout: just the splitter (buttons removed)
        central = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(splitter)
        central.setLayout(central_layout)
        self.setCentralWidget(central)

        self.current_path = None
        self.rows = []
        self.pair_paths = None

    def create_intro_panel(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout()

        title = QLabel('<h2>Bem-vindo ao GF Editor - Developed By Fuleco.</h2>')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setPlainText(
            'Bem-vindo ao GF Editor - Developed By Fuleco.\n\n'
            'Este editor foi desenvolvido para editar arquivos do Grand Fantasia (C_/S_).\n'
            'Funcionalidades principais:\n'
            '- Suporte a arquivos espelhados cliente/servidor (C_ <-> S_)\n'
            "- Preserva campos 'Tip' com quebras de linha\n"
            '- Leitura com fallback de encoding (BIG5, UTF-8, latin-1)\n\n'
            'Use o painel a esquerda para escolher um modulo e clique em "Open" para carregar arquivos.'
        )
        layout.addWidget(desc)

        btn_open = QPushButton('Open')
        btn_open.clicked.connect(self.open_file)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn_open)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()
        w.setLayout(layout)
        return w

    def _find_splitter(self) -> Optional[QSplitter]:
        central = self.centralWidget()
        if central is None:
            return None
        layout = central.layout()
        if layout is None:
            return None
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if isinstance(w, QSplitter):
                return w
        return None

    def show_intro(self):
        """Restore the intro panel on the right side of the splitter."""
        splitter = self._find_splitter()
        if splitter is None:
            return
        # if intro is already visible at slot 1, do nothing (keep home visible)
        try:
            current = splitter.widget(1)
        except Exception:
            current = None
        if current is self.intro_panel:
            return

        old = current
        # insert intro panel at index 1 and remove old widget
        splitter.insertWidget(1, self.intro_panel)
        if old is not None and old is not self.intro_panel:
            old.setParent(None)

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

        # If we detected a client/server pair, read both and compare for divergences.
        # We still load the primary (client) file into the table, but show a warning
        # if the server file differs so the user can decide what to do.
        self.rows = []
        if getattr(self, 'pair_paths', None):
            client_path, server_path = self.pair_paths
            try:
                client_rows = _gfio.read_pipe_file(client_path, encoding=encoding, expected_fields=93)
            except Exception as exc:
                QMessageBox.critical(self, 'Read error', f'Failed to read client file: {exc}')
                return
            try:
                server_rows = _gfio.read_pipe_file(server_path, encoding=encoding, expected_fields=93)
            except Exception as exc:
                # still load client but inform about server read failure
                self.rows = client_rows
                QMessageBox.warning(self, 'Server read error', f'Failed to read server mirror: {exc}')
                self.populate_table()
                return

            # compare lengths
            if len(client_rows) != len(server_rows):
                QMessageBox.warning(self, 'Client/Server mismatch',
                                    f'Client and Server have different number of records: {len(client_rows)} vs {len(server_rows)}')
            else:
                # look for first differing row
                diff_index = None
                for i, (a, b) in enumerate(zip(client_rows, server_rows)):
                    if a != b:
                        diff_index = i
                        break
                if diff_index is not None:
                    # create a short preview of the differing row (first 6 cols)
                    a = client_rows[diff_index]
                    b = server_rows[diff_index]
                    a_preview = '|'.join(a[:6])
                    b_preview = '|'.join(b[:6])
                    QMessageBox.warning(self, 'Client/Server mismatch',
                                        f'Files differ at row {diff_index+1} (1-based).\nClient preview: {a_preview}\nServer preview: {b_preview}')

            # load client rows into table for editing
            self.rows = client_rows
        else:
            try:
                self.rows = _gfio.read_pipe_file(self.current_path, encoding=encoding, expected_fields=93)
            except Exception as exc:
                QMessageBox.critical(self, 'Read error', f'Failed to read file: {exc}')
                return
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

        # Special-case: modules.items should show two quick actions (Edit Item / Edit ItemMall)
        if module_path == 'modules.items':
            panel = QWidget()
            layout = QVBoxLayout()
            title = QLabel('<b>Items</b>')
            layout.addWidget(title)

            btn_item = QPushButton('Editar Item')
            btn_item.clicked.connect(self._handle_edit_item)
            layout.addWidget(btn_item)

            btn_itemmall = QPushButton('Editar ItemMall')
            btn_itemmall.clicked.connect(self._handle_edit_itemmall)
            layout.addWidget(btn_itemmall)

            layout.addStretch()
            panel.setLayout(layout)
        else:
            # If module doesn't expose panel_widget, show a friendly placeholder instead of crashing
            if not hasattr(mod, 'panel_widget'):
                placeholder = QWidget()
                layout = QVBoxLayout()
                label = QLabel(f'Module "{module_path}" has no UI panel implemented yet.')
                layout.addWidget(label)
                open_btn = QPushButton('Open files...')
                open_btn.clicked.connect(self.open_file)
                layout.addWidget(open_btn)
                layout.addStretch()
                placeholder.setLayout(layout)
                panel = placeholder
            else:
                # remove right widget and replace with module panel
                panel = mod.panel_widget(self)
        # assume right widget is index 1 in splitter
        splitter = self._find_splitter()
        if splitter is None:
            QMessageBox.warning(self, 'UI error', 'Cannot find layout splitter')
            return
        # replace widget at index 1
        old = splitter.widget(1)
        splitter.insertWidget(1, panel)
        if old is not None:
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

    def _find_client_server_pair(self, base: str):
        """Try to locate client/server file paths for a given base name (e.g. 'C_Item' or 'C_ItemMall').

        Returns (client_path, server_path) or (None, None) if not found.
        """
        db_dir = Path(self.lib_path) / 'data' / 'db'
        server_dir = Path(self.lib_path) / 'data' / 'serverdb'
        # look for client file starting with base
        client_candidates = list(db_dir.glob(f"{base}*.ini")) + list(db_dir.glob(f"{base}*.txt"))
        if not client_candidates:
            # try without prefix (fallback)
            client_candidates = list(db_dir.glob(f"{base}*") )
        if not client_candidates:
            return None, None
        client_path = str(client_candidates[0])
        # try to build server path by replacing db dir with serverdir and C_ -> S_
        name = Path(client_path).name
        if name.startswith('C_'):
            server_name = name.replace('C_', 'S_', 1)
        else:
            server_name = name
        server_path = str((server_dir / server_name))
        if not Path(server_path).exists():
            # try to find any S_ variant
            server_candidates = list(server_dir.glob(f"S_{name[2:]}*.ini")) + list(server_dir.glob(f"S_{name[2:]}*.txt"))
            if server_candidates:
                server_path = str(server_candidates[0])
            else:
                server_path = None
        return client_path, server_path

    def _show_rows_in_table_panel(self, header, rows):
        """Replace right pane with a panel containing the table and load rows."""
        # set rows and populate table then insert table into right pane
        self.rows = rows
        self.populate_table()
        panel = QWidget()
        layout = QVBoxLayout()
        info = QLabel(f'Rows: {len(rows)} Columns: {len(header)}')
        layout.addWidget(info)
        layout.addWidget(self.table)
        panel.setLayout(layout)

        splitter = self._find_splitter()
        if splitter is None:
            QMessageBox.warning(self, 'UI error', 'Cannot find layout splitter to show items')
            return
        old = splitter.widget(1)
        splitter.insertWidget(1, panel)
        if old is not None:
            old.setParent(None)

    def _handle_edit_item(self):
        # try to find C_Item / S_Item pair
        client_path, server_path = self._find_client_server_pair('C_Item')
        items_mod = __import__('modules.items', fromlist=['read_items_pair', 'read_items'])
        if client_path is None:
            QMessageBox.warning(self, 'Not found', 'Client C_Item file not found under Lib/data/db')
            return
        if server_path is None:
            # try read single file
            header, rows, items = items_mod.read_items(client_path, delimiter='|', encoding='big5')
            self._show_rows_in_table_panel(header, rows)
            QMessageBox.information(self, 'Loaded', f'Loaded client file {client_path} (server mirror not found)')
            return
        # attempt to read pair
        try:
            header, rows, items = items_mod.read_items_pair(client_path, server_path, delimiter='|', encoding='big5')
            self._show_rows_in_table_panel(header, rows)
            QMessageBox.information(self, 'Loaded', f'Loaded pair:\nClient: {client_path}\nServer: {server_path}')
        except ValueError as ve:
            # pairs differ; try to load client and show warning
            header, rows, items = items_mod.read_items(client_path, delimiter='|', encoding='big5')
            self._show_rows_in_table_panel(header, rows)
            QMessageBox.warning(self, 'Pair mismatch', f'Client and server differ: {ve}\nLoaded client file.')

    def _handle_edit_itemmall(self):
        client_path, server_path = self._find_client_server_pair('C_ItemMall')
        items_mod = __import__('modules.items', fromlist=['read_items_pair', 'read_items'])
        if client_path is None:
            QMessageBox.warning(self, 'Not found', 'Client C_ItemMall file not found under Lib/data/db')
            return
        if server_path is None:
            header, rows, items = items_mod.read_items(client_path, delimiter='|', encoding='big5')
            self._show_rows_in_table_panel(header, rows)
            QMessageBox.information(self, 'Loaded', f'Loaded client file {client_path} (server mirror not found)')
            return
        try:
            header, rows, items = items_mod.read_items_pair(client_path, server_path, delimiter='|', encoding='big5')
            self._show_rows_in_table_panel(header, rows)
            QMessageBox.information(self, 'Loaded', f'Loaded pair:\nClient: {client_path}\nServer: {server_path}')
        except ValueError as ve:
            header, rows, items = items_mod.read_items(client_path, delimiter='|', encoding='big5')
            self._show_rows_in_table_panel(header, rows)
            QMessageBox.warning(self, 'Pair mismatch', f'Client and server differ: {ve}\nLoaded client file.')

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
