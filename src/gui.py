"""Minimal GUI for GF Editor using PySide6.

This provides: open file, show first lines in a table, save (writes back raw pipe-delimited).
"""
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QWidget, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox,
    QListWidget, QSplitter, QLabel, QTextEdit, QScrollArea, QFormLayout, QLineEdit,
    QGroupBox, QGridLayout, QCheckBox, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
import sys
from pathlib import Path
from typing import Optional
import gfio as _gfio


class MainWindow(QMainWindow):
    """Clean, minimal main window that delegates editing to modules.

    Responsibilities:
    - discover panels under src/modules
    - open data files (client/server pair detection)
    - display table of rows
    - delegate detailed editing to module panels (e.g. modules.items.panel)
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('GF Editor - Prototype')

        # runtime state
        self.lib_path = self.find_lib()
        self.current_path = None
        self.rows = []
        self.pair_paths = None
        self._current_worker = None

        # module discovery
        self.modules = []
        modules_dir = Path(__file__).parent / 'modules'
        if modules_dir.exists():
            for p in sorted(modules_dir.iterdir()):
                if p.is_dir() and (p / '__init__.py').exists():
                    self.modules.append((p.name.capitalize(), f'modules.{p.name}'))

        # UI: left module list, right content area
        self.module_list = QListWidget()
        for name, _ in self.modules:
            self.module_list.addItem(name)
        self.module_list.currentRowChanged.connect(self.on_module_changed)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        home_btn = QPushButton('Home')
        home_btn.clicked.connect(self.show_intro)
        left_layout.addWidget(home_btn)
        left_layout.addWidget(self.module_list)
        left_layout.addStretch()
        left_panel.setLayout(left_layout)

        self.table = QTableWidget()
        self.intro_panel = self.create_intro_panel()

        splitter = QSplitter()
        splitter.addWidget(left_panel)
        splitter.addWidget(self.intro_panel)
        splitter.setSizes([150, 800])

        central = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(splitter)
        central.setLayout(central_layout)
        self.setCentralWidget(central)

    def create_intro_panel(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('<h2>Bem-vindo ao GF Editor</h2>'))
        info = QTextEdit()
        info.setReadOnly(True)
        # use ASCII-only text to avoid source encoding issues
        info.setPlainText('Use o painel a esquerda para escolher um modulo ou abrir um arquivo C_/S_.')
        layout.addWidget(info)
        btn_open = QPushButton('Open')
        btn_open.clicked.connect(self.open_file)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(btn_open)
        row.addStretch()
        layout.addLayout(row)
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

    def find_lib(self):
        """Locate the repository Assets folder by walking up from cwd (fallback to cwd/Assets)."""
        p = Path.cwd()
        for _ in range(10):
            candidate = p / 'Assets'
            if candidate.exists():
                return candidate
            if p.parent == p:
                break
            p = p.parent
        return Path.cwd() / 'Assets'

    def on_module_changed(self, row: int):
        """Load the module panel (calls module's panel_widget) into the right area."""
        if row < 0 or row >= len(self.modules):
            return
        module_path = self.modules[row][1]
        try:
            mod = __import__(module_path, fromlist=['panel_widget'])
        except Exception:
            QMessageBox.warning(self, 'Module load error', f'Failed to load {module_path}')
            return

        if hasattr(mod, 'panel_widget'):
            panel = mod.panel_widget(self)
        else:
            # simple placeholder if no UI provided
            panel = QWidget()
            l = QVBoxLayout()
            l.addWidget(QLabel(f'Module "{module_path}" has no panel_widget'))
            panel.setLayout(l)

        splitter = self._find_splitter()
        if splitter is None:
            QMessageBox.warning(self, 'UI error', 'Cannot find layout splitter')
            return
        old = splitter.widget(1)
        splitter.insertWidget(1, panel)
        if old is not None:
            old.setParent(None)

    def show_intro(self):
        splitter = self._find_splitter()
        if splitter is None:
            return
        current = splitter.widget(1)
        if current is self.intro_panel:
            return
        old = current
        splitter.insertWidget(1, self.intro_panel)
        if old is not None and old is not self.intro_panel:
            old.setParent(None)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open file', str(Path.cwd() / 'Assets'))
        if not path:
            return
        self.current_path = path
        # try to find client/server pair
        p = Path(path)
        try:
            if 'Assets{}Client'.format(Path.sep) in str(p).replace('/', Path.sep):
                name = p.name
                if name.startswith('C_'):
                    counterpart = Path(str(p).replace(str(Path('Assets') / 'Client'), str(Path('Assets') / 'Server'))).with_name(name.replace('C_', 'S_', 1))
                    if counterpart.exists():
                        self.pair_paths = (str(p), str(counterpart))
        except Exception:
            self.pair_paths = None

        # read in background
        if getattr(self, 'pair_paths', None):
            client_path, server_path = self.pair_paths
            worker = ReadPairWorker(client_path, server_path, encoding='big5', expected=93)
        else:
            worker = ReadPairWorker(self.current_path, None, encoding='big5', expected=93)
        worker.result.connect(self._on_read_result)
        worker.error.connect(self._on_read_error)
        self._current_worker = worker
        QApplication.setOverrideCursor(Qt.WaitCursor)
        worker.start()

    def _find_client_server_pair(self, base: str):
        db_dir = Path(self.lib_path) / 'Client'
        server_dir = Path(self.lib_path) / 'Server'
        client_candidates = list(db_dir.glob(f"{base}*.ini")) + list(db_dir.glob(f"{base}*.txt"))
        if not client_candidates:
            return None, None
        client_path = str(client_candidates[0])
        name = Path(client_path).name
        if name.startswith('C_'):
            server_name = name.replace('C_', 'S_', 1)
        else:
            server_name = name
        server_path = str((server_dir / server_name))
        if not Path(server_path).exists():
            server_candidates = list(server_dir.glob(f"S_{name[2:]}*.ini")) + list(server_dir.glob(f"S_{name[2:]}*.txt"))
            if server_candidates:
                server_path = str(server_candidates[0])
            else:
                server_path = None
        return client_path, server_path

    def _on_read_result(self, data):
        QApplication.restoreOverrideCursor()
        self._current_worker = None
        client_rows = data.get('client')
        server_rows = data.get('server')
        try:
            from modules.items import reader as items_reader
            header = items_reader.DEFAULT_HEADER.copy()
        except Exception:
            header = [f'col{i}' for i in range(93)]

        if client_rows is None:
            QMessageBox.critical(self, 'Read error', 'Failed to read primary file (no data)')
            return
        self._show_rows_in_table_panel(header, client_rows)
        if server_rows is None:
            QMessageBox.information(self, 'Loaded', 'Loaded client file (server mirror not found)')
        elif client_rows == server_rows:
            QMessageBox.information(self, 'Loaded', 'Loaded pair (identical)')
        else:
            QMessageBox.warning(self, 'Pair mismatch', 'Client and server differ (loaded client file).')

    def _on_read_error(self, msg: str):
        QApplication.restoreOverrideCursor()
        self._current_worker = None
        QMessageBox.critical(self, 'Read error', f'Failed to read files: {msg}')

    def populate_table(self, header: Optional[list] = None):
        if not self.rows:
            self.table.clear()
            return
        max_cols = max(len(r) for r in self.rows)
        desired_cols = max(max_cols, len(header) if header else 0)
        self.table.setColumnCount(desired_cols)
        self.table.setRowCount(len(self.rows))
        if header:
            labels = list(header)[:desired_cols]
            try:
                self.table.setHorizontalHeaderLabels(labels)
            except Exception:
                pass
        for i, row in enumerate(self.rows):
            for j in range(desired_cols):
                val = row[j] if j < len(row) else ''
                self.table.setItem(i, j, QTableWidgetItem(val))

    def _show_rows_in_table_panel(self, header, rows):
        self.rows = rows
        self.populate_table(header)
        panel = QWidget()
        layout = QVBoxLayout()
        info = QLabel(f'Rows: {len(rows)} Columns: {len(header)}')
        layout.addWidget(info)
        toolbar = QHBoxLayout()
        btn_table = QPushButton('Tabela (CSV)')
        btn_editor = QPushButton('Editor detalhado')
        toolbar.addWidget(btn_table)
        toolbar.addWidget(btn_editor)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        layout.addWidget(self.table)

        # open professional editor on double click
        def _open(idx=None):
            i = self.table.currentRow() if idx is None else idx
            if i < 0:
                i = 0
            self.open_professional_editor(i, header)

        self.table.itemDoubleClicked.connect(lambda item: _open())
        btn_table.clicked.connect(lambda: None)
        btn_editor.clicked.connect(lambda: _open())

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
        client_path, server_path = self._find_client_server_pair('C_Item')
        if client_path is None:
            QMessageBox.warning(self, 'Not found', 'Client C_Item file not found under Assets/Client')
            return
        worker = ReadPairWorker(client_path, server_path, encoding='big5', expected=93)
        worker.result.connect(self._on_read_result)
        worker.error.connect(self._on_read_error)
        self._current_worker = worker
        QApplication.setOverrideCursor(Qt.WaitCursor)
        worker.start()

    def _handle_edit_itemmall(self):
        client_path, server_path = self._find_client_server_pair('C_ItemMall')
        if client_path is None:
            QMessageBox.warning(self, 'Not found', 'Client C_ItemMall file not found under Assets/Client')
            return
        worker = ReadPairWorker(client_path, server_path, encoding='big5', expected=93)
        worker.result.connect(self._on_read_result)
        worker.error.connect(self._on_read_error)
        self._current_worker = worker
        QApplication.setOverrideCursor(Qt.WaitCursor)
        worker.start()

    def open_professional_editor(self, index: int, header: list):
        try:
            panel_mod = __import__('modules.items.panel', fromlist=['build_professional_editor'])
            editor = panel_mod.build_professional_editor(self, self.rows, header)
        except Exception:
            try:
                pkg = __import__('modules.items', fromlist=['panel_widget'])
                if hasattr(pkg, 'panel_widget'):
                    editor = pkg.panel_widget(self)
                else:
                    raise
            except Exception as exc:
                QMessageBox.warning(self, 'Editor error', f'Failed to open professional editor: {exc}')
                return
        splitter = self._find_splitter()
        if splitter is None:
            QMessageBox.warning(self, 'UI error', 'Cannot find layout splitter')
            return
        old = splitter.widget(1)
        splitter.insertWidget(1, editor)
        if old is not None:
            old.setParent(None)

    def save_file(self):
        if not self.current_path:
            QMessageBox.warning(self, 'No file', 'No file opened')
            return
        rows = []
        for i in range(self.table.rowCount()):
            row = []
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                row.append(item.text() if item else '')
            rows.append(row)
        Path(self.current_path + '.bak').write_text('backup', encoding='utf-8')
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


class ReadPairWorker(QThread):
    """QThread worker that reads a client file and an optional server file
    using gfio.read_pipe_file and emits the result as a dict: {'client': rows, 'server': rows}
    """
    result = Signal(object)
    error = Signal(str)

    def __init__(self, client_path: Optional[str], server_path: Optional[str], encoding: str = 'big5', expected: int = 93):
        super().__init__()
        self.client_path = client_path
        self.server_path = server_path
        self.encoding = encoding
        self.expected = expected

    def run(self):
        try:
            data = {}
            if self.client_path:
                data['client'] = _gfio.read_pipe_file(self.client_path, encoding=self.encoding, expected_fields=self.expected)
            else:
                data['client'] = None
            if self.server_path:
                data['server'] = _gfio.read_pipe_file(self.server_path, encoding=self.encoding, expected_fields=self.expected)
            else:
                data['server'] = None
            self.result.emit(data)
        except Exception as e:
            self.error.emit(str(e))
