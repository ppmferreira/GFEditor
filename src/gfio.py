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

    # If expected_fields is provided, read whole file and split logical
    # records by the pattern '\n' followed by an ID (digits and a pipe).
    # This reliably groups multiline Tip fields into the same logical record.
    if expected_fields is None:
        with open(path, 'r', encoding=encoding, errors='replace', newline='') as f:
            i = 0
            for raw in f:
                if limit is not None and i >= limit:
                    break
                line = raw.rstrip('\r\n')
                rows.append(line.split('|'))
                i += 1
        return rows

    # expected_fields provided: use regex split on newline before an ID
    import re
    with open(path, 'r', encoding=encoding, errors='replace', newline='') as f:
        text = f.read()

    # Split at newlines that precede a numeric ID + pipe. Keep initial segment.
    parts = re.split(r'\r?\n(?=\d+\|)', text)
    expected_len = expected_fields
    count = 0
    for part in parts:
        if limit is not None and count >= limit:
            break
        # strip trailing newline characters (if any) then split by pipe
        record = part.rstrip('\r\n')
        fields = record.split('|')
        # normalize to expected length
        if len(fields) < expected_len:
            fields += [''] * (expected_len - len(fields))
        elif len(fields) > expected_len:
            fields = fields[:expected_len]
        rows.append(fields)
        count += 1
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
