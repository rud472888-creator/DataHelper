from __future__ import annotations

from pathlib import Path

from frameproof.config.settings import AppSettings
from frameproof.core import batch_runner
from frameproof.core.adapter_resolver import AdapterSelection
from frameproof.core.models import (
    AdapterErrorCode,
    AdapterDependencyState,
    BatchStatus,
    CapturePlan,
    CaptureProfile,
    CaptureResult,
    CaptureStatus,
    ClipCandidate,
    ClipInfo,
    FormatFamily,
    ProbeResult,
)
from frameproof.core.progress_events import BatchStageEvent, RowDiscoveredEvent, RowUpdatedEvent


class _FakeAdapter:
    name = "ffmpeg"
    format_families = ("standard",)
    required_tools = ("ffmpeg", "ffprobe")

    def __init__(self, clip: ClipInfo) -> None:
        self._clip = clip

    def is_available(self) -> AdapterDependencyState:
        return AdapterDependencyState.AVAILABLE

    def dependency_details(self) -> dict[str, object]:
        return {}

    def probe(self, candidate: ClipCandidate) -> ProbeResult:
        return ProbeResult(
            ok=True,
            adapter_name="ffmpeg",
            format_family=FormatFamily.STANDARD,
            clip=self._clip,
        )

    def capture(
        self,
        candidate: ClipCandidate,
        plan: CapturePlan,
        profile: CaptureProfile,
        staging_dir: Path,
    ) -> tuple[CaptureResult, ...]:
        return tuple(
            CaptureResult(
                label=request.label,
                requested_ratio=request.requested_ratio,
                requested_frame_index=request.requested_frame_index,
                requested_seconds=request.requested_seconds,
                actual_frame_index=request.requested_frame_index,
                actual_seconds=request.requested_seconds,
                actual_timecode=f"01:00:00:{index:02d}",
                image_path_temp=str(staging_dir / f"{request.label.lower()}.png"),
                duplicate_of=request.duplicate_of,
                status=CaptureStatus.SUCCESS,
            )
            for index, request in enumerate(plan.requests)
        )


def test_run_batch_emits_truthful_progress_and_output_paths(tmp_path: Path, monkeypatch: object) -> None:
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"clip")
    settings = AppSettings.from_mapping(
        {
            "input": {"paths": [str(clip_path)]},
            "output": {"pdf_path": str(tmp_path / "report.pdf")},
        }
    )
    candidate = ClipCandidate(candidate_id="clip-1", source_path=str(clip_path), format_hint="mp4")
    clip = ClipInfo(
        clip_id="clip-1",
        clip_name=clip_path.name,
        source_path=str(clip_path),
        format_family=FormatFamily.STANDARD,
        duration_seconds=10.0,
        frame_count=240,
        fps_num=24,
        fps_den=1,
    )
    adapter = _FakeAdapter(clip)

    monkeypatch.setattr(batch_runner, "scan_inputs", lambda *args, **kwargs: (clip_path,))
    monkeypatch.setattr(batch_runner, "group_clip_candidates", lambda _paths: (candidate,))
    monkeypatch.setattr(
        batch_runner,
        "resolve_adapter",
        lambda current_candidate, _settings, **_kwargs: AdapterSelection(current_candidate, FormatFamily.STANDARD, "ffmpeg", adapter),
    )

    def fake_render_pdf(output_path: Path, _settings: AppSettings, _items: object, _summary: object) -> None:
        output_path.write_bytes(b"pdf")

    def fake_write_manifests(output_settings: object, _items: object, _summary: object) -> tuple[Path, Path]:
        assert isinstance(output_settings, object)
        csv_path = settings.output.pdf_path.with_suffix(".csv")
        json_path = settings.output.pdf_path.with_suffix(".json")
        csv_path.write_text("csv", encoding="utf-8")
        json_path.write_text("json", encoding="utf-8")
        return csv_path, json_path

    monkeypatch.setattr(batch_runner, "render_pdf", fake_render_pdf)
    monkeypatch.setattr(batch_runner, "write_manifests", fake_write_manifests)

    events: list[object] = []
    outcome = batch_runner.run_batch(settings, progress_callback=events.append)

    assert outcome.exit_code == 0
    assert outcome.pdf_path == settings.output.pdf_path
    assert outcome.csv_path == settings.output.pdf_path.with_suffix(".csv")
    assert outcome.json_path == settings.output.pdf_path.with_suffix(".json")
    discovered_rows = [event for event in events if isinstance(event, RowDiscoveredEvent)]
    assert discovered_rows
    assert discovered_rows[0].row.pdf == ""
    assert any(isinstance(event, BatchStageEvent) and event.stage == "render" for event in events)
    updated_rows = [event for event in events if isinstance(event, RowUpdatedEvent)]
    assert updated_rows
    assert updated_rows[-1].row.probe == "success"
    assert updated_rows[-1].row.capture == "success"
    assert updated_rows[-1].row.pdf == "included"


