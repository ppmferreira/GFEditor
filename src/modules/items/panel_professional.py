"""Professional Item Editor Panel with Tabs and Advanced Features."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea,
    QLineEdit, QTextEdit, QFormLayout, QGroupBox, QGridLayout, QCheckBox,
    QTableWidgetItem, QComboBox, QMessageBox, QSpinBox, QTabWidget,
    QDoubleSpinBox, QTableWidget, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path
import gfio
from . import flags as item_flags


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

        editor = build_professional_editor(parent, client_rows, header)

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


def build_professional_editor(parent, rows, header):
    """Build a professional multi-tab item editor."""
    container = QWidget()
    main_layout = QVBoxLayout()

    state = {'rows': rows, 'header': header, 'index': 0}

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
    btn_search = QPushButton('?? Search')
    
    ctrl_row.addWidget(QLabel('Item:'))
    ctrl_row.addWidget(btn_prev)
    ctrl_row.addWidget(selector)
    ctrl_row.addWidget(btn_next)
    ctrl_row.addWidget(btn_search)
    ctrl_row.addStretch()
    main_layout.addLayout(ctrl_row)

    # ============= TABS =============
    tabs = QTabWidget()

    # TAB 1: BASIC INFO
    tab_basic = create_tab_basic(rows, header, state)
    tabs.addTab(tab_basic, "?? Basic Info")

    # TAB 2: PARAMETERS
    tab_params = create_tab_parameters(rows, header, state)
    tabs.addTab(tab_params, "?? Parameters")

    # TAB 3: FLAGS & RESTRICTIONS
    tab_flags = create_tab_flags_restrictions(rows, header, state)
    tabs.addTab(tab_flags, "?? Flags & Restrictions")

    # TAB 4: ENCHANT & SPECIAL
    tab_enchant = create_tab_enchant_special(rows, header, state)
    tabs.addTab(tab_enchant, "? Enchant & Special")

    # TAB 5: ADVANCED
    tab_advanced = create_tab_advanced(rows, header, state)
    tabs.addTab(tab_advanced, "?? Advanced")

    main_layout.addWidget(tabs)

    # ============= SAVE BUTTONS =============
    btn_row = QHBoxLayout()
    btn_save = QPushButton('?? Save')
    btn_save_close = QPushButton('? Save and Close')
    btn_save_disk = QPushButton('?? Save to Disk')
    btn_compare = QPushButton('?? Compare')
    
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

    try:
        table = getattr(parent, 'table', None)
        if table is not None:
            sel = table.currentRow() if hasattr(table, 'currentRow') else 0
            load_index(sel if 0 <= sel < len(rows) else 0)
        else:
            load_index(0)
    except Exception:
        load_index(0)

    container.setLayout(main_layout)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(container)
    return scroll


# ============= TAB 1: BASIC INFO =============
def create_tab_basic(rows, header, state):
    tab = QWidget()
    layout = QVBoxLayout()

    # Left: Icon preview
    left = QVBoxLayout()
    icon_label = QLabel()
    icon_label.setFixedSize(200, 200)
    icon_label.setStyleSheet('background: #1a2a3a; border: 2px solid #00d4ff;')
    icon_label.setAlignment(Qt.AlignCenter)
    left.addWidget(QLabel('<b>Icon Preview</b>'))
    left.addWidget(icon_label)
    left.addStretch()

    # Right: Basic fields
    right = QFormLayout()
    
    fields_basic = {
        'Id': ('ID', QLineEdit()),
        'Name': ('Name', QLineEdit()),
        'IconFilename': ('Icon File', QLineEdit()),
        'ItemType': ('Item Type', QComboBox()),
        'ItemQuality': ('Quality', QComboBox()),
        'Target': ('Target', QComboBox()),
        'MaxStack': ('Max Stack', QSpinBox()),
        'SysPrice': ('Sys Price', QSpinBox()),
        'WeaponEffectId': ('Weapon Effect ID', QSpinBox()),
        'FlyEffectId': ('Fly Effect ID', QSpinBox()),
        'Tip': ('Description/Tip', QTextEdit()),
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
    body.addLayout(left)
    body.addLayout(right)
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
                widget.setText(val)
        except:
            pass
        
        # Update icon preview
        if key == 'IconFilename':
            try:
                icon_name = row[1] if len(row) > 1 else ''
                icon_path = Path(getattr(state.get('parent'), 'lib_path', Path.cwd() / 'Assets')) / 'itemicon' / icon_name
                if icon_path.exists():
                    pix = QPixmap(str(icon_path))
                    if pix and not pix.isNull():
                        tab.icon_label.setPixmap(pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
    layout = QGridLayout()

    params = {
        'MaxHp': 'Max HP', 'MaxMp': 'Max MP',
        'Str': 'STR', 'Con': 'CON', 'Int': 'INT', 'Vol': 'VOL', 'Dex': 'DEX',
        'Attack': 'Attack', 'RangeAttack': 'Range Attack',
        'AvgPhysicoDamage': 'Avg Physico Damage', 'RandPhysicoDamage': 'Rand Physico Damage',
        'PhysicoDefence': 'Physico Defence', 'MagicDefence': 'Magic Defence',
        'HitRate': 'Hit Rate', 'DodgeRate': 'Dodge Rate',
        'PhysicoCriticalRate': 'Physico Critical Rate', 'PhysicoCriticalDamage': 'Physico Critical Damage',
        'MagicCriticalRate': 'Magic Critical Rate', 'MagicCriticalDamage': 'Magic Critical Damage',
        'AttackSpeed': 'Attack Speed', 'AttackRange': 'Attack Range',
        'CastingTime': 'Casting Time', 'CoolDownTime': 'Cool Down Time',
    }

    tab.widgets_params = {}
    row_idx = 0
    col_idx = 0
    
    for key, label in params.items():
        widget = QSpinBox()
        widget.setMaximum(999999)
        tab.widgets_params[key] = widget
        layout.addWidget(QLabel(label + ':'), row_idx, col_idx)
        layout.addWidget(widget, row_idx, col_idx + 1)
        col_idx += 2
        if col_idx >= 4:
            col_idx = 0
            row_idx += 1

    tab.setLayout(layout)
    return tab


def update_tab_parameters(tab, row, header, state):
    for key, widget in tab.widgets_params.items():
        try:
            idx = header.index(key)
            val = row[idx] if idx < len(row) else '0'
            widget.setValue(int(val) if val.isdigit() else 0)
        except:
            pass


def save_tab_parameters(tab, row, header):
    for key, widget in tab.widgets_params.items():
        try:
            idx = header.index(key)
            while len(row) <= idx:
                row.append('')
            row[idx] = str(widget.value())
        except:
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
    for flag_name in sorted(item_flags.FLAGS.keys()):
        if flag_name not in ['OnlyStartBit', 'ReplaceableStartBit', 'Only', 'Replaceable']:
            cb = QCheckBox(flag_name)
            tab.widgets_flags[flag_name] = cb
            flags_layout.addWidget(cb, r, c)
            c += 1
            if c >= 3:
                c = 0
                r += 1
    
    flags_group.setLayout(flags_layout)
    layout.addWidget(flags_group)

    # Flags Plus section
    flags_plus_group = QGroupBox('Item Flags Plus (OpFlagsPlus)')
    flags_plus_layout = QGridLayout()
    
    tab.widgets_flags_plus = {}
    r = 0
    c = 0
    for flag_name in sorted(item_flags.FLAGS_PLUS.keys()):
        if flag_name not in ['ISRideCombine', 'ISChairCombine']:
            cb = QCheckBox(flag_name)
            tab.widgets_flags_plus[flag_name] = cb
            flags_plus_layout.addWidget(cb, r, c)
            c += 1
            if c >= 3:
                c = 0
                r += 1
    
    flags_plus_group.setLayout(flags_plus_layout)
    layout.addWidget(flags_plus_group)

    # Class Restrictions
    class_group = QGroupBox('Class Restrictions')
    class_layout = QGridLayout()
    
    classes = ['Novice','Fighter','Warrior','Berserker','Warlord','Templar','Paladin',
               'Ranger','Archer','Sniper','Assassin','Hunter','Sharpshooter','Blademaster',
               'Priest','Cleric','Sage','Prophet','Druid','Shaman','Mage','Wizard','Necromancer']
    
    tab.widgets_classes = {}
    r = 0
    c = 0
    for class_name in classes:
        cb = QCheckBox(class_name)
        tab.widgets_classes[class_name] = cb
        class_layout.addWidget(cb, r, c)
        c += 1
        if c >= 4:
            c = 0
            r += 1
    
    class_group.setLayout(class_layout)
    layout.addWidget(class_group)

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
    except:
        pass

    # Update flags plus
    try:
        idx = header.index('OpFlagsPlus')
        flags_plus_value = int(row[idx]) if idx < len(row) and row[idx].isdigit() else 0
        decoded = item_flags.decode_flags_plus(flags_plus_value)
        for flag_name, cb in tab.widgets_flags_plus.items():
            cb.setChecked(flag_name in decoded)
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
        'MaxDurability': ('Max Durability', QSpinBox()),
        'BackpackSize': ('Backpack Size', QSpinBox()),
        'LimitType': ('Limit Type', QSpinBox()),
        'BlockRate': ('Block Rate', QSpinBox()),
        'LogLevel': ('Log Level', QSpinBox()),
        'AuctionType': ('Auction Type', QSpinBox()),
        'RestrictEventPosId': ('Event Pos ID', QSpinBox()),
        'MissionPosId': ('Mission Pos ID', QSpinBox()),
        'ModelId': ('Model ID', QSpinBox()),
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
