from __future__ import annotations

from pathlib import Path
import time

from frameproof.config.settings import AppSettings
from frameproof.core.batch_runner import BatchRunOutcome
from frameproof.core.progress_events import BatchStageEvent
from frameproof.core.report_builder import BatchReport
from frameproof.core.models import BatchStatus, BatchSummary
from frameproof.gui import batch_controller
from frameproof.gui.batch_controller import BatchController


def wait_until(app: object, predicate: object, timeout_ms: int = 3000) -> None:
    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline:
        assert hasattr(app, "processEvents")
        app.processEvents()
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("Timed out waiting for Qt condition")


def test_batch_controller_forwards_progress_and_completion(qapp: object, monkeypatch: object) -> None:
    settings = AppSettings.from_mapping(
        {
            "input": {"paths": ["/tmp/input.mp4"]},
            "output": {"pdf_path": "/tmp/report.pdf"},
        }
    )
    events: list[object] = []
    outcomes: list[BatchRunOutcome] = []
    failures: list[str] = []

    def fake_run_batch(
        _settings: AppSettings,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> BatchRunOutcome:
        assert progress_callback is not None
        progress_callback(BatchStageEvent(event_type="stage_started", stage="scan", message="Scanning"))
        return BatchRunOutcome(
            exit_code=0,
            report=BatchReport(
                items=(),
                summary=BatchSummary(
                    total_clips=0,
                    success_count=0,
                    partial_success_count=0,
                    probe_failed_count=0,
                    decode_failed_count=0,
                    skipped_count=0,
                    status=BatchStatus.SUCCESS,
                ),
            ),
            pdf_path=Path("/tmp/report.pdf"),
        )

    monkeypatch.setattr(batch_controller, "run_batch", fake_run_batch)

    controller = BatchController()
    controller.progress_event.connect(events.append)
    controller.batch_finished.connect(outcomes.append)
    controller.batch_failed.connect(failures.append)
    controller.start_batch(settings)

    wait_until(qapp, lambda: bool(outcomes) or bool(failures))

    assert not failures
    assert outcomes[0].pdf_path == Path("/tmp/report.pdf")
    assert any(isinstance(event, BatchStageEvent) and event.stage == "scan" for event in events)
