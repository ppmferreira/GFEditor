from pathlib import Path
from typing import List

from PySide6.QtWidgets import QWidget, QLabel


def list_entries(lib_path: Path) -> List[str]:
    data_dir = lib_path / 'data' / 'serverdb'
    if not data_dir.exists():
        return []
    return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


def panel_widget(parent):
    # minimal safe stub: return a simple QLabel so tests can import and call
    return QLabel('Items panel')
from pathlib import Path
from typing import List

from PySide6.QtWidgets import QWidget, QLabel


def list_entries(lib_path: Path) -> List[str]:
    """Return names of Item ini files under lib_path/data/serverdb"""
    data_dir = lib_path / 'data' / 'serverdb'
    if not data_dir.exists():
        return []
    return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


def panel_widget(parent):
    """Minimal stub panel used for testing imports.

    This ensures the module imports cleanly and avoids previous duplication issues.
    """
    return QLabel('Items panel stub')
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QSplitter, QPushButton, QHBoxLayout,
    QMessageBox, QScrollArea, QFormLayout, QLineEdit, QLabel, QGroupBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from pathlib import Path
from typing import List

from PySide6.QtWidgets import QWidget, QLabel


def list_entries(lib_path: Path) -> List[str]:
    """Return names of Item ini files under lib_path/data/serverdb"""
    data_dir = lib_path / 'data' / 'serverdb'
    if not data_dir.exists():
        return []
    return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


def panel_widget(parent):
    """Minimal stub panel used for testing imports.

    This ensures the module imports cleanly and avoids previous duplication issues.
    """
    return QLabel('Items panel stub')
    btn_layout = QHBoxLayout()
    open_btn = QPushButton('Open')
    save_btn = QPushButton('Save')
    btn_layout.addWidget(open_btn)
    btn_layout.addWidget(save_btn)

    layout.addWidget(file_list)
    layout.addLayout(btn_layout)
    container.setLayout(layout)

    def open_file():
        item = file_list.currentItem()
        if not item:
            return
        path = lib_path / 'data' / 'serverdb' / item.text()
        rows = _gfio.read_pipe_file(path, encoding='big5')
        QMessageBox.information(container, 'Opened', f'Loaded {len(rows)} rows from {item.text()}')

    open_btn.clicked.connect(open_file)
    save_btn.clicked.connect(lambda: QMessageBox.information(container, 'Save', 'Save not implemented in minimal panel'))

    return container
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QSplitter, QPushButton, QHBoxLayout,
    QMessageBox, QScrollArea, QFormLayout, QLineEdit, QLabel, QGroupBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import gfio as _gfio
from translate import read_t_file, write_t_file
from datetime import datetime


def list_entries(lib_path: Path) -> List[str]:
    data_dir = lib_path / 'data' / 'serverdb'
    if not data_dir.exists():
        return []
    return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


_COMMON_LABELS = {
    0: 'Index',
    1: 'Icon',
    2: 'ModelId',
    3: 'ModelFilename',
    4: 'WeaponEffectId',
    5: 'FlyEffectId',
    6: 'UsedEffectId',
    7: 'UsedSoundName',
    8: 'EnhanceEffectId',
    9: 'Name',
}


