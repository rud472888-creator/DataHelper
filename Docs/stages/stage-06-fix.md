# Stage 06 Fix

- lane: dev
- subphase: fix
- status: complete
- source_qa_report: `docs/reports/qa/stage-06-qa-report.md`
- next_recommended_prompt: `[Stage 6-QA]`

## Fix Scope

- Re-check only the Stage 6 QA blockers around GUI smoke startup and GUI test-lane execution.
- Keep Stage 6 limited to the existing GUI/runtime path and existing hardening coverage. No new product features, validation weakening, or Stage 7 work are allowed here.

## QA Issues And Fixes

1. The reported blocking GUI smoke failure does not reproduce in the current repository state. Fresh rerun of `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` exits `0` on this host.
2. The reported GUI test-collection suppression does not reproduce in the current repository state. Fresh rerun of `python -m pytest tests/unit/gui -q` executes the GUI suite directly and returns `6 passed`.
3. No product-source or test edits were required in this fix session. Current `src/frameproof/gui/` and `tests/unit/gui/` already satisfy the Stage 6 QA blockers; this fix phase updates the durable Dev records so the next fresh QA session uses current evidence instead of the stale failure report.

## Changed Files

- `docs/stages/stage-06-fix.md`
- `docs/reports/dev/stage-06-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation Results

- `python -m pytest` -> PASS (`95 passed, 9 skipped`)
- `python -m pytest tests/unit/gui -q` -> PASS (`6 passed`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `python -m frameproof --help` -> PASS
- `python -m frameproof --input <unsupported.txt> --output <unsupported.pdf>` -> PASS (`returncode=2`, invalid-input fatal, no output artifacts written)
- `python -m frameproof --input <clip.braw> --output <raw.pdf>` -> PASS (`returncode=2`, RAW dependency-missing fatal, no output artifacts written)
- `python -m frameproof --input <broken.mp4> --output <standard.pdf> --ffmpeg-path /missing/ffmpeg --ffprobe-path /missing/ffprobe --mediainfo-path /missing/mediainfo` -> PASS (`returncode=2`, standard dependency-missing fatal, no output artifacts written)
- `python -m frameproof.gui --help` -> PASS
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS

## Re-QA Instruction

- Run a fresh Stage 6 QA session with `[Stage 6-QA]`.
- Re-run the exact GUI smoke command and the direct GUI pytest lane before making any new source assumptions.
- Re-run the Stage 6 CLI fatal/dependency-missing smokes and confirm they still leave no stray PDF/CSV/JSON artifacts behind.
- Do not begin Stage 7 until the new Stage 6 QA run returns PASS.
