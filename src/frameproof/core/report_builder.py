from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace

from .models import (
    BatchStatus,
    BatchSummary,
    CapturePoint,
    CaptureResult,
    CaptureStatus,
    ClipInfo,
    ClipStatus,
    ProbeResult,
    ReportItem,
)
from .timecode import calculate_timecode_display, resolve_timecode_display


@dataclass(frozen=True)
class BatchReport:
    items: tuple[ReportItem, ...]
    summary: BatchSummary


def build_report_item(
    probe_result: ProbeResult,
    capture_results: Iterable[CaptureResult] = (),
) -> ReportItem:
    clip = probe_result.clip
    if clip is None:
        clip = _placeholder_clip(probe_result)
        return ReportItem(
            clip=clip,
            captures=(),
            status=probe_result.status,
            adapter_name=probe_result.adapter_name,
            warnings=probe_result.warnings,
            errors=probe_result.errors,
        )

    clip = _with_calculated_end_timecode(clip)
    captures = tuple(_build_capture_point(clip, result) for result in capture_results)
    status = _resolve_clip_status(probe_result.status, captures)
    warnings = _merge_strings(
        probe_result.warnings,
        *(capture.warnings for capture in captures),
    )
    errors = tuple(probe_result.errors) + tuple(
        error
        for capture in captures
        for error in capture.errors
    )
    return ReportItem(
        clip=clip,
        captures=captures,
        status=status,
        adapter_name=probe_result.adapter_name,
        warnings=warnings,
        errors=errors,
    )


def build_batch_report(items: Iterable[ReportItem]) -> BatchReport:
    item_tuple = tuple(items)
    return BatchReport(items=item_tuple, summary=build_batch_summary(item_tuple))


def build_batch_summary(items: Iterable[ReportItem]) -> BatchSummary:
    item_tuple = tuple(items)
    counts = Counter(item.status for item in item_tuple)

    success_count = counts[ClipStatus.SUCCESS]
    partial_success_count = counts[ClipStatus.PARTIAL_SUCCESS] + counts[ClipStatus.METADATA_INCOMPLETE]
    probe_failed_count = counts[ClipStatus.PROBE_FAILED]
    decode_failed_count = counts[ClipStatus.DECODE_FAILED]
    skipped_count = counts[ClipStatus.UNSUPPORTED_FORMAT] + counts[ClipStatus.DEPENDENCY_MISSING]

    if not item_tuple:
        status = BatchStatus.FAILED
    elif probe_failed_count or decode_failed_count or skipped_count or partial_success_count:
        status = BatchStatus.PARTIAL_SUCCESS
    else:
        status = BatchStatus.SUCCESS

    return BatchSummary(
        total_clips=len(item_tuple),
        success_count=success_count,
        partial_success_count=partial_success_count,
        probe_failed_count=probe_failed_count,
        decode_failed_count=decode_failed_count,
        skipped_count=skipped_count,
        status=status,
    )


def with_exported_image_paths(
    item: ReportItem,
    exported_paths_by_label: Mapping[str, str | None],
) -> ReportItem:
    captures = tuple(
        replace(
            capture,
            image_path_exported=exported_paths_by_label.get(capture.label, capture.image_path_exported),
        )
        for capture in item.captures
    )
    return replace(item, captures=captures)


def _build_capture_point(clip: ClipInfo, result: CaptureResult) -> CapturePoint:
    timecode_display = resolve_timecode_display(
        actual_timecode=result.actual_timecode,
        actual_timecode_source=result.actual_timecode_source,
        start_timecode=clip.start_timecode,
        # The container only stores the first frame's timecode; showing it for
        # a later capture would mislabel that frame, so elapsed time wins there.
        container_timecode=clip.start_timecode if _is_first_frame(result) else None,
        actual_frame_index=result.actual_frame_index,
        actual_seconds=result.actual_seconds,
        fps_num=clip.fps_num,
        fps_den=clip.fps_den,
        tc_drop_frame=clip.tc_drop_frame,
    )
    warnings = _merge_strings(result.warnings, timecode_display.warnings)
    return CapturePoint.from_capture_result(
        CaptureResult(
            label=result.label,
            requested_ratio=result.requested_ratio,
            requested_frame_index=result.requested_frame_index,
            requested_seconds=result.requested_seconds,
            actual_frame_index=result.actual_frame_index,
            actual_seconds=result.actual_seconds,
            actual_timecode=None if timecode_display.value == "N/A" else timecode_display.value,
            actual_timecode_source=timecode_display.source,
            image_path_temp=result.image_path_temp,
            duplicate_of=result.duplicate_of,
            status=result.status,
            warnings=warnings,
            errors=result.errors,
        )
    )


def _is_first_frame(result: CaptureResult) -> bool:
    if result.actual_frame_index is not None:
        return result.actual_frame_index == 0
    return result.actual_seconds is None or result.actual_seconds == 0


def _with_calculated_end_timecode(clip: ClipInfo) -> ClipInfo:
    if clip.end_timecode is not None or clip.frame_count is None or clip.frame_count <= 0:
        return clip
    display = calculate_timecode_display(
        start_timecode=clip.start_timecode,
        frame_offset=clip.frame_count - 1,
        fps_num=clip.fps_num,
        fps_den=clip.fps_den,
        tc_drop_frame=clip.tc_drop_frame,
    )
    if display is None:
        return clip
    return replace(clip, end_timecode=display.value)


def _resolve_clip_status(
    probe_status: ClipStatus,
    captures: tuple[CapturePoint, ...],
) -> ClipStatus:
    if probe_status not in (ClipStatus.SUCCESS, ClipStatus.METADATA_INCOMPLETE):
        return probe_status
    if not captures:
        return probe_status

    has_decode_failed = any(capture.status is CaptureStatus.DECODE_FAILED for capture in captures)
    has_metadata_incomplete = probe_status is ClipStatus.METADATA_INCOMPLETE or any(
        capture.status is CaptureStatus.METADATA_INCOMPLETE for capture in captures
    )

    if has_decode_failed:
        succeeded = any(capture.status is not CaptureStatus.DECODE_FAILED for capture in captures)
        return ClipStatus.PARTIAL_SUCCESS if succeeded else ClipStatus.DECODE_FAILED
    if has_metadata_incomplete:
        return ClipStatus.METADATA_INCOMPLETE
    return ClipStatus.SUCCESS


def _placeholder_clip(probe_result: ProbeResult) -> ClipInfo:
    source_path = probe_result.metadata_raw.get("source_path")
    clip_name = probe_result.metadata_raw.get("clip_name")
    candidate_id = probe_result.metadata_raw.get("candidate_id")
    return ClipInfo(
        clip_id=str(candidate_id or source_path or clip_name or f"{probe_result.adapter_name}-unresolved"),
        clip_name=str(clip_name or source_path or "Unresolved Clip"),
        source_path=str(source_path or clip_name or "unknown"),
        format_family=probe_result.format_family,
        duration_seconds=0.0,
        metadata_raw=probe_result.metadata_raw,
    )


def _merge_strings(*values: Iterable[str]) -> tuple[str, ...]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in values:
        for value in group:
            if value not in seen:
                seen.add(value)
                merged.append(value)
    return tuple(merged)