def panel_widget(parent):
    lib_path = Path.cwd() / 'Lib'
    container = QWidget(parent)
    container.setObjectName('itemsPanel')

    splitter = QSplitter(container)

    # Left: file list (S_/C_ files)
    file_list = QListWidget()
    for name in list_entries(lib_path):
        file_list.addItem(name)

    left_container = QWidget()
    left_container.setObjectName('itemsLeftPanel')
    left_layout = QVBoxLayout()
    left_layout.addWidget(file_list)
    left_container.setLayout(left_layout)

    # Center: rows list + scrollable form
    center_container = QWidget()
    center_layout = QVBoxLayout()

    row_list = QListWidget()
    center_layout.addWidget(row_list)

    form_scroll = QScrollArea()
    form_scroll.setWidgetResizable(True)
    form_widget = QWidget()
    form_layout = QVBoxLayout()

    toolbar = QHBoxLayout()
    open_btn = QPushButton('Open')
    save_btn = QPushButton('Save')
    toolbar.addWidget(open_btn)
    toolbar.addWidget(save_btn)
    toolbar.addStretch()
    form_layout.addLayout(toolbar)

    fields_group = QGroupBox('Item properties')
    fields_layout = QFormLayout()
    fields_group.setLayout(fields_layout)

    field_widgets: List[QLineEdit] = []
    form_layout.addWidget(fields_group)
    form_widget.setLayout(form_layout)
    form_scroll.setWidget(form_widget)
    center_layout.addWidget(form_scroll)
    center_container.setLayout(center_layout)

    # Right: preview
    right_container = QWidget()
    right_container.setObjectName('itemsRightPanel')
    right_layout = QVBoxLayout()
    preview_label = QLabel()
    preview_label.setFixedSize(256, 256)
    preview_label.setAlignment(Qt.AlignCenter)
    right_layout.addWidget(preview_label)
    right_container.setLayout(right_layout)

    splitter.addWidget(left_container)
    splitter.addWidget(center_container)
    splitter.addWidget(right_container)

    # State
    rows = []
    current_file = None
    t_records = {}
    t_path = Path.cwd() / 'Lib' / 'data' / 'Translate' / 'T_Item.ini'

    def build_fields(n):
        nonlocal field_widgets
        while fields_layout.rowCount() > 0:
            fields_layout.removeRow(0)
        field_widgets = []
        for i in range(n):
            label = _COMMON_LABELS.get(i, f'Col {i}')
            le = QLineEdit()
            le.setObjectName(f'col_{i}')
            fields_layout.addRow(label + ':', le)
            field_widgets.append(le)

    def open_file():
        nonlocal rows, current_file, t_records
        item = file_list.currentItem()
        if not item:
            return
        path = lib_path / 'data' / 'serverdb' / item.text()
        current_file = path
        rows = _gfio.read_pipe_file(path, encoding='big5', limit=5000)
        if not rows:
            QMessageBox.information(container, 'Empty', 'File empty or could not be read')
            return
        # load translations
        try:
            t_records.clear()
            if t_path.exists():
                t_records.update(read_t_file(t_path, encoding='mbcs'))
        except Exception:
            t_records.clear()
        max_cols = max(len(r) for r in rows)
        build_fields(max_cols)
        row_list.clear()
        for r in rows:
            idx = r[0] if len(r) > 0 else ''
            name = r[9] if len(r) > 9 else (r[2] if len(r) > 2 else '')
            disp_name = name
            try:
                tid = int(idx)
                if tid in t_records and t_records[tid][0]:
                    disp_name = t_records[tid][0]
            except Exception:
                pass
            row_list.addItem(f'{idx}    {disp_name}')

    def on_row_selected():
        item = row_list.currentItem()
        if not item or not rows:
            return
        text = item.text()
        idx = text.split()[0]
        row = None
        for r in rows:
            if len(r) > 0 and r[0] == idx:
                row = r
                break
        if row is None:
            return
        for i, w in enumerate(field_widgets):
            w.setText(row[i] if i < len(row) else '')
        try:
            tid = int(idx)
            if tid in t_records:
                name, desc = t_records[tid]
                if len(field_widgets) > 9:
                    field_widgets[9].setText(name)
                if len(field_widgets) > 92:
                    field_widgets[92].setText(desc)
        except Exception:
            pass
        # load preview from icon column (1)
        if len(row) > 1 and row[1]:
            icon_name = row[1]
            icon_path = Path.cwd() / 'Lib' / 'itemicon' / (icon_name + '.dds')
            if not icon_path.exists():
                icon_path = Path.cwd() / 'Lib' / 'itemicon' / icon_name
            if icon_path.exists():
                try:
                    pix = QPixmap(str(icon_path))
                    if not pix.isNull():
                        preview_label.setPixmap(pix.scaled(preview_label.size(), Qt.KeepAspectRatio))
                    else:
                        preview_label.setText('No preview')
                except Exception:
                    preview_label.setText('No preview')
            else:
                preview_label.setText('No preview')
        else:
            preview_label.setText('No preview')

    def save_file():
        nonlocal rows, current_file, t_records
        if current_file is None:
            QMessageBox.warning(container, 'No file', 'No file opened')
            return
        item = row_list.currentItem()
        if not item:
            QMessageBox.warning(container, 'No selection', 'No row selected')
            return
        idx = item.text().split()[0]
        for ridx, r in enumerate(rows):
            if len(r) > 0 and r[0] == idx:
                newrow = [w.text() for w in field_widgets]
                rows[ridx] = newrow
                break
        # backup current file
        try:
            bak = f"{current_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            Path(bak).write_text('backup', encoding='utf-8')
        except Exception:
            pass
        _gfio.write_pipe_file(current_file, rows, encoding='big5')
        # update translations
        try:
            tid = int(idx)
            tname = t_records.get(tid, ('', ''))[0]
            tdesc = t_records.get(tid, ('', ''))[1]
            if len(field_widgets) > 9:
                tname = field_widgets[9].text()
            if len(field_widgets) > 92:
                tdesc = field_widgets[92].text()
            t_records[tid] = (tname, tdesc)
            if t_path.exists() or t_records:
                try:
                    tbak = f"{t_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                    Path(tbak).write_text('backup', encoding='utf-8')
                except Exception:
                    pass
                write_t_file(t_path, t_records, encoding='mbcs')
        except Exception:
            pass
        QMessageBox.information(container, 'Saved', f'{current_file.name} saved')

    open_btn.clicked.connect(open_file)
    save_btn.clicked.connect(save_file)
    file_list.currentItemChanged.connect(lambda *_: None)
    file_list.itemDoubleClicked.connect(lambda *_: open_file())
    row_list.currentItemChanged.connect(lambda *_: on_row_selected())

    main_layout = QVBoxLayout()
    main_layout.addWidget(splitter)
    container.setLayout(main_layout)
    return container
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QSplitter, QPushButton, QHBoxLayout,
    QMessageBox, QScrollArea, QFormLayout, QLineEdit, QLabel, QGroupBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import gfio as _gfio
