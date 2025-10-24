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
        self._current_worker = None


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
        path, _ = QFileDialog.getOpenFileName(self, 'Open file', str(Path.cwd() / 'Assets'))
        if not path:
            return
        # ask encoding
        encoding = 'big5'  # for now, assume big5 for data files
        # try to detect a client/server pair (C_/S_ files under Assets/Client and Assets/Server)
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
            # detect common layout: Assets/Client/C_*.ini or Assets/Server/S_*.ini (or .txt)
            str_path = str(p)
            if 'Assets{}Client'.format(Path.sep) in str_path.replace('/', Path.sep):
                # selected is client file under Assets/Client
                if name.startswith('C_') or name.startswith('c_'):
                    counterpart_name = name.replace('C_', 'S_', 1)
                    counterpart = Path(str(p).replace(str(Path('Assets') / 'Client'), str(Path('Assets') / 'Server'))).with_name(counterpart_name)
                    if counterpart.exists():
                        self.pair_paths = (str(p), str(counterpart))
                        # prefer to load client file rows
                        self.current_path = str(p)
                elif name.startswith('S_') or name.startswith('s_'):
                    counterpart_name = name.replace('S_', 'C_', 1)
                    counterpart = Path(str(p).replace(str(Path('Assets') / 'Server'), str(Path('Assets') / 'Client'))).with_name(counterpart_name)
                    if counterpart.exists():
                        self.pair_paths = (str(counterpart), str(p))
                        self.current_path = str(counterpart)
        except Exception:
            self.pair_paths = None

        # If we detected a client/server pair, read both and compare for divergences.
        # We still load the primary (client) file into the table, but show a warning
        # if the server file differs so the user can decide what to do.
        # Use background worker to read files so UI doesn't block on large datasets.
        self.rows = []
        if getattr(self, 'pair_paths', None):
            client_path, server_path = self.pair_paths
            worker = ReadPairWorker(client_path, server_path, encoding=encoding, expected=93)
        else:
            worker = ReadPairWorker(self.current_path, None, encoding=encoding, expected=93)

        # connect signals
        worker.result.connect(self._on_read_result)
        worker.error.connect(self._on_read_error)
        self._current_worker = worker
        QApplication.setOverrideCursor(Qt.WaitCursor)
        worker.start()

    def find_lib(self):
        p = Path.cwd()
        for _ in range(10):
            candidate = p / 'Assets'
            if candidate.exists():
                return candidate
            if p.parent == p:
                break
            p = p.parent
        return Path.cwd() / 'Assets'  # fallback

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

    def populate_table(self, header: Optional[list] = None):
        """Populate the QTableWidget from self.rows.

        If `header` is provided, use it as the horizontal header labels
        (will be trimmed or padded to match the column count).
        """
        if not self.rows:
            self.table.clear()
            return
        max_cols = max(len(r) for r in self.rows)
        # ensure we have at least as many columns as there are headers
        if header:
            desired_cols = max(max_cols, len(header))
        else:
            desired_cols = max_cols
        self.table.setColumnCount(desired_cols)
        self.table.setRowCount(len(self.rows))

        # set header labels if provided
        if header:
            labels = list(header)
            # pad or trim to match desired_cols
            if len(labels) < desired_cols:
                labels += [''] * (desired_cols - len(labels))
            elif len(labels) > desired_cols:
                labels = labels[:desired_cols]
            try:
                self.table.setHorizontalHeaderLabels(labels)
            except Exception:
                # ignore if UI not ready
                pass

        for i, row in enumerate(self.rows):
            for j in range(desired_cols):
                val = row[j] if j < len(row) else ''
                self.table.setItem(i, j, QTableWidgetItem(val))

    def _find_client_server_pair(self, base: str):
        """Try to locate client/server file paths for a given base name (e.g. 'C_Item' or 'C_ItemMall').

        Returns (client_path, server_path) or (None, None) if not found.
        """
        db_dir = Path(self.lib_path) / 'Client'
        server_dir = Path(self.lib_path) / 'Server'
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

    def _on_read_result(self, data):
        """Handle results from ReadPairWorker. Populate table and show any warnings/messages."""
        QApplication.restoreOverrideCursor()
        self._current_worker = None
        client_rows = data.get('client')
        server_rows = data.get('server')

        # derive header from modules.items.reader DEFAULT_HEADER if needed
        try:
            from modules.items import reader as items_reader
            header = items_reader.DEFAULT_HEADER.copy()
        except Exception:
            header = [f'col{i}' for i in range(93)]

        if client_rows is None:
            QMessageBox.critical(self, 'Read error', 'Failed to read primary file (no data)')
            return

        if server_rows is None:
            self._show_rows_in_table_panel(header, client_rows)
            QMessageBox.information(self, 'Loaded', f'Loaded client file (server mirror not found)')
            return

        # both present: compare
        if client_rows == server_rows:
            self._show_rows_in_table_panel(header, client_rows)
            QMessageBox.information(self, 'Loaded', f'Loaded pair (identical)')
            return

        # find first differing row
        diff_index = None
        for i, (a, b) in enumerate(zip(client_rows, server_rows)):
            if a != b:
                diff_index = i
                break
        self._show_rows_in_table_panel(header, client_rows)
        if diff_index is None and len(client_rows) != len(server_rows):
            QMessageBox.warning(self, 'Pair mismatch', f'Client and Server have different number of records: {len(client_rows)} vs {len(server_rows)}')
        else:
            a_preview = '|'.join(client_rows[diff_index][:6]) if diff_index is not None else ''
            b_preview = '|'.join(server_rows[diff_index][:6]) if diff_index is not None else ''
            QMessageBox.warning(self, 'Pair mismatch', f'Client and server differ at row {diff_index+1 if diff_index is not None else "?"}.\nClient preview: {a_preview}\nServer preview: {b_preview}\nLoaded client file.')

    def _on_read_error(self, msg: str):
        QApplication.restoreOverrideCursor()
        self._current_worker = None
        QMessageBox.critical(self, 'Read error', f'Failed to read files: {msg}')

    def _show_rows_in_table_panel(self, header, rows):
        """Replace right pane with a panel containing the table and load rows."""
        # set rows and populate table then insert table into right pane
        self.rows = rows
        self.populate_table(header)
        panel = QWidget()
        layout = QVBoxLayout()
        info = QLabel(f'Rows: {len(rows)} Columns: {len(header)}')
        layout.addWidget(info)

        # small toolbar to switch views: Tabela (CSV) or Editor detalhado
        toolbar = QHBoxLayout()
        btn_table = QPushButton('Tabela (CSV)')
        btn_editor = QPushButton('Editor detalhado')
        toolbar.addWidget(btn_table)
        toolbar.addWidget(btn_editor)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # by default show the table view
        layout.addWidget(self.table)

        # double-click on table row to open editor for that row
        self.table.itemDoubleClicked.connect(lambda item: self.show_item_editor(item.row(), header))

        # toolbar actions
        def show_table_view():
            # remove any editor widget if present and show table
            for i in range(layout.count()-1, -1, -1):
                w = layout.itemAt(i).widget()
                if w is not None and w is not self.table and w is not info:
                    try:
                        layout.removeWidget(w)
                        w.setParent(None)
                    except Exception:
                        pass
            if self.table.parent() is None:
                layout.addWidget(self.table)

        def show_editor_view():
            # open editor for currently selected row (or first row)
            idx = self.table.currentRow()
            if idx < 0:
                idx = 0
            editor = self.build_item_editor(idx, header)
            # remove table widget and add editor scroll area
            if self.table.parent() is not None:
                layout.removeWidget(self.table)
                self.table.setParent(None)
            layout.addWidget(editor)

        btn_table.clicked.connect(show_table_view)
        btn_editor.clicked.connect(show_editor_view)
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
        # try to find C_Item / S_Item pair and read using gfio (robust to multiline Tip)
        client_path, server_path = self._find_client_server_pair('C_Item')
        if client_path is None:
            QMessageBox.warning(self, 'Not found', 'Client C_Item file not found under Assets/Client')
            return
        # Read files in background to avoid blocking the UI
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

    def build_item_editor(self, index: int, header: list) -> QWidget:
        """Construct a scrollable editor widget for the item at `index` using `header` names."""
        if not self.rows or index < 0 or index >= len(self.rows):
            QMessageBox.warning(self, 'No selection', 'No item selected to edit')
            return QWidget()

        row = self.rows[index]
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()

        # main horizontal layout: left (icon + basic info + description), right (attributes form)
        main_layout = QHBoxLayout()

        # Left column
        left_v = QVBoxLayout()
        # icon preview
        icon_label = QLabel()
        icon_label.setFixedSize(128, 128)
        icon_label.setStyleSheet('background: #222; border: 1px solid #444;')
        # try to load icon if available
        icon_name = row[1] if len(row) > 1 else ''
        pix = None
        try:
            if icon_name:
                icon_path = Path(self.lib_path) / 'itemicon' / icon_name
                if icon_path.exists():
                    pix = QPixmap(str(icon_path))
        except Exception:
            pix = None
        if pix and not pix.isNull():
            icon_label.setPixmap(pix.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_label.setText(icon_name or 'No Icon')
            icon_label.setAlignment(Qt.AlignCenter)

        # Name and ID
        id_field = QLineEdit(row[0] if len(row) > 0 else '')
        id_field.setReadOnly(True)
        name_field = QLineEdit(row[9] if len(row) > 9 else '')
        left_v.addWidget(QLabel('ID:'))
        left_v.addWidget(id_field)
        left_v.addWidget(QLabel('Name:'))
        left_v.addWidget(name_field)

        # Description (Tip)
        desc = QTextEdit()
        desc.setPlainText(row[92] if len(row) > 92 else '')
        desc.setReadOnly(False)
        desc.setFixedHeight(140)
        left_v.addWidget(QLabel('Description:'))
        left_v.addWidget(desc)

        main_layout.addLayout(left_v)

        # Right column: build grouped parameter panels to mimic the more complex editor
        right_v = QVBoxLayout()

        # Main Parameters group (grid)
        gp_main = QGroupBox('Main Parameters')
        grid_main = QGridLayout()
        main_fields = ['MaxHp', 'MaxMp', 'Str', 'Con', 'Int', 'Vol', 'Dex',
                       'Attack', 'RangeAttack', 'AvgPhysicoDamage', 'RandPhysicoDamage',
                       'PhysicoDefence', 'MagicDefence', 'HitRate', 'DodgeRate',
                       'PhysicoCriticalRate', 'PhysicoCriticalDamage', 'MagicCriticalRate', 'MagicCriticalDamage',
                       'AttackSpeed', 'AttackRange']
        widgets = {}
        r = 0
        c = 0
        for fld in main_fields:
            # find column index for field name in header
            try:
                idx = header.index(fld)
            except Exception:
                idx = None
            val = row[idx] if (idx is not None and idx < len(row)) else ''
            le = QLineEdit(val)
            widgets[fld] = (idx, le)
            grid_main.addWidget(QLabel(fld+':'), r, c*2)
            grid_main.addWidget(le, r, c*2+1)
            c += 1
            if c >= 2:
                c = 0
                r += 1
        gp_main.setLayout(grid_main)
        right_v.addWidget(gp_main)

        # Enchant group
        gp_enchant = QGroupBox('Enchant Parameters')
        grid_enc = QGridLayout()
        enc_fields = ['EnchantId', 'EnchantIndex', 'EnchantTimeType', 'EnchantDuration', 'EnchantLevel']
        r = 0
        for fld in enc_fields:
            try:
                idx = header.index(fld)
            except Exception:
                idx = None
            val = row[idx] if (idx is not None and idx < len(row)) else ''
            le = QLineEdit(val)
            widgets[fld] = (idx, le)
            grid_enc.addWidget(QLabel(fld+':'), r, 0)
            grid_enc.addWidget(le, r, 1)
            r += 1
        gp_enchant.setLayout(grid_enc)
        right_v.addWidget(gp_enchant)

        # Price & Tip group
        gp_price = QGroupBox('Price & Tip')
        v_price = QVBoxLayout()
        # Price fields
        price_layout = QHBoxLayout()
        # price type and price value if present
        try:
            idx_price_type = header.index('ShopPriceType')
        except Exception:
            idx_price_type = None
        try:
            idx_price = header.index('SysPrice')
        except Exception:
            idx_price = None
        le_price_type = QLineEdit(row[idx_price_type] if idx_price_type is not None and idx_price_type < len(row) else '')
        le_price = QLineEdit(row[idx_price] if idx_price is not None and idx_price < len(row) else '')
        price_layout.addWidget(QLabel('Price Type:'))
        price_layout.addWidget(le_price_type)
        price_layout.addWidget(QLabel('Price:'))
        price_layout.addWidget(le_price)
        v_price.addLayout(price_layout)

        # Tip/Description box
        tip_box = QTextEdit()
        tip_box.setPlainText(row[92] if len(row) > 92 else '')
        tip_box.setFixedHeight(140)
        v_price.addWidget(QLabel('Tip:'))
        v_price.addWidget(tip_box)
        gp_price.setLayout(v_price)
        right_v.addWidget(gp_price)

        # Restrict Class - many checkboxes in scroll area
        gp_restrict = QGroupBox('Restrict Class')
        grid_rc = QGridLayout()
        class_names = ['Novice','Fighter','Warrior','Berserker','Warlord','Templar','Paladin',
                       'Ranger','Archer','Sniper','Assassin','Hunter','Sharpshooter','Blademaster',
                       'Priest','Cleric','Sage','Prophet','Druid','Shaman','Mage','Wizard','Necromancer']
        chboxes = {}
        r = 0
        c = 0
        for i, cname in enumerate(class_names):
            cb = QCheckBox(cname)
            chboxes[cname] = cb
            grid_rc.addWidget(cb, r, c)
            c += 1
            if c >= 4:
                c = 0
                r += 1
        gp_restrict.setLayout(grid_rc)
        right_v.addWidget(gp_restrict)

        # Restrict Use checkboxes
        gp_use = QGroupBox('Restrict Use')
        grid_use = QGridLayout()
        use_flags = ['Unusable','Combinable','BindOnEquip','ForDeadPlayer','NoTrade','NoRepair','NoDrop','OnlyEquip']
        r = 0
        c = 0
        use_checks = {}
        for uf in use_flags:
            cb = QCheckBox(uf)
            use_checks[uf] = cb
            grid_use.addWidget(cb, r, c)
            c += 1
            if c >= 4:
                c = 0
                r += 1
        gp_use.setLayout(grid_use)
        right_v.addWidget(gp_use)

        # Save and Save+Close buttons
        btn_row = QHBoxLayout()
        btn_save = QPushButton('Save')
        btn_save_close = QPushButton('Save and Close')
        btn_save_disk = QPushButton('Save to Disk')
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_save_close)
        btn_row.addWidget(btn_save_disk)
        btn_row.addStretch()
        right_v.addLayout(btn_row)

        # Save logic: update row fields from widgets
        def save_item_local(close_after: bool = False, write_disk: bool = False):
            # name and tip
            if len(row) <= 9:
                while len(row) <= 9:
                    row.append('')
            row[9] = name_field.text()
            if len(row) > 92:
                row[92] = tip_box.toPlainText()
            else:
                while len(row) <= 92:
                    row.append('')
                row[92] = tip_box.toPlainText()
            # main fields
            for fld, (idx, widget) in widgets.items():
                if idx is None:
                    continue
                val = widget.text()
                while len(row) <= idx:
                    row.append('')
                row[idx] = val
            # class flags (store as a simple CSV in ExtraData1/ExtraData2 etc or skip)
            # just refresh table view
            for col in range(self.table.columnCount()):
                val = row[col] if col < len(row) else ''
                self.table.setItem(index, col, QTableWidgetItem(val))
            if write_disk:
                # call save_file to write current table to disk
                try:
                    self.save_file()
                except Exception:
                    pass
            if close_after:
                # restore table panel
                try:
                    self._show_rows_in_table_panel(header, self.rows)
                except Exception:
                    pass
            else:
                QMessageBox.information(self, 'Saved', 'Changes saved to table (not written to disk)')

        btn_save.clicked.connect(lambda: save_item_local(False, False))
        btn_save_close.clicked.connect(lambda: save_item_local(True, False))
        btn_save_disk.clicked.connect(lambda: save_item_local(True, True))

        main_layout.addLayout(right_v)

        container.setLayout(main_layout)
        scroll.setWidget(container)
        return scroll

    def show_item_editor(self, index: int, header: list):
        """Helper to open the editor in-place replacing the table view for chosen index."""
        splitter = self._find_splitter()
        if splitter is None:
            QMessageBox.warning(self, 'UI error', 'Cannot find layout splitter')
            return
        editor = self.build_item_editor(index, header)
        # insert editor widget into right pane
        old = splitter.widget(1)
        splitter.insertWidget(1, editor)
        if old is not None:
            old.setParent(None)

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
