from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from threading import Event
from types import TracebackType

from frameproof.config.settings import AppSettings, OutputSettings
from frameproof.core.adapter_resolver import AdapterSelection, resolve_adapter
from frameproof.core.capture_planner import build_capture_plan
from frameproof.core.capture_service import run_captures
from frameproof.core.clip_grouper import group_clip_candidates
from frameproof.core.dependency_inspector import DependencyInspector
from frameproof.core.models import (
    AdapterError,
    AdapterErrorCode,
    BatchStatus,
    BatchSummary,
    CaptureResult,
    ClipInfo,
    ClipStatus,
    ReportItem,
)
from frameproof.core.probe_service import run_probe
from frameproof.core.progress_events import (
    BatchProgressCallback,
    BatchStageEvent,
    DependencyStatusEvent,
    ProgressRow,
    RowDiscoveredEvent,
    RowUpdatedEvent,
    warning_summary,
)
from frameproof.core.report_builder import BatchReport, build_batch_report, build_report_item, with_exported_image_paths
from frameproof.core.scanner import scan_inputs
from frameproof.output import export_stills, write_manifests
from frameproof.render import render_pdf


@dataclass(frozen=True)
class BatchRunOutcome:
    exit_code: int
    report: BatchReport
    pdf_path: Path | None = None
    csv_path: Path | None = None
    json_path: Path | None = None
    error_message: str | None = None
    fatal_error: AdapterError | None = None


class BatchCancelToken:
    def __init__(self) -> None:
        self._event = Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()


