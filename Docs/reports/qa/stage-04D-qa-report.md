# Stage 04D QA Report

- gate: passed
- verdict: PASS
- stage: stage-04D
- lane: qa
- next_recommended_prompt: `[Stage 5-Plan]`
- stage_5_status: unblocked-by-qa

## Scope

Independent QA review of Stage 4D GUI delivery against:

- `Docs/stages/stage-04D-plan.md`
- `Docs/stages/stage-04D-implement.md`
- `Docs/reports/dev/stage-04D-handoff.md`
- `Docs/ui-spec.md`
- `src/frameproof/`
- `tests/`

This was a QA-only gate. No product code was modified. Only QA documents were updated.

## Checked Files

- `AGENTS.md`
- `Docs/qa.md`
- `Docs/stages/stage-04D-plan.md`
- `Docs/stages/stage-04D-implement.md`
- `Docs/reports/dev/stage-04D-handoff.md`
- `Docs/ui-spec.md`
- `src/frameproof/cli.py`
- `src/frameproof/core/batch_runner.py`
- `src/frameproof/gui/__main__.py`
- `src/frameproof/gui/app.py`
- `src/frameproof/gui/batch_controller.py`
- `src/frameproof/gui/dependency_dialog.py`
- `src/frameproof/gui/main_window.py`
- `src/frameproof/gui/settings_store.py`
- `src/frameproof/gui/status_text.py`
- `src/frameproof/gui/view_state.py`
- `tests/manual/gui_smoke_checklist.md`
- `tests/unit/core/test_batch_runner.py`
- `tests/unit/gui/test_batch_controller.py`
- `tests/unit/gui/test_main_window.py`
- `tests/unit/gui/test_settings_store.py`
- `tests/unit/test_gui_status_text.py`

## Command Results

- `python -m pytest` -> PASS

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-8.3.2, pluggy-1.6.0
rootdir: /Users/server_jay/Desktop/DataHelper
configfile: pyproject.toml
testpaths: tests
collected 84 items

tests/integration/test_cli_standard_pipeline.py ss
tests/integration/test_dependency_missing.py .
tests/integration/test_raw_dependency_missing.py .
tests/test_cli.py ......
tests/test_package.py ..
tests/unit/adapters/test_arriraw_art_adapter_client.py ..
tests/unit/adapters/test_base.py ...
tests/unit/adapters/test_braw_adapter_client.py ..
tests/unit/adapters/test_ffmpeg_adapter.py ....
tests/unit/adapters/test_r3d_adapter_client.py ..
tests/unit/config/test_settings.py .....
tests/unit/core/test_batch_runner.py ..
tests/unit/core/test_capture_planner.py ......
tests/unit/core/test_clip_grouper.py ...
tests/unit/core/test_dependency_inspector.py ....
tests/unit/core/test_models.py ............
tests/unit/core/test_report_builder.py ....
tests/unit/core/test_scanner.py ..
tests/unit/core/test_timecode.py ......
tests/unit/gui/test_batch_controller.py .
tests/unit/gui/test_main_window.py .
tests/unit/gui/test_settings_store.py .
tests/unit/output/test_manifest_writer.py ...
tests/unit/output/test_still_exporter.py ....
tests/unit/render/test_pdf_renderer.py ...
tests/unit/test_gui_status_text.py ..

======================== 82 passed, 2 skipped in 3.24s =========================
```

- `ruff check .` -> PASS

```text
All checks passed!
```

- `mypy src` -> PASS

```text
Success: no issues found in 41 source files
```

- `python -m frameproof.gui --help` -> PASS

```text
usage: python -m frameproof.gui [-h] [--settings-file PATH] [--smoke-test]

Launch the Frame Proof PySide6 GUI.

options:
  -h, --help            show this help message and exit
  --settings-file PATH  Override the GUI settings INI file location.
  --smoke-test          Create and show the GUI briefly, then exit without
                        starting a batch.
