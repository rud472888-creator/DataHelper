from __future__ import annotations

from pathlib import Path

from frameproof.core.scanner import scan_inputs


def test_scan_inputs_filters_extensions_and_sorts_deterministically(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    nested = source_root / "nested"
    nested.mkdir(parents=True)
    keep_b = source_root / "B.mov"
    keep_a = nested / "a.mp4"
    skip = nested / "ignore.txt"
    keep_b.write_bytes(b"b")
    keep_a.write_bytes(b"a")
    skip.write_text("nope", encoding="utf-8")

    result = scan_inputs((source_root,), recursive=True, extensions=("mov", "mp4"))

    assert result == (keep_b.resolve(), keep_a.resolve())


def test_scan_inputs_honors_non_recursive_mode(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    nested = source_root / "nested"
    nested.mkdir(parents=True)
    top_level = source_root / "clip.mov"
    nested_level = nested / "clip.mp4"
    top_level.write_bytes(b"top")
    nested_level.write_bytes(b"nested")

    result = scan_inputs((source_root,), recursive=False, extensions=("mov", "mp4"))

    assert result == (top_level.resolve(),)


def test_scan_inputs_ignores_appledouble_sidecar_media_names(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    clip = source_root / "PACR0155.MOV"
    appledouble = source_root / "._PACR0155.MOV"
    clip.write_bytes(b"movie")
    appledouble.write_bytes(b"metadata")

    result = scan_inputs((source_root,), recursive=False, extensions=("mov",))

    assert result == (clip.resolve(),)


def test_scan_inputs_supports_non_ascii_and_space_filled_paths(tmp_path: Path) -> None:
    source_root = tmp_path / "소스 폴더"
    source_root.mkdir()
    keep_a = source_root / "베타 Clip.MP4"
    keep_b = source_root / "alpha clip.mov"
    skip = source_root / "ignore.txt"
    keep_a.write_bytes(b"a")
    keep_b.write_bytes(b"b")
    skip.write_text("skip", encoding="utf-8")

    result = scan_inputs((source_root,), recursive=False, extensions=("mov", "mp4"))

    expected = tuple(sorted((keep_a.resolve(), keep_b.resolve()), key=lambda item: str(item).lower()))
    assert result == expected
