"""CLI for src-based package."""
from pathlib import Path
import sys
from . import gfio as _io


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print('Usage: gfeditor <path_to_file> [encoding]')
        return 1
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
