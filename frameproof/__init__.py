"""Repo-root shim for direct module execution during bootstrap."""

from __future__ import annotations

import importlib
from pathlib import Path

_SRC_PACKAGE = Path(__file__).resolve().parent.parent / "src" / "frameproof"

if _SRC_PACKAGE.is_dir():
    src_path = str(_SRC_PACKAGE)
    if src_path not in __path__:
        __path__.append(src_path)

__version__ = importlib.import_module("frameproof.__about__").__version__

__all__ = ["__version__"]
