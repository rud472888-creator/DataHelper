# Stage 05 Fix

- lane: dev
- subphase: fix
- status: complete
- source_qa_report: `docs/reports/qa/stage-05-qa-report.md`
- next_recommended_prompt: `[Stage 5-QA]`

## Fix Scope

- Fix only the Stage 5 QA-reported desktop-size responsiveness defect and the missing automated/visual proof for that requirement.
- Keep Stage 5 limited to the existing GUI surface, existing PDF artifact flow, and regression coverage. No new features, data-contract changes, or Stage 6 work are allowed here.

## QA Issues And Fixes

1. Blocking: the main window now fits the required desktop viewport. `src/frameproof/gui/main_window.py` compacts the Stage 5 overview and guidance copy, keeps the dependency/start/cancel actions on one row, stacks the report controls and output toggles more narrowly, and lowers the hard minimum heights on the source list and progress table. Under the styled app the window now reports `minimumSizeHint=880x720`, and the artifact probe records `requested=1024x720 actual=1024x720`.
2. Moderate: Stage 5 validation now guards the resize target directly. `tests/unit/gui/test_main_window.py` asserts the styled main window stays within the `1024x720` minimum-size target and honors the requested `1280x860` artifact viewport. `scripts/generate_visual_artifacts.py` now records requested vs actual geometry in `artifacts/stage-05/verification-summary.txt` and renders screenshots at the widget's logical size, so `sips` now reports `1280x860` for the main-window artifacts and `1180x520` for the dependency dialog.

## Changed Files

- `src/frameproof/gui/main_window.py`
- `scripts/generate_visual_artifacts.py`
- `tests/unit/gui/test_main_window.py`
- `docs/stages/stage-05-fix.md`
- `docs/reports/dev/stage-05-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`
- `artifacts/stage-05/gui/gui-empty.png`
- `artifacts/stage-05/gui/gui-partial.png`
- `artifacts/stage-05/gui/gui-error.png`
- `artifacts/stage-05/gui/dependency-dialog.png`
- `artifacts/stage-05/verification-summary.txt`

## Validation Results

- `python -m pytest` -> PASS (`87 passed, 2 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `python scripts/generate_visual_artifacts.py` -> PASS
- `sips -g pixelWidth -g pixelHeight artifacts/stage-05/gui/gui-empty.png artifacts/stage-05/gui/gui-partial.png artifacts/stage-05/gui/gui-error.png artifacts/stage-05/gui/dependency-dialog.png` -> PASS (`1280x860` for the main window artifacts, `1180x520` for the dependency dialog)

## Re-QA Instruction

- Run a fresh Stage 5 QA session with `[Stage 5-QA]`.
- Recheck the Stage 5 GUI at `1024x720` and the generated `1280x860` artifact viewport.
- Read `artifacts/stage-05/verification-summary.txt` and confirm the recorded geometry probes match the intended viewport evidence.
- Do not begin Stage 6 until the new Stage 5 QA run returns PASS.
