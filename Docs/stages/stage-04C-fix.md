# Stage 04C Fix

- lane: dev
- subphase: fix
- status: complete
- source_qa_report: `docs/reports/qa/stage-04C-qa-report.md`
- next_recommended_prompt: `[Stage 4C-QA]`

## Fix Scope

- Fix only the Stage 4C QA-reported Layout A `requested_ratio` omission and the missing regression coverage that allowed it to pass automated validation.
- Keep Stage 4C limited to the existing detail PDF renderer and its tests. No GUI work, RAW adapter changes, manifest-schema changes, or still-export scope changes are allowed here.

## QA Issues And Fixes

1. Layout A detail cards now render `Requested ratio` from the existing `CapturePoint.requested_ratio` data in `src/frameproof/render/pdf_renderer.py`, restoring PDF parity with the manifest outputs and `docs/ui-spec.md`.
2. `tests/unit/render/test_pdf_renderer.py` now asserts the rendered ratio text (`Requested ratio: 0.500`) so future regressions fail in the automated suite before QA.

## Changed Files

- `src/frameproof/render/pdf_renderer.py`
- `tests/unit/render/test_pdf_renderer.py`
- `docs/stages/stage-04C-fix.md`
- `docs/reports/dev/stage-04C-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation Results

- `python -m pytest` -> PASS (`75 passed, 2 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `command -v ffmpeg` -> no output, exit code `1`
- `command -v ffprobe` -> no output, exit code `1`

## Re-QA Instruction

- Run a fresh Stage 4C QA session with `[Stage 4C-QA]`.
- Recheck the Layout A PDF artifact and confirm the per-frame detail block now includes `Requested ratio` while CSV and JSON manifest parity remains intact.
- Do not begin Stage 4D until the new Stage 4C QA run returns PASS.
