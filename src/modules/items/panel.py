from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea,
    QLineEdit, QTextEdit, QFormLayout, QGroupBox, QGridLayout, QCheckBox,
    QTableWidgetItem
)
from PySide6.QtCore import Qt
from pathlib import Path
import gfio


def panel_widget(parent):
    """Return a module-specific panel for items. The panel is self-contained
    and can open a detailed item editor in the main splitter area.

    `parent` is the MainWindow instance; we will use its splitter to show
    the editor widget.
    """
    w = QWidget()
    layout = QVBoxLayout()
    title = QLabel('<b>Items Module</b>')
    title.setAlignment(Qt.AlignLeft)
    layout.addWidget(title)

    btn_row = QHBoxLayout()
    btn_item = QPushButton('Editar Item')
    btn_itemmall = QPushButton('Editar ItemMall')
    btn_row.addWidget(btn_item)
    btn_row.addWidget(btn_itemmall)
    layout.addLayout(btn_row)

    info = QLabel('Use the buttons above to open the item editors (client/server pair aware).')
    info.setWordWrap(True)
    layout.addWidget(info)
    layout.addStretch()

    def _find_client_server_pair(base: str):
        lib_path = getattr(parent, 'lib_path', Path.cwd() / 'Lib')
        db_dir = Path(lib_path) / 'data' / 'db'
        server_dir = Path(lib_path) / 'data' / 'serverdb'
        client_candidates = list(db_dir.glob(f"{base}*.ini")) + list(db_dir.glob(f"{base}*.txt"))
        if not client_candidates:
            client_candidates = list(db_dir.glob(f"{base}*"))
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


    def open_editor_for(base: str):
        client_path, server_path = _find_client_server_pair(base)
        if client_path is None:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(parent, 'Not found', f'Client {base} file not found under Lib/data/db')
            return

        try:
            client_rows = gfio.read_pipe_file(client_path, encoding='big5', expected_fields=93)
        except Exception as exc:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(parent, 'Read error', f'Failed to read client file: {exc}')
            return

        server_rows = None
        if server_path:
            try:
                server_rows = gfio.read_pipe_file(server_path, encoding='big5', expected_fields=93)
            except Exception:
                server_rows = None

        # derive header from DEFAULT_HEADER in reader
        try:
            from . import reader as items_reader
            header = items_reader.DEFAULT_HEADER.copy()
        except Exception:
            header = [f'col{i}' for i in range(93)]

        # Build editor widget (simplified version of MainWindow's builder)
        editor = build_item_editor_widget(parent, client_rows, header)

        # insert into main splitter (replace right pane)
        splitter = parent._find_splitter()
        if splitter is None:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(parent, 'UI error', 'Cannot find layout splitter')
            return
        old = splitter.widget(1)
        splitter.insertWidget(1, editor)
        if old is not None:
            old.setParent(None)


    def on_item():
        open_editor_for('C_Item')


    def on_itemmall():
        open_editor_for('C_ItemMall')


    btn_item.clicked.connect(on_item)
    btn_itemmall.clicked.connect(on_itemmall)

    w.setLayout(layout)
    return w