```

- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS

```text
qt.qpa.fonts: Populating font family aliases took 84 ms. Replace uses of missing font family "IBM Plex Sans" with one that exists to avoid this cost.
This plugin does not support propagateSizeHints()
```

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/unit/gui -vv` -> PASS

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-8.3.2, pluggy-1.6.0 -- /Users/server_jay/Desktop/DataHelper/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/server_jay/Desktop/DataHelper
configfile: pyproject.toml
collecting ... collected 3 items

tests/unit/gui/test_batch_controller.py::test_batch_controller_forwards_progress_and_completion PASSED
tests/unit/gui/test_main_window.py::test_main_window_loads_saved_state_and_updates_progress_table PASSED
tests/unit/gui/test_settings_store.py::test_settings_store_round_trips_gui_defaults PASSED

============================== 3 passed in 0.42s ===============================
```

- `QT_QPA_PLATFORM=offscreen python -m pytest tests/unit/test_gui_status_text.py -vv` -> PASS

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-8.3.2, pluggy-1.6.0 -- /Users/server_jay/Desktop/DataHelper/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/server_jay/Desktop/DataHelper
configfile: pyproject.toml
collecting ... collected 2 items

tests/unit/test_gui_status_text.py::test_dependency_state_label_matches_stage_4d_ui_spec PASSED
tests/unit/test_gui_status_text.py::test_dependency_status_summary_uses_operator_facing_labels PASSED

============================== 2 passed in 0.02s ===============================
```

- Offscreen widget inspection script -> PASS

```text
window_title: Frame Proof
source_count: 1
include_subfolders_default: True
layout_label: Detailed File Report (Layout A)
middle_count: 2
export_stills: True
write_csv: True
write_json: False
include_failed: True
path_privacy: Hidden
table_columns: ['Clip', 'Format', 'Probe', 'Capture', 'PDF', 'Warning']
dependency_summary: Dependency status: ffmpeg=configured path missing, ffprobe=configured path missing, mediainfo=configured path missing, braw_adapter=configured path missing, r3d_adapter=not configured, arri_art_cmd=not configured
dialog_status_ffmpeg: configured path missing
dialog_status_braw: configured path missing
dialog_status_r3d: not configured
```

## GUI Observations

- Shared pipeline reuse: PASS. `src/frameproof/gui/batch_controller.py:20-30` calls `run_batch()` directly, while `src/frameproof/cli.py:170-206` feeds the same validated `AppSettings` into the same core runner.
- Main screen controls: PASS. `src/frameproof/gui/main_window.py:68-166` defines source file and folder pickers, include-subfolders toggle, output PDF picker, project name, middle-frame selector, layout selector, path-privacy selector, still-export toggle, CSV and JSON toggles, failed-files toggle, dependency button, start and cancel buttons, banner, and the required six-column progress table.
- Dependency screen behavior: PASS. `src/frameproof/gui/dependency_dialog.py:51-153` shows FFmpeg, FFprobe, MediaInfo, BRAW adapter, R3D adapter, and ARRI ART CMD rows, allows edits and re-checks, and applies operator-facing dependency labels through `src/frameproof/gui/status_text.py:6-18`.
- Settings persistence: PASS. `src/frameproof/gui/settings_store.py:11-95` persists source paths, output defaults, report defaults, privacy mode, and adapter paths via an INI-backed `QSettings` store. `src/frameproof/gui/main_window.py:174-185` loads those values and `src/frameproof/gui/main_window.py:311-327` collects updated form state.
- Progress UX: PASS. `src/frameproof/core/batch_runner.py:88-97` emits row discovery events before per-clip work completes, `src/frameproof/core/batch_runner.py:191-205` sets final PDF inclusion state truthfully, and `src/frameproof/gui/main_window.py:334-396` renders running, cancelled, failed, and success banner states without inventing a parallel status model.
- Screenshots: unavailable in this terminal-only QA session. Offscreen smoke and widget inspection were used instead.

## Evidence

### Shared pipeline reuse is correct