def run_batch(
    settings: AppSettings,
    *,
    progress_callback: BatchProgressCallback | None = None,
    cancel_token: BatchCancelToken | None = None,
) -> BatchRunOutcome:
    progress = progress_callback or (lambda event: None)
    cancellation = cancel_token or BatchCancelToken()

    try:
        _validate_output_targets(settings.output)
    except OSError as exc:
        return _fatal_outcome(
            _empty_report(status=BatchStatus.FAILED),
            code=AdapterErrorCode.OUTPUT_WRITE_FAILED,
            message=f"Output path validation failed: {exc}",
            detail={"stage": "validation"},
        )

    progress(BatchStageEvent(event_type="stage_started", stage="scan", message="Scanning selected inputs"))
    if cancellation.is_cancelled():
        return _cancelled_outcome(progress, build_batch_report(()), "Cancelled before scan started")

    scanned_paths = scan_inputs(
        settings.input.paths,
        recursive=settings.input.recursive,
        extensions=settings.input.extensions,
    )
    if not scanned_paths:
        report = _empty_report(status=BatchStatus.FAILED)
        return BatchRunOutcome(exit_code=2, report=report, error_message="No supported input files were found.")

    progress(
        BatchStageEvent(
            event_type="stage_completed",
            stage="scan",
            message=f"Found {len(scanned_paths)} supported input file(s)",
            total_clips=len(scanned_paths),
        )
    )
    progress(BatchStageEvent(event_type="stage_started", stage="dependencies", message="Checking dependencies"))
    dependencies = DependencyInspector(settings.adapters).all_dependencies()
    progress(DependencyStatusEvent(dependencies=dependencies))
    progress(BatchStageEvent(event_type="stage_completed", stage="dependencies", message="Dependency check complete"))

    candidates = group_clip_candidates(scanned_paths)
    selections = tuple(resolve_adapter(candidate, settings.adapters) for candidate in candidates)
    rows = {
        selection.candidate.candidate_id: _build_initial_row(selection)
        for selection in selections
    }
    row_indexes = {selection.candidate.candidate_id: index for index, selection in enumerate(selections)}
    for selection in selections:
        candidate_id = selection.candidate.candidate_id
        progress(RowDiscoveredEvent(row_index=row_indexes[candidate_id], row=rows[candidate_id]))

    report_items: list[ReportItem] = []
    processed_count = 0

    with _staging_root(settings.output.staging_dir) as staging_root:
        for selection in selections:
            if cancellation.is_cancelled():
                _emit_pdf_status(progress, row_indexes, rows, "skipped")
                return _cancelled_outcome(
                    progress,
                    build_batch_report(report_items),
                    "Cancelled before starting the next clip",
                )

            candidate_id = selection.candidate.candidate_id
            total = len(selections)
            progress(
                BatchStageEvent(
                    event_type="stage_started",
                    stage="probe",
                    message=f"Probing {selection.candidate.source_path.rsplit('/', 1)[-1]}",
                    processed_clips=processed_count,
                    total_clips=total,
                )
            )
            rows[candidate_id] = replace(rows[candidate_id], probe="running", warning="")
            progress(RowUpdatedEvent(row_index=row_indexes[candidate_id], row=rows[candidate_id]))

            probe_execution = run_probe(selection)
            capture_results: tuple[CaptureResult, ...] = ()
            capture_clip = _capture_ready_clip(probe_execution.result.clip, probe_execution.result.status)
            if capture_clip is not None and selection.adapter is not None:
                rows[candidate_id] = replace(rows[candidate_id], capture="running")
                progress(RowUpdatedEvent(row_index=row_indexes[candidate_id], row=rows[candidate_id]))
                capture_plan = build_capture_plan(capture_clip, settings.capture.middle_count)
                capture_results = run_captures(
                    selection.adapter,
                    selection.candidate,
                    capture_plan,
                    profile_name=settings.capture.profile,
                    staging_dir=staging_root / selection.candidate.candidate_id,
                )

            report_item = build_report_item(probe_execution.result, capture_results)
            report_items.append(report_item)
            processed_count += 1

            rows[candidate_id] = _row_from_report_item(rows[candidate_id], report_item)
            progress(
                RowUpdatedEvent(
                    row_index=row_indexes[candidate_id],
                    row=rows[candidate_id],
                    report_item=report_item,
                )
            )
            progress(
                BatchStageEvent(
                    event_type="stage_completed",
                    stage="clip",
                    message=f"Finished {report_item.clip.clip_name}",
                    processed_clips=processed_count,
                    total_clips=len(selections),
                )
            )

        batch_report = build_batch_report(report_items)
        if cancellation.is_cancelled():
            _emit_pdf_status(progress, row_indexes, rows, "skipped")
            return _cancelled_outcome(progress, batch_report, "Cancelled before output generation")

        if batch_report.items and all(item.status is ClipStatus.DEPENDENCY_MISSING for item in batch_report.items):
            _emit_pdf_status(progress, row_indexes, rows, "skipped")
            return BatchRunOutcome(exit_code=2, report=batch_report)

        output_stage = "prepare_output"
        try:
            _ensure_output_parent(settings.output)

            if settings.output.export_stills:
                assert settings.output.stills_dir is not None
                output_stage = "stills"
                progress(BatchStageEvent(event_type="stage_started", stage="stills", message="Exporting PNG stills"))
                batch_report = BatchReport(
                    items=tuple(
                        with_exported_image_paths(item, export_stills(item, settings.output.stills_dir))
                        for item in batch_report.items
                    ),
                    summary=batch_report.summary,
                )
                progress(BatchStageEvent(event_type="stage_completed", stage="stills", message="PNG still export complete"))

            if cancellation.is_cancelled():
                _emit_pdf_status(progress, row_indexes, rows, "skipped")
                return _cancelled_outcome(progress, batch_report, "Cancelled before PDF rendering")

            output_stage = "render"
            progress(BatchStageEvent(event_type="stage_started", stage="render", message="Rendering PDF"))
            render_pdf(settings.output.pdf_path, settings, batch_report.items, batch_report.summary)
            _emit_pdf_status(progress, row_indexes, rows, "included", report_items=batch_report.items)
            progress(BatchStageEvent(event_type="stage_completed", stage="render", message="PDF render complete"))

            if cancellation.is_cancelled():
                return _cancelled_outcome(progress, batch_report, "Cancelled before manifest writing", pdf_path=settings.output.pdf_path)

            output_stage = "manifests"
            progress(BatchStageEvent(event_type="stage_started", stage="manifests", message="Writing manifests"))
            csv_path, json_path = write_manifests(settings.output, batch_report.items, batch_report.summary)
            progress(BatchStageEvent(event_type="stage_completed", stage="manifests", message="Manifest write complete"))
        except Exception as exc:
            failure_report = _with_output_failure(batch_report)
            _cleanup_output_artifacts(settings.output)
            _emit_pdf_status(progress, row_indexes, rows, "failed", report_items=batch_report.items)
            return _fatal_outcome(
                failure_report,
                code=AdapterErrorCode.RENDERER_FAILED if output_stage == "render" else AdapterErrorCode.OUTPUT_WRITE_FAILED,
                message=f"{output_stage.replace('_', ' ')} failed: {exc}",
                detail={"stage": output_stage},
            )

    return BatchRunOutcome(
        exit_code=0,
        report=batch_report,
        pdf_path=settings.output.pdf_path,
        csv_path=csv_path,
        json_path=json_path,
    )