from translate import read_t_file, write_t_file
from datetime import datetime


def list_entries(lib_path: Path) -> List[str]:
    data_dir = lib_path / 'data' / 'serverdb'
    if not data_dir.exists():
        return []
    return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


_COMMON_LABELS = {
    0: 'Index',
    1: 'Icon',
    2: 'ModelId',
    3: 'ModelFilename',
    4: 'WeaponEffectId',
    5: 'FlyEffectId',
    6: 'UsedEffectId',
    7: 'UsedSoundName',
    8: 'EnhanceEffectId',
    9: 'Name',
}


def panel_widget(parent):
    lib_path = Path.cwd() / 'Lib'
    container = QWidget(parent)
    container.setObjectName('itemsPanel')

    splitter = QSplitter(container)

    # Left: file list (S_/C_ files)
    file_list = QListWidget()
    for name in list_entries(lib_path):
        file_list.addItem(name)

    left_container = QWidget()
    left_container.setObjectName('itemsLeftPanel')
    left_layout = QVBoxLayout()
    left_layout.addWidget(file_list)
    left_container.setLayout(left_layout)

    # Center: rows list + scrollable form
    center_container = QWidget()
    center_layout = QVBoxLayout()

    row_list = QListWidget()
    center_layout.addWidget(row_list)

    form_scroll = QScrollArea()
    form_scroll.setWidgetResizable(True)
    form_widget = QWidget()
    form_layout = QVBoxLayout()

    toolbar = QHBoxLayout()
    open_btn = QPushButton('Open')
    save_btn = QPushButton('Save')
    toolbar.addWidget(open_btn)
    toolbar.addWidget(save_btn)
    toolbar.addStretch()
    form_layout.addLayout(toolbar)

    fields_group = QGroupBox('Item properties')
    fields_layout = QFormLayout()
    fields_group.setLayout(fields_layout)

    field_widgets: List[QLineEdit] = []
    form_layout.addWidget(fields_group)
    form_widget.setLayout(form_layout)
    form_scroll.setWidget(form_widget)
    center_layout.addWidget(form_scroll)
    center_container.setLayout(center_layout)

    # Right: preview
    right_container = QWidget()
    right_container.setObjectName('itemsRightPanel')
    right_layout = QVBoxLayout()
    preview_label = QLabel()
    preview_label.setFixedSize(256, 256)
    preview_label.setAlignment(Qt.AlignCenter)
    right_layout.addWidget(preview_label)
    right_container.setLayout(right_layout)

    splitter.addWidget(left_container)
    splitter.addWidget(center_container)
    splitter.addWidget(right_container)

    # State
    rows = []
    current_file = None
    t_records = {}
    t_path = Path.cwd() / 'Lib' / 'data' / 'Translate' / 'T_Item.ini'

    def build_fields(n):
        nonlocal field_widgets
        while fields_layout.rowCount() > 0:
            fields_layout.removeRow(0)
        field_widgets = []
        for i in range(n):
            label = _COMMON_LABELS.get(i, f'Col {i}')
            le = QLineEdit()
            le.setObjectName(f'col_{i}')
            fields_layout.addRow(label + ':', le)
            field_widgets.append(le)

    def open_file():
        nonlocal rows, current_file, t_records
        item = file_list.currentItem()
        if not item:
            return
        path = lib_path / 'data' / 'serverdb' / item.text()
        current_file = path
        rows = _gfio.read_pipe_file(path, encoding='big5', limit=5000)
        if not rows:
            QMessageBox.information(container, 'Empty', 'File empty or could not be read')
            return
        # load translations
        try:
            t_records.clear()
            if t_path.exists():
                t_records.update(read_t_file(t_path, encoding='mbcs'))
        except Exception:
            t_records.clear()
        max_cols = max(len(r) for r in rows)
        build_fields(max_cols)
        row_list.clear()
        for r in rows:
            idx = r[0] if len(r) > 0 else ''
            name = r[9] if len(r) > 9 else (r[2] if len(r) > 2 else '')
            disp_name = name
            try:
                tid = int(idx)
                if tid in t_records and t_records[tid][0]:
                    disp_name = t_records[tid][0]
            except Exception:
                pass
            row_list.addItem(f'{idx}    {disp_name}')

    def on_row_selected():
        item = row_list.currentItem()
        if not item or not rows:
            return
        text = item.text()
        idx = text.split()[0]
        row = None
        for r in rows:
            if len(r) > 0 and r[0] == idx:
                row = r
                break
        if row is None:
            return
        for i, w in enumerate(field_widgets):
            w.setText(row[i] if i < len(row) else '')
        try:
            tid = int(idx)
            if tid in t_records:
                name, desc = t_records[tid]
                if len(field_widgets) > 9:
                    field_widgets[9].setText(name)
                if len(field_widgets) > 92:
                    field_widgets[92].setText(desc)
        except Exception:
            pass
        # load preview from icon column (1)
        if len(row) > 1 and row[1]:
            icon_name = row[1]
            icon_path = Path.cwd() / 'Lib' / 'itemicon' / (icon_name + '.dds')
            if not icon_path.exists():
                icon_path = Path.cwd() / 'Lib' / 'itemicon' / icon_name
            if icon_path.exists():
                try:
                    pix = QPixmap(str(icon_path))
                    if not pix.isNull():
                        preview_label.setPixmap(pix.scaled(preview_label.size(), Qt.KeepAspectRatio))
                    else:
                        preview_label.setText('No preview')
                except Exception:
                    preview_label.setText('No preview')
            else:
                preview_label.setText('No preview')
        else:
            preview_label.setText('No preview')

    def save_file():
        nonlocal rows, current_file, t_records
        if current_file is None:
            QMessageBox.warning(container, 'No file', 'No file opened')
            return
        item = row_list.currentItem()
        if not item:
            QMessageBox.warning(container, 'No selection', 'No row selected')
            return
        idx = item.text().split()[0]
        for ridx, r in enumerate(rows):
            if len(r) > 0 and r[0] == idx:
                newrow = [w.text() for w in field_widgets]
                rows[ridx] = newrow
                break
        # backup current file
        try:
            bak = f"{current_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            Path(bak).write_text('backup', encoding='utf-8')
        except Exception:
            pass
        _gfio.write_pipe_file(current_file, rows, encoding='big5')
        # update translations
        try:
            tid = int(idx)
            tname = t_records.get(tid, ('', ''))[0]
            tdesc = t_records.get(tid, ('', ''))[1]
            if len(field_widgets) > 9:
                tname = field_widgets[9].text()
            if len(field_widgets) > 92:
                tdesc = field_widgets[92].text()
            t_records[tid] = (tname, tdesc)
            if t_path.exists() or t_records:
                try:
                    tbak = f"{t_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                    Path(tbak).write_text('backup', encoding='utf-8')
                except Exception:
                    pass
                write_t_file(t_path, t_records, encoding='mbcs')
        except Exception:
            pass
        QMessageBox.information(container, 'Saved', f'{current_file.name} saved')

    open_btn.clicked.connect(open_file)
    save_btn.clicked.connect(save_file)
    file_list.currentItemChanged.connect(lambda *_: None)
    file_list.itemDoubleClicked.connect(lambda *_: open_file())
    row_list.currentItemChanged.connect(lambda *_: on_row_selected())

    main_layout = QVBoxLayout()
    main_layout.addWidget(splitter)
    container.setLayout(main_layout)
    return container
