"""CLI for src-based package."""
from pathlib import Path
import sys
from . import gfio as _io
from .modules.items import read_items, write_items_pair


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print('Usage: gfeditor <path_to_file> [encoding]')
        print('       gfeditor import-items <src_path> [client_dest] [server_dest]')
        return 1

    if argv[0] == 'import-items':
        # import-items <src_path> [client_dest] [server_dest]
        if len(argv) < 2:
            print('Usage: gfeditor import-items <src_path> [client_dest] [server_dest]')
            return 1
        src = Path(argv[1])
        if not src.is_absolute():
            src = Path.cwd() / argv[1]
        if not src.exists():
            print('Source file not found:', src)
            return 2

        client_dest = Path(argv[2]) if len(argv) > 2 else Path('Lib/data/db/C_Item_import.txt')
        server_dest = Path(argv[3]) if len(argv) > 3 else Path('Lib/data/serverdb/S_Item_import.txt')

        # ensure parent dirs
        client_dest.parent.mkdir(parents=True, exist_ok=True)
        server_dest.parent.mkdir(parents=True, exist_ok=True)

        # read source (assume delimiter '|' and encoding big5 by default)
        header, rows, items = read_items(str(src), delimiter='|', encoding='big5')
        print(f'Read {len(rows)} rows, {len(items)} items, columns: {len(header)}')

        # write to client and server paths
        write_items_pair(header, rows, str(client_dest), str(server_dest), delimiter='|', encoding='big5')
        print('Wrote client:', client_dest)
        print('Wrote server:', server_dest)
        return 0

    # default: show a preview of the file using gfio
    p = Path(argv[0])
    if not p.is_absolute():
        p = Path.cwd() / argv[0]
    encoding = argv[1] if len(argv) > 1 else None
    if not p.exists():
        print('File not found:', p)
        return 2
    rows = _io.read_pipe_file(str(p), encoding=encoding, limit=20)
    for i, r in enumerate(rows[:20]):
        print(f'{i+1:4}:', r[:10])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
