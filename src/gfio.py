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

    # expected_fields provided: find logical records that start with an ID at
    # the beginning of a line. This ignores blank lines and any leading
    # non-record header. We use a DOTALL/multiline regex to capture from a
    # line that begins with digits+"|" up to (but not including) the next
    # such line or end-of-file. This is robust against Tip fields that
    # contain embedded newlines.
    import re
    with open(path, 'r', encoding=encoding, errors='replace', newline='') as f:
        text = f.read()

    # Pattern: from line start (^) match optional spaces then digits + '|' and
    # consume lazily until the next line that also starts with digits+| or EOF.
    pattern = re.compile(r'(?ms)^\s*\d+\|.*?(?=(?:\r?\n\s*\d+\|)|\Z)')
    matches = pattern.findall(text)

    expected_len = expected_fields
    count = 0
    for match in matches:
        if limit is not None and count >= limit:
            break
        record = match.rstrip('\r\n')
        fields = record.split('|')
        # ensure first field (id) has no stray CR/LF or surrounding whitespace
        if fields:
            fields[0] = fields[0].lstrip('\r\n').strip()
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
    # Use the same regex strategy as read_pipe_file to detect logical records
    # that start with an ID. This avoids miscounting when Tip fields contain
    # embedded newlines or when blank lines exist between records.
    import re
    ids = []
    with open(path, 'r', encoding=encoding, errors='replace', newline='') as f:
        text = f.read()

    pattern = re.compile(r'(?ms)^\s*(\d+)\|.*?(?=(?:\r?\n\s*\d+\|)|\Z)')
    count = 0
    for m in pattern.finditer(text):
        if limit is not None and count >= limit:
            break
        id_str = m.group(1).strip()
        ids.append(id_str)
        count += 1
    return ids


def write_pipe_file(path: str, rows: List[List[str]], encoding: str = 'utf-8') -> None:
    # use errors='replace' to avoid raising on characters not representable in target encoding
    with open(path, 'w', encoding=encoding, errors='replace', newline='') as f:
        for row in rows:
            f.write('|'.join(row) + '\n')