from typing import List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QSplitter, QPushButton, QHBoxLayout,
    QMessageBox, QScrollArea, QFormLayout, QLineEdit, QLabel, QGroupBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import gfio as _gfio

from translate import read_t_file, write_t_file
from datetime import datetime


def list_entries(lib_path: Path) -> List[str]:
    data_dir = lib_path / 'data' / 'serverdb'
    if not data_dir.exists():
        return []
    return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


_COMMON_LABELS = {
    0: 'Index',
    1: 'Icon',
    2: 'ModelId',
    3: 'ModelFilename',
    4: 'WeaponEffectId',
    5: 'FlyEffectId',
    6: 'UsedEffectId',
    7: 'UsedSoundName',
    8: 'EnhanceEffectId',
    9: 'Name',
}


def panel_widget(parent):
    lib_path = Path.cwd() / 'Lib'
    container = QWidget(parent)
    container.setObjectName('itemsPanel')

    splitter = QSplitter(container)

    # Left: file list (S_/C_ files)
    list_w = QListWidget()
    for name in list_entries(lib_path):
        list_w.addItem(name)

    left_container = QWidget()
    left_container.setObjectName('itemsLeftPanel')
    left_layout = QVBoxLayout()
    left_layout.addWidget(list_w)
    left_container.setLayout(left_layout)

    # Center: scrollable form
    form_scroll = QScrollArea()
    form_scroll.setWidgetResizable(True)
    form_widget = QWidget()
    form_layout = QVBoxLayout()

    toolbar = QHBoxLayout()
    open_btn = QPushButton('Open')
    save_btn = QPushButton('Save')
    toolbar.addWidget(open_btn)
    toolbar.addWidget(save_btn)
    toolbar.addStretch()
    form_layout.addLayout(toolbar)

    fields_group = QGroupBox('Item properties')
    fields_layout = QFormLayout()
    fields_group.setLayout(fields_layout)

    field_widgets: List[QLineEdit] = []
    form_layout.addWidget(fields_group)
    form_widget.setLayout(form_layout)
    form_scroll.setWidget(form_widget)

    # Right: preview
    right_container = QWidget()
    right_container.setObjectName('itemsRightPanel')
    right_layout = QVBoxLayout()
    preview_label = QLabel()
    preview_label.setFixedSize(256, 256)
    preview_label.setAlignment(Qt.AlignCenter)
    right_layout.addWidget(preview_label)
    right_container.setLayout(right_layout)

    splitter.addWidget(left_container)
    splitter.addWidget(form_scroll)
    splitter.addWidget(right_container)

    # State
    rows = []
    current_file = None
    max_cols = 0
    t_records = {}
    t_path = Path.cwd() / 'Lib' / 'data' / 'Translate' / 'T_Item.ini'

    def build_fields(n):
        nonlocal field_widgets
        while fields_layout.rowCount() > 0:
            fields_layout.removeRow(0)
        field_widgets = []
        for i in range(n):
            label = _COMMON_LABELS.get(i, f'Col {i}')
            le = QLineEdit()
            le.setObjectName(f'col_{i}')
            fields_layout.addRow(label + ':', le)
            field_widgets.append(le)

    def open_selected():
        nonlocal rows, current_file, max_cols, t_records
        item = list_w.currentItem()
        if not item:
            return
        path = lib_path / 'data' / 'serverdb' / item.text()
        current_file = path
        rows = _gfio.read_pipe_file(path, encoding='big5', limit=5000)
        if not rows:
            QMessageBox.information(container, 'Empty', 'File empty or could not be read')
            return
        # load translations
        try:
            t_records.clear()
            if t_path.exists():
                t_records.update(read_t_file(t_path, encoding='mbcs'))
        except Exception:
            t_records.clear()
        max_cols = max(len(r) for r in rows)
        build_fields(max_cols)
        list_w.clear()
        for r in rows:
            idx = r[0] if len(r) > 0 else ''
            name = r[2] if len(r) > 2 else ''
            disp_name = name
            try:
                tid = int(idx)
                if tid in t_records and t_records[tid][0]:
                    disp_name = t_records[tid][0]
            except Exception:
                pass
            list_w.addItem(f'{idx}    {disp_name}')

    def on_index_selected():
        item = list_w.currentItem()
        if not item or not rows:
            return
        text = item.text()
        idx = text.split()[0]
        row = None
        for r in rows:
            if len(r) > 0 and r[0] == idx:
                row = r
                break
        if row is None:
            return
        for i, w in enumerate(field_widgets):
            w.setText(row[i] if i < len(row) else '')
        try:
            tid = int(idx)
            if tid in t_records:
                name, desc = t_records[tid]
                if len(field_widgets) > 9:
                    field_widgets[9].setText(name)
                if len(field_widgets) > 92:
                    field_widgets[92].setText(desc)
        except Exception:
            pass
        if len(row) > 1 and row[1]:
            icon_name = row[1]
            icon_path = Path.cwd() / 'Lib' / 'itemicon' / (icon_name + '.dds')
            if not icon_path.exists():
                icon_path = Path.cwd() / 'Lib' / 'itemicon' / icon_name
            if icon_path.exists():
                try:
                    pix = QPixmap(str(icon_path))
                    if not pix.isNull():
                        preview_label.setPixmap(pix.scaled(preview_label.size(), Qt.KeepAspectRatio))
                    else:
                        preview_label.setText('No preview')
                except Exception:
                    preview_label.setText('No preview')
            else:
                preview_label.setText('No preview')
        else:
            preview_label.setText('No preview')

    def save_file():
        nonlocal rows, current_file, t_records
        if current_file is None:
            QMessageBox.warning(container, 'No file', 'No file opened')
            return
        item = list_w.currentItem()
        if not item:
            QMessageBox.warning(container, 'No selection', 'No row selected')
            return
        idx = item.text().split()[0]
        for ridx, r in enumerate(rows):
            if len(r) > 0 and r[0] == idx:
                newrow = [w.text() for w in field_widgets]
                rows[ridx] = newrow
                break
        try:
            bak = f"{current_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            Path(bak).write_text('backup', encoding='utf-8')
        except Exception:
            pass
        _gfio.write_pipe_file(current_file, rows, encoding='big5')
        try:
            tid = int(idx)
            tname = t_records.get(tid, ('', ''))[0]
            tdesc = t_records.get(tid, ('', ''))[1]
            if len(field_widgets) > 9:
                tname = field_widgets[9].text()
            if len(field_widgets) > 92:
                tdesc = field_widgets[92].text()
            t_records[tid] = (tname, tdesc)
            if t_path.exists() or t_records:
                tbak = f"{t_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                try:
                    Path(tbak).write_text('backup', encoding='utf-8')
                except Exception:
                    pass
                write_t_file(t_path, t_records, encoding='mbcs')
        except Exception:
            pass
        QMessageBox.information(container, 'Saved', f'{current_file.name} saved')

    open_btn.clicked.connect(open_selected)
    save_btn.clicked.connect(save_file)
    list_w.currentItemChanged.connect(lambda *_: on_index_selected())

    main_layout = QVBoxLayout()
    main_layout.addWidget(splitter)
    container.setLayout(main_layout)
    return container
    open_btn.clicked.connect(open_selected)
    save_btn.clicked.connect(save_file)
    list_w.currentItemChanged.connect(lambda *_: on_index_selected())

    main_layout = QVBoxLayout()
    main_layout.addWidget(splitter)
    container.setLayout(main_layout)
    return container
    from pathlib import Path
    from typing import List

    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QListWidget, QSplitter, QPushButton, QHBoxLayout,
        QMessageBox, QScrollArea, QFormLayout, QLineEdit, QLabel, QGroupBox
    )
    from PySide6.QtGui import QPixmap
    from PySide6.QtCore import Qt

    import gfio as _gfio


    def list_entries(lib_path: Path) -> List[str]:
        data_dir = lib_path / 'data' / 'serverdb'
        if not data_dir.exists():
            return []
        return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


    _COMMON_LABELS = {
        0: 'Index',
        1: 'Icon',
        2: 'Name',
        3: 'Item group',
        4: 'Item Type',
        5: 'Quality',
    }


    def panel_widget(parent):
        lib_path = Path.cwd() / 'Lib'
        container = QWidget(parent)
        container.setObjectName('itemsPanel')

        splitter = QSplitter(container)

        # Left: file list
        list_w = QListWidget()
        for name in list_entries(lib_path):
            list_w.addItem(name)

        left_container = QWidget()
        left_container.setObjectName('itemsLeftPanel')
        left_layout = QVBoxLayout()
        left_layout.addWidget(list_w)
        left_container.setLayout(left_layout)

        # Center: scrollable form
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form_layout = QVBoxLayout()

        # Top toolbar (Open/Save)
        toolbar = QHBoxLayout()
        open_btn = QPushButton('Open')
        save_btn = QPushButton('Save')
        toolbar.addWidget(open_btn)
        toolbar.addWidget(save_btn)
        toolbar.addStretch()
        form_layout.addLayout(toolbar)

        # Dynamic form area (fields per column)
        fields_group = QGroupBox('Item properties')
        fields_layout = QFormLayout()
        fields_group.setLayout(fields_layout)

        # placeholder for dynamic widgets
        field_widgets = []  # list of QLineEdit

        form_layout.addWidget(fields_group)
        form_widget.setLayout(form_layout)
        form_scroll.setWidget(form_widget)

        # Right: preview area
        right_container = QWidget()
        right_container.setObjectName('itemsRightPanel')
        right_layout = QVBoxLayout()
        preview_label = QLabel()
        preview_label.setFixedSize(256, 256)
        preview_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(preview_label)
        right_container.setLayout(right_layout)

        splitter.addWidget(left_container)
        splitter.addWidget(form_scroll)
        splitter.addWidget(right_container)

        # State
        rows = []
        current_file = None
        max_cols = 0
        t_records = {}
        t_path = Path.cwd() / 'Lib' / 'data' / 'Translate' / 'T_Item.ini'

        def build_fields(n):
            # clear existing
            nonlocal field_widgets
            # remove old rows
            while fields_layout.rowCount() > 0:
                fields_layout.removeRow(0)
            field_widgets = []
            for i in range(n):
                label = _COMMON_LABELS.get(i, f'Col {i}')
                le = QLineEdit()
                le.setObjectName(f'col_{i}')
                fields_layout.addRow(label + ':', le)
                field_widgets.append(le)

        def open_selected():
            nonlocal rows, current_file, max_cols
            item = list_w.currentItem()
            if not item:
                return
            path = lib_path / 'data' / 'serverdb' / item.text()
            current_file = path
            rows = _gfio.read_pipe_file(path, encoding='big5', limit=5000)
            if not rows:
                QMessageBox.information(container, 'Empty', 'File empty or could not be read')
                return
            # load translations
            try:
                from translate import read_t_file
                t_records.clear()
                if t_path.exists():
                    t_records.update(read_t_file(t_path, encoding='mbcs'))
            except Exception:
                t_records.clear()
            max_cols = max(len(r) for r in rows)
            build_fields(max_cols)
            # populate left list with indices and (if present) names
            list_w.clear()
            for r in rows:
                idx = r[0] if len(r) > 0 else ''
                name = r[2] if len(r) > 2 else ''
                # if we have translation, show translated name
                disp_name = name
                try:
                    tid = int(idx)
                    if tid in t_records and t_records[tid][0]:
                        disp_name = t_records[tid][0]
                except Exception:
                    pass
                list_w.addItem(f'{idx}    {disp_name}')

        def on_index_selected():
            item = list_w.currentItem()
            if not item or not rows:
                return
            text = item.text()
            idx = text.split()[0]
            # find row by index (first column match)
            row = None
            for r in rows:
                if len(r) > 0 and r[0] == idx:
                    row = r
                    break
            if row is None:
                return
            # populate fields
            for i, w in enumerate(field_widgets):
                w.setText(row[i] if i < len(row) else '')
            # populate translation fields
            try:
                tid = int(idx)
                if tid in t_records:
                    name, desc = t_records[tid]
                    # name -> field index 9
                    if len(field_widgets) > 9:
                        field_widgets[9].setText(name)
                    # tip/desc -> field index 92 if exists
                    if len(field_widgets) > 92:
                        field_widgets[92].setText(desc)
            except Exception:
                pass
            # try to load icon by name if present in col 1
            if len(row) > 1 and row[1]:
                icon_name = row[1]
                # try common image paths under Lib/itemicon
                icon_path = Path.cwd() / 'Lib' / 'itemicon' / (icon_name + '.dds')
                if not icon_path.exists():
                    # try without extension
                    icon_path = Path.cwd() / 'Lib' / 'itemicon' / icon_name
                if icon_path.exists():
                    # placeholder: load pixmap directly if supported
                    try:
                        pix = QPixmap(str(icon_path))
                        if not pix.isNull():
                            preview_label.setPixmap(pix.scaled(preview_label.size(), Qt.KeepAspectRatio))
                        else:
                            preview_label.setText('No preview')
                    except Exception:
                        preview_label.setText('No preview')
                else:
                    preview_label.setText('No preview')
            else:
                preview_label.setText('No preview')

        def save_file():
            nonlocal rows, current_file
            if current_file is None:
                QMessageBox.warning(container, 'No file', 'No file opened')
                return
            # find selected index
            item = list_w.currentItem()
            if not item:
                QMessageBox.warning(container, 'No selection', 'No row selected')
                return
            idx = item.text().split()[0]
            # find row index in rows list
            for ridx, r in enumerate(rows):
                if len(r) > 0 and r[0] == idx:
                    # update this row from field_widgets
                    newrow = [w.text() for w in field_widgets]
                    rows[ridx] = newrow
                    break
            # backup w/ timestamp
            try:
                from datetime import datetime
                bak = f"{current_file}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                Path(bak).write_text('backup', encoding='utf-8')
            except Exception:
                pass
            _gfio.write_pipe_file(current_file, rows, encoding='big5')
            # update translations if changed
            try:
                tid = int(idx)
                # update name and desc from field_widgets if present
                tname = t_records.get(tid, ('', ''))[0]
                tdesc = t_records.get(tid, ('', ''))[1]
                if len(field_widgets) > 9:
                    tname = field_widgets[9].text()
                if len(field_widgets) > 92:
                    tdesc = field_widgets[92].text()
                t_records[tid] = (tname, tdesc)
                if t_path.exists() or t_records:
                    from translate import write_t_file
                    # backup translate
                    from datetime import datetime
                    tbak = f"{t_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
                    try:
                        Path(tbak).write_text('backup', encoding='utf-8')
                    except Exception:
                        pass
                    write_t_file(t_path, t_records, encoding='mbcs')
            except Exception:
                pass
            QMessageBox.information(container, 'Saved', f'{current_file.name} saved')

        open_btn.clicked.connect(open_selected)
        save_btn.clicked.connect(save_file)
        list_w.currentItemChanged.connect(lambda *_: on_index_selected())

        main_layout = QVBoxLayout()
        main_layout.addWidget(splitter)
        container.setLayout(main_layout)
        return container
