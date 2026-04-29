#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH_FILES = [
    ROOT / 'docs' / 'stage.md',
    ROOT / 'docs' / 'reports' / 'status' / 'current-status.md',
]
STATE = ROOT / '.hermes-orchestrator-watch.state'


def snapshot() -> str:
    parts = []
    for path in WATCH_FILES:
        if path.exists():
            stat = path.stat()
            parts.append(f"{path}:{stat.st_size}:{stat.st_mtime_ns}")
        else:
            parts.append(f"{path}:missing")
    return '\n'.join(parts)


def main() -> int:
    current = snapshot()
    previous = STATE.read_text(encoding='utf-8') if STATE.exists() else ''
    if current != previous:
        STATE.write_text(current, encoding='utf-8')
        print('orchestrator watcher: state changed; Hermes should re-read docs/stage.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
