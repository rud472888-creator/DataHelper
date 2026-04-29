# Stage 03 Dev Handoff

- status: complete
- run_type: fix
- stage: stage-03
- lane: dev
- summary: Resolved the Stage 3 shared-schema QA failures by aligning `CaptureStatus` to the capture-only contract, expanding `BatchSummary` to the documented normalized counters, and adding regression tests that lock both surfaces. Fresh Stage 3 QA is required before any Stage 4A work.
- source_qa_report: `docs/reports/qa/stage-03-qa-report.md`
- latest_fix_artifact: `docs/stages/stage-03-fix.md`
- next_recommended_prompt: `[Stage 3-QA]`
- implementation_allowed_by_board: false
- qa_required: true

## QA Findings Resolved

- `CaptureStatus` no longer includes clip-only values. Capture records now accept only `success`, `decode_failed`, `metadata_incomplete`, and `skipped_duplicate`, matching `docs/api-contract.md` and `docs/data-inventory.md`.
- `BatchSummary` now exposes the documented aggregate breakdown for `success`, `partial_success`, `probe_failed`, `decode_failed`, and `skipped` items instead of the lossy `failed_count` bucket.
- `tests/unit/core/test_models.py` now locks both contract surfaces so future drift will fail the unit suite instead of reaching QA.

## Updated Files

- `src/frameproof/core/models.py`
- `tests/unit/core/test_models.py`
- `docs/stages/stage-03-fix.md`
- `docs/reports/dev/stage-03-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation

- `python -m pytest tests/unit` -> PASS (`32 passed`)
- `python -m pytest` -> PASS (`38 passed`)
- `ruff check .` -> PASS
- `mypy src` -> PASS

## Remaining Blockers

- Fresh Stage 3 QA is still required.
- Stage 4A remains blocked until the next QA run returns PASS.

## Fresh Session Notes

- Use repository files only; do not rely on hidden session history.
- For Stage 3 QA, review `src/frameproof/core/models.py`, `tests/unit/core/test_models.py`, and the Stage 2 contract docs directly.
- The board now points at `[Stage 3-QA]`; do not begin Stage 4A until QA passes.
