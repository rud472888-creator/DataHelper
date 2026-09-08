from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from frameproof.adapters.arriraw_art_adapter_client import ARRIRAWArtAdapterClient
from frameproof.adapters.braw_adapter_client import BRAWAdapterClient
from frameproof.adapters.base import CaptureAdapter
from frameproof.adapters.ffmpeg_adapter import FFmpegAdapter
from frameproof.adapters.r3d_adapter_client import R3DAdapterClient
from frameproof.config.settings import AdapterSettings
from frameproof.core.models import ClipCandidate, ClipStatus, FormatFamily

STANDARD_EXTENSIONS: frozenset[str] = frozenset(
    {
        "avi",
        "m4v",
        "mkv",
        "mov",
        "mp4",
        "mxf",
        "mpeg",
        "mpg",
        "webm",
        "wmv",
    }
)

RAW_EXTENSION_MAP: dict[str, FormatFamily] = {
    "braw": FormatFamily.BRAW,
    "r3d": FormatFamily.R3D,
    "ari": FormatFamily.ARRIRAW,
}

_RECOGNIZED_ARRIRAW_PICTURE_CODING_ULS: tuple[bytes, ...] = tuple(
    bytes.fromhex(value)
    for value in (
        "060e2b340401010d0401020102010101",
        "060e2b340401010d0401020102010102",
        "060e2b340401010d0401020102010103",
        "060e2b340401010d0401020102010201",
        "060e2b340401010d0401020102010202",
        "060e2b340401010d0f01020101010100",
        "060e2b340401010d0f01020101010200",
    )
)
_MXF_HEADER_SCAN_LIMIT_BYTES = 16 * 1024 * 1024
_MXF_HEADER_SCAN_CHUNK_BYTES = 64 * 1024
_MXF_SCAN_OVERLAP_BYTES = len(_RECOGNIZED_ARRIRAW_PICTURE_CODING_ULS[0]) - 1


@dataclass(frozen=True)
class AdapterSelection:
    candidate: ClipCandidate
    format_family: FormatFamily
    adapter_name: str
    adapter: CaptureAdapter | None
    terminal_status: ClipStatus | None = None
    terminal_message: str | None = None


def resolve_adapter(candidate: ClipCandidate, settings: AdapterSettings) -> AdapterSelection:
    extension = (candidate.format_hint or "").lower()
    raw_family = RAW_EXTENSION_MAP.get(extension)
    if raw_family is FormatFamily.BRAW:
        return AdapterSelection(
            candidate=candidate,
            format_family=raw_family,
            adapter_name="braw_adapter",
            adapter=BRAWAdapterClient(settings),
        )
    if raw_family is FormatFamily.R3D:
        return AdapterSelection(
            candidate=candidate,
            format_family=raw_family,
            adapter_name="r3d_adapter",
            adapter=R3DAdapterClient(settings),
        )
    if raw_family is FormatFamily.ARRIRAW or (extension == "mxf" and _is_arriraw_mxf(candidate)):
        return AdapterSelection(
            candidate=candidate,
            format_family=FormatFamily.ARRIRAW,
            adapter_name="arriraw_art_adapter",
            adapter=ARRIRAWArtAdapterClient(settings),
        )

    if extension not in STANDARD_EXTENSIONS:
        return AdapterSelection(
            candidate=candidate,
            format_family=FormatFamily.STANDARD,
            adapter_name="unsupported_standard",
            adapter=None,
            terminal_status=ClipStatus.UNSUPPORTED_FORMAT,
            terminal_message=f"{extension or 'unknown'} is not a Stage 4A standard-video extension",
        )

    return AdapterSelection(
        candidate=candidate,
        format_family=FormatFamily.STANDARD,
        adapter_name="ffmpeg",
        adapter=FFmpegAdapter(settings),
    )


def _is_arriraw_mxf(candidate: ClipCandidate) -> bool:
    try:
        with Path(candidate.source_path).open("rb") as source:
            return _stream_contains_arriraw_ul(source)
    except OSError:
        return False


def _stream_contains_arriraw_ul(source: BinaryIO) -> bool:
    remaining = _MXF_HEADER_SCAN_LIMIT_BYTES
    overlap = b""

    while remaining > 0:
        chunk = source.read(min(_MXF_HEADER_SCAN_CHUNK_BYTES, remaining))
        if not chunk:
            return False
        remaining -= len(chunk)

        scan_window = overlap + chunk
        if any(
            ul in scan_window for ul in _RECOGNIZED_ARRIRAW_PICTURE_CODING_ULS
        ):
            return True
        overlap = scan_window[-_MXF_SCAN_OVERLAP_BYTES:]

    return False
