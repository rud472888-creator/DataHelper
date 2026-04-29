# Stage 04D Fix

- lane: dev
- subphase: fix
- status: complete
- source_qa_report: `docs/reports/qa/stage-04D-qa-report.md`
- next_recommended_prompt: `[Stage 4D-QA]`

## Fix Scope

- Fix only the Stage 4D QA-reported dependency-label and progress-vocabulary mismatches in the GUI.
- Keep Stage 4D limited to the existing shared runner, existing GUI surfaces, and regression coverage. No new GUI features, architecture changes, or Stage 5 work are allowed here.

## QA Issues And Fixes

1. Dependency status text now uses the exact operator-facing labels required by `docs/ui-spec.md`: `available`, `configured path missing`, `not configured`, and `runtime startup failure`. The dialog and main-window summary now share one formatter so the wording cannot drift between surfaces.
2. The progress row model no longer invents a `pending` PDF state. Rows now start with a blank PDF cell before render, and the UI only surfaces the approved post-render values `included`, `skipped`, and `failed`.
3. Regression coverage now locks both fixes in the automated suite. `tests/unit/core/test_batch_runner.py` asserts the pre-render PDF cell is blank, and `tests/unit/test_gui_status_text.py` asserts the required dependency labels and summary text.
4. The live GUI smoke rerun remains environment-blocked on this machine. `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` still aborts with `Incompatible processor ... neon`, so fresh QA must re-run live GUI checks on a supported Qt runtime host.

## Changed Files

- `src/frameproof/core/progress_events.py`
- `src/frameproof/gui/status_text.py`
- `src/frameproof/gui/dependency_dialog.py`
- `src/frameproof/gui/main_window.py`
- `tests/unit/core/test_batch_runner.py`
- `tests/unit/test_gui_status_text.py`
- `docs/stages/stage-04D-fix.md`
- `docs/reports/dev/stage-04D-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation Results

- `python -m pytest` -> PASS (`79 passed, 2 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `python -m frameproof.gui --help` -> PASS
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> BLOCKED on this machine by `Incompatible processor ... neon`

## Re-QA Instruction

- Run a fresh Stage 4D QA session with `[Stage 4D-QA]`.
- Recheck that dependency states use the exact Stage 4D wording in both the dependency dialog and the main summary.
- Recheck that newly discovered progress rows do not show `pending` in the `PDF` column and only surface `included`, `skipped`, or `failed` once output truth is known.
- Re-run the live GUI smoke/manual checklist on a machine with a working Qt runtime.
- Do not begin Stage 5 until the new Stage 4D QA run returns PASS.
