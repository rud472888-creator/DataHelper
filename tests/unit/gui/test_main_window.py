from __future__ import annotations

from pathlib import Path

from frameproof.core.batch_runner import BatchRunOutcome
from frameproof.core.models import BatchStatus, BatchSummary, FormatFamily
from frameproof.core.progress_events import ProgressRow, RowDiscoveredEvent, RowUpdatedEvent
from frameproof.core.report_builder import BatchReport
from frameproof.gui.app import create_application
from frameproof.gui.main_window import MainWindow
from frameproof.gui.qt import QMessageBox, QObject, Signal
from frameproof.gui.settings_store import GuiStoredSettings, SettingsStore


class _FakeController(QObject):
    progress_event = Signal(object)
    batch_finished = Signal(object)
    batch_failed = Signal(str)
    running_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.started_settings: list[object] = []
        self.cancelled = False

    def start_batch(self, settings: object) -> None:
        self.started_settings.append(settings)
        self.running_changed.emit(True)

    def cancel(self) -> None:
        self.cancelled = True


def test_main_window_loads_saved_state_and_updates_progress_table(qapp: object, tmp_path: Path) -> None:
    store = SettingsStore(tmp_path / "gui.ini")
    store.save(
        GuiStoredSettings(
            source_paths=(str(tmp_path / "source.mov"),),
            output_pdf_path=str(tmp_path / "report.pdf"),
            project_name="Saved Project",
            middle_count=2,
            layout="detail",
            export_stills=True,
        )
    )
    controller = _FakeController()
    window = MainWindow(store, controller)

    assert window._sources_list.count() == 1
    assert window._project_name_edit.text() == "Saved Project"
    assert window._middle_count_spin.value() == 2
    assert window._export_stills_checkbox.isChecked() is True

    window._start_button.click()

    assert controller.started_settings
    loaded = store.load()
    assert loaded.project_name == "Saved Project"

    row = ProgressRow(candidate_id="clip-1", clip_name="A001.mov", format_family=FormatFamily.STANDARD)
    controller.progress_event.emit(RowDiscoveredEvent(row_index=0, row=row))
    controller.progress_event.emit(
        RowUpdatedEvent(row_index=0, row=ProgressRow(candidate_id="clip-1", clip_name="A001.mov", format_family=FormatFamily.STANDARD, probe="success", capture="partial", pdf="included", warning="fallback timecode"))
    )

    assert window._progress_table.item(0, 0).text() == "A001.mov"
    assert window._progress_table.item(0, 2).text() == "success"
    assert window._progress_table.item(0, 3).text() == "partial"
    assert window._progress_table.item(0, 4).text() == "included"
    assert "fallback timecode" in window._progress_table.item(0, 5).text()

    controller.batch_finished.emit(
        BatchRunOutcome(
            exit_code=0,
            report=BatchReport(
                items=(),
                summary=BatchSummary(
                    total_clips=1,
                    success_count=1,
                    partial_success_count=0,
                    probe_failed_count=0,
                    decode_failed_count=0,
                    skipped_count=0,
                    status=BatchStatus.SUCCESS,
                ),
            ),
            pdf_path=Path(tmp_path / "report.pdf"),
        )
    )

    assert "Batch complete." in window._banner_label.text()
    assert "Layout:" in window._overview_status_label.text()
    assert "inputs and output are set" in window._run_readiness_label.text()


def test_main_window_matches_stage5_desktop_geometry_target(qapp: object, tmp_path: Path) -> None:
    create_application()
    store = SettingsStore(tmp_path / "gui.ini")
    store.save(
        GuiStoredSettings(
            source_paths=("/show/day01", "/show/day02/B010_R001.braw"),
            output_pdf_path=str(tmp_path / "report.pdf"),
            project_name="Stage 5 Artifact Run",
            middle_count=2,
            layout="contact_sheet",
            export_stills=True,
        )
    )
    window = MainWindow(store, _FakeController())

    assert window.minimumSizeHint().width() <= 1024
    assert window.minimumSizeHint().height() <= 720

    window.resize(1280, 860)
    window.show()
    assert hasattr(qapp, "processEvents")
    qapp.processEvents()

    assert window.width() == 1280
    assert window.height() == 860
    assert window._dependency_button.isVisible() is True
    assert window._start_button.isVisible() is True
    assert window._cancel_button.isVisible() is True
    assert window._progress_table.isVisible() is True


def test_main_window_surfaces_output_caution_and_validation_errors(
    qapp: object, tmp_path: Path, monkeypatch: object
) -> None:
    store = SettingsStore(tmp_path / "gui.ini")
    store.save(
        GuiStoredSettings(
            source_paths=(str(tmp_path / "footage"),),
            output_pdf_path=str(tmp_path / "footage" / "exports" / "report.pdf"),
        )
    )
    window = MainWindow(store, _FakeController())

    assert "inside a selected source tree" in window._output_note_label.text()
    assert "Readiness: inputs and output are set." in window._run_readiness_label.text()

    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda *args, **kwargs: QMessageBox.StandardButton.Ok))
    window._output_pdf_edit.setText("")
    window._start_button.click()

    assert window._banner_label.text() == "Cannot start batch."
    assert "Select an output PDF path." in window._run_summary_label.text()


def test_main_window_partial_finish_banner_mentions_partial_visibility(qapp: object, tmp_path: Path) -> None:
    store = SettingsStore(tmp_path / "gui.ini")
    store.save(
        GuiStoredSettings(
            source_paths=(str(tmp_path / "source.mov"),),
            output_pdf_path=str(tmp_path / "report.pdf"),
        )
    )
    window = MainWindow(store, _FakeController())

    window._handle_batch_finished(
        BatchRunOutcome(
            exit_code=0,
            report=BatchReport(
                items=(),
                summary=BatchSummary(
                    total_clips=3,
                    success_count=1,
                    partial_success_count=1,
                    probe_failed_count=1,
                    decode_failed_count=0,
                    skipped_count=0,
                    status=BatchStatus.PARTIAL_SUCCESS,
                ),
            ),
            pdf_path=Path(tmp_path / "report.pdf"),
        )
    )

    assert window._banner_label.text() == "Batch complete."
    assert "partial or failed clips are still visible below" in window._run_summary_label.text()
