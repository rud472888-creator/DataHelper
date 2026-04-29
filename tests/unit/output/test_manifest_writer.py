from __future__ import annotations

import json
from pathlib import Path

from frameproof.config.settings import OutputSettings
from frameproof.core.models import (
    AdapterError,
    AdapterErrorCode,
    BatchStatus,
    BatchSummary,
    CapturePoint,
    CaptureStatus,
    ClipInfo,
    ClipStatus,
    FormatFamily,
    ReportItem,
    TimecodeSource,
)
from frameproof.output.manifest_writer import build_manifest_rows, write_manifests


def make_clip(**overrides: object) -> ClipInfo:
    payload: dict[str, object] = {
        "clip_id": "clip-1",
        "clip_name": "clip.mov",
        "source_path": "/clips/clip.mov",
        "format_family": FormatFamily.STANDARD,
        "frame_count": 48,
        "duration_seconds": 2.0,
        "fps_num": 24,
        "fps_den": 1,
        "width": 1920,
        "height": 1080,
    }
    payload.update(overrides)
    return ClipInfo(**payload)


def make_summary(total: int) -> BatchSummary:
    return BatchSummary(
        total_clips=total,
        success_count=1,
        partial_success_count=1 if total > 1 else 0,
        probe_failed_count=0,
        decode_failed_count=0,
        skipped_count=0,
        status=BatchStatus.PARTIAL_SUCCESS if total > 1 else BatchStatus.SUCCESS,
    )


def test_build_manifest_rows_preserves_exported_image_paths_and_failures() -> None:
    success_item = ReportItem(
        clip=make_clip(),
        captures=(
            CapturePoint(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=1,
                actual_seconds=0.041,
                actual_timecode="01:00:00:01",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_exported="/exports/clip__start.png",
                status=CaptureStatus.SUCCESS,
                warnings=("capture warning",),
            ),
            CapturePoint(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=47,
                requested_seconds=1.958,
                actual_frame_index=47,
                actual_seconds=1.958,
                actual_timecode="01:00:01:23",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_exported="/exports/clip__end.png",
                status=CaptureStatus.SUCCESS,
            ),
        ),
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
        warnings=("clip warning",),
    )
    failed_item = ReportItem(
        clip=make_clip(clip_id="clip-2", clip_name="broken.mov", source_path="/clips/broken.mov"),
        captures=(),
        status=ClipStatus.PROBE_FAILED,
        adapter_name="ffmpeg",
        errors=(AdapterError(code=AdapterErrorCode.PROBE_FAILED, message="probe failed"),),
    )

    rows = build_manifest_rows((success_item, failed_item))

    assert rows[0]["image_path"] == "/exports/clip__start.png"
    assert rows[0]["actual_timecode"] == "01:00:00:01"
    assert rows[0]["warnings"] == "clip warning | capture warning"
    assert rows[2]["capture_label"] == ""
    assert rows[2]["status"] == "probe_failed"
    assert rows[2]["errors"] == "probe failed"


def test_build_manifest_rows_keeps_partial_capture_parity_when_stills_are_off() -> None:
    item = ReportItem(
        clip=make_clip(),
        captures=(
            CapturePoint(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=0,
                actual_seconds=0.0,
                actual_timecode="01:00:00:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                status=CaptureStatus.SUCCESS,
            ),
            CapturePoint(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=47,
                requested_seconds=1.958,
                status=CaptureStatus.DECODE_FAILED,
                warnings=("fallback timecode",),
                errors=(AdapterError(code=AdapterErrorCode.DECODE_FAILED, message="decode failed"),),
            ),
        ),
        status=ClipStatus.PARTIAL_SUCCESS,
        adapter_name="ffmpeg",
        warnings=("clip degraded",),
        errors=(AdapterError(code=AdapterErrorCode.DECODE_FAILED, message="decode failed"),),
    )

    rows = build_manifest_rows((item,))

    assert rows[0]["image_path"] is None
    assert rows[1]["capture_label"] == "End"
    assert rows[1]["requested_frame_index"] == 47
    assert rows[1]["requested_seconds"] == 1.958
    assert rows[1]["actual_frame_index"] is None
    assert rows[1]["actual_seconds"] is None
    assert rows[1]["actual_timecode"] is None
    assert rows[1]["status"] == "decode_failed"
    assert rows[1]["warnings"] == "clip degraded | fallback timecode"
    assert rows[1]["errors"] == "decode failed"


def test_write_manifests_keeps_clip_and_row_parity(tmp_path: Path) -> None:
    item = ReportItem(
        clip=make_clip(),
        captures=(
            CapturePoint(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=0,
                actual_seconds=0.0,
                actual_timecode="01:00:00:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_exported=str(tmp_path / "stills" / "start.png"),
                status=CaptureStatus.SUCCESS,
            ),
            CapturePoint(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=47,
                requested_seconds=1.958,
                actual_frame_index=47,
                actual_seconds=1.958,
                actual_timecode="01:00:01:23",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_exported=str(tmp_path / "stills" / "end.png"),
                status=CaptureStatus.SUCCESS,
            ),
        ),
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
    )
    output = OutputSettings(
        pdf_path=tmp_path / "report.pdf",
        csv_path=tmp_path / "report.csv",
        json_path=tmp_path / "report.json",
    )

    csv_path, json_path = write_manifests(output, (item,), make_summary(1))

    assert csv_path == tmp_path / "report.csv"
    assert json_path == tmp_path / "report.json"

    payload = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert payload["rows"][0]["image_path"] == str(tmp_path / "stills" / "start.png")
    assert payload["clips"][0]["captures"][0]["image_path"] == str(tmp_path / "stills" / "start.png")
    assert payload["clips"][0]["captures"][0]["requested_frame_index"] == payload["rows"][0]["requested_frame_index"]


def test_write_manifests_preserves_duplicate_slot_parity(tmp_path: Path) -> None:
    item = ReportItem(
        clip=make_clip(frame_count=1),
        captures=(
            CapturePoint(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=0,
                actual_seconds=0.0,
                actual_timecode="01:00:00:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                status=CaptureStatus.SUCCESS,
            ),
            CapturePoint(
                label="Mid1",
                requested_ratio=0.25,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=0,
                actual_seconds=0.0,
                actual_timecode="01:00:00:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                duplicate_of="Start",
                status=CaptureStatus.SKIPPED_DUPLICATE,
                warnings=("short_clip_duplicate",),
            ),
            CapturePoint(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=0,
                actual_seconds=0.0,
                actual_timecode="01:00:00:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                duplicate_of="Start",
                status=CaptureStatus.SKIPPED_DUPLICATE,
                warnings=("short_clip_duplicate",),
            ),
        ),
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
    )
    output = OutputSettings(
        pdf_path=tmp_path / "report.pdf",
        csv_path=tmp_path / "report.csv",
        json_path=tmp_path / "report.json",
    )

    csv_path, json_path = write_manifests(output, (item,), make_summary(1))
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert csv_path == tmp_path / "report.csv"
    assert payload["rows"][1]["capture_label"] == "Mid1"
    assert payload["rows"][1]["status"] == "skipped_duplicate"
    assert payload["clips"][0]["captures"][1]["duplicate_of"] == "Start"
