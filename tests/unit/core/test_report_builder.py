from __future__ import annotations

from frameproof.core.models import (
    AdapterError,
    AdapterErrorCode,
    BatchStatus,
    CaptureResult,
    CaptureStatus,
    ClipInfo,
    ClipStatus,
    FormatFamily,
    ProbeResult,
)
from frameproof.core.report_builder import build_batch_summary, build_report_item, with_exported_image_paths


def make_clip(**overrides: object) -> ClipInfo:
    payload: dict[str, object] = {
        "clip_id": "candidate-0001",
        "clip_name": "clip.mov",
        "source_path": "/clips/clip.mov",
        "format_family": FormatFamily.STANDARD,
        "frame_count": 24,
        "duration_seconds": 1.0,
        "fps_num": 24,
        "fps_den": 1,
        "width": 1920,
        "height": 1080,
    }
    payload.update(overrides)
    return ClipInfo(**payload)


def test_build_report_item_marks_partial_success_when_some_captures_fail() -> None:
    probe = ProbeResult(
        ok=True,
        adapter_name="ffmpeg",
        format_family=FormatFamily.STANDARD,
        clip=make_clip(start_timecode="01:00:00:00"),
        status=ClipStatus.SUCCESS,
    )
    captures = (
        CaptureResult(
            label="Start",
            requested_ratio=0.0,
            requested_frame_index=0,
            actual_frame_index=0,
            actual_seconds=0.0,
            status=CaptureStatus.SUCCESS,
        ),
        CaptureResult(
            label="End",
            requested_ratio=1.0,
            requested_frame_index=23,
            status=CaptureStatus.DECODE_FAILED,
            errors=(AdapterError(code=AdapterErrorCode.DECODE_FAILED, message="decode failed"),),
        ),
    )

    item = build_report_item(probe, captures)

    assert item.status is ClipStatus.PARTIAL_SUCCESS
    assert item.captures[0].actual_timecode == "01:00:00:00 (calculated)"
    assert item.captures[1].status is CaptureStatus.DECODE_FAILED
    assert item.errors[0].message == "decode failed"


def test_build_report_item_preserves_probe_failures_without_capture_records() -> None:
    probe = ProbeResult(
        ok=False,
        adapter_name="ffmpeg",
        format_family=FormatFamily.STANDARD,
        status=ClipStatus.PROBE_FAILED,
        errors=(AdapterError(code=AdapterErrorCode.PROBE_FAILED, message="ffprobe failed"),),
        metadata_raw={"candidate_id": "candidate-0002", "source_path": "/clips/bad.mp4", "clip_name": "bad.mp4"},
    )

    item = build_report_item(probe)

    assert item.clip.clip_id == "candidate-0002"
    assert item.status is ClipStatus.PROBE_FAILED
    assert item.captures == ()


def test_build_batch_summary_uses_normalized_stage_counts() -> None:
    items = (
        build_report_item(
            ProbeResult(
                ok=True,
                adapter_name="ffmpeg",
                format_family=FormatFamily.STANDARD,
                clip=make_clip(clip_id="success", clip_name="success.mov", source_path="/clips/success.mov"),
                status=ClipStatus.SUCCESS,
            ),
            (
                CaptureResult(
                    label="Start",
                    requested_ratio=0.0,
                    requested_frame_index=0,
                    actual_frame_index=0,
                    actual_seconds=0.0,
                ),
                CaptureResult(
                    label="End",
                    requested_ratio=1.0,
                    requested_frame_index=23,
                    actual_frame_index=23,
                    actual_seconds=23 / 24,
                ),
            ),
        ),
        build_report_item(
            ProbeResult(
                ok=False,
                adapter_name="ffmpeg",
                format_family=FormatFamily.STANDARD,
                status=ClipStatus.DEPENDENCY_MISSING,
                errors=(AdapterError(code=AdapterErrorCode.DEPENDENCY_MISSING, message="missing"),),
                metadata_raw={"candidate_id": "missing", "source_path": "/clips/missing.mp4", "clip_name": "missing.mp4"},
            )
        ),
    )

    summary = build_batch_summary(items)

    assert summary.total_clips == 2
    assert summary.success_count == 1
    assert summary.skipped_count == 1
    assert summary.status is BatchStatus.PARTIAL_SUCCESS


def test_with_exported_image_paths_updates_matching_capture_labels() -> None:
    item = build_report_item(
        ProbeResult(
            ok=True,
            adapter_name="ffmpeg",
            format_family=FormatFamily.STANDARD,
            clip=make_clip(),
            status=ClipStatus.SUCCESS,
        ),
        (
            CaptureResult(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                actual_frame_index=0,
                actual_seconds=0.0,
            ),
            CaptureResult(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=23,
                actual_frame_index=23,
                actual_seconds=23 / 24,
            ),
        ),
    )

    updated = with_exported_image_paths(item, {"Start": "/exports/start.png"})

    assert updated.captures[0].image_path_exported == "/exports/start.png"
    assert updated.captures[1].image_path_exported is None
