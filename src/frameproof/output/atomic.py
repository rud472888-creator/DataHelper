from __future__ import annotations

import os
import secrets
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def atomic_output_path(destination: Path) -> Iterator[Path]:
    """Yield a sibling temp path that replaces ``destination`` only on success.

    Readers polling the destination (the orchestrator checks for non-empty
    files) never observe a half-written artifact, and an interrupted write
    leaves no truncated file behind.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_name(f".{destination.name}.{secrets.token_hex(6)}.partial")
    # Created with 0o666 so the process umask applies, like a direct write.
    os.close(os.open(temp_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o666))
    try:
        yield temp_path
        os.replace(temp_path, destination)
    finally:
        temp_path.unlink(missing_ok=True)
