from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QTextEdit, QScrollArea, QGroupBox, QFormLayout, QCheckBox, QMessageBox,
    QListWidget, QListWidgetItem
)
from PySide6.QtGui import QIntValidator

from .schema import SCHEMA, ENUMS, OPFLAGS, OPFLAGSPLUS
from . import panel_new as backend


class ItemsPanel(QWidget):
    def __init__(self, parent=None, lib_path: Optional[Path] = None):
        super().__init__(parent)
        self.lib_path = lib_path or (Path.cwd() / 'Lib')
        self.current_file = None
        self.rows: List[List[str]] = []
        self.current_row_idx: Optional[int] = None

        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)

        # File selector
        h = QHBoxLayout()
        h.addWidget(QLabel('ServerDB file:'))
        self.file_combo = QComboBox()
        self.file_combo.addItems(backend.list_entries(self.lib_path))
        self.file_combo.currentTextChanged.connect(self.on_file_changed)
        h.addWidget(self.file_combo)
        reload_btn = QPushButton('Reload')
        reload_btn.clicked.connect(self.reload_files)
        h.addWidget(reload_btn)
        open_btn = QPushButton('Open')
        open_btn.clicked.connect(self.open_selected_file)
        h.addWidget(open_btn)
        main.addLayout(h)

        # file list (compat for old UI tests)
        self.file_list = QListWidget()
        for f in backend.list_entries(self.lib_path):
            QListWidgetItem(f, self.file_list)
        # sync selection from list to combo
        self.file_list.currentItemChanged.connect(lambda cur, prev: self._on_file_list_changed(cur))
        main.addWidget(self.file_list)

        # Row selector (Id) + search
        h2 = QHBoxLayout()
        h2.addWidget(QLabel('Id:'))
        self.id_combo = QComboBox()
        self.id_combo.currentTextChanged.connect(self.on_id_changed)
        h2.addWidget(self.id_combo)
        self.id_search = QLineEdit()
        self.id_search.setPlaceholderText('Buscar Id...')
        h2.addWidget(self.id_search)
        find_btn = QPushButton('Find')
        find_btn.clicked.connect(self.find_id)
        h2.addWidget(find_btn)
        main.addLayout(h2)

        # Scroll area with form
        self.form_area = QScrollArea()
        self.form_area.setWidgetResizable(True)
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.form_area.setWidget(self.form_widget)
        main.addWidget(self.form_area)

        # Buttons
        btns = QHBoxLayout()
        self.save_row_btn = QPushButton('Save Row (and sync translations)')
        self.save_row_btn.clicked.connect(self.save_current_row)
        btns.addWidget(self.save_row_btn)
        self.save_file_btn = QPushButton('Save File (all rows)')
        self.save_file_btn.clicked.connect(self.save_file)
        btns.addWidget(self.save_file_btn)
        main.addLayout(btns)

        # Build form controls per SCHEMA
        self.controls: Dict[int, Any] = {}
        for idx, name, typ in SCHEMA:
            widget = None
            if typ == 'int':
                le = QLineEdit()
                le.setValidator(QIntValidator())
                widget = le
            elif typ == 'str':
                widget = QLineEdit()
            elif typ == 'trans':
                widget = QLineEdit()
            elif typ == 'trans_multiline':
                widget = QTextEdit()
            elif typ.startswith('enum:'):
                enum_name = typ.split(':', 1)[1]
                cb = QComboBox()
                enum_map = ENUMS.get(enum_name, {})
                # show display names, store numeric keys in userData
                for k in sorted(enum_map.keys()):
                    cb.addItem(enum_map[k], k)
                widget = cb
            elif typ.startswith('flags:'):
                flags_name = typ.split(':', 1)[1]
                grp = QGroupBox(name)
                # arrange checkboxes in two columns
                v = QHBoxLayout()
                col1 = QVBoxLayout()
                col2 = QVBoxLayout()
                flag_map = {}
                # prefer explicit maps OPFLAGS / OPFLAGSPLUS from schema if available
                if flags_name == 'OpFlags' and OPFLAGS:
                    flag_map = OPFLAGS
                elif flags_name == 'OpFlagsPlus' and OPFLAGSPLUS:
                    flag_map = OPFLAGSPLUS
                else:
                    flag_map = ENUMS.get(flags_name, {})
                items = []
                if flag_map:
                    # flag_map may be {name: value} (schema) or {value: name} (alternate).
                    for k, vv in flag_map.items():
                        if isinstance(k, int):
                            val = int(k)
                            label = str(vv)
                        else:
                            # k is likely name, vv is numeric
                            try:
                                val = int(vv)
                            except Exception:
                                # fallback: try numeric in key
                                try:
                                    val = int(k)
                                except Exception:
                                    val = 0
                            label = str(k)
                        items.append((val, label))
                # sort by numeric key for stability
                items.sort(key=lambda t: t[0])
                for i, (fk, fv) in enumerate(items):
                    cb = QCheckBox(fv)
                    cb.setProperty('flag_key', fk)
                    # alternate columns
                    if i % 2 == 0:
                        col1.addWidget(cb)
                    else:
                        col2.addWidget(cb)
                v.addLayout(col1)
                v.addLayout(col2)
                grp.setLayout(v)
                widget = grp
            else:
                widget = QLineEdit()

            # Store widget and add to form
            self.controls[idx] = widget
            if typ.startswith('flags:'):
                # Already used name in group
                self.form_layout.addRow(QLabel(name + ':'), widget)
            else:
                self.form_layout.addRow(QLabel(name + ':'), widget)

        # Populate initial file
        if self.file_combo.count() > 0:
            self.on_file_changed(self.file_combo.currentText())

    def _on_file_list_changed(self, current):
        if current is None:
            return
        name = current.text()
        idx = self.file_combo.findText(name)
        if idx >= 0:
            self.file_combo.setCurrentIndex(idx)

    def open_selected_file(self):
        item = self.file_list.currentItem()
        if not item:
            QMessageBox.information(self, 'No selection', 'No file selected in list')
            return
        name = item.text()
        idx = self.file_combo.findText(name)
        if idx >= 0:
            self.file_combo.setCurrentIndex(idx)
            self.on_file_changed(name)

    def reload_files(self):
        self.file_combo.clear()
        self.file_combo.addItems(backend.list_entries(self.lib_path))

    def on_file_changed(self, filename: str):
        if not filename:
            return
        self.current_file = filename
        s_path = self.lib_path / 'data' / 'serverdb' / filename
        try:
            self.rows = backend.load_rows(s_path)
        except Exception as e:
            QMessageBox.warning(self, 'Load error', f'Failed to load {filename}: {e}')
            self.rows = []
        # populate id combo
        self.id_combo.clear()
        for r in self.rows:
            if len(r) > 0 and r[0].strip() != '':
                self.id_combo.addItem(r[0])
        # clear search
        self.id_search.setText('')
        if self.id_combo.count() > 0:
            self.on_id_changed(self.id_combo.currentText())

    def find_id(self):
        key = self.id_search.text().strip()
        if not key:
            return
        idx = self.id_combo.findText(key)
        if idx >= 0:
            self.id_combo.setCurrentIndex(idx)
            return
        QMessageBox.information(self, 'Not found', f'Id {key} not found in current file')

    def on_id_changed(self, idstr: str):
        if not idstr:
            return
        # find row
        for idx, r in enumerate(self.rows):
            if len(r) > 0 and r[0] == idstr:
                self.current_row_idx = idx
                self._populate_form_from_row(r)
                return

    def _populate_form_from_row(self, row: List[str]):
        # Ensure row length
        row_len = max(len(row), max(k for k, *_ in SCHEMA) + 1)
        for idx, name, typ in SCHEMA:
            val = row[idx] if idx < len(row) else ''
            w = self.controls.get(idx)
            if w is None:
                continue
            if isinstance(w, QLineEdit):
                w.setText(val)
            elif isinstance(w, QTextEdit):
                w.setPlainText(val)
            elif hasattr(w, 'addItem') and isinstance(w, QComboBox):
                # find index with userData == int(val)
                try:
                    ival = int(val)
                except Exception:
                    ival = None
                if ival is not None:
                    for i in range(w.count()):
                        if w.itemData(i) == ival:
                            w.setCurrentIndex(i)
                            break
            elif isinstance(w, QGroupBox):
                # flags: set checkboxes inside
                for child in w.findChildren(QCheckBox):
                    fk = child.property('flag_key')
                    try:
                        mask = int(val)
                    except Exception:
                        mask = 0
                    child.setChecked(bool(mask & fk))

    def _gather_row(self) -> List[str]:
        # produce a list of strings aligned with SCHEMA indices
        max_idx = max(idx for idx, *_ in SCHEMA)
        out = [''] * (max_idx + 1)
        for idx, name, typ in SCHEMA:
            w = self.controls.get(idx)
            sval = ''
            if isinstance(w, QLineEdit):
                sval = w.text()
            elif isinstance(w, QTextEdit):
                sval = w.toPlainText()
            elif hasattr(w, 'addItem') and isinstance(w, QComboBox):
                data = w.currentData()
                sval = str(data) if data is not None else ''
            elif isinstance(w, QGroupBox):
                mask = 0
                for child in w.findChildren(QCheckBox):
                    if child.isChecked():
                        fk = child.property('flag_key')
                        mask |= int(fk)
                sval = str(mask)
            else:
                # fallback
                try:
                    sval = str(w.text())
                except Exception:
                    sval = ''
            out[idx] = sval
        return out

    def save_current_row(self):
        if self.current_file is None or self.current_row_idx is None:
            QMessageBox.warning(self, 'No selection', 'No file or row selected')
            return
        newrow = self._gather_row()
        idval = newrow[0]
        # translation fields: Name at col 9, Tip at col 92
        t_name = newrow[9] if len(newrow) > 9 else None
        t_tip = newrow[92] if len(newrow) > 92 else None
        try:
            backend.save_row_and_sync_translations(self.lib_path, self.current_file, idval, newrow,
                                                   t_name=t_name, t_tip=t_tip)
            QMessageBox.information(self, 'Saved', f'Row {idval} saved and translations synced')
        except Exception as e:
            QMessageBox.critical(self, 'Save error', f'Failed to save row: {e}')

    def save_file(self):
        # write full rows to file (backend.save_rows not exported from panel_new; use load/save via paths)
        if self.current_file is None:
            QMessageBox.warning(self, 'No file', 'No file selected')
            return
        s_path = self.lib_path / 'data' / 'serverdb' / self.current_file
        try:
            backend.save_rows(s_path, self.rows)
            QMessageBox.information(self, 'Saved', f'File {self.current_file} saved')
        except Exception as e:
            QMessageBox.critical(self, 'Save error', f'Failed to save file: {e}')


def panel_widget(parent, lib_path: Optional[Path] = None):
    try:
        return ItemsPanel(parent, lib_path=lib_path)
    except Exception:
        return None


def list_entries(lib_path: Path):
    return backend.list_entries(lib_path)
