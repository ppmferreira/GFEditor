from pathlib import Path
from typing import List, Dict, Tuple, Optional
import shutil

import gfio as _gfio
from translate import read_t_file, write_t_file
from datetime import datetime


def list_entries(lib_path: Path) -> List[str]:
    data_dir = lib_path / 'data' / 'serverdb'
    if not data_dir.exists():
        return []
    # Prefer canonical item files (server and client variants). Return whichever exist.
    preferred_order = ('S_Item.ini', 'S_ItemMall.ini', 'C_Item.ini', 'C_ItemMall.ini')
    preferred = [name for name in preferred_order if (data_dir / name).exists()]
    if preferred:
        return preferred
    # fallback: return all matching *Item*.ini
    return [p.name for p in sorted(data_dir.glob('*Item*.ini'))]


def load_rows(path: Path, encoding: str = 'big5', limit: Optional[int] = None) -> List[List[str]]:
    # determine expected fields from schema (max index + 1)
    try:
        from .schema import SCHEMA as _SC
        expected = max(idx for idx, *_ in _SC) + 1
    except Exception:
        expected = None
    return _gfio.read_pipe_file(path, encoding=encoding, limit=limit, expected_fields=expected)


def read_ids(path: Path, encoding: str = 'big5', limit: Optional[int] = None) -> List[str]:
    """Read just the Id column from the serverdb file for fast population of combo lists."""
    return _gfio.read_ids(path, encoding=encoding, limit=limit)


def save_rows(path: Path, rows: List[List[str]], encoding: str = 'big5') -> None:
    _gfio.write_pipe_file(path, rows, encoding=encoding)


def load_translations(t_path: Path, encoding: str = 'mbcs') -> Dict[int, Tuple[str, str]]:
    if not t_path.exists():
        return {}
    return read_t_file(t_path, encoding=encoding)


def save_translations(t_path: Path, records: Dict[int, Tuple[str, str]], encoding: str = 'mbcs') -> None:
    write_t_file(t_path, records, encoding=encoding)


def backup_file(path: Path) -> None:
    bak = path.with_name(f"{path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
    try:
        shutil.copy2(path, bak)
    except Exception:
        # best-effort: if copy fails, try writing a tiny marker
        try:
            bak.write_text('backup', encoding='utf-8')
        except Exception:
            pass


def save_row_and_sync_translations(lib_path: Path, filename: str, row_index_key: str, newrow: List[str],
                                   t_name: Optional[str] = None, t_tip: Optional[str] = None,
                                   encoding_sc: str = 'big5', encoding_t: str = 'mbcs') -> None:
    """Save updated row in the given serverdb file and update T_Item.ini accordingly.

    row_index_key: value of Id column to match (string).
    newrow: list of column values (strings).
    t_name / t_tip: optional translation values to write into T_Item.ini for that Id.
    """
    s_path = lib_path / 'data' / 'serverdb' / filename
    t_path = lib_path / 'data' / 'Translate' / 'T_Item.ini'

    rows = load_rows(s_path, encoding=encoding_sc)
    if not rows:
        raise RuntimeError('Empty or missing rows')
    updated = False
    for idx, r in enumerate(rows):
        if len(r) > 0 and r[0] == row_index_key:
            rows[idx] = newrow
            updated = True
            break
    if not updated:
        raise KeyError(f'Id {row_index_key} not found in {filename}')

    # backup and write
    if s_path.exists():
        backup_file(s_path)
    save_rows(s_path, rows, encoding=encoding_sc)

    # translations
    trecs = {}
    if t_path.exists():
        trecs = load_translations(t_path, encoding=encoding_t)
    try:
        tid = int(row_index_key)
    except Exception:
        tid = None
    if tid is not None:
        name = t_name if t_name is not None else trecs.get(tid, ('', ''))[0]
        tip = t_tip if t_tip is not None else trecs.get(tid, ('', ''))[1]
        trecs[tid] = (name, tip)
        if t_path.exists():
            backup_file(t_path)
        else:
            # ensure folder exists
            t_path.parent.mkdir(parents=True, exist_ok=True)
        save_translations(t_path, trecs, encoding=encoding_t)


# Minimal Qt widget (optional) kept simple to avoid heavy GUI logic here.
def panel_widget(parent, lib_path: Optional[Path] = None):
    try:
        from PySide6.QtWidgets import QLabel
    except Exception:
        # if Qt not available, still allow imports
        return None
    if lib_path is None:
        lib_path = Path.cwd() / 'Lib'
    return QLabel(f'Items editor (uses lib {lib_path})')
