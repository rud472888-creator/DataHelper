from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

from .models import ClipCandidate

_R3D_PART_SUFFIX = ".r3d"
_R3D_PART_DIGITS = 3
_R3D_FIRST_PART_NUMBER = 1
_CANONICAL_RED_CLIP_STEM = re.compile(r"[A-Z][0-9]{3}_[A-Z][0-9]{3}_[0-9]{4}[A-Z0-9]{2}")
_ARRIRAW_FRAME_SUFFIX = ".ari"


def group_clip_candidates(paths: Sequence[Path]) -> tuple[ClipCandidate, ...]:
    path_groups = _build_r3d_groups(paths)
    path_groups.update(_build_arriraw_groups(paths))
    candidates: list[ClipCandidate] = []
    consumed: set[tuple[str, str]] = set()

    for path in paths:
        path_key = _path_key(path)
        if path_key in consumed:
            continue

        group_paths = path_groups.get(path_key)
        if group_paths is None:
            group_paths = (path,)

        for grouped_path in group_paths:
            consumed.add(_path_key(grouped_path))

        source_path = group_paths[0]
        stat = source_path.stat()
        candidates.append(
            ClipCandidate(
                candidate_id=f"candidate-{len(candidates) + 1:04d}",
                source_path=str(source_path),
                part_files=tuple(str(grouped_path) for grouped_path in group_paths),
                file_size_bytes=stat.st_size,
                modified_time=stat.st_mtime,
                format_hint=source_path.suffix.lower().lstrip(".") or None,
            )
        )

    return tuple(candidates)


def group_standard_clips(paths: Sequence[Path]) -> tuple[ClipCandidate, ...]:
    return group_clip_candidates(paths)


def _build_r3d_groups(paths: Sequence[Path]) -> dict[tuple[str, str], tuple[Path, ...]]:
    grouped_parts: dict[tuple[str, str], list[tuple[int, Path]]] = {}
    for path in paths:
        group_key = _r3d_group_key(path)
        if group_key is None:
            continue
        grouped_parts.setdefault(group_key, []).append((_r3d_part_number(path), path))

    resolved: dict[tuple[str, str], tuple[Path, ...]] = {}
    for group_key, members in grouped_parts.items():
        if len(members) < 2 or not any(number == _R3D_FIRST_PART_NUMBER for number, _ in members):
            continue
        ordered_paths = tuple(path for _, path in sorted(members, key=lambda member: member[0]))
        for path in ordered_paths:
            resolved[_path_key(path)] = ordered_paths
    return resolved


def _build_arriraw_groups(paths: Sequence[Path]) -> dict[tuple[str, str], tuple[Path, ...]]:
    grouped_frames: dict[tuple[str, str], list[tuple[int, Path]]] = {}
    for path in paths:
        group_key = _arriraw_group_key(path)
        if group_key is None:
            continue
        grouped_frames.setdefault(group_key, []).append((_arriraw_frame_number(path), path))

    resolved: dict[tuple[str, str], tuple[Path, ...]] = {}
    for members in grouped_frames.values():
        if len(members) < 2:
            continue
        ordered_paths = tuple(path for _, path in sorted(members, key=lambda member: member[0]))
        for path in ordered_paths:
            resolved[_path_key(path)] = ordered_paths
    return resolved


def _r3d_group_key(path: Path) -> tuple[str, str] | None:
    if path.suffix.lower() != _R3D_PART_SUFFIX:
        return None
    stem = path.stem
    base, separator, suffix = stem.rpartition("_")
    if separator != "_" or not base or len(suffix) != _R3D_PART_DIGITS or not suffix.isdigit():
        return None
    if not path.parent.name.lower().endswith(".rdc") and _CANONICAL_RED_CLIP_STEM.fullmatch(base) is None:
        return None
    return (str(path.parent.resolve()), base)


def _r3d_part_number(path: Path) -> int:
    return int(path.stem.rpartition("_")[2])


def _arriraw_group_key(path: Path) -> tuple[str, str] | None:
    if path.suffix.lower() != _ARRIRAW_FRAME_SUFFIX:
        return None
    base, separator, frame_number = path.stem.rpartition(".")
    if separator != "." or not base or not frame_number.isdigit():
        return None
    return (str(path.parent.resolve()), base)


def _arriraw_frame_number(path: Path) -> int:
    return int(path.stem.rpartition(".")[2])


def _path_key(path: Path) -> tuple[str, str]:
    return (str(path.parent.resolve()), path.name)
