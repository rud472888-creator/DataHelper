from __future__ import annotations

from frameproof.config.settings import AppSettings
from frameproof.core.batch_runner import BatchCancelToken, BatchRunOutcome, run_batch
from frameproof.core.progress_events import BatchProgressEvent
from frameproof.gui.qt import QObject, QThread, Signal


class _BatchWorker(QObject):
    progress_event = Signal(object)
    batch_finished = Signal(object)
    batch_failed = Signal(str)

    def __init__(self, settings: AppSettings, cancel_token: BatchCancelToken) -> None:
        super().__init__()
        self._settings = settings
        self._cancel_token = cancel_token

    def run(self) -> None:
        try:
            outcome = run_batch(
                self._settings,
                progress_callback=self._emit_progress,
                cancel_token=self._cancel_token,
            )
        except Exception as exc:
            self.batch_failed.emit(str(exc))
            return
        self.batch_finished.emit(outcome)

    def _emit_progress(self, event: BatchProgressEvent) -> None:
        self.progress_event.emit(event)


class BatchController(QObject):
    progress_event = Signal(object)
    batch_finished = Signal(object)
    batch_failed = Signal(str)
    running_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None
        self._worker: _BatchWorker | None = None
        self._cancel_token: BatchCancelToken | None = None
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def start_batch(self, settings: AppSettings) -> None:
        if self._is_running:
            raise RuntimeError("A batch is already running")

        self._cancel_token = BatchCancelToken()
        self._thread = QThread()
        self._worker = _BatchWorker(settings, self._cancel_token)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress_event.connect(self.progress_event.emit)
        self._worker.batch_finished.connect(self._handle_finished)
        self._worker.batch_failed.connect(self._handle_failed)
        self._worker.batch_finished.connect(self._thread.quit)
        self._worker.batch_failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)
        self._set_running(True)
        self._thread.start()

    def cancel(self) -> None:
        if self._cancel_token is not None:
            self._cancel_token.cancel()

    def _handle_finished(self, outcome: BatchRunOutcome) -> None:
        self.batch_finished.emit(outcome)

    def _handle_failed(self, message: str) -> None:
        self.batch_failed.emit(message)

    def _cleanup_thread(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
        if self._thread is not None:
            self._thread.deleteLater()
        self._worker = None
        self._thread = None
        self._cancel_token = None
        self._set_running(False)

    def _set_running(self, value: bool) -> None:
        if self._is_running == value:
            return
        self._is_running = value
        self.running_changed.emit(value)
