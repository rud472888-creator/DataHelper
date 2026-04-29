# Stage 04C Dev Handoff

- status: complete
- run_type: fix
- stage: stage-04C
- lane: dev
- summary: Resolved the Stage 4C QA failure by restoring `requested_ratio` to Layout A capture cards and tightening the detailed-PDF regression test so the omission cannot silently pass again. Fresh Stage 4C QA is required before any Stage 4D work.
- source_qa_report: `docs/reports/qa/stage-04C-qa-report.md`
- latest_fix_artifact: `docs/stages/stage-04C-fix.md`
- next_recommended_prompt: `[Stage 4C-QA]`
- implementation_allowed_by_board: false
- qa_required: true

## QA Findings Resolved

- Layout A detail cards now render `Requested ratio` directly from the existing `CapturePoint.requested_ratio` field, closing the PDF-versus-manifest parity gap QA found.
- The detailed PDF regression test now asserts `Requested ratio: 0.500`, so the required field is covered by the automated suite rather than only by manual artifact inspection.

## Updated Files

- `src/frameproof/render/pdf_renderer.py`
- `tests/unit/render/test_pdf_renderer.py`
- `docs/stages/stage-04C-fix.md`
- `docs/reports/dev/stage-04C-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation

- `python -m pytest` -> PASS (`75 passed, 2 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `command -v ffmpeg` -> no output, exit code `1`
- `command -v ffprobe` -> no output, exit code `1`

## Remaining Risks

- FFmpeg-backed live standard-video smoke remains blocked on this machine because `ffmpeg` and `ffprobe` are absent.
- Fresh Stage 4C QA is still required.
- Stage 4D remains blocked until the new QA run returns PASS.

## Fresh Session Notes

- Use repository files only; do not rely on prior chat state.
- For re-QA, inspect `src/frameproof/render/pdf_renderer.py`, `tests/unit/render/test_pdf_renderer.py`, and `docs/stages/stage-04C-fix.md` first.
- The board now points at `[Stage 4C-QA]`; do not begin Stage 4D until QA passes.
