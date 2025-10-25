from pathlib import Path
import tempfile, shutil, io, re
from typing import Optional, Tuple, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QDialog, QFormLayout, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt

class TranslateFile:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.header_lines: List[str] = []
        self.records: List[dict] = []
        self._load()

    def _load(self):
        self.header_lines = []
        self.records = []
        if not self.path.exists():
            return
        with open(self.path, 'r', encoding='utf-8', errors='ignore') as fh:
            current_id = None
            current_name = ''
            current_desc_lines: List[str] = []
            seen = False
            for raw in fh:
                line = raw.rstrip('\n')
                m = re.match(r'^\s*(\d+)\|', line)
                if m:
                    if current_id is not None:
                        self.records.append({'id': current_id, 'name': current_name, 'desc_lines': current_desc_lines})
                    seen = True
                    parts = line.split('|')
                    current_id = parts[0]
                    current_name = parts[1] if len(parts) >= 2 else ''
                    desc_part = '|'.join(parts[2:]) if len(parts) >= 3 else ''
                    current_desc_lines = [desc_part] if desc_part != '' else []
                else:
                    if not seen:
                        self.header_lines.append(line)
                    else:
                        if current_id is not None:
                            current_desc_lines.append(line)
                        else:
                            self.header_lines.append(line)
            if current_id is not None:
                self.records.append({'id': current_id, 'name': current_name, 'desc_lines': current_desc_lines})

    def get(self, item_id: str) -> Optional[Tuple[str, str]]:
        for rec in self.records:
            if rec['id'] == str(item_id):
                return rec['name'], '\n'.join(rec['desc_lines']).strip()
        return None

    def find_index(self, item_id: str) -> Optional[int]:
        for i, rec in enumerate(self.records):
            if rec['id'] == str(item_id):
                return i
        return None

    def set(self, item_id: str, name: str, desc: str, insert_at: Optional[int] = None) -> int:
        item_id = str(item_id)
        idx = self.find_index(item_id)
        desc_lines = [] if desc is None else desc.split('\n')
        if idx is not None:
            self.records[idx]['name'] = name
            self.records[idx]['desc_lines'] = desc_lines
            return idx
        new_rec = {'id': item_id, 'name': name, 'desc_lines': desc_lines}
        if insert_at is None or insert_at >= len(self.records):
            self.records.append(new_rec)
            return len(self.records) - 1
        pos = max(0, int(insert_at))
        self.records.insert(pos, new_rec)
        return pos

    def save(self):
        tmp_fd, tmp_path = tempfile.mkstemp(prefix='translate_', suffix='.tmp', dir=str(self.path.parent))
        try:
            with io.open(tmp_fd, 'w', encoding='utf-8', errors='replace') as fh:
                for hl in self.header_lines:
                    fh.write(hl + '\n')
                for rec in self.records:
                    id_ = rec['id']
                    name = rec['name'] or ''
                    desc_lines = rec.get('desc_lines', [])
                    # tratar linhas vazias ou com apenas whitespace como ausÍncia de descriÁ„o
                    if not desc_lines or (len(desc_lines) == 1 and desc_lines[0].strip() == ''):
                        fh.write(f"{id_}|{name}||\n")
                    else:
                        first = desc_lines[0]
                        fh.write(f"{id_}|{name}|{first}\n")
                        for extra in desc_lines[1:]:
                            fh.write(extra + '\n')
            shutil.move(tmp_path, str(self.path))
        finally:
            try:
                if Path(tmp_path).exists():
                    Path(tmp_path).unlink()
            except Exception:
                pass

def _resolve_path(lib_base: Optional[Path], translate_name: str) -> Path:
    if lib_base is None:
        lib_base = Path.cwd() / 'Assets'
    return Path(lib_base) / 'Translate' / translate_name

def load_translate(lib_base: Optional[Path], translate_name: str) -> TranslateFile:
    p = _resolve_path(lib_base, translate_name)
    return TranslateFile(p)

def get_translation(translate_name: str, item_id: str, lib_base: Optional[Path] = None) -> Optional[Tuple[str, str]]:
    tf = load_translate(lib_base, translate_name)
    return tf.get(item_id)

def set_translation(translate_name: str, item_id: str, name: str, desc: str, insert_at: Optional[int] = None, lib_base: Optional[Path] = None) -> int:
    tf = load_translate(lib_base, translate_name)
    idx = tf.set(item_id, name, desc, insert_at=insert_at)
    tf.save()
    return idx