def _build_initial_row(selection: AdapterSelection) -> ProgressRow:
    return ProgressRow(
        candidate_id=selection.candidate.candidate_id,
        clip_name=Path(selection.candidate.source_path).name,
        format_family=selection.format_family,
    )


def _row_from_report_item(row: ProgressRow, report_item: ReportItem) -> ProgressRow:
    error_messages = tuple(error.message for error in report_item.errors)
    return replace(
        row,
        probe=_probe_cell_status(report_item.status),
        capture=_capture_cell_status(report_item.status),
        warning=warning_summary(report_item.warnings, error_messages),
        report_status=report_item.status,
    )


def _probe_cell_status(status: ClipStatus) -> str:
    if status in {ClipStatus.SUCCESS, ClipStatus.PARTIAL_SUCCESS, ClipStatus.METADATA_INCOMPLETE}:
        return "success"
    return "fail"


def _capture_cell_status(status: ClipStatus) -> str:
    if status is ClipStatus.SUCCESS:
        return "success"
    if status in {ClipStatus.PARTIAL_SUCCESS, ClipStatus.METADATA_INCOMPLETE}:
        return "partial"
    return "fail"


def _emit_pdf_status(
    progress: BatchProgressCallback,
    row_indexes: dict[str, int],
    rows: dict[str, ProgressRow],
    pdf_status: str,
    *,
    report_items: tuple[ReportItem, ...] | None = None,
) -> None:
    report_items_by_id = {item.clip.clip_id: item for item in report_items or ()}
    for candidate_id, row in rows.items():
        report_item = report_items_by_id.get(candidate_id)
        rows[candidate_id] = replace(row, pdf=pdf_status)
        progress(
            RowUpdatedEvent(
                row_index=row_indexes[candidate_id],
                row=rows[candidate_id],
                report_item=report_item,
            )
        )


def _cancelled_outcome(
    progress: BatchProgressCallback,
    report: BatchReport,
    message: str,
    *,
    pdf_path: Path | None = None,
) -> BatchRunOutcome:
    progress(BatchStageEvent(event_type="stage_cancelled", stage="cancelled", message=message))
    return BatchRunOutcome(
        exit_code=1,
        report=_with_status(report, BatchStatus.CANCELLED),
        pdf_path=pdf_path,
        error_message=message,
    )


def _empty_report(*, status: BatchStatus) -> BatchReport:
    return BatchReport(
        items=(),
        summary=BatchSummary(
            total_clips=0,
            success_count=0,
            partial_success_count=0,
            probe_failed_count=0,
            decode_failed_count=0,
            skipped_count=0,
            status=status,
        ),
    )


def _with_status(report: BatchReport, status: BatchStatus) -> BatchReport:
    summary = report.summary
    return BatchReport(
        items=report.items,
        summary=BatchSummary(
            total_clips=summary.total_clips,
            success_count=summary.success_count,
            partial_success_count=summary.partial_success_count,
            probe_failed_count=summary.probe_failed_count,
            decode_failed_count=summary.decode_failed_count,
            skipped_count=summary.skipped_count,
            status=status,
        ),
    )


def _capture_ready_clip(
    clip: ClipInfo | None,
    probe_status: ClipStatus,
) -> ClipInfo | None:
    if clip is None:
        return None
    if probe_status in {
        ClipStatus.SUCCESS,
        ClipStatus.METADATA_INCOMPLETE,
    }:
        return clip
    return None


