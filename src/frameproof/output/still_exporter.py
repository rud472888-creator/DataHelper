from __future__ import annotations

import hashlib
import re
import shutil
import unicodedata
from pathlib import Path

from frameproof.core.models import CapturePoint, ReportItem

_UNDERSCORE_RUN_PATTERN = re.compile(r"_+")
_MAX_COMPONENT_LENGTH = 120


def export_stills(item: ReportItem, stills_dir: Path) -> dict[str, str | None]:
    clip_directory = _safe_child_path(
        stills_dir,
        item.clip.logical_clip_name or item.clip.clip_name,
        fallback=item.clip.clip_id,
    )
    exported_paths: dict[str, str | None] = {}
    used_filenames: set[str] = set()

    for capture in item.captures:
        source_path = _capture_source_path(capture)
        if source_path is None:
            exported_paths[capture.label] = None
            continue

        clip_directory.mkdir(parents=True, exist_ok=True)
        stem = "__".join(
            (
                sanitize_path_component(item.clip.clip_name, fallback=item.clip.clip_id),
                sanitize_path_component(capture.label.lower(), fallback="capture"),
                _position_token(capture),
            )
        )
        destination = _resolve_destination(clip_directory, stem, used_filenames)
        shutil.copy2(source_path, destination)
        exported_paths[capture.label] = str(destination)

    return exported_paths


def sanitize_path_component(
    value: str,
    *,
    fallback: str,
    max_length: int = _MAX_COMPONENT_LENGTH,
) -> str:
    safe_fallback = _sanitize_raw_component(fallback)
    if safe_fallback in {"", ".", ".."}:
        safe_fallback = "capture"

    sanitized = _sanitize_raw_component(value)
    if sanitized in {"", ".", ".."}:
        sanitized = safe_fallback
    if len(sanitized) > max_length:
        digest = hashlib.sha1(sanitized.encode("utf-8")).hexdigest()[:10]
        prefix_length = max(1, max_length - len(digest) - 2)
        sanitized = f"{sanitized[:prefix_length]}__{digest}"
    return sanitized


def _sanitize_raw_component(value: str) -> str:
    characters: list[str] = []
    for char in value.strip():
        if char in {"\\", "/", ":"}:
            characters.append("_")
            continue
        if char == ";":
            characters.append("_df_")
            continue
        if char.isspace():
            characters.append("_")
            continue
        if char.isalnum() or char in {"_", "-", "."}:
            characters.append(char)
            continue
        category = unicodedata.category(char)
        if category.startswith(("L", "N")):
            characters.append(char)
            continue
        characters.append("_")

    sanitized = "".join(characters)
    sanitized = _UNDERSCORE_RUN_PATTERN.sub("_", sanitized)
    return sanitized.strip(" ._")


def _capture_source_path(capture: CapturePoint) -> Path | None:
    if capture.image_path_temp is None:
        return None
    source_path = Path(capture.image_path_temp)
    if not source_path.is_file():
        return None
    return source_path


def _position_token(capture: CapturePoint) -> str:
    if capture.actual_timecode:
        return sanitize_path_component(capture.actual_timecode, fallback="timecode")
    if capture.actual_frame_index is not None:
        return f"frame_{capture.actual_frame_index:06d}"
    if capture.actual_seconds is not None:
        return sanitize_path_component(f"sec_{capture.actual_seconds:0.3f}", fallback="seconds")
    if capture.requested_frame_index is not None:
        return f"requested_frame_{capture.requested_frame_index:06d}"
    if capture.requested_seconds is not None:
        return sanitize_path_component(f"requested_sec_{capture.requested_seconds:0.3f}", fallback="requested")
    return "capture"


def _resolve_destination(directory: Path, stem: str, used_filenames: set[str]) -> Path:
    safe_stem = sanitize_path_component(stem, fallback="capture")
    base_name = f"{safe_stem}.png"
    candidate = _safe_child_path(directory, base_name, fallback="capture.png")
    if not candidate.exists() and base_name not in used_filenames:
        used_filenames.add(base_name)
        return candidate

    suffix_index = 1
    while True:
        suffix = f"_{suffix_index:03d}"
        bounded_stem = _bounded_stem_with_suffix(safe_stem, suffix)
        candidate_name = f"{bounded_stem}{suffix}.png"
        candidate = _safe_child_path(directory, candidate_name, fallback="capture.png")
        if not candidate.exists() and candidate_name not in used_filenames:
            used_filenames.add(candidate_name)
            return candidate
        suffix_index += 1


def _bounded_stem_with_suffix(stem: str, suffix: str) -> str:
    max_stem_length = _MAX_COMPONENT_LENGTH - len(".png") - len(suffix)
    return sanitize_path_component(stem, fallback="capture", max_length=max_stem_length)


def _safe_child_path(directory: Path, name: str, *, fallback: str | None = None) -> Path:
    safe_name = sanitize_path_component(name, fallback=fallback or "capture")
    candidate = directory / safe_name
    resolved_directory = directory.resolve(strict=False)
    resolved_candidate = candidate.resolve(strict=False)
    if resolved_candidate != resolved_directory and resolved_directory not in resolved_candidate.parents:
        raise ValueError(f"unsafe export path resolved outside stills directory: {candidate}")
    return candidate
