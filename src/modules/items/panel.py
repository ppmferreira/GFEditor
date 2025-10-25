"""Professional Item Editor Panel with Tabs and Advanced Features."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea,
    QLineEdit, QTextEdit, QFormLayout, QGroupBox, QGridLayout, QCheckBox,
    QTableWidgetItem, QComboBox, QMessageBox, QSpinBox, QTabWidget,
    QDoubleSpinBox, QTableWidget, QHeaderView, QAbstractItemView, QDialog, QFileDialog
)
from PySide6.QtCore import Qt, QCoreApplication, QSettings
from PySide6.QtGui import QPixmap, QImage
from pathlib import Path
import io
import subprocess
import shutil
import tempfile
import gfio
from . import flags as item_flags
from . import translate as item_translate
import re


def panel_widget(parent):
    """Return a professional item editor panel with tabs and advanced features."""
    w = QWidget()
    layout = QVBoxLayout()
    title = QLabel('<b>Items Module - Professional Editor</b>')
    title.setAlignment(Qt.AlignLeft)
    layout.addWidget(title)

    btn_row = QHBoxLayout()
    btn_item = QPushButton('Editar Item')
    btn_itemmall = QPushButton('Editar ItemMall')
    btn_row.addWidget(btn_item)
    btn_row.addWidget(btn_itemmall)
    layout.addLayout(btn_row)

    info = QLabel('Use the buttons above to open the professional item editor.')
    info.setWordWrap(True)
    layout.addWidget(info)
    layout.addStretch()

    def _find_client_server_pair(base: str):
        lib_path = getattr(parent, 'lib_path', Path.cwd() / 'Assets')
        db_dir = Path(lib_path) / 'Client'
        server_dir = Path(lib_path) / 'Server'
        
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
            QMessageBox.warning(parent, 'Not found', f'Client {base} file not found')
            return

        try:
            client_rows = gfio.read_pipe_file(client_path, encoding='big5', expected_fields=93)
        except Exception as exc:
            QMessageBox.critical(parent, 'Read error', f'Failed to read: {exc}')
            return

        server_rows = None
        if server_path:
            try:
                server_rows = gfio.read_pipe_file(server_path, encoding='big5', expected_fields=93)
            except Exception:
                server_rows = None

        try:
            from . import reader as items_reader
            header = items_reader.DEFAULT_HEADER.copy()
        except Exception:
            header = [f'col{i}' for i in range(93)]

        editor = build_professional_editor(parent, client_rows, header, base)

        splitter = parent._find_splitter()
        if splitter is None:
            QMessageBox.warning(parent, 'UI error', 'Cannot find layout splitter')
            return
        old = splitter.widget(1)
        splitter.insertWidget(1, editor)
        if old is not None:
            old.setParent(None)

    btn_item.clicked.connect(lambda: open_editor_for('C_Item'))
    btn_itemmall.clicked.connect(lambda: open_editor_for('C_ItemMall'))

    w.setLayout(layout)
    return w


def build_professional_editor(parent, rows, header, source_base=None):
    """Build a professional multi-tab item editor."""
    container = QWidget()
    # Normalize header: if header doesn't match expected DEFAULT_HEADER length,
    # prefer the canonical DEFAULT_HEADER to keep field-to-widget mapping stable.
    try:
        from . import reader as items_reader
        expected_len = len(items_reader.DEFAULT_HEADER)
        if header is None or len(header) != expected_len:
            header = items_reader.DEFAULT_HEADER.copy()
    except Exception:
        # if import fails, leave header as-is
        pass
    # name the widget so the stylesheet targets only this editor panel
    # keep objectName so global qss (src/style/style.qss) can target it
    container.setObjectName('item_panel')
    main_layout = QVBoxLayout()

    # keep a reference to parent so sub-widgets can access app paths/settings
    state = {'rows': rows, 'header': header, 'index': 0, 'parent': parent, 'source_base': source_base}

    # application settings (persist UI preferences like the RestrictClass mode)
    try:
        settings = QSettings('GFEditor', 'GFEditor')
        state['settings'] = settings
    except Exception:
        state['settings'] = None

    # create a per-run cache directory for converted icons (DDS -> PNG)
    try:
        icon_cache_dir = Path(tempfile.mkdtemp(prefix='gfeditor_icons_'))
        state['icon_cache_dir'] = str(icon_cache_dir)
        app = QCoreApplication.instance()
        if app is not None:
            # remove cache when application quits
            try:
                app.aboutToQuit.connect(lambda: shutil.rmtree(icon_cache_dir, ignore_errors=True))
            except Exception:
                pass
    except Exception:
        state['icon_cache_dir'] = None

    # ============= TOP CONTROLS =============
    ctrl_row = QHBoxLayout()
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
    btn_search = QPushButton('Search Item')
    btn_csv = QPushButton('View CSV')
    
    ctrl_row.addWidget(QLabel('Item:'))
    ctrl_row.addWidget(btn_prev)
    ctrl_row.addWidget(selector)
    ctrl_row.addWidget(btn_next)
    ctrl_row.addWidget(btn_search)
    ctrl_row.addWidget(btn_csv)
    # debug/info label to help trace which source was used to build this editor
    info_label = QLabel('')
    info_label.setObjectName('item_editor_info')
    ctrl_row.addWidget(info_label)
    ctrl_row.addStretch()
    main_layout.addLayout(ctrl_row)

    # ============= TABS =============
    tabs = QTabWidget()

    # TAB 1: BASIC INFO
    tab_basic = create_tab_basic(rows, header, state)
    tabs.addTab(tab_basic, "Basic Info")

    # TAB 2: PARAMETERS
    tab_params = create_tab_parameters(rows, header, state)
    tabs.addTab(tab_params, "Parameters")

    # TAB 3: FLAGS & RESTRICTIONS
    tab_flags = create_tab_flags_restrictions(rows, header, state)
    tabs.addTab(tab_flags, "Flags & Restrictions")

    # TAB 4: ENCHANT & SPECIAL
    tab_enchant = create_tab_enchant_special(rows, header, state)
    tabs.addTab(tab_enchant, "Enchant & Special")

    # TAB 5: ADVANCED
    tab_advanced = create_tab_advanced(rows, header, state)
    tabs.addTab(tab_advanced, "Advanced")

    # TAB 6: TRANSLATE
    tab_translate = item_translate.create_tab_translate(rows, header, state)
    tabs.addTab(tab_translate, "Translate")

    # (Removed Other/Raw tab - raw fields are no longer shown in a separate tab)

    main_layout.addWidget(tabs)

    # ============= SAVE BUTTONS =============
    btn_row = QHBoxLayout()
    btn_save = QPushButton('Save')
    btn_save_close = QPushButton('Save and Close')
    btn_save_disk = QPushButton('Save to Disk')
    btn_compare = QPushButton('Compare')
    
    btn_row.addWidget(btn_save)
    btn_row.addWidget(btn_save_close)
    btn_row.addWidget(btn_save_disk)
    btn_row.addWidget(btn_compare)
    btn_row.addStretch()
    main_layout.addLayout(btn_row)

    # ============= LOAD LOGIC =============
    def load_index(idx):
        if idx < 0 or idx >= len(rows):
            return
        state['index'] = idx
        selector.setCurrentIndex(idx)
        
        # Update all tabs
        update_tab_basic(tab_basic, rows[idx], header, state)
        update_tab_parameters(tab_params, rows[idx], header, state)
        update_tab_flags_restrictions(tab_flags, rows[idx], header, state)
        update_tab_enchant_special(tab_enchant, rows[idx], header, state)
        update_tab_advanced(tab_advanced, rows[idx], header, state)
        # Update translate tab (shows name/description from Assets/Translate)
        try:
            item_translate.update_tab_translate(tab_translate, rows[idx], header, state)
        except Exception:
            pass

    def save_current(close_after=False, write_disk=False):
        idx = state['index']
        r = rows[idx]
        while len(r) <= 92:
            r.append('')

        # Save from all tabs
        save_tab_basic(tab_basic, r, header)
        save_tab_parameters(tab_params, r, header)
        save_tab_flags_restrictions(tab_flags, r, header)
        save_tab_enchant_special(tab_enchant, r, header)
        save_tab_advanced(tab_advanced, r, header)

        # Update parent table
        try:
            table = getattr(parent, 'table', None)
            if table is not None:
                sel_row = table.currentRow() if hasattr(table, 'currentRow') else 0
                for col in range(table.columnCount()):
                    val = r[col] if col < len(r) else ''
                    table.setItem(sel_row, col, QTableWidgetItem(val))
        except Exception:
            pass

        if write_disk:
            try:
                parent.save_file()
            except Exception:
                pass

        selector.setItemText(idx, _display_label_for_row(idx))
        
        if close_after:
            try:
                parent._show_rows_in_table_panel(header, rows)
            except Exception:
                pass

    # ============= CONNECTIONS =============
    btn_prev.clicked.connect(lambda: load_index(max(0, state['index'] - 1)))
    btn_next.clicked.connect(lambda: load_index(min(len(rows) - 1, state['index'] + 1)))
    selector.currentIndexChanged.connect(load_index)
    btn_save.clicked.connect(lambda: save_current(False, False))
    btn_save_close.clicked.connect(lambda: save_current(True, False))
    btn_save_disk.clicked.connect(lambda: save_current(True, True))
    btn_search.clicked.connect(lambda: show_search_dialog(rows, load_index))
    btn_compare.clicked.connect(lambda: QMessageBox.info(parent, 'Compare', 'Compare feature coming soon!'))
    # CSV viewer: show all rows as CSV in a dialog
    def show_csv():
        try:
            # prepare table data
            tbl = QTableWidget()
            tbl.setColumnCount(len(header))
            tbl.setHorizontalHeaderLabels(list(header))
            tbl.setRowCount(len(rows))
            for ri, r in enumerate(rows):
                for ci in range(len(header)):
                    val = r[ci] if ci < len(r) else ''
                    tbl.setItem(ri, ci, QTableWidgetItem(str(val)))
            tbl.setAlternatingRowColors(True)
            # size columns to contents so headers and cells are visible; allow horizontal scroll
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        except Exception as exc:
            QMessageBox.warning(parent, 'CSV error', f'Failed to build table: {exc}')
            return

        # show a modal dialog that contains only the table (and a Close button)
        dlg = QDialog(parent)
        dlg.setWindowTitle('CSV Table View')
        dlg.setMinimumSize(1000, 700)
        v = QVBoxLayout()
        v.addWidget(tbl)

        btn_close = QPushButton('Close')
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        v.addLayout(btn_row)

        dlg.setLayout(v)

        btn_close.clicked.connect(dlg.accept)
        dlg.exec()

    btn_csv.clicked.connect(show_csv)

    try:
        table = getattr(parent, 'table', None)
        if table is not None:
            sel = table.currentRow() if hasattr(table, 'currentRow') else 0
            load_index(sel if 0 <= sel < len(rows) else 0)
        else:
            load_index(0)
    except Exception:
        load_index(0)

    # populate info label with source and row count for debugging/consistency checks
    try:
        sb = state.get('source_base') or source_base
        info_label.setText(f"Source: {sb or 'unknown'}  Rows: {len(rows)}")
    except Exception:
        pass

    container.setLayout(main_layout)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(container)
    return scroll


# ============= TAB 1: BASIC INFO =============
def create_tab_basic(rows, header, state):
    tab = QWidget()
    layout = QVBoxLayout()

    # Left: Icon preview (wrapped in a widget with fixed width so layout is stable)
    left = QVBoxLayout()
    icon_label = QLabel()
    icon_label.setFixedSize(200, 200)
    icon_label.setStyleSheet('background: #1a2a3a; border: 2px solid #00d4ff;')
    icon_label.setAlignment(Qt.AlignCenter)
    left.addWidget(QLabel('<b>Icon Preview</b>'))
    left.addWidget(icon_label)
    left.addStretch()
    left_widget = QWidget()
    left_widget.setLayout(left)
    left_widget.setFixedWidth(240)  # give a bit of padding beyond the icon size

    # Right: Basic fields (wrap QFormLayout in a QWidget so we can control stretch)
    right = QFormLayout()
    right_widget = QWidget()
    
    fields_basic = {
        'Id': ('ID', QLineEdit()),
        'Name': ('Name', QLineEdit()),
        'IconFilename': ('Icon File', QLineEdit()),
        'ItemType': ('Item Type', QComboBox()),
        'ItemQuality': ('Quality', QComboBox()),
        'Target': ('Target', QComboBox()),
        'MaxStack': ('Max Stack', QSpinBox()),
        'ShopPriceType': ('Shop Price Type', QSpinBox()),
        'SysPrice': ('Sys Price', QSpinBox()),
        'WeaponEffectId': ('Weapon Effect ID', QSpinBox()),
        'FlyEffectId': ('Fly Effect ID', QSpinBox()),
    # 'Tip' is the header column name in files; label it as 'Description' in UI
    'Tip': ('Description', QTextEdit()),
    }

    # Setup combo boxes
    fields_basic['ItemType'][1].addItems([''] + list(item_flags.ITEM_TYPE.values()))
    fields_basic['ItemQuality'][1].addItems([''] + list(item_flags.QUALITY.values()))
    fields_basic['Target'][1].addItems([''] + list(item_flags.TARGET.values()))

    tab.widgets_basic = {}
    for key, (label, widget) in fields_basic.items():
        if isinstance(widget, QSpinBox):
            widget.setMaximum(999999)
        elif isinstance(widget, QComboBox):
            pass
        tab.widgets_basic[key] = widget
        right.addRow(label, widget)

    tab.icon_label = icon_label

    body = QHBoxLayout()
    # add the fixed-width left widget and the expanding right widget
    right_widget.setLayout(right)
    body.addWidget(left_widget)
    body.addWidget(right_widget)
    # ensure right_widget expands and left_widget stays fixed
    body.setStretch(0, 0)
    body.setStretch(1, 1)
    layout.addLayout(body)
    layout.addStretch()
    
    tab.setLayout(layout)
    return tab


def update_tab_basic(tab, row, header, state):
    for key, widget in tab.widgets_basic.items():
        try:
            idx = header.index(key)
            val = row[idx] if idx < len(row) else ''
            
            if isinstance(widget, QSpinBox):
                widget.setValue(int(val) if val and val.isdigit() else 0)
            elif isinstance(widget, QComboBox):
                if key == 'ItemType':
                    name = item_flags.get_item_type_name(int(val)) if val.isdigit() else val
                elif key == 'ItemQuality':
                    name = item_flags.get_quality_name(int(val)) if val.isdigit() else val
                elif key == 'Target':
                    name = item_flags.get_target_name(int(val)) if val.isdigit() else val
                else:
                    name = val
                idx_combo = widget.findText(name) if name else 0
                widget.setCurrentIndex(max(0, idx_combo))
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(val)
            else:
                # If Name is empty, try Translate files as fallback (T_Item or T_ItemMall)
                if key == 'Name' and (val is None or str(val).strip() == ''):
                    try:
                        src = state.get('source_base') or ''
                        translate_name = 'T_Item.ini'
                        s = str(src).lower()
                        if 'itemmall' in s or 'item_mall' in s:
                            translate_name = 'T_ItemMall.ini'
                        lib_base = Path(getattr(state.get('parent'), 'lib_path', Path.cwd() / 'Assets'))
                        tr = item_translate.get_translation(translate_name, row[0] if len(row) > 0 else '', lib_base=lib_base)
                        if tr and tr[0]:
                            widget.setText(tr[0])
                        else:
                            widget.setText(val)
                    except Exception:
                        widget.setText(val)
                else:
                    widget.setText(val)
        except:
            pass
        
        # Update icon preview
        if key == 'IconFilename':
            try:
                # prefer the value in the widget; fallback to header lookup
                icon_name = ''
                try:
                    if isinstance(widget, QLineEdit):
                        icon_name = widget.text()
                except Exception:
                    pass
                if not icon_name:
                    try:
                        idx_icon = header.index('IconFilename')
                        icon_name = row[idx_icon] if idx_icon < len(row) else ''
                    except Exception:
                        icon_name = ''

                lib_base = Path(getattr(state.get('parent'), 'lib_path', Path.cwd() / 'Assets'))
                icon_dir = lib_base / 'itemicon'
                icon_path = None

                # resolve icon path: respect provided filename, try common extensions and case variants
                if icon_name:
                    tentative = icon_dir / icon_name
                    if tentative.exists():
                        icon_path = tentative
                    else:
                        # if icon_name already has an extension, try common case variants
                        suffix = Path(icon_name).suffix
                        if suffix:
                            # try lowercase/uppercase replacement
                            for ext in (suffix.lower(), suffix.upper()):
                                p2 = icon_dir / (Path(icon_name).stem + ext)
                                if p2.exists():
                                    icon_path = p2
                                    break
                        # try adding common extensions if none matched
                        if icon_path is None:
                            for ext in ('.dds', '.DDS', '.png', '.bmp', '.jpg', '.jpeg', '.gif'):
                                p2 = icon_dir / (icon_name + ext) if not Path(icon_name).suffix else icon_dir / (Path(icon_name).stem + ext)
                                if p2.exists():
                                    icon_path = p2
                                    break

                # if we found a candidate file, try to load it; prefer QPixmap, but use Pillow or external tools for DDS
                if icon_path and icon_path.exists():
                    loaded = False
                    # prepare cache path (use mtime to invalidate when file changes)
                    cache_png = None
                    try:
                        cache_root = state.get('icon_cache_dir')
                        if cache_root:
                            cache_root = Path(cache_root)
                            cache_png = cache_root / f"{icon_path.stem}_{icon_path.stat().st_mtime_ns}.png"
                    except Exception:
                        cache_png = None

                    # if cached PNG exists, load it quickly
                    if cache_png is not None and cache_png.exists():
                        try:
                            pix = QPixmap(str(cache_png))
                            if not pix.isNull():
                                tab.icon_label.setPixmap(pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                                tab.icon_label.setToolTip(str(cache_png))
                                loaded = True
                        except Exception:
                            loaded = False
                    try:
                        pix = QPixmap(str(icon_path))
                        if not pix.isNull():
                            tab.icon_label.setPixmap(pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                            tab.icon_label.setToolTip(str(icon_path))
                            loaded = True
                    except Exception:
                        loaded = False

                    if not loaded:
                        # Try Pillow as a robust fallback (supports DDS with plugin)
                        try:
                            from PIL import Image
                            im = Image.open(str(icon_path))
                            im = im.convert('RGBA')
                            w, h = im.size
                            # raw bytes in RGBA order
                            data = im.tobytes('raw', 'RGBA')
                            # try preferred Qt formats; fall back safely
                            try:
                                qimg = QImage(data, w, h, QImage.Format_RGBA8888)
                            except Exception:
                                try:
                                    qimg = QImage(data, w, h, QImage.Format_RGBA8888_Premultiplied)
                                except Exception:
                                    # last resort: use ARGB32 (may require byte order adjustments depending on platform)
                                    qimg = QImage(data, w, h, QImage.Format_ARGB32)
                            pix2 = QPixmap.fromImage(qimg)
                            if not pix2.isNull():
                                # save converted PNG to cache if available
                                try:
                                    if cache_png is not None:
                                        im.save(str(cache_png), format='PNG')
                                        tab.icon_label.setToolTip(str(cache_png))
                                    else:
                                        tab.icon_label.setToolTip(str(icon_path))
                                except Exception:
                                    tab.icon_label.setToolTip(str(icon_path))
                                tab.icon_label.setPixmap(pix2.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                                loaded = True
                        except Exception:
                            loaded = False
                            # Pillow failed to open (likely DDS unsupported). Try external converters if present.
                            try:
                                # Prefer ImageMagick 'magick' which can output PNG to stdout
                                magick = shutil.which('magick')
                                if magick:
                                    # write direct to cache_png when possible
                                    if cache_png is not None:
                                        try:
                                            subprocess.run([magick, str(icon_path), str(cache_png)], check=True)
                                            if cache_png.exists():
                                                pix2 = QPixmap(str(cache_png))
                                                if not pix2.isNull():
                                                    tab.icon_label.setPixmap(pix2.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                                                    tab.icon_label.setToolTip(str(cache_png) + ' (converted via magick)')
                                                    loaded = True
                                        except Exception:
                                            loaded = False
                                    else:
                                        proc = subprocess.run([magick, str(icon_path), 'png:-'], capture_output=True, check=True)
                                        if proc.stdout:
                                            from PIL import Image
                                            im = Image.open(io.BytesIO(proc.stdout))
                                            im = im.convert('RGBA')
                                            w, h = im.size
                                            data = im.tobytes('raw', 'RGBA')
                                            try:
                                                qimg = QImage(data, w, h, QImage.Format_RGBA8888)
                                            except Exception:
                                                qimg = QImage(data, w, h, QImage.Format_ARGB32)
                                            pix2 = QPixmap.fromImage(qimg)
                                            if not pix2.isNull():
                                                tab.icon_label.setPixmap(pix2.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                                                tab.icon_label.setToolTip(str(icon_path) + ' (converted via magick)')
                                                loaded = True
                                # fallback to texconv (DirectXTex) if available
                                if not loaded:
                                    texconv = shutil.which('texconv')
                                    if texconv:
                                        tmpd = tempfile.mkdtemp(prefix='gfeditor_texconv_')
                                        try:
                                            # texconv will write PNG(s) to the output dir; if cache available, use it
                                            out_dir = tmpd
                                            if cache_png is not None:
                                                out_dir = str(cache_root)
                                            subprocess.run([texconv, '-ft', 'PNG', '-o', out_dir, str(icon_path)], check=True)
                                            pngs = list(Path(out_dir).glob('*.png'))
                                            if pngs:
                                                first_png = pngs[0]
                                                # if using tmpd, move to cache name
                                                target_png = cache_png if (cache_png is not None) else first_png
                                                if cache_png is not None and str(first_png) != str(cache_png):
                                                    try:
                                                        shutil.move(str(first_png), str(cache_png))
                                                        first_png = cache_png
                                                    except Exception:
                                                        pass
                                                from PIL import Image
                                                im = Image.open(str(first_png))
                                                im = im.convert('RGBA')
                                                w, h = im.size
                                                data = im.tobytes('raw', 'RGBA')
                                                try:
                                                    qimg = QImage(data, w, h, QImage.Format_RGBA8888)
                                                except Exception:
                                                    qimg = QImage(data, w, h, QImage.Format_ARGB32)
                                                pix2 = QPixmap.fromImage(qimg)
                                                if not pix2.isNull():
                                                    tab.icon_label.setPixmap(pix2.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                                                    tab.icon_label.setToolTip(str(first_png) + ' (converted via texconv)')
                                                    loaded = True
                                        finally:
                                            try:
                                                shutil.rmtree(tmpd)
                                            except Exception:
                                                pass
                            except Exception:
                                # external conversion failed — keep loaded = False
                                loaded = False

                    if not loaded:
                        # cannot load — clear preview and hint to user about Pillow requirement
                        tab.icon_label.setPixmap(QPixmap())
                        tab.icon_label.setToolTip('Icone nao encontrado ou formato nao suportado. Para DDS instale Pillow + plugin DDS (ex: pillow-dds).')
                else:
                    # clear pixmap if not found or no name provided
                    tab.icon_label.setPixmap(QPixmap())
            except:
                pass


def save_tab_basic(tab, row, header):
    for key, widget in tab.widgets_basic.items():
        try:
            idx = header.index(key)
            while len(row) <= idx:
                row.append('')
            
            if isinstance(widget, QSpinBox):
                row[idx] = str(widget.value())
            elif isinstance(widget, QComboBox):
                if key == 'ItemType':
                    val = item_flags.get_item_type_value(widget.currentText())
                elif key == 'ItemQuality':
                    val = item_flags.get_quality_value(widget.currentText())
                elif key == 'Target':
                    val = item_flags.get_target_value(widget.currentText())
                else:
                    val = widget.currentText()
                row[idx] = str(val) if val else ''
            elif isinstance(widget, QTextEdit):
                row[idx] = widget.toPlainText()
            else:
                row[idx] = widget.text()
        except:
            pass


# ============= TAB 2: PARAMETERS =============
def create_tab_parameters(rows, header, state):
    tab = QWidget()

    # We'll split parameters into logical groups to improve readability
    # Left column groups: Primary Stats, Combat
    # Right column groups: Defense, Timing, Misc
    left_col = QVBoxLayout()
    right_col = QVBoxLayout()

    tab.widgets_params = {}

    # Primary Stats
    primary = QGroupBox('Primary Stats')
    pl = QFormLayout()
    primary_fields = {
        'MaxHp': 'Max HP', 'MaxMp': 'Max MP',
        'Str': 'STR', 'Vit': 'VIT', 'Int': 'INT', 'Von': 'VON', 'Agi': 'AGI', 'MaxDurability': 'Max Durability',
    }
    for key, label in primary_fields.items():
        widget = QSpinBox()
        widget.setMaximum(999999)
        tab.widgets_params[key] = widget
        pl.addRow(label + ':', widget)
    primary.setLayout(pl)
    left_col.addWidget(primary)

    # Combat related fields
    combat = QGroupBox('Combat')
    cl = QFormLayout()
    combat_fields = {
        'Attack': 'Attack','MagicDamage': 'Magic Damage', 'RangeAttack': 'Range Attack', 'AttackSpeed': 'Attack Speed',
        'AttackRange': 'Attack Range', 'AvgPhysicoDamage': 'Avg Physico Damage', 'RandPhysicoDamage': 'Rand Physico Damage',
        'PhysicoCriticalRate': 'Physico Critical Rate', 'PhysicoCriticalDamage': 'Physico Critical Damage',
        'MagicCriticalRate': 'Magic Critical Rate', 'MagicCriticalDamage': 'Magic Critical Damage'
    }
    for key, label in combat_fields.items():
        widget = QSpinBox()
        widget.setMaximum(999999)
        tab.widgets_params[key] = widget
        cl.addRow(label + ':', widget)
    combat.setLayout(cl)
    left_col.addWidget(combat)

    # Defense related fields
    defense = QGroupBox('Defense / Evasion')
    dl = QFormLayout()
    defense_fields = {
        'PhysicoDefence': 'Physico Defence', 'MagicDefence': 'Magic Defence',
        'HitRate': 'Hit Rate', 'DodgeRate': 'Dodge Rate'
    }
    for key, label in defense_fields.items():
        widget = QSpinBox()
        widget.setMaximum(999999)
        tab.widgets_params[key] = widget
        dl.addRow(label + ':', widget)
    defense.setLayout(dl)
    right_col.addWidget(defense)

    # Timing / Casting
    timing = QGroupBox('Casting & Cooldowns')
    tl = QFormLayout()
    timing_fields = {
        'CastingTime': 'Casting Time', 'CoolDownTime': 'Cool Down Time'
    }
    for key, label in timing_fields.items():
        widget = QSpinBox()
        widget.setMaximum(999999)
        tab.widgets_params[key] = widget
        tl.addRow(label + ':', widget)
    timing.setLayout(tl)
    right_col.addWidget(timing)

    # Misc / Other
    misc = QGroupBox('Misc')
    ml = QFormLayout()
    misc_fields = {
        'WeaponEffectId': 'Weapon Effect ID', 'FlyEffectId': 'Fly Effect ID',
        'ElfSkillId': 'Elf Skill ID', 'BackpackSize': 'Backpack Size', 'LimitType': 'Limit Type',
        'EquipType': 'Equip Type', 'ItemGroup': 'Item Group','MaxStack': 'Max Stack'
    }
    for key, label in misc_fields.items():
        widget = QSpinBox()
        widget.setMaximum(999999)
        tab.widgets_params[key] = widget
        ml.addRow(label + ':', widget)
    misc.setLayout(ml)
    right_col.addWidget(misc)

    # Model & Effects
    visual = QGroupBox('Visual / Effects')
    visl = QFormLayout()
    visual_fields = {
        'ModelId': 'Model ID', 'ModelFilename': 'Model File', 'UsedEffectId': 'Used Effect ID',
        'UsedSoundName': 'Used Sound', 'EnhanceEffectId': 'Enhance Effect ID'
    }
    for key, label in visual_fields.items():
        # ModelId is an alphanumeric code (e.g. 'A10072') — use QLineEdit.
        # filenames and names use QLineEdit as well; numeric ids use QSpinBox.
        if key == 'ModelId' or 'File' in label or 'Sound' in label:
            w = QLineEdit()
        else:
            w = QSpinBox()
            w.setMaximum(999999)
        tab.widgets_params[key] = w
        visl.addRow(label + ':', w)
    visual.setLayout(visl)
    right_col.addWidget(visual)

    # Penetration & Extra Damage
    pen = QGroupBox('Penetration / Extra Damage')
    penl = QFormLayout()
    pen_fields = {
        'PhysicalPenetration': 'Physical Penetration',
        'MagicPenetration': 'Magical Penetration', 'PhysicalPenetrationDefence': 'Physical Penetration Defence',
        'MagicPenetrationDefence': 'Magical Penetration Defence', 'AttributeResist': 'Attribute Resist'
    }
    for key, label in pen_fields.items():
        widget = QSpinBox()
        widget.setMaximum(999999)
        tab.widgets_params[key] = widget
        penl.addRow(label + ':', widget)
    pen.setLayout(penl)
    right_col.addWidget(pen)

    # Meta / Grouping
    meta = QGroupBox('Meta / Grouping')
    ml2 = QFormLayout()
    meta_fields = {
        'CoolDownGroup': 'Cool Down Group', 'RebirthCount': 'Rebirth Count', 'RebirthScore': 'Rebirth Score',
        'RebirthMaxScore': 'Rebirth Max Score', 'DueDateTime': 'Due Date/Time', 'ExtraData1': 'Extra Data 1',
        'ExtraData2': 'Extra Data 2', 'ExtraData3': 'Extra Data 3'
    }
    for key, label in meta_fields.items():
        # DueDateTime and ExtraData may be text
        if 'Due' in label or 'Extra Data' in label:
            w = QLineEdit()
        else:
            w = QSpinBox()
            w.setMaximum(999999)
        tab.widgets_params[key] = w
        ml2.addRow(label + ':', w)
    meta.setLayout(ml2)
    right_col.addWidget(meta)

    # Assemble two columns
    layout = QHBoxLayout()
    layout.addLayout(left_col)
    layout.addLayout(right_col)
    tab.setLayout(layout)
    return tab


def update_tab_parameters(tab, row, header, state):
    for key, widget in tab.widgets_params.items():
        try:
            idx = header.index(key)
            val = row[idx] if idx < len(row) else ''
            # support both numeric spinboxes and line edits
            if isinstance(widget, QSpinBox):
                widget.setValue(int(val) if str(val).lstrip('-').isdigit() else 0)
            elif isinstance(widget, QLineEdit):
                widget.setText(str(val))
            else:
                try:
                    widget.setValue(int(val))
                except Exception:
                    pass
        except Exception:
            pass


def save_tab_parameters(tab, row, header):
    for key, widget in tab.widgets_params.items():
        try:
            idx = header.index(key)
            while len(row) <= idx:
                row.append('')
            if isinstance(widget, QSpinBox):
                row[idx] = str(widget.value())
            elif isinstance(widget, QLineEdit):
                row[idx] = widget.text()
            else:
                try:
                    row[idx] = str(widget.value())
                except Exception:
                    row[idx] = ''
        except Exception:
            pass


# ============= TAB 3: FLAGS & RESTRICTIONS =============
def create_tab_flags_restrictions(rows, header, state):
    tab = QWidget()
    layout = QVBoxLayout()

    # Flags section
    flags_group = QGroupBox('Item Flags (OpFlags)')
    flags_layout = QGridLayout()
    
    tab.widgets_flags = {}
    r = 0
    c = 0
    # include all flags defined in flags.py
    for flag_name in sorted(item_flags.FLAGS.keys()):
        cb = QCheckBox(flag_name)
        tab.widgets_flags[flag_name] = cb
        flags_layout.addWidget(cb, r, c)
        c += 1
        if c >= 3:
            c = 0
            r += 1

    # numeric input to show/edit raw OpFlags value
    flags_input = QLineEdit()
    flags_input.setPlaceholderText('Enter integer value or edit checkboxes')
    flags_input.setFixedWidth(220)
    flags_layout.addWidget(QLabel('OpFlags Value:'), max(0, r+1), 0, 1, 2)
    flags_layout.addWidget(flags_input, max(0, r+2), 0, 1, 2)

    # expose numeric field references on tab for later updates
    tab.flags_input = flags_input
    flags_group.setLayout(flags_layout)
    layout.addWidget(flags_group)

    # Flags Plus section
    flags_plus_group = QGroupBox('Item Flags Plus (OpFlagsPlus)')
    flags_plus_layout = QGridLayout()
    
    tab.widgets_flags_plus = {}
    r = 0
    c = 0
    for flag_name in sorted(item_flags.FLAGS_PLUS.keys()):
        cb = QCheckBox(flag_name)
        tab.widgets_flags_plus[flag_name] = cb
        flags_plus_layout.addWidget(cb, r, c)
        c += 1
        if c >= 3:
            c = 0
            r += 1

    # numeric input for OpFlagsPlus
    flags_plus_input = QLineEdit()
    flags_plus_input.setPlaceholderText('Enter integer value or edit checkboxes')
    flags_plus_input.setFixedWidth(220)
    flags_plus_layout.addWidget(QLabel('OpFlagsPlus Value:'), max(0, r+1), 0, 1, 2)
    flags_plus_layout.addWidget(flags_plus_input, max(0, r+2), 0, 1, 2)
    
    tab.flags_plus_input = flags_plus_input
    flags_plus_group.setLayout(flags_plus_layout)
    layout.addWidget(flags_plus_group)

    # -- wiring: keep numeric input and checkboxes in sync --
    def recompute_opflags():
        try:
            checked = [name for name, cb in tab.widgets_flags.items() if cb.isChecked()]
            val = item_flags.encode_flags(checked)
            tab.flags_input.setText(str(val))
        except Exception:
            pass

    def recompute_opflags_plus():
        try:
            checked = [name for name, cb in tab.widgets_flags_plus.items() if cb.isChecked()]
            val = item_flags.encode_flags_plus(checked)
            tab.flags_plus_input.setText(str(val))
        except Exception:
            pass

    # connect checkboxes -> numeric
    for name, cb in tab.widgets_flags.items():
        cb.stateChanged.connect(lambda _state, cb=cb: recompute_opflags())
    for name, cb in tab.widgets_flags_plus.items():
        cb.stateChanged.connect(lambda _state, cb=cb: recompute_opflags_plus())

    # numeric -> checkboxes
    def apply_flags_from_input(text):
        try:
            v = int(text) if str(text).strip().lstrip('-').isdigit() else 0
            decoded = item_flags.decode_flags(v)
            for fname, cb in tab.widgets_flags.items():
                cb.setChecked(fname in decoded)
        except Exception:
            pass

    def apply_flags_plus_from_input(text):
        try:
            v = int(text) if str(text).strip().lstrip('-').isdigit() else 0
            decoded = item_flags.decode_flags_plus(v)
            for fname, cb in tab.widgets_flags_plus.items():
                cb.setChecked(fname in decoded)
        except Exception:
            pass

    try:
        tab.flags_input.editingFinished.connect(lambda: apply_flags_from_input(tab.flags_input.text()))
        tab.flags_plus_input.editingFinished.connect(lambda: apply_flags_plus_from_input(tab.flags_plus_input.text()))
    except Exception:
        pass

    # Class Restrictions (use canonical class list from flags module)
    class_group = QGroupBox('RestrictClass')
    class_layout = QGridLayout()

    tab.widgets_classes = {}
    r = 0
    c = 0
    for class_name in item_flags.CLASSES:
        cb = QCheckBox(class_name)
        tab.widgets_classes[class_name] = cb
        class_layout.addWidget(cb, r, c)
        c += 1
        if c >= 4:
            c = 0
            r += 1

    # after listing class checkboxes, add the numeric RestrictClass field inside the same group
    # compute rows used (r currently points to next row)
    class_layout.addWidget(QLabel('RestrictClass Value:'), max(0, r+1), 0, 1, 2)
    restrict_input = QLineEdit()
    restrict_input.setPlaceholderText('HEX (sem prefixo 0x)')
    restrict_input.setFixedWidth(220)
    class_layout.addWidget(restrict_input, max(0, r+2), 0, 1, 2)
    tab.restrict_input = restrict_input

    # NOTE: always use server-side class IDs as bit positions for RestrictClass.
    # The editor will interpret and write RestrictClass using server IDs (CLASS_IDS / ID_TO_CLASS).

    class_group.setLayout(class_layout)
    layout.addWidget(class_group)

    # helper to recompute RestrictClass mask from checkboxes (always server-ID based)
    def recompute_restrictclass():
        try:
            checked = [name for name, cb in tab.widgets_classes.items() if cb.isChecked()]
            mask = item_flags.class_names_to_mask(checked)
            # show only the hex digits (sem '0x' e sem decimal)
            tab.restrict_input.setText(f"{mask:X}")
        except Exception:
            pass

    # apply numeric input value to checkboxes (accept hex 0x.. or decimal)
    def apply_restrict_from_input(text):
        try:
            t = str(text).strip()
            # Always interpret RestrictClass input as hexadecimal.
            # Accept '0x..', '0x.. / ..' or plain hex digits (even if they look numeric).
            if '/' in t:
                parts = [p.strip() for p in t.split('/')]
                hex_part = next((p for p in parts if p.lower().startswith('0x')), parts[0])
                try:
                    v = int(hex_part, 16)
                except Exception:
                    # fallback: try parse entire string as hex (without 0x)
                    try:
                        v = int(t.replace('/', '').replace(' ', ''), 16)
                    except Exception:
                        v = 0
            else:
                try:
                    v = int(t, 16)
                except Exception:
                    v = 0

            # always decode using server IDs -> map bits to server ID numbers
            decoded_names = []
            for bit in range(0, 128):
                if v & (1 << bit):
                    name = item_flags.ID_TO_CLASS.get(bit)
                    if name:
                        decoded_names.append(name)
            for cname, cb in tab.widgets_classes.items():
                try:
                    cb.blockSignals(True)
                    cb.setChecked(cname in decoded_names)
                finally:
                    cb.blockSignals(False)
        except Exception:
            pass

    # connect existing class checkboxes to recompute when changed
    for cname, cb in tab.widgets_classes.items():
        cb.stateChanged.connect(lambda _s, cb=cb: recompute_restrictclass())

    try:
        tab.restrict_input.editingFinished.connect(lambda: apply_restrict_from_input(tab.restrict_input.text()))
    except Exception:
        pass

    # Other restrictions
    other_group = QGroupBox('Other Restrictions')
    other_layout = QFormLayout()
    
    tab.widgets_restrictions = {}
    restrict_fields = {
        'RestrictGender': 'Gender (0=All, 1=Male, 2=Female)',
        'RestrictLevel': 'Min Level',
        'RestrictMaxLevel': 'Max Level',
        'RestrictAlign': 'Alignment',
        'RestrictPrestige': 'Prestige',
    }
    
    for key, label in restrict_fields.items():
        widget = QSpinBox()
        widget.setMaximum(999999)
        tab.widgets_restrictions[key] = widget
        other_layout.addRow(label + ':', widget)
    
    other_group.setLayout(other_layout)
    layout.addWidget(other_group)

    layout.addStretch()
    tab.setLayout(layout)
    return tab


def update_tab_flags_restrictions(tab, row, header, state):
    # Update flags
    try:
        idx = header.index('OpFlags')
        flags_value = int(row[idx]) if idx < len(row) and row[idx].isdigit() else 0
        decoded = item_flags.decode_flags(flags_value)
        for flag_name, cb in tab.widgets_flags.items():
            cb.setChecked(flag_name in decoded)
        # update numeric input if present
        try:
            if hasattr(tab, 'flags_input') and tab.flags_input is not None:
                tab.flags_input.setText(str(flags_value))
        except Exception:
            pass
    except:
        pass

    # Update flags plus
    try:
        idx = header.index('OpFlagsPlus')
        flags_plus_value = int(row[idx]) if idx < len(row) and row[idx].isdigit() else 0
        decoded = item_flags.decode_flags_plus(flags_plus_value)
        for flag_name, cb in tab.widgets_flags_plus.items():
            cb.setChecked(flag_name in decoded)
        try:
            if hasattr(tab, 'flags_plus_input') and tab.flags_plus_input is not None:
                tab.flags_plus_input.setText(str(flags_plus_value))
        except Exception:
            pass
    except:
        pass

    # Update restrictions
    for key, widget in tab.widgets_restrictions.items():
        try:
            idx = header.index(key)
            val = row[idx] if idx < len(row) else '0'
            widget.setValue(int(val) if val.isdigit() else 0)
        except:
            pass

    # Update RestrictClass bitmask into class checkboxes (if present in header)
    try:
        idx = header.index('RestrictClass')
        raw_val = row[idx] if idx < len(row) else ''
        # Always interpret RestrictClass as hexadecimal server-ID bitmask.
        # Accept formats like '0xHEX', '0xHEX / DEC' or plain hex digits.
        val = 0
        try:
            t = str(raw_val).strip()
            if not t:
                val = 0
            elif '/' in t:
                parts = [p.strip() for p in t.split('/')]
                hex_part = next((p for p in parts if p.lower().startswith('0x')), parts[0])
                try:
                    val = int(hex_part, 16)
                except Exception:
                    try:
                        val = int(t.replace('/', '').replace(' ', ''), 16)
                    except Exception:
                        val = 0
            else:
                try:
                    val = int(t, 16)
                except Exception:
                    val = 0
        except Exception:
            val = 0

        # decode using server IDs
        decoded_names = []
        for bit in range(0, 128):
            if val & (1 << bit):
                name = item_flags.ID_TO_CLASS.get(bit)
                if name:
                    decoded_names.append(name)
        # set checkboxes without emitting signals to avoid intermediate recompute
        for cname, cb in tab.widgets_classes.items():
            try:
                cb.blockSignals(True)
                cb.setChecked(cname in decoded_names)
            finally:
                cb.blockSignals(False)

        # update numeric input if present
        try:
                    if hasattr(tab, 'restrict_input') and tab.restrict_input is not None:
                        # display only hex digits (sem '0x' e sem decimal)
                        tab.restrict_input.setText(f"{val:X}")
        except Exception:
            pass
    except Exception:
        pass


def save_tab_flags_restrictions(tab, row, header):
    # Save flags
    try:
        idx = header.index('OpFlags')
        while len(row) <= idx:
            row.append('')
        checked = [name for name, cb in tab.widgets_flags.items() if cb.isChecked()]
        row[idx] = str(item_flags.encode_flags(checked))
    except:
        pass

    # Save flags plus
    try:
        idx = header.index('OpFlagsPlus')
        while len(row) <= idx:
            row.append('')
        checked = [name for name, cb in tab.widgets_flags_plus.items() if cb.isChecked()]
        row[idx] = str(item_flags.encode_flags_plus(checked))
    except:
        pass

    # Save restrictions
    for key, widget in tab.widgets_restrictions.items():
        try:
            idx = header.index(key)
            while len(row) <= idx:
                row.append('')
            row[idx] = str(widget.value())
        except:
            pass

    # Save RestrictClass bitmask from class checkboxes
    try:
        idx = header.index('RestrictClass')
        while len(row) <= idx:
            row.append('')
        checked = [name for name, cb in tab.widgets_classes.items() if cb.isChecked()]
        # always save using server-class-ID positions
        mask = item_flags.class_names_to_mask(checked)
        # write canonical form: hex / decimal so it's explicit and round-trippable
        row[idx] = f"0x{mask:X} / {mask}"
    except Exception:
        pass


# ============= TAB 4: ENCHANT & SPECIAL =============
def create_tab_enchant_special(rows, header, state):
    tab = QWidget()
    layout = QFormLayout()

    enchant_fields = {
        'EnchantType': ('Enchant Type', QSpinBox()),
        'EnchantId': ('Enchant ID', QSpinBox()),
        'EnchantTimeType': ('Enchant Time Type', QSpinBox()),
        'EnchantDuration': ('Enchant Duration', QSpinBox()),
        'ExpertLevel': ('Expert Level', QSpinBox()),
        'ExpertEnchantId': ('Expert Enchant ID', QSpinBox()),
        'ElfSkillId': ('Elf Skill ID', QSpinBox()),
        'TreasureBuffs1': ('Treasure Buff 1', QSpinBox()),
        'TreasureBuffs2': ('Treasure Buff 2', QSpinBox()),
        'TreasureBuffs3': ('Treasure Buff 3', QSpinBox()),
        'TreasureBuffs4': ('Treasure Buff 4', QSpinBox()),
        'Attribute': ('Attribute', QSpinBox()),
        'AttributeRate': ('Attribute Rate', QSpinBox()),
        'AttributeDamage': ('Attribute Damage', QSpinBox()),
        'SpecialType': ('Special Type', QSpinBox()),
        'SpecialRate': ('Special Rate', QSpinBox()),
        'SpecialDamage': ('Special Damage', QSpinBox()),
    }

    tab.widgets_enchant = {}
    for key, (label, widget) in enchant_fields.items():
        widget.setMaximum(999999)
        tab.widgets_enchant[key] = widget
        layout.addRow(label + ':', widget)

    tab.setLayout(layout)
    return tab


def update_tab_enchant_special(tab, row, header, state):
    for key, widget in tab.widgets_enchant.items():
        try:
            idx = header.index(key)
            val = row[idx] if idx < len(row) else '0'
            widget.setValue(int(val) if val.isdigit() else 0)
        except:
            pass


def save_tab_enchant_special(tab, row, header):
    for key, widget in tab.widgets_enchant.items():
        try:
            idx = header.index(key)
            while len(row) <= idx:
                row.append('')
            row[idx] = str(widget.value())
        except:
            pass


# ============= TAB 5: ADVANCED =============
def create_tab_advanced(rows, header, state):
    tab = QWidget()
    layout = QFormLayout()

    advanced_fields = {
        'DropRate': ('Drop Rate', QSpinBox()),
        'DropIndex': ('Drop Index', QSpinBox()),
        'MaxSocket': ('Max Socket', QSpinBox()),
        'SocketRate': ('Socket Rate', QSpinBox()),
        'BackpackSize': ('Backpack Size', QSpinBox()),
        'LimitType': ('Limit Type', QSpinBox()),
        'BlockRate': ('Block Rate', QSpinBox()),
        'LogLevel': ('Log Level', QSpinBox()),
        'AuctionType': ('Auction Type', QSpinBox()),
        'RestrictEventPosId': ('Event Pos ID', QSpinBox()),
        'MissionPosId': ('Mission Pos ID', QSpinBox()),
        'WeaponEffectId': ('Weapon Effect', QSpinBox()),
    }

    tab.widgets_advanced = {}
    for key, (label, widget) in advanced_fields.items():
        widget.setMaximum(999999)
        tab.widgets_advanced[key] = widget
        layout.addRow(label + ':', widget)

    tab.setLayout(layout)
    return tab


def update_tab_advanced(tab, row, header, state):
    for key, widget in tab.widgets_advanced.items():
        try:
            idx = header.index(key)
            val = row[idx] if idx < len(row) else '0'
            widget.setValue(int(val) if val.isdigit() else 0)
        except:
            pass


def save_tab_advanced(tab, row, header):
    for key, widget in tab.widgets_advanced.items():
        try:
            idx = header.index(key)
            while len(row) <= idx:
                row.append('')
            row[idx] = str(widget.value())
        except:
            pass


def show_search_dialog(rows, on_select):
    """Show a search dialog to find items."""
    dialog = QWidget()
    dialog.setWindowTitle('Search Items')
    layout = QVBoxLayout()

    search_input = QLineEdit()
    search_input.setPlaceholderText('Search by ID or Name...')

    results_table = QTableWidget()
    results_table.setColumnCount(3)
    results_table.setHorizontalHeaderLabels(['ID', 'Name', 'Index'])
    results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def perform_search():
        query = search_input.text().lower()
        results_table.setRowCount(0)
        
        for i, row in enumerate(rows):
            item_id = row[0] if len(row) > 0 else ''
            item_name = row[9] if len(row) > 9 else ''
            
            if query in str(item_id).lower() or query in str(item_name).lower():
                row_idx = results_table.rowCount()
                results_table.insertRow(row_idx)
                results_table.setItem(row_idx, 0, QTableWidgetItem(str(item_id)))
                results_table.setItem(row_idx, 1, QTableWidgetItem(str(item_name)))
                results_table.setItem(row_idx, 2, QTableWidgetItem(str(i)))

    def select_item():
        if results_table.currentRow() >= 0:
            idx = int(results_table.item(results_table.currentRow(), 2).text())
            on_select(idx)
            dialog.close()

    search_input.textChanged.connect(perform_search)
    results_table.doubleClicked.connect(select_item)

    layout.addWidget(QLabel('Search:'))
    layout.addWidget(search_input)
    layout.addWidget(results_table)
    
    btn = QPushButton('Select')
    btn.clicked.connect(select_item)
    layout.addWidget(btn)

    dialog.setLayout(layout)
    dialog.resize(600, 400)
    dialog.show()


# Raw/Other tab removed — raw helpers deleted to keep UI focused