def build_item_editor_widget(parent, rows, header):
    """Create a detailed editor widget for the provided rows and header.

    Supports selecting any record (by index or ID), next/prev navigation, and
    writes back changes into the `rows` list. The parent table (if present)
    will be updated on save.
    """
    container = QWidget()
    main_layout = QVBoxLayout()

    # state
    state = {
        'rows': rows,
        'header': header,
        'index': 0
    }

    # Top controls: selector + prev/next
    ctrl_row = QHBoxLayout()
    from PySide6.QtWidgets import QComboBox
    selector = QComboBox()
    def _display_label_for_row(idx):
        r = rows[idx]
        name = r[9] if len(r) > 9 else ''
        idv = r[0] if len(r) > 0 else str(idx)
        return f"{idx}: {idv} - {name}"

    for i in range(len(rows)):
        selector.addItem(_display_label_for_row(i))

    btn_prev = QPushButton('< Prev')
    btn_next = QPushButton('Next >')
    ctrl_row.addWidget(btn_prev)
    ctrl_row.addWidget(selector)
    ctrl_row.addWidget(btn_next)
    main_layout.addLayout(ctrl_row)

    # editor area (two columns)
    body = QWidget()
    body_layout = QHBoxLayout()
    body.setLayout(body_layout)

    # Left column: icon, id, name, description
    left_v = QVBoxLayout()
    icon_label = QLabel()
    icon_label.setFixedSize(128, 128)
    icon_label.setStyleSheet('background: #f0f5f8; border: 1px solid #dfeaf0;')
    id_field = QLineEdit()
    id_field.setReadOnly(True)
    name_field = QLineEdit()
    desc = QTextEdit()
    desc.setFixedHeight(140)
    left_v.addWidget(icon_label)
    left_v.addWidget(QLabel('ID:'))
    left_v.addWidget(id_field)
    left_v.addWidget(QLabel('Name:'))
    left_v.addWidget(name_field)
    left_v.addWidget(QLabel('Description:'))
    left_v.addWidget(desc)

    body_layout.addLayout(left_v)

    # Right column: param groups
    right_v = QVBoxLayout()
    gp_main = QGroupBox('Main Parameters')
    grid_main = QGridLayout()
    sample_fields = ['MaxHp', 'MaxMp', 'Str', 'Con', 'Int', 'Dex', 'Attack', 'AttackSpeed']
    widgets = {}
    r = 0
    c = 0
    for fld in sample_fields:
        try:
            idx = header.index(fld)
        except Exception:
            idx = None
        le = QLineEdit()
        widgets[fld] = (idx, le)
        grid_main.addWidget(QLabel(fld+':'), r, c*2)
        grid_main.addWidget(le, r, c*2+1)
        c += 1
        if c >= 2:
            c = 0
            r += 1
    gp_main.setLayout(grid_main)
    right_v.addWidget(gp_main)

    # Save buttons
    btn_row = QHBoxLayout()
    btn_save = QPushButton('Save')
    btn_save_close = QPushButton('Save and Close')
    btn_save_disk = QPushButton('Save to Disk')
    btn_row.addWidget(btn_save)
    btn_row.addWidget(btn_save_close)
    btn_row.addWidget(btn_save_disk)
    right_v.addLayout(btn_row)

    body_layout.addLayout(right_v)
    main_layout.addWidget(body)

    # helper to load a given index into widgets
    def load_index(idx):
        if idx < 0 or idx >= len(rows):
            return
        state['index'] = idx
        r = rows[idx]
        # icon
        icon_name = r[1] if len(r) > 1 else ''
        try:
            if icon_name:
                icon_path = Path(getattr(parent, 'lib_path', Path.cwd() / 'Lib')) / 'itemicon' / icon_name
                if icon_path.exists():
                    from PySide6.QtGui import QPixmap
                    pix = QPixmap(str(icon_path))
                    if pix and not pix.isNull():
                        icon_label.setPixmap(pix.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    else:
                        icon_label.setText(icon_name)
                        icon_label.setAlignment(Qt.AlignCenter)
                else:
                    icon_label.setText(icon_name or 'No Icon')
                    icon_label.setAlignment(Qt.AlignCenter)
            else:
                icon_label.setText('')
        except Exception:
            icon_label.setText(icon_name or '')

        id_field.setText(r[0] if len(r) > 0 else '')
        name_field.setText(r[9] if len(r) > 9 else '')
        desc.setPlainText(r[92] if len(r) > 92 else '')
        for fld, (idx, w) in widgets.items():
            if idx is None:
                w.setText('')
            else:
                w.setText(r[idx] if idx < len(r) else '')
        # update selector display text
        selector.setItemText(idx, _display_label_for_row(idx))
        selector.setCurrentIndex(idx)

    def save_current(close_after=False, write_disk=False):
        idx = state['index']
        r = rows[idx]
        # ensure length
        while len(r) <= 92:
            r.append('')
        r[9] = name_field.text()
        r[92] = desc.toPlainText()
        for fld, (colidx, w) in widgets.items():
            if colidx is None:
                continue
            while len(r) <= colidx:
                r.append('')
            r[colidx] = w.text()

        # update parent's table if present
        try:
            table = getattr(parent, 'table', None)
            if table is not None:
                sel_row = None
                if hasattr(table, 'currentRow'):
                    try:
                        sel_row = table.currentRow()
                    except Exception:
                        sel_row = None
                # fall back to 0 if unknown
                target_table_row = sel_row if (sel_row is not None and sel_row >= 0) else 0
                for col in range(table.columnCount()):
                    val = r[col] if col < len(r) else ''
                    table.setItem(target_table_row, col, QTableWidgetItem(val))
        except Exception:
            pass

        if write_disk:
            try:
                parent.save_file()
            except Exception:
                pass

        # refresh selector label
        selector.setItemText(idx, _display_label_for_row(idx))
        if close_after:
            try:
                parent._show_rows_in_table_panel(header, rows)
            except Exception:
                pass

    # connections
    def on_prev():
        i = max(0, state['index'] - 1)
        load_index(i)

    def on_next():
        i = min(len(rows) - 1, state['index'] + 1)
        load_index(i)

    def on_selector_changed(idx):
        load_index(idx)

    btn_prev.clicked.connect(on_prev)
    btn_next.clicked.connect(on_next)
    selector.currentIndexChanged.connect(on_selector_changed)
    btn_save.clicked.connect(lambda: save_current(False, False))
    btn_save_close.clicked.connect(lambda: save_current(True, False))
    btn_save_disk.clicked.connect(lambda: save_current(True, True))

    # If parent.table has a selection, try to open that row
    try:
        table = getattr(parent, 'table', None)
        if table is not None:
            sel = None
            try:
                sel = table.currentRow()
            except Exception:
                sel = None
            if sel is not None and 0 <= sel < len(rows):
                load_index(sel)
            else:
                load_index(0)
        else:
            load_index(0)
    except Exception:
        load_index(0)

    container.setLayout(main_layout)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(container)
    return scroll
