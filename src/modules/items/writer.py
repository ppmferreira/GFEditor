import os
import csv
from typing import List


def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def write_items_pair(header: List[str], rows: List[List[str]], client_path: str, server_path: str, delimiter: str = '|', encoding: str = 'big5') -> None:
    """Write header and rows to two files (client and server).

    Note: client/server item files are expected to be encoded in BIG5;
    this function defaults to `encoding='big5'` for that reason.

    The same content is written to both paths so C_ and S_ remain identical.
    """
    # Ensure directories exist
    _ensure_dir(client_path)
    _ensure_dir(server_path)

    for path in (client_path, server_path):
        with open(path, 'w', encoding=encoding, newline='') as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(header)
            for row in rows:
                # make sure row has same length
                if len(row) < len(header):
                    row = row + [''] * (len(header) - len(row))
                elif len(row) > len(header):
                    row = row[:len(header)]
                writer.writerow(row)