def test_run_batch_honors_cancellation_between_clips(tmp_path: Path, monkeypatch: object) -> None:
    first_path = tmp_path / "a.mp4"
    second_path = tmp_path / "b.mp4"
    first_path.write_bytes(b"a")
    second_path.write_bytes(b"b")
    settings = AppSettings.from_mapping(
        {
            "input": {"paths": [str(first_path), str(second_path)]},
            "output": {"pdf_path": str(tmp_path / "report.pdf")},
        }
    )
    candidates = (
        ClipCandidate(candidate_id="clip-1", source_path=str(first_path), format_hint="mp4"),
        ClipCandidate(candidate_id="clip-2", source_path=str(second_path), format_hint="mp4"),
    )

    def make_clip(candidate: ClipCandidate) -> ClipInfo:
        return ClipInfo(
            clip_id=candidate.candidate_id,
            clip_name=Path(candidate.source_path).name,
            source_path=candidate.source_path,
            format_family=FormatFamily.STANDARD,
            duration_seconds=12.0,
            frame_count=288,
            fps_num=24,
            fps_den=1,
        )

    monkeypatch.setattr(batch_runner, "scan_inputs", lambda *args, **kwargs: (first_path, second_path))
    monkeypatch.setattr(batch_runner, "group_clip_candidates", lambda _paths: candidates)
    monkeypatch.setattr(
        batch_runner,
        "resolve_adapter",
        lambda candidate, _settings, **_kwargs: AdapterSelection(candidate, FormatFamily.STANDARD, "ffmpeg", _FakeAdapter(make_clip(candidate))),
    )

    cancel_token = batch_runner.BatchCancelToken()
    events: list[object] = []

    def on_event(event: object) -> None:
        events.append(event)
        if isinstance(event, RowUpdatedEvent) and event.row.candidate_id == "clip-1" and event.row.capture == "success":
            cancel_token.cancel()

    outcome = batch_runner.run_batch(settings, progress_callback=on_event, cancel_token=cancel_token)

    assert outcome.exit_code == 1
    assert outcome.report.summary.status.value == "cancelled"
    assert any(isinstance(event, BatchStageEvent) and event.event_type == "stage_cancelled" for event in events)
    final_rows = [event.row for event in events if isinstance(event, RowUpdatedEvent)]
    assert any(row.candidate_id == "clip-2" and row.pdf == "skipped" for row in final_rows)


def test_run_batch_fails_before_scan_when_output_target_is_a_directory(tmp_path: Path, monkeypatch: object) -> None:
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"clip")
    blocked_pdf = tmp_path / "blocked.pdf"
    blocked_pdf.mkdir()
    settings = AppSettings.from_mapping(
        {
            "input": {"paths": [str(clip_path)]},
            "output": {"pdf_path": str(blocked_pdf)},
        }
    )

    monkeypatch.setattr(
        batch_runner,
        "scan_inputs",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("scan_inputs should not run")),
    )

    outcome = batch_runner.run_batch(settings)

    assert outcome.exit_code == 2
    assert outcome.report.summary.status is BatchStatus.FAILED
    assert outcome.fatal_error is not None
    assert outcome.fatal_error.code is AdapterErrorCode.OUTPUT_WRITE_FAILED
    assert "directory" in (outcome.error_message or "")


