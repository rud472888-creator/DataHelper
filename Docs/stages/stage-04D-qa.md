# Stage 04D QA

- lane: qa
- stage: stage-04D
- verdict: PASS
- gate: passed
- next_recommended_prompt: `[Stage 5-Plan]`
- stage_5_status: unblocked-by-qa

## Summary

Independent QA re-ran Stage 4D in a fresh session against the Stage 4D plan, implementation notes, dev handoff, UI spec, current GUI/core source, and current tests. The required command suite passes in the current tree: `python -m pytest` (`82 passed, 2 skipped`), `ruff check .`, `mypy src`, `python -m frameproof.gui --help`, and `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test`. The GUI-specific pytest lane also executes directly on this host: `QT_QPA_PLATFORM=offscreen python -m pytest tests/unit/gui -vv` returns `3 passed`.

Stage 4D now satisfies the QA gate. The GUI remains a thin client over the shared `frameproof.core.batch_runner.run_batch()` path, settings persistence is implemented through the QSettings-backed store, the dependency surfaces use the exact operator-facing labels required by the UI spec, and the progress UX no longer exposes an out-of-spec PDF placeholder state. Offscreen widget inspection also confirmed the required controls, progress-table columns, dependency summary behavior, and persisted form defaults. No blocking defects were found, so Stage 5 is unblocked.

## Evidence Checked

- `AGENTS.md`
- `Docs/qa.md`
- `Docs/stages/stage-04D-plan.md`
- `Docs/stages/stage-04D-implement.md`
- `Docs/reports/dev/stage-04D-handoff.md`
- `Docs/ui-spec.md`
- `src/frameproof/cli.py`
- `src/frameproof/core/batch_runner.py`
- `src/frameproof/gui/__main__.py`
- `src/frameproof/gui/batch_controller.py`
- `src/frameproof/gui/dependency_dialog.py`
- `src/frameproof/gui/main_window.py`
- `src/frameproof/gui/settings_store.py`
- `src/frameproof/gui/status_text.py`
- `tests/manual/gui_smoke_checklist.md`
- `tests/unit/core/test_batch_runner.py`
- `tests/unit/gui/test_batch_controller.py`
- `tests/unit/gui/test_main_window.py`
- `tests/unit/gui/test_settings_store.py`
- `tests/unit/test_gui_status_text.py`

## Validation Results

- `python -m pytest` -> PASS (`82 passed, 2 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS (`Success: no issues found in 41 source files`)
- `python -m frameproof.gui --help` -> PASS
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/unit/gui -vv` -> PASS (`3 passed`)
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/unit/test_gui_status_text.py -vv` -> PASS (`2 passed`)
- Offscreen GUI inspection script -> PASS

## Evaluation

- Spec fidelity / product depth: PASS. Required Stage 4D controls, dependency wording, shared pipeline reuse, settings persistence, progress-table vocabulary, and cancel language are present in the current tree.
- Functionality: PASS. The GUI builds one validated `AppSettings` mapping, refreshes dependency status before launch, persists operator defaults, runs batch work on a worker thread, and forwards truthful progress/output state from the shared runner.
- Visual design / UX clarity: PASS. The current window structure exposes the required controls, banner, dependency dialog, and progress table; the smoke run and offscreen inspection show the window can be created successfully on this host.
- Code quality / maintainability: PASS. CLI and GUI both call the same `run_batch()` entrypoint, dependency-label mapping is centralized, and persistence remains isolated to `SettingsStore`.
- Accessibility / responsiveness: PASS. The GUI now launches in offscreen smoke mode on this host, the controller uses `QThread` to keep work off the UI thread, and the GUI-targeted tests execute directly.
- Validation completeness: PASS. Required static checks, full pytest, direct GUI pytest, help output, smoke launch, source inspection, and offscreen widget inspection were all completed in this session.

## Findings

1. Shared pipeline reuse is intact. CLI and GUI both call `run_batch(settings)`, and no GUI-only scan/probe/capture/render path was found.
2. Dependency-state wording matches the UI spec. The dialog and summary surfaces use `available`, `configured path missing`, `not configured`, and `runtime startup failure`.
3. Settings persistence is real, not decorative. Source paths, output defaults, report defaults, privacy mode, and adapter paths are stored and restored through the GUI settings store.
4. Progress UX matches the Stage 4D contract. Rows are added as candidates are discovered, statuses update without a fake PDF placeholder state, and cancel remains cooperative.
5. Non-blocking observation: offscreen smoke logs a host font fallback warning because `IBM Plex Sans` is not installed locally, but the GUI still launches and the QA gate is unaffected.

## Gate Decision

PASS. Stage 04D satisfies the QA gate in this session.

Exact next recommended prompt: `[Stage 5-Plan]`

Stop after QA.
