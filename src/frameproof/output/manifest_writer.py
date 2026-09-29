from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from frameproof.config.settings import OutputSettings
from frameproof.core.models import AdapterError, CapturePoint
from frameproof.core.models import BatchSummary, ReportItem
from frameproof.output.atomic import atomic_output_path


def build_manifest_rows(items: tuple[ReportItem, ...]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        if item.captures:
            for capture in item.captures:
                warnings = _merge_messages(item.warnings, capture.warnings)
                errors = _merge_errors(item.errors, capture.errors)
                rows.append(
                    {
                        "clip_id": item.clip.clip_id,
                        "clip_name": item.clip.clip_name,
                        "logical_clip_name": item.clip.logical_clip_name,
                        "source_path": item.clip.source_path,
                        "format_family": item.clip.format_family.value,
                        "adapter_name": item.adapter_name,
                        "capture_label": capture.label,
                        "requested_ratio": capture.requested_ratio,
                        "requested_frame_index": capture.requested_frame_index,
                        "requested_seconds": capture.requested_seconds,
                        "actual_frame_index": capture.actual_frame_index,
                        "actual_seconds": capture.actual_seconds,
                        "actual_timecode": capture.actual_timecode,
                        "actual_timecode_source": (
                            capture.actual_timecode_source.value if capture.actual_timecode_source is not None else None
                        ),
                        "image_path": capture.image_path_exported,
                        "status": capture.status.value,
                        "warnings": " | ".join(warnings),
                        "errors": " | ".join(error.message for error in errors),
                    }
                )
            continue

        rows.append(
            {
                "clip_id": item.clip.clip_id,
                "clip_name": item.clip.clip_name,
                "logical_clip_name": item.clip.logical_clip_name,
                "source_path": item.clip.source_path,
                "format_family": item.clip.format_family.value,
                "adapter_name": item.adapter_name,
                "capture_label": "",
                "requested_ratio": None,
                "requested_frame_index": None,
                "requested_seconds": None,
                "actual_frame_index": None,
                "actual_seconds": None,
                "actual_timecode": None,
                "actual_timecode_source": None,
                "image_path": None,
                "status": item.status.value,
                "warnings": " | ".join(_merge_messages(item.warnings)),
                "errors": " | ".join(error.message for error in _merge_errors(item.errors)),
            }
        )
    return rows


def write_manifests(
    output_settings: OutputSettings,
    items: tuple[ReportItem, ...],
    summary: BatchSummary,
) -> tuple[Path | None, Path | None]:
    rows = build_manifest_rows(items)
    csv_path = _resolve_manifest_path(output_settings.pdf_path, output_settings.csv_path, ".csv")
    json_path = _resolve_manifest_path(output_settings.pdf_path, output_settings.json_path, ".json")

    if output_settings.write_csv:
        assert csv_path is not None
        with atomic_output_path(csv_path) as temp_path, temp_path.open("w", encoding="utf-8", newline="") as handle:
            if rows:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    if output_settings.write_json:
        assert json_path is not None
        payload = {
            "summary": {
                "total_clips": summary.total_clips,
                "success_count": summary.success_count,
                "partial_success_count": summary.partial_success_count,
                "probe_failed_count": summary.probe_failed_count,
                "decode_failed_count": summary.decode_failed_count,
                "skipped_count": summary.skipped_count,
                "status": summary.status.value,
            },
            "rows": rows,
            "clips": [_serialize_report_item(item) for item in items],
        }
        with atomic_output_path(json_path) as temp_path:
            temp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    return csv_path if output_settings.write_csv else None, json_path if output_settings.write_json else None


def _resolve_manifest_path(pdf_path: Path, configured_path: Path | None, suffix: str) -> Path | None:
    if configured_path is not None:
        return configured_path
    return pdf_path.with_suffix(suffix)


def _serialize_report_item(item: ReportItem) -> dict[str, Any]:
    return {
        "clip": {
            "clip_id": item.clip.clip_id,
            "clip_name": item.clip.clip_name,
            "logical_clip_name": item.clip.logical_clip_name,
            "source_path": item.clip.source_path,
            "format_family": item.clip.format_family.value,
            "container": item.clip.container,
            "codec": item.clip.codec,
            "file_size_bytes": item.clip.file_size_bytes,
            "duration_seconds": item.clip.duration_seconds,
            "frame_count": item.clip.frame_count,
            "fps_num": item.clip.fps_num,
            "fps_den": item.clip.fps_den,
            "width": item.clip.width,
            "height": item.clip.height,
            "start_timecode": item.clip.start_timecode,
            "end_timecode": item.clip.end_timecode,
        },
        "adapter_name": item.adapter_name,
        "status": item.status.value,
        "warnings": list(item.warnings),
        "errors": [error.message for error in item.errors],
        "captures": [
            _serialize_capture(capture)
            for capture in item.captures
        ],
    }


def _serialize_capture(capture: CapturePoint) -> dict[str, Any]:
    return {
        "label": capture.label,
        "requested_ratio": capture.requested_ratio,
        "requested_frame_index": capture.requested_frame_index,
        "requested_seconds": capture.requested_seconds,
        "actual_frame_index": capture.actual_frame_index,
        "actual_seconds": capture.actual_seconds,
        "actual_timecode": capture.actual_timecode,
        "actual_timecode_source": (
            capture.actual_timecode_source.value if capture.actual_timecode_source is not None else None
        ),
        "image_path": capture.image_path_exported,
        "duplicate_of": capture.duplicate_of,
        "status": capture.status.value,
        "warnings": list(capture.warnings),
        "errors": [error.message for error in capture.errors],
    }


def _merge_messages(*message_groups: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in message_groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                merged.append(value)
    return tuple(merged)


def _merge_errors(*error_groups: tuple[AdapterError, ...]) -> tuple[AdapterError, ...]:
    merged: list[AdapterError] = []
    seen: set[tuple[str, str]] = set()
    for group in error_groups:
        for error in group:
            key = (error.code.value, error.message)
            if key not in seen:
                seen.add(key)
                merged.append(error)
    return tuple(merged)