def test_run_batch_cleans_partial_output_artifacts_when_manifest_write_fails(tmp_path: Path, monkeypatch: object) -> None:
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"clip")
    settings = AppSettings.from_mapping(
        {
            "input": {"paths": [str(clip_path)]},
            "output": {"pdf_path": str(tmp_path / "report.pdf")},
        }
    )
    candidate = ClipCandidate(candidate_id="clip-1", source_path=str(clip_path), format_hint="mp4")
    clip = ClipInfo(
        clip_id="clip-1",
        clip_name=clip_path.name,
        source_path=str(clip_path),
        format_family=FormatFamily.STANDARD,
        duration_seconds=10.0,
        frame_count=240,
        fps_num=24,
        fps_den=1,
    )
    adapter = _FakeAdapter(clip)

    monkeypatch.setattr(batch_runner, "scan_inputs", lambda *args, **kwargs: (clip_path,))
    monkeypatch.setattr(batch_runner, "group_clip_candidates", lambda _paths: (candidate,))
    monkeypatch.setattr(
        batch_runner,
        "resolve_adapter",
        lambda current_candidate, _settings, **_kwargs: AdapterSelection(current_candidate, FormatFamily.STANDARD, "ffmpeg", adapter),
    )

    def fake_render_pdf(output_path: Path, _settings: AppSettings, _items: object, _summary: object) -> None:
        output_path.write_bytes(b"pdf")

    def fake_write_manifests(output_settings: object, _items: object, _summary: object) -> tuple[Path, Path]:
        del output_settings, _items, _summary
        csv_path = settings.output.pdf_path.with_suffix(".csv")
        csv_path.write_text("csv", encoding="utf-8")
        raise OSError("disk full")

    monkeypatch.setattr(batch_runner, "render_pdf", fake_render_pdf)
    monkeypatch.setattr(batch_runner, "write_manifests", fake_write_manifests)

    outcome = batch_runner.run_batch(settings)

    assert outcome.exit_code == 2
    assert outcome.pdf_path is None
    assert outcome.csv_path is None
    assert outcome.json_path is None
    assert outcome.fatal_error is not None
    assert outcome.fatal_error.code is AdapterErrorCode.OUTPUT_WRITE_FAILED
    assert not settings.output.pdf_path.exists()
    assert not settings.output.pdf_path.with_suffix(".csv").exists()


def test_run_batch_uses_app_owned_staging_and_leaves_source_bytes_unchanged(
    tmp_path: Path,
    monkeypatch: object,
) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    clip_path = source_dir / "clip.mp4"
    original_bytes = b"clip-bytes"
    clip_path.write_bytes(original_bytes)
    settings = AppSettings.from_mapping(
        {
            "input": {"paths": [str(clip_path)]},
            "output": {"pdf_path": str(tmp_path / "report.pdf")},
        }
    )
    candidate = ClipCandidate(candidate_id="clip-1", source_path=str(clip_path), format_hint="mp4")
    clip = ClipInfo(
        clip_id="clip-1",
        clip_name=clip_path.name,
        source_path=str(clip_path),
        format_family=FormatFamily.STANDARD,
        duration_seconds=10.0,
        frame_count=240,
        fps_num=24,
        fps_den=1,
    )
    adapter = _FakeAdapter(clip)
    seen_staging_dirs: list[Path] = []

    monkeypatch.setattr(batch_runner, "scan_inputs", lambda *args, **kwargs: (clip_path,))
    monkeypatch.setattr(batch_runner, "group_clip_candidates", lambda _paths: (candidate,))
    monkeypatch.setattr(
        batch_runner,
        "resolve_adapter",
        lambda current_candidate, _settings, **_kwargs: AdapterSelection(current_candidate, FormatFamily.STANDARD, "ffmpeg", adapter),
    )

    def fake_run_captures(
        _adapter: object,
        _candidate: ClipCandidate,
        plan: CapturePlan,
        *,
        profile_name: str,
        staging_dir: Path,
    ) -> tuple[CaptureResult, ...]:
        del _adapter, _candidate, profile_name
        seen_staging_dirs.append(staging_dir)
        return tuple(
            CaptureResult(
                label=request.label,
                requested_ratio=request.requested_ratio,
                requested_frame_index=request.requested_frame_index,
                requested_seconds=request.requested_seconds,
                actual_frame_index=request.requested_frame_index,
                actual_seconds=request.requested_seconds,
                actual_timecode=f"01:00:00:{index:02d}",
                image_path_temp=str(staging_dir / f"{request.label.lower()}.png"),
                duplicate_of=request.duplicate_of,
                status=CaptureStatus.SUCCESS,
            )
            for index, request in enumerate(plan.requests)
        )

    monkeypatch.setattr(batch_runner, "run_captures", fake_run_captures)
    monkeypatch.setattr(batch_runner, "render_pdf", lambda output_path, *_args: output_path.write_bytes(b"pdf"))
    monkeypatch.setattr(
        batch_runner,
        "write_manifests",
        lambda _output_settings, _items, _summary: (
            settings.output.pdf_path.with_suffix(".csv"),
            settings.output.pdf_path.with_suffix(".json"),
        ),
    )

    outcome = batch_runner.run_batch(settings)

    assert outcome.exit_code == 0
    assert clip_path.read_bytes() == original_bytes
    assert seen_staging_dirs
    assert source_dir.resolve() not in seen_staging_dirs[0].resolve().parents
