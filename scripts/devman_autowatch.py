#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path('/Users/server_jay/Desktop/DataHelper')
STATE_PATH = REPO_ROOT / '.devman' / 'watch-state.json'
WATCH_GLOBS = [
    'docs/stage.md',
    'docs/reports/status/current-status.md',
    'docs/reports/dev/*.md',
    'docs/reports/qa/*.md',
]
STABLE_SECONDS = 30


def watched_files():
    files = []
    for pattern in WATCH_GLOBS:
        files.extend(sorted(REPO_ROOT.glob(pattern)))
    return [p for p in files if p.is_file()]


def load_state():
    if not STATE_PATH.exists():
        return {'files': {}, 'last_triggered_at': None}
    return json.loads(STATE_PATH.read_text(encoding='utf-8'))


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')


def scan(now):
    state = load_state()
    files_state = state.setdefault('files', {})
    pending = []
    active = set()
    for path in watched_files():
        active.add(str(path))
        stat = path.stat()
        sig = f'{stat.st_size}:{stat.st_mtime_ns}'
        record = files_state.get(str(path))
        if record is None or record.get('signature') != sig:
            files_state[str(path)] = {
                'signature': sig,
                'first_seen_at': now,
                'last_seen_at': now,
                'processed_signature': record.get('processed_signature') if record else None,
            }
            continue
        record['last_seen_at'] = now
        if now - float(record.get('first_seen_at', now)) >= STABLE_SECONDS and record.get('processed_signature') != sig:
            pending.append((str(path), sig))
    for stale in list(files_state.keys()):
        if stale not in active:
            del files_state[stale]
    save_state(state)
    return state, pending


def main():
    now = time.time()
    state, pending = scan(now)
    if not pending:
        return 0
    script = REPO_ROOT / 'scripts' / 'run_devman_cycle.sh'
    result = subprocess.run([str(script)], cwd=str(REPO_ROOT), text=True, capture_output=True)
    if result.returncode == 0:
        for path, sig in pending:
            state['files'][path]['processed_signature'] = sig
            state['files'][path]['processed_at'] = now
        state['last_triggered_at'] = now
        save_state(state)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
