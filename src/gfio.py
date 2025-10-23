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


def read_pipe_file(path: str, encoding: Optional[str] = None, limit: Optional[int] = None) -> List[List[str]]:
    if encoding is None:
        encoding = detect_encoding(path)
    rows: List[List[str]] = []
    with open(path, 'r', encoding=encoding, errors='replace', newline='') as f:
        for i, raw in enumerate(f):
            if limit is not None and i >= limit:
                break
            line = raw.rstrip('\r\n')
            fields = line.split('|')
            rows.append(fields)
    return rows


def write_pipe_file(path: str, rows: List[List[str]], encoding: str = 'utf-8') -> None:
    # use errors='replace' to avoid raising on characters not representable in target encoding
    with open(path, 'w', encoding=encoding, errors='replace', newline='') as f:
        for row in rows:
            f.write('|'.join(row) + '\n')
