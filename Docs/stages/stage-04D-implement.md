# Stage 04D Implement

- lane: dev
- stage: stage-04D
- subphase: implement
- status: complete
- scope_boundary: pyside6-gui-over-shared-pipeline
- next_recommended_prompt: `[Stage 4D-QA]`

## Delivered Scope

- Extracted the shared batch execution path into `frameproof.core.batch_runner` so the GUI reuses the existing CLI/core pipeline instead of creating a second media-processing path.
- Added truthful progress-stage and row events for scan, dependency check, probe, capture, render, manifest write, cancellation, and completion.
- Added a new PySide6 GUI package with:
- source file and source folder selectors
- output PDF selector
- project-name field
- middle-frame count selector
- layout selector
- still-export toggle
- CSV/JSON manifest toggles
- failed-files-section toggle
- progress table
- dependency dialog
- start and cancel controls
- Added GUI settings persistence for form defaults and adapter paths through a `QSettings` INI store.
- Added a dedicated GUI entrypoint via `python -m frameproof.gui` and `frameproof-gui`.
- Added automated shared-runner tests plus GUI persistence/controller tests, along with a manual GUI verification checklist for supported Qt environments.

## Changed Files And Reasons

- `pyproject.toml` adds the GUI dependency declaration and script entrypoint.
- `src/frameproof/cli.py` now reuses the shared batch runner.
- `src/frameproof/core/batch_runner.py` owns shared orchestration, cancellation, and progress emission.
- `src/frameproof/core/progress_events.py` defines immutable event payloads for GUI progress state.
- `src/frameproof/gui/__main__.py` provides GUI CLI help plus launch/smoke entrypoints.
- `src/frameproof/gui/app.py` bootstraps the Qt application and app styling.
- `src/frameproof/gui/batch_controller.py` runs the shared pipeline on a worker thread and forwards events into Qt signals.
- `src/frameproof/gui/dependency_dialog.py` exposes dependency status and adapter path editing.
- `src/frameproof/gui/main_window.py` implements the Stage 4D operator surface and progress table.
- `src/frameproof/gui/settings_store.py` persists GUI defaults and adapter paths.
- `src/frameproof/gui/view_state.py` holds GUI-facing row/banner state helpers.
- `tests/unit/core/test_batch_runner.py` locks truthful progress and cooperative cancel behavior.
- `tests/unit/gui/` adds GUI persistence/controller coverage and runtime-compatibility collection guards.
- `tests/manual/gui_smoke_checklist.md` records manual verification for supported Qt machines.

## State Ownership

| Concern | Owning layer |
|---|---|
| validated batch runtime settings | `frameproof.config.settings.AppSettings` |
| shared batch execution | `frameproof.core.batch_runner` |
| progress event truth | `frameproof.core.progress_events` |
| GUI form + table presentation state | `frameproof.gui.main_window` + `frameproof.gui.view_state` |
| persisted operator defaults | `frameproof.gui.settings_store` |
| dependency truth | `frameproof.core.dependency_inspector.DependencyInspector` |
| cancel intent | `frameproof.core.batch_runner.BatchCancelToken` |
| final clip/report truth | `ReportItem`, `BatchReport`, `BatchSummary` |

## Validation Results

- `python -m pytest` -> PASS (`77 passed, 2 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `python -m frameproof --help` -> PASS
- `python -m frameproof.gui --help` -> PASS
- GUI smoke launch -> BLOCKED on this machine because the installed Qt runtime aborts with `Incompatible processor ... neon`

## Known Gaps

- Automated GUI smoke remains machine-dependent because the local Qt runtime is not executable here.
- FFmpeg-backed integration remains skipped on this machine because `ffmpeg` and `ffprobe` are unavailable.
- Fresh Stage 4D QA is still required.

## Manual Verification

- Use `tests/manual/gui_smoke_checklist.md` on a machine with a working Qt runtime.
- Confirm settings persist across relaunch.
- Confirm dependency edits persist and refresh correctly.
- Confirm the shared pipeline starts from the GUI and produces the same PDF/manifest artifacts as the CLI.
- Confirm cancellation prevents new clip work from starting after the current clip completes.
