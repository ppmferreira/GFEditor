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
        import os
        # Use ANSI (mbcs) on Windows to match project requirement; fallback to utf-8 on other OSes
        enc = 'mbcs' if os.name == 'nt' else 'utf-8'
        with open(self.path, 'r', encoding=enc, errors='ignore') as fh:
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
                    # partes da descriÁ„o (tudo apÛs o segundo pipe)
                    desc_parts = parts[2:] if len(parts) >= 3 else []
                    # se todas as partes de descriÁ„o estiverem vazias => descriÁ„o vazia
                    if len(desc_parts) == 0 or all(p == '' for p in desc_parts):
                        desc_part = ''
                    else:
                        # join parts but strip trailing '|' characters that mark end-of-record
                        desc_part = '|'.join(desc_parts).rstrip('|')
                    current_desc_lines = [desc_part] if desc_part != '' else []
                else:
                    if not seen:
                        self.header_lines.append(line)
                    else:
                        if current_id is not None:
                            # strip trailing pipe characters from continuation lines to avoid
                            # preserving format markers as content (prevents double '||' on save)
                            current_desc_lines.append(line.rstrip('|'))
                        else:
                            self.header_lines.append(line)
            if current_id is not None:
                self.records.append({'id': current_id, 'name': current_name, 'desc_lines': current_desc_lines})

    def get(self, item_id: str) -> Optional[Tuple[str, str]]:
        for rec in self.records:
            if rec['id'] == str(item_id):
                name = rec['name'] or ''
                desc = '\n'.join(rec['desc_lines']).strip()
                # sanitize both name and description for display:
                # - remove tokens like $12$ used in some translation dumps
                # - remove trailing pipe characters left by some file formats
                # - strip surrounding quotes on each line
                def _sanitize(text: str) -> str:
                    if not text:
                        return ''
                    t = text.strip()
                    # remove $number$ markers
                    t = re.sub(r"\$\d+\$", '', t)
                    # collapse any pipe that is used as end-of-line marker: '|\n' -> '\n'
                    t = t.replace('|\n', '\n')
                    # remove trailing pipes
                    while t.endswith('|'):
                        t = t[:-1].rstrip()
                    # strip surrounding quotes on each line
                    lines = [ln.strip() for ln in t.split('\n')]
                    def _strip_quotes(ln: str) -> str:
                        if len(ln) >= 2 and ((ln.startswith('"') and ln.endswith('"')) or (ln.startswith("'") and ln.endswith("'"))):
                            return ln[1:-1]
                        return ln
                    lines = [_strip_quotes(ln) for ln in lines]
                    return '\n'.join(lines).strip()

                return _sanitize(name), _sanitize(desc)
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
            # use os.fdopen to correctly wrap the fd returned by mkstemp
            import os
            enc = 'mbcs' if os.name == 'nt' else 'utf-8'
            with os.fdopen(tmp_fd, 'w', encoding=enc, errors='replace') as fh:
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
                        # Preserve multiple lines so the last line ends with '|' and
                        # intermediate lines are written as-is (allow blank lines).
                        # If there's only one line, write it as id|name|line|
                        first = desc_lines[0]
                        if len(desc_lines) == 1:
                            fh.write(f"{id_}|{name}|{first}|\n")
                        else:
                            # first line: no trailing pipe
                            fh.write(f"{id_}|{name}|{first}\n")
                            # middle lines (could be empty) - preserve exact text
                            for mid in desc_lines[1:-1]:
                                fh.write(mid + "\n")
                            # last line: terminate with '|' to mark end of record
                            last = desc_lines[-1]
                            fh.write(f"{last}|\n")
            # mover arquivo tempor·rio para destino (substitui o arquivo existente)
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
                # If translation does not exist, append as the last record (insert_at=None)
                # so new translations are always created at the end of the file.
                insert_at = None
                if tf.find_index(item_id) is not None:
                    # existing record - retain position
                    insert_at = tf.find_index(item_id)
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