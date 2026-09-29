from __future__ import annotations

from pathlib import Path

import pytest

from frameproof.adapters.arriraw_art_adapter_client import ARRIRAWArtAdapterClient
from frameproof.adapters.ffmpeg_adapter import FFmpegAdapter
from frameproof.config.settings import AdapterSettings
from frameproof.core import adapter_resolver
from frameproof.core.adapter_resolver import resolve_adapter
from frameproof.core.models import ClipCandidate, FormatFamily


def _candidate(source_path: Path, *, part_files: tuple[str, ...] | None = None) -> ClipCandidate:
    return ClipCandidate(
        candidate_id="candidate-0001",
        source_path=str(source_path),
        part_files=part_files or (str(source_path),),
        format_hint="mxf",
    )


@pytest.mark.parametrize(
    "ul_hex",
    (
        "060e2b340401010d0401020102010101",
        "060e2b340401010d0401020102010102",
        "060e2b340401010d0401020102010103",
        "060e2b340401010d0401020102010201",
        "060e2b340401010d0401020102010202",
        "060e2b340401010d0f01020101010100",
        "060e2b340401010d0f01020101010200",
    ),
)
def test_resolve_adapter_routes_recognized_arriraw_picture_coding_mxf_to_art(
    tmp_path: Path,
    ul_hex: str,
) -> None:
    source_path = tmp_path / "arriraw.mxf"
    source_path.write_bytes(b"MXF header" + bytes.fromhex(ul_hex) + b"metadata")
    candidate = _candidate(source_path, part_files=(str(source_path), str(tmp_path / "companion.mxf")))

    selection = resolve_adapter(candidate, AdapterSettings())

    assert selection.candidate is candidate
    assert selection.candidate.part_files == candidate.part_files
    assert selection.format_family is FormatFamily.ARRIRAW
    assert selection.adapter_name == "arriraw_art_adapter"
    assert isinstance(selection.adapter, ARRIRAWArtAdapterClient)


def test_resolve_adapter_keeps_mxf_without_recognized_arriraw_picture_coding_ul_on_ffmpeg_path(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "standard.mxf"
    source_path.write_bytes(b"regular MXF header metadata")

    selection = resolve_adapter(_candidate(source_path), AdapterSettings())

    assert selection.format_family is FormatFamily.STANDARD
    assert selection.adapter_name == "ffmpeg"
    assert isinstance(selection.adapter, FFmpegAdapter)


def test_resolve_adapter_detects_arriraw_ul_across_scan_chunk_boundary(tmp_path: Path) -> None:
    ul = adapter_resolver._RECOGNIZED_ARRIRAW_PICTURE_CODING_ULS[0]
    source_path = tmp_path / "boundary.mxf"
    source_path.write_bytes(b"x" * (adapter_resolver._MXF_HEADER_SCAN_CHUNK_BYTES - 8) + ul)

    selection = resolve_adapter(_candidate(source_path), AdapterSettings())

    assert selection.format_family is FormatFamily.ARRIRAW
    assert selection.adapter_name == "arriraw_art_adapter"


def test_resolve_adapter_does_not_scan_past_mxf_header_limit(monkeypatch, tmp_path: Path) -> None:
    ul = adapter_resolver._RECOGNIZED_ARRIRAW_PICTURE_CODING_ULS[0]
    source_path = tmp_path / "large-standard.mxf"
    source_path.write_bytes(b"x" * 32 + ul)
    monkeypatch.setattr(adapter_resolver, "_MXF_HEADER_SCAN_LIMIT_BYTES", 32)
    monkeypatch.setattr(adapter_resolver, "_MXF_HEADER_SCAN_CHUNK_BYTES", 8)

    selection = resolve_adapter(_candidate(source_path), AdapterSettings())

    assert selection.format_family is FormatFamily.STANDARD
    assert selection.adapter_name == "ffmpeg"


def test_resolve_adapter_falls_back_to_ffmpeg_when_mxf_read_fails(monkeypatch, tmp_path: Path) -> None:
    source_path = tmp_path / "unreadable.mxf"
    source_path.write_bytes(b"MXF")

    class FailingReader:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return None

        def read(self, size: int) -> bytes:
            raise OSError("read failed")

    monkeypatch.setattr(Path, "open", lambda path, mode: FailingReader())

    selection = resolve_adapter(_candidate(source_path), AdapterSettings())

    assert selection.format_family is FormatFamily.STANDARD
    assert selection.adapter_name == "ffmpeg"
    assert isinstance(selection.adapter, FFmpegAdapter)


def test_resolve_adapter_shares_one_adapter_per_type_with_a_batch_cache(tmp_path: Path) -> None:
    cache: dict[str, object] = {}
    first = resolve_adapter(
        ClipCandidate(candidate_id="a", source_path=str(tmp_path / "a.mov"), format_hint="mov"),
        AdapterSettings(),
        adapter_cache=cache,  # type: ignore[arg-type]
    )
    second = resolve_adapter(
        ClipCandidate(candidate_id="b", source_path=str(tmp_path / "b.mp4"), format_hint="mp4"),
        AdapterSettings(),
        adapter_cache=cache,  # type: ignore[arg-type]
    )
    uncached = resolve_adapter(
        ClipCandidate(candidate_id="c", source_path=str(tmp_path / "c.mp4"), format_hint="mp4"),
        AdapterSettings(),
    )

    assert isinstance(first.adapter, FFmpegAdapter)
    assert first.adapter is second.adapter
    assert uncached.adapter is not first.adapter
