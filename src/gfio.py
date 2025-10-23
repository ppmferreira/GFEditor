# -*- coding: utf-8 -*-
"""IO utilities for GF Editor (in src package)."""
from typing import List, Optional
import chardet


def detect_encoding(path: str, default: str = 'utf-8') -> str:
    with open(path, 'rb') as f:
        sample = f.read(4096)
    if not sample:
        return default
    detected = chardet.detect(sample)
    enc = detected.get('encoding') or default
    return enc


def read_pipe_file(path: str, encoding: Optional[str] = None, limit: Optional[int] = None,
                   expected_fields: Optional[int] = None) -> List[List[str]]:
    """Read a pipe-delimited file.

    If expected_fields is provided, this will accumulate physical lines until a
    logical record contains at least that many fields. This supports fields that
    contain embedded newlines (e.g., multilingual Tip fields).
    """
    if encoding is None:
        encoding = detect_encoding(path)
    rows: List[List[str]] = []
    with open(path, 'r', encoding=encoding, errors='replace', newline='') as f:
        i = 0
        cur_buf = None  # accumulated physical lines for current logical record
        for raw in f:
            if limit is not None and i >= limit:
                break
            line = raw.rstrip('\r\n')
            # fast path: no multiline expected
            if expected_fields is None:
                rows.append(line.split('|'))
                i += 1
                continue

            # Decide whether this physical line starts a new logical record.
            # Heuristic: if the first field looks like an integer id, treat as new record.
            first_field = line.split('|', 1)[0]
            is_new = False
            try:
                # allow numeric ids (possibly empty strings will raise)
                if first_field != '':
                    _ = int(first_field)
                    is_new = True
            except Exception:
                is_new = False

            if cur_buf is None:
                # start new buffer
                cur_buf = line
                # if this single line already has expected fields, finalize immediately
                if len(cur_buf.split('|')) >= expected_fields:
                    rows.append(cur_buf.split('|'))
                    cur_buf = None
                    i += 1
                continue

            # cur_buf exists: decide if this line is continuation or new record
            if is_new:
                # finalize previous
                rows.append(cur_buf.split('|'))
                i += 1
                # start new buffer with this line
                cur_buf = line
                if len(cur_buf.split('|')) >= expected_fields:
                    rows.append(cur_buf.split('|'))
                    cur_buf = None
                    i += 1
            else:
                # continuation: append with newline and keep accumulating
                cur_buf += '\n' + line

        # end for
        if cur_buf is not None and (limit is None or i < limit):
            rows.append(cur_buf.split('|'))
            i += 1
    return rows


def read_ids(path: str, encoding: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
    """Read only the first field (Id) from each line to avoid loading full dataset into memory.

    Returns a list of id strings (may be empty strings for blank ids).
    """
    if encoding is None:
        encoding = detect_encoding(path)
    ids = []
    with open(path, 'r', encoding=encoding, errors='replace', newline='') as f:
        cur_id = None
        count = 0
        for raw in f:
            if limit is not None and count >= limit:
                break
            line = raw.rstrip('\r\n')
            first = line.split('|', 1)[0]
            is_new = False
            try:
                if first != '':
                    _ = int(first)
                    is_new = True
            except Exception:
                is_new = False

            if is_new:
                ids.append(first)
                cur_id = first
                count += 1
            else:
                # continuation line - ignore for ids
                continue
    return ids


def write_pipe_file(path: str, rows: List[List[str]], encoding: str = 'utf-8') -> None:
    # use errors='replace' to avoid raising on characters not representable in target encoding
    with open(path, 'w', encoding=encoding, errors='replace', newline='') as f:
        for row in rows:
            f.write('|'.join(row) + '\n')