def create_tab_translate(rows, header, state):
    tab = QWidget()
    tab.setObjectName('translateTab')
    layout = QVBoxLayout()
    # margens e espaÁamento mais compactos para a aba
    layout.setContentsMargins(6, 6, 6, 6)
    layout.setSpacing(6)
    # garantir alinhamento ao topo para evitar espaÁamentos verticais grandes
    layout.setAlignment(Qt.AlignTop)
    tab.trans_name = QLineEdit()
    tab.trans_name.setReadOnly(True)
    tab.trans_desc = QTextEdit()
    tab.trans_desc.setReadOnly(True)
    # menor altura fixa com scroll autom·tico
    tab.trans_desc.setMinimumHeight(80)
    tab.trans_desc.setMaximumHeight(160)
    tab.trans_desc.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    btn_row = QHBoxLayout()
    tab.btn_edit = QPushButton('Editar')
    tab.btn_create = QPushButton('Criar tradu√ß√£o')
    btn_row.addWidget(tab.btn_edit)
    btn_row.addWidget(tab.btn_create)
    btn_row.addStretch()
    tab.source_label = QLabel('')
    # rÛtulos com estilo simples (negrito) para evitar depender do CSS global
    lbl_name = QLabel('Translation Name')
    lbl_name.setStyleSheet('font-weight:600;')
    lbl_desc = QLabel('Translation Description')
    lbl_desc.setStyleSheet('font-weight:600;')
    layout.addWidget(lbl_name)
    # padding leve para o campo
    # campo de nome mais compacto e sem expans„o vertical
    tab.trans_name.setStyleSheet('padding:4px; border-radius:4px;')
    tab.trans_name.setFixedHeight(28)
    tab.trans_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    layout.addWidget(tab.trans_name)
    layout.addWidget(lbl_desc)
    tab.trans_desc.setStyleSheet('padding:4px; border-radius:4px;')
    # altura razo·vel fixa; mantÈm scrollbar quando necess·rio
    tab.trans_desc.setFixedHeight(120)
    tab.trans_desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    layout.addWidget(tab.trans_desc)
    layout.addLayout(btn_row)
    # label de fonte com estilo discreto
    tab.source_label.setStyleSheet('color: #9aa0a6; font-size:11px;')
    layout.addWidget(tab.source_label)
    # forÁa os widgets para o topo quando a ·rea for maior
    layout.addStretch()
    tab.setLayout(layout)

    def on_edit_clicked():
        try:
            item_id = None
            if state.get('index') is not None and len(rows) > state['index']:
                item_id = str(rows[state['index']][0]) if len(rows[state['index']]) > 0 else None
            if not item_id:
                QMessageBox.warning(None, 'Translate', 'Item ID inv√°lido')
                return
            source = state.get('source_base') or ''
            src_lower = str(source).lower()
            translate_name = 'T_Item.ini'
            if 'itemmall' in src_lower or 'item_mall' in src_lower:
                translate_name = 'T_ItemMall.ini'
            lib_base = Path(getattr(state.get('parent'), 'lib_path', Path.cwd() / 'Assets'))
            tf = load_translate(lib_base, translate_name)
            existing = tf.get(item_id)
            dlg = QDialog()
            dlg.setWindowTitle('Editar tradu√ß√£o')
            form = QFormLayout()
            in_name = QLineEdit(existing[0] if existing else '')
            in_desc = QTextEdit(existing[1] if existing else '')
            form.addRow('Nome:', in_name)
            form.addRow('Descri√ß√£o:', in_desc)
            btns = QHBoxLayout()
            ok = QPushButton('Salvar')
            cancel = QPushButton('Cancelar')
            btns.addStretch()
            btns.addWidget(ok)
            btns.addWidget(cancel)
            v = QVBoxLayout()
            v.addLayout(form)
            v.addLayout(btns)
            dlg.setLayout(v)

            def do_save():
                name = in_name.text()
                desc = in_desc.toPlainText()
                insert_at = None
                if tf.find_index(item_id) is None:
                    insert_at = state.get('index', None)
                tf.set(item_id, name, desc, insert_at=insert_at)
                try:
                    tf.save()
                except Exception as exc:
                    QMessageBox.critical(None, 'Erro', f'Falha ao salvar tradu√ß√£o: {exc}')
                dlg.accept()
                try:
                    update_tab_translate(tab, rows[state.get('index', 0)], header, state)
                except Exception:
                    pass

            ok.clicked.connect(do_save)
            cancel.clicked.connect(dlg.reject)
            dlg.exec()
        except Exception as exc:
            QMessageBox.warning(None, 'Erro', f'Falha ao editar tradu√ß√£o: {exc}')

    def on_create_clicked():
        on_edit_clicked()

    tab.btn_edit.clicked.connect(on_edit_clicked)
    tab.btn_create.clicked.connect(on_create_clicked)
    return tab

def update_tab_translate(tab, row, header, state):
    try:
        item_id = None
        if len(row) > 0:
            item_id = str(row[0]).strip()
        if not item_id:
            tab.trans_name.setText('')
            tab.trans_desc.setPlainText('')
            tab.btn_create.setEnabled(False)
            tab.btn_edit.setEnabled(False)
            tab.source_label.setText('')
            return
        source = state.get('source_base') or ''
        src_lower = str(source).lower()
        translate_name = 'T_Item.ini'
        if 'itemmall' in src_lower or 'item_mall' in src_lower:
            translate_name = 'T_ItemMall.ini'
        lib_base = Path(getattr(state.get('parent'), 'lib_path', Path.cwd() / 'Assets'))
        tf = load_translate(lib_base, translate_name)
        found = tf.get(item_id)
        if found is None:
            tab.trans_name.setText(f'-- sem tradu√ß√£o para id {item_id} --')
            tab.trans_desc.setPlainText('')
            tab.btn_create.setEnabled(True)
            tab.btn_edit.setEnabled(True)
        else:
            tab.trans_name.setText(found[0])
            tab.trans_desc.setPlainText(found[1])
            tab.btn_create.setEnabled(False)
            tab.btn_edit.setEnabled(True)
        tab.source_label.setText(f'Fonte: {translate_name}')
    except Exception:
        try:
            tab.trans_name.setText('')
            tab.trans_desc.setPlainText('')
        except Exception:
            pass