class _staging_root:
    def __init__(self, configured_root: Path | None) -> None:
        self._configured_root = configured_root
        self._temporary_directory: tempfile.TemporaryDirectory[str] | None = None
        self.path: Path | None = None

    def __enter__(self) -> Path:
        if self._configured_root is not None:
            self._configured_root.mkdir(parents=True, exist_ok=True)
            self.path = self._configured_root
            return self._configured_root

        self._temporary_directory = tempfile.TemporaryDirectory(prefix="frameproof-")
        self.path = Path(self._temporary_directory.__enter__())
        return self.path

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._temporary_directory is not None:
            self._temporary_directory.__exit__(exc_type, exc, exc_tb)


def _with_output_failure(batch_report: BatchReport) -> BatchReport:
    return _with_status(batch_report, BatchStatus.FAILED)


def _fatal_outcome(
    report: BatchReport,
    *,
    code: AdapterErrorCode,
    message: str,
    detail: dict[str, object] | None = None,
) -> BatchRunOutcome:
    return BatchRunOutcome(
        exit_code=2,
        report=report,
        error_message=message,
        fatal_error=AdapterError(code=code, message=message, detail=detail or {}),
    )


def _validate_output_targets(output_settings: OutputSettings) -> None:
    file_targets = [
        ("pdf", output_settings.pdf_path),
        ("csv", _resolved_manifest_path(output_settings, suffix=".csv") if output_settings.write_csv else None),
        ("json", _resolved_manifest_path(output_settings, suffix=".json") if output_settings.write_json else None),
    ]
    directory_targets = [
        ("stills", output_settings.stills_dir if output_settings.export_stills else None),
        ("staging", output_settings.staging_dir),
    ]

    seen_targets: dict[Path, str] = {}
    for label, raw_path in (*file_targets, *directory_targets):
        if raw_path is None:
            continue
        normalized = raw_path.expanduser().resolve(strict=False)
        if normalized in seen_targets:
            raise OSError(f"{label} target duplicates the {seen_targets[normalized]} target: {raw_path}")
        seen_targets[normalized] = label

    for _, raw_path in file_targets:
        if raw_path is None:
            continue
        _assert_writable_file_target(raw_path)

    for _, raw_path in directory_targets:
        if raw_path is None:
            continue
        _assert_writable_directory_target(raw_path)


def _resolved_manifest_path(output_settings: OutputSettings, *, suffix: str) -> Path:
    if suffix == ".csv" and output_settings.csv_path is not None:
        return output_settings.csv_path
    if suffix == ".json" and output_settings.json_path is not None:
        return output_settings.json_path
    return output_settings.pdf_path.with_suffix(suffix)


def _assert_writable_file_target(path: Path) -> None:
    if path.exists() and path.is_dir():
        raise OSError(f"{path} is a directory, expected a writable file path")
    if path.exists() and not path.is_file():
        raise OSError(f"{path} is not a regular file")
    _assert_writable_directory_target(path.parent)
    if path.exists() and not os.access(path, os.W_OK):
        raise OSError(f"{path} is not writable")


def _assert_writable_directory_target(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise OSError(f"{path} is not a directory")
    path.mkdir(parents=True, exist_ok=True)
    if not os.access(path, os.W_OK | os.X_OK):
        raise OSError(f"{path} is not writable")
    try:
        with tempfile.NamedTemporaryFile(dir=path, prefix=".frameproof-write-check-", delete=True):
            pass
    except OSError as exc:
        raise OSError(f"{path} is not writable") from exc


def _cleanup_output_artifacts(output_settings: OutputSettings) -> None:
    artifact_paths = [output_settings.pdf_path]
    if output_settings.write_csv:
        artifact_paths.append(_resolved_manifest_path(output_settings, suffix=".csv"))
    if output_settings.write_json:
        artifact_paths.append(_resolved_manifest_path(output_settings, suffix=".json"))

    for artifact_path in artifact_paths:
        if artifact_path.exists() and artifact_path.is_file():
            artifact_path.unlink()


def _ensure_output_parent(output_settings: OutputSettings) -> None:
    output_settings.pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if output_settings.export_stills and output_settings.stills_dir is not None:
        output_settings.stills_dir.parent.mkdir(parents=True, exist_ok=True)
    if output_settings.csv_path is not None:
        output_settings.csv_path.parent.mkdir(parents=True, exist_ok=True)
    if output_settings.json_path is not None:
        output_settings.json_path.parent.mkdir(parents=True, exist_ok=True)
