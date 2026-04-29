from __future__ import annotations

from dataclasses import dataclass

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
    if raw_family is FormatFamily.ARRIRAW:
        return AdapterSelection(
            candidate=candidate,
            format_family=raw_family,
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
