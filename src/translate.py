# -*- coding: utf-8 -*-
from pathlib import Path
import re
from typing import Dict, Tuple


def read_t_file(path: Path, encoding: str = None) -> Dict[int, Tuple[str, str]]:
    """Read a T_ file and return dict[id] = (name, desc_raw).

    The parser detects records starting with digits + '|' and groups lines until
    the next record. It preserves the raw description field (may include tags
    like $7$/$12$).
    """
    if encoding is None:
        # prefer system ANSI on Windows
        try:
            enc = 'mbcs'
        except Exception:
            enc = 'latin-1'
    else:
        enc = encoding

    text = Path(path).read_text(encoding=enc, errors='replace')
    lines = text.splitlines(True)

    records = {}
    buf = ''
    current_id = None
    # regex to detect start of record: digits followed by '|'
    start_re = re.compile(r'^(\d+)\|')
    for line in lines:
        m = start_re.match(line)
        if m:
            # flush previous
            if buf:
                # parse previous buf
                rid, name, desc = _parse_t_record(buf)
                records[int(rid)] = (name, desc)
            buf = line
            current_id = m.group(1)
        else:
            buf += line
    if buf:
        rid, name, desc = _parse_t_record(buf)
        records[int(rid)] = (name, desc)
    return records


def _parse_t_record(buf: str) -> Tuple[str, str, str]:
    # split first two '|' occurrences: id|name|desc|
    parts = buf.split('|')
    rid = parts[0].strip()
    name = parts[1] if len(parts) > 1 else ''
    # description is everything after the second '|', rejoin and strip trailing '|'
    if len(parts) > 2:
        desc = '|'.join(parts[2:])
        if desc.endswith('|'):
            desc = desc[:-1]
    else:
        desc = ''
    return rid, name, desc


def write_t_file(path: Path, records: Dict[int, Tuple[str, str]], encoding: str = None) -> None:
    """Write the T_ file from the dict. Keeps ascending key order."""
    if encoding is None:
        try:
            enc = 'mbcs'
        except Exception:
            enc = 'latin-1'
    else:
        enc = encoding

    out_lines = []
    for rid in sorted(records.keys()):
        name, desc = records[rid]
        # ensure desc ends without trailing newline handling — keep as-is
        out_lines.append(f"{rid}|{name}|{desc}|\n")

    Path(path).write_text(''.join(out_lines), encoding=enc, errors='replace')
