# Stage 04D Dev Handoff

- status: complete
- run_type: fix
- stage: stage-04D
- lane: dev
- summary: Resolved the Stage 4D QA vocabulary defects by switching dependency surfaces to the exact operator-facing labels and removing the out-of-spec `pending` PDF state from progress rows. Fresh Stage 4D QA is required, and live GUI smoke remains environment-blocked on this host.
- source_qa_report: `docs/reports/qa/stage-04D-qa-report.md`
- latest_fix_artifact: `docs/stages/stage-04D-fix.md`
- next_recommended_prompt: `[Stage 4D-QA]`
- implementation_allowed_by_board: false
- qa_required: true

## QA Findings Resolved

- Dependency dialog and main-window dependency summary now use one shared formatter that maps `configured_missing`, `not_configured`, and `runtime_error` to the exact Stage 4D labels `configured path missing`, `not configured`, and `runtime startup failure`.
- Progress rows no longer expose the unapproved `pending` PDF state. The pre-render cell is blank, and only the approved final values `included`, `skipped`, and `failed` are shown once output truth is known.
- New regression coverage locks both fixes into the required automated suite even on hosts where Qt GUI tests are skipped.
- The offscreen GUI smoke rerun is still blocked on this machine by the installed Qt runtime requiring `neon`, so fresh QA must validate live GUI behavior on a supported runtime host.

## Updated Files

- `src/frameproof/core/progress_events.py`
- `src/frameproof/gui/dependency_dialog.py`
- `src/frameproof/gui/main_window.py`
- `src/frameproof/gui/status_text.py`
- `tests/unit/core/test_batch_runner.py`
- `tests/unit/test_gui_status_text.py`
- `docs/stages/stage-04D-fix.md`
- `docs/reports/dev/stage-04D-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation

- `python -m pytest` -> PASS (`79 passed, 2 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `python -m frameproof.gui --help` -> PASS
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> BLOCKED on this machine because the installed Qt runtime aborts with `Incompatible processor ... neon`

## Remaining Risks

- Live GUI execution still needs QA on a machine with a working Qt runtime.
- Stage 4D QA must verify the dependency dialog wording, dependency summary wording, and blank-to-final PDF cell behavior on a supported runtime.
- Stage 5 remains blocked until fresh Stage 4D QA returns PASS.

## Fresh Session Notes

- Use repository files only; do not rely on hidden session history.
- Read `docs/stages/stage-04D-fix.md`, `docs/reports/qa/stage-04D-qa-report.md`, `docs/implement.md`, and the updated GUI status-mapping files first.
- Stop at QA; do not begin Stage 5 from this handoff.