- `Docs/ui-spec.md` requires the GUI to stay thin and reuse the shared pipeline.
- `src/frameproof/cli.py:170-206` and `src/frameproof/gui/batch_controller.py:20-30` both call `run_batch(settings)`.
- `src/frameproof/core/batch_runner.py:53-213` owns scanning, dependency inspection, grouping, probe, capture, render, manifest writing, and cancellation.
- Repo-wide search found no GUI module calling `scan_inputs`, `run_probe`, `run_captures`, `render_pdf`, or `write_manifests` directly outside the shared runner path.

### Dependency and progress vocabulary match the Stage 4D contract

- `src/frameproof/gui/status_text.py:6-18` maps the exact required dependency labels: `available`, `configured path missing`, `not configured`, and `runtime startup failure`.
- `tests/unit/test_gui_status_text.py:8-48` locks those labels and the summary string into the automated suite.
- `tests/unit/core/test_batch_runner.py:112-127` verifies that newly discovered rows start with a blank `PDF` cell and end with `included` once output truth is known.
- `tests/unit/core/test_batch_runner.py:130-180` verifies cooperative cancellation and confirms later rows become `skipped` rather than silently continuing.

### Required GUI surfaces exist in the current source

- `src/frameproof/gui/main_window.py:78-157` defines the main operator surface and the required progress-table columns.
- `src/frameproof/gui/main_window.py:248-261` refreshes dependency status, resets prior progress, and starts the worker-thread batch run.
- `src/frameproof/gui/main_window.py:263-265` keeps cancel explicit with the required “no new clip work” language.
- `src/frameproof/gui/dependency_dialog.py:51-143` implements the dependency-check surface with tool rows, status text, re-check, save, and close actions.

### Settings persistence is real, not cosmetic

- `src/frameproof/gui/settings_store.py:48-91` loads and saves source paths, output PDF, last output directory, project name, middle count, layout, still-export, CSV/JSON toggles, failed-files toggle, privacy mode, and adapter paths.
- `tests/unit/gui/test_settings_store.py:8-34` covers the round-trip persistence contract.
- `tests/unit/gui/test_main_window.py:34-91` confirms saved state is loaded back into the form and that progress-table updates render through the GUI.

### Validation completeness is sufficient for PASS

- Full automated validation passed in this session: `python -m pytest`, `ruff check .`, and `mypy src`.
- GUI-specific validation also passed in this session: `python -m frameproof.gui --help`, offscreen smoke, `tests/unit/gui`, `tests/unit/test_gui_status_text.py`, and offscreen widget inspection.
- The only runtime warning observed was local font fallback for missing `IBM Plex Sans`; it did not prevent launch or test execution.

## Evaluation

- Spec fidelity / product depth: PASS. The current GUI exposes the required Stage 4D controls, dependency-state vocabulary, progress-table contract, settings persistence, and shared-pipeline reuse.
- Functionality: PASS. The GUI constructs one validated `AppSettings` object, refreshes dependency state before launch, persists operator defaults, and uses the shared batch runner with cooperative cancellation.
- Visual design / UX clarity: PASS. Offscreen creation succeeds, the UI structure matches the spec, and the operator-facing status/banner text is explicit and truthful.
- Code quality / maintainability: PASS. Shared execution remains centralized in `run_batch()`, label mapping is centralized in `status_text.py`, and persistence is isolated to `SettingsStore`.
- Accessibility / responsiveness: PASS. The controller runs work on `QThread`, the GUI can be created in offscreen mode on this host, and the GUI test lane executes successfully.
- Validation completeness: PASS. The required command suite ran, targeted GUI validation ran, and source/runtime inspection covered the remaining Stage 4D gate concerns.

## Defects

No blocking defects found.

Non-blocking observation:

1. Offscreen smoke logs a host-specific font fallback warning because `IBM Plex Sans` is not installed locally. The GUI still launches and the QA gate is unaffected.

## Verdict

PASS. Stage 4D satisfies the QA gate in this session and Stage 5 is unblocked.

Exact next recommended prompt: `[Stage 5-Plan]`

Stop after QA.
