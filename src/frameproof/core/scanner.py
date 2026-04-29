from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence


def _normalized_extension(path: Path) -> str:
    return path.suffix.lower().lstrip(".")


def scan_inputs(
    input_paths: Sequence[Path],
    *,
    recursive: bool,
    extensions: Iterable[str],
) -> tuple[Path, ...]:
    allowed_extensions = {extension.lower().lstrip(".") for extension in extensions if extension.strip()}
    discovered: set[Path] = set()

    for raw_path in input_paths:
        path = raw_path.expanduser()
        if path.is_file():
            if _normalized_extension(path) in allowed_extensions:
                discovered.add(path.resolve())
            continue

        if not path.is_dir():
            continue

        iterator = path.rglob("*") if recursive else path.glob("*")
        for child in iterator:
            if child.is_file() and _normalized_extension(child) in allowed_extensions:
                discovered.add(child.resolve())

    return tuple(sorted(discovered, key=lambda item: str(item).lower()))
