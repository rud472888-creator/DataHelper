from __future__ import annotations

from pathlib import Path

from PIL import Image

from frameproof.core.models import CapturePoint, CaptureStatus, ClipInfo, ClipStatus, FormatFamily, ReportItem
from frameproof.output.still_exporter import export_stills, sanitize_path_component


def make_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (32, 18), color=(12, 34, 56)).save(path)


def make_item(image_path: str | None, *, clip_name: str = "A001:Shot/01.mov", actual_timecode: str = "01:00:00;12") -> ReportItem:
    clip = ClipInfo(
        clip_id="clip-1",
        clip_name=clip_name,
        source_path="/show/reel/A001:Shot/01.mov",
        format_family=FormatFamily.STANDARD,
        frame_count=48,
        duration_seconds=2.0,
        fps_num=24,
        fps_den=1,
    )
    start = CapturePoint(
        label="Start",
        requested_ratio=0.0,
        requested_frame_index=0,
        actual_frame_index=0,
        actual_seconds=0.0,
        actual_timecode=actual_timecode,
        image_path_temp=image_path,
        status=CaptureStatus.SUCCESS,
    )
    end = CapturePoint(
        label="End",
        requested_ratio=1.0,
        requested_frame_index=47,
        actual_frame_index=47,
        actual_seconds=1.958,
        actual_timecode="01:00:01:23",
        image_path_temp=image_path,
        status=CaptureStatus.SUCCESS,
    )
    return ReportItem(clip=clip, captures=(start, end), status=ClipStatus.SUCCESS, adapter_name="ffmpeg")


def test_sanitize_path_component_handles_drop_frame_and_long_names() -> None:
    sanitized = sanitize_path_component("Clip:Name;Drop/Frame", fallback="fallback")
    long_name = sanitize_path_component("x" * 200, fallback="fallback", max_length=40)

    assert sanitized == "Clip_Name_df_Drop_Frame"
    assert len(long_name) <= 40
    assert "__" in long_name


def test_sanitize_path_component_sanitizes_fallbacks_too() -> None:
    sanitized = sanitize_path_component("../..", fallback="../unsafe:name")

    assert sanitized == "unsafe_name"


def test_sanitize_path_component_preserves_non_ascii_letters() -> None:
    sanitized = sanitize_path_component("한글 Clip 01", fallback="fallback")

    assert sanitized == "한글_Clip_01"


def test_export_stills_copies_pngs_and_adds_collision_suffix(tmp_path: Path) -> None:
    source_png = tmp_path / "capture.png"
    make_png(source_png)
    item = make_item(str(source_png))

    first = export_stills(item, tmp_path / "stills")
    second = export_stills(item, tmp_path / "stills")

    first_path = Path(first["Start"] or "")
    second_path = Path(second["Start"] or "")

    assert first_path.is_file()
    assert second_path.is_file()
    assert "_df_" in first_path.name
    assert first_path.parent.name == "A001_Shot_01.mov"
    assert second_path.name.endswith("_001.png")


def test_export_stills_skips_missing_temp_images(tmp_path: Path) -> None:
    item = make_item(None)

    exported = export_stills(item, tmp_path / "stills")

    assert exported == {"Start": None, "End": None}
    assert not (tmp_path / "stills").exists()


def test_export_stills_keeps_traversal_like_names_inside_stills_root(tmp_path: Path) -> None:
    source_png = tmp_path / "capture.png"
    make_png(source_png)
    item = make_item(
        str(source_png),
        clip_name="../한글:샷.mov",
        actual_timecode="../01:00:00;12",
    )

    exported = export_stills(item, tmp_path / "stills root")

    start_path = Path(exported["Start"] or "")
    stills_root = (tmp_path / "stills root").resolve()

    assert start_path.is_file()
    assert stills_root in start_path.resolve().parents
    assert start_path.parent.name == "한글_샷.mov"
