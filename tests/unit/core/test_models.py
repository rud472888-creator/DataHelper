from __future__ import annotations

import pytest

from frameproof.core.models import (
    AdapterError,
    AdapterErrorCode,
    BatchStatus,
    BatchSummary,
    CapturePoint,
    CaptureResult,
    CaptureStatus,
    ClipInfo,
    ClipStatus,
    FormatFamily,
    ProbeResult,
    ReportItem,
    TimecodeSource,
)


def test_clip_info_requires_frame_count_or_duration() -> None:
    with pytest.raises(ValueError, match="must not both be null"):
        ClipInfo(
            clip_id="clip-1",
            clip_name="A001_C001.mov",
            source_path="/clips/A001_C001.mov",
            format_family=FormatFamily.STANDARD,
        )


def test_clip_info_requires_fps_pair() -> None:
    with pytest.raises(ValueError, match="provided together"):
        ClipInfo(
            clip_id="clip-1",
            clip_name="A001_C001.mov",
            source_path="/clips/A001_C001.mov",
            format_family=FormatFamily.STANDARD,
            duration_seconds=10.0,
            fps_num=24,
        )


def test_clip_info_defaults_non_null_collections() -> None:
    clip = ClipInfo(
        clip_id="clip-1",
        clip_name="A001_C001.mov",
        source_path="/clips/A001_C001.mov",
        format_family=FormatFamily.STANDARD,
        frame_count=100,
    )

    assert clip.part_files == ()
    assert clip.metadata_raw == {}


def test_capture_point_requires_requested_position_data() -> None:
    with pytest.raises(ValueError, match="requested position data"):
        CapturePoint(
            label="Start",
            requested_ratio=0.0,
            actual_frame_index=0,
        )


def test_capture_point_allows_decode_failed_without_actual_position() -> None:
    point = CapturePoint(
        label="End",
        requested_ratio=1.0,
        requested_frame_index=99,
        status=CaptureStatus.DECODE_FAILED,
    )

    assert point.status is CaptureStatus.DECODE_FAILED
    assert point.actual_frame_index is None


def test_status_and_source_vocabularies_match_stage_contract() -> None:
    assert ClipStatus.DEPENDENCY_MISSING.value == "dependency_missing"
    assert {status.value for status in CaptureStatus} == {
        "success",
        "decode_failed",
        "metadata_incomplete",
        "skipped_duplicate",
    }
    assert TimecodeSource.ELAPSED_FALLBACK.value == "elapsed_fallback"


def test_probe_result_can_represent_dependency_missing() -> None:
    probe = ProbeResult(
        ok=False,
        adapter_name="r3d_adapter",
        format_family=FormatFamily.R3D,
        status=ClipStatus.DEPENDENCY_MISSING,
        errors=(
            AdapterError(
                code=AdapterErrorCode.DEPENDENCY_MISSING,
                message="RED SDK runtime not found",
            ),
        ),
    )

    assert probe.clip is None
    assert probe.status is ClipStatus.DEPENDENCY_MISSING
    assert probe.errors[0].code is AdapterErrorCode.DEPENDENCY_MISSING


def test_report_item_requires_canonical_capture_order() -> None:
    clip = ClipInfo(
        clip_id="clip-1",
        clip_name="A001_C001.mov",
        source_path="/clips/A001_C001.mov",
        format_family=FormatFamily.STANDARD,
        frame_count=10,
    )
    start = CapturePoint(
        label="Start",
        requested_ratio=0.0,
        requested_frame_index=0,
        actual_frame_index=0,
    )
    end = CapturePoint(
        label="End",
        requested_ratio=1.0,
        requested_frame_index=9,
        actual_frame_index=9,
    )

    with pytest.raises(ValueError, match="canonical"):
        ReportItem(clip=clip, captures=(end, start), status=ClipStatus.SUCCESS)


def test_capture_point_from_result_preserves_capture_fields() -> None:
    result = CaptureResult(
        label="Mid1",
        requested_ratio=0.5,
        requested_frame_index=5,
        actual_frame_index=5,
        actual_timecode="01:00:00:05",
        actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
        warnings=("native",),
    )

    point = CapturePoint.from_capture_result(result, image_path_exported="/exports/mid1.png")

    assert point.image_path_exported == "/exports/mid1.png"
    assert point.actual_timecode_source is TimecodeSource.NATIVE_ADAPTER
    assert point.warnings == ("native",)


def test_capture_result_rejects_clip_only_status_values() -> None:
    with pytest.raises(ValueError, match="partial_success"):
        CaptureResult(
            label="Start",
            requested_ratio=0.0,
            requested_frame_index=0,
            actual_frame_index=0,
            status="partial_success",
        )


def test_batch_summary_tracks_documented_normalized_counters() -> None:
    summary = BatchSummary(
        total_clips=5,
        success_count=2,
        partial_success_count=1,
        probe_failed_count=1,
        decode_failed_count=1,
        skipped_count=3,
        status=BatchStatus.PARTIAL_SUCCESS,
    )

    assert summary.status is BatchStatus.PARTIAL_SUCCESS
    assert summary.probe_failed_count == 1
    assert summary.decode_failed_count == 1
    assert summary.skipped_count == 3
    assert not hasattr(summary, "failed_count")


def test_batch_summary_rejects_negative_counters() -> None:
    with pytest.raises(ValueError, match="skipped_count"):
        BatchSummary(
            total_clips=1,
            success_count=1,
            partial_success_count=0,
            probe_failed_count=0,
            decode_failed_count=0,
            skipped_count=-1,
            status=BatchStatus.SUCCESS,
        )
