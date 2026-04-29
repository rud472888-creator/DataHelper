# Stage 03 Fix

- lane: dev
- subphase: fix
- status: complete
- source_qa_report: `docs/reports/qa/stage-03-qa-report.md`
- next_recommended_prompt: `[Stage 3-QA]`

## Fix Scope

- Fix only the Stage 3 QA-reported shared-schema contract issues.
- Keep Stage 3 limited to the reusable foundation layer. No Stage 4A pipeline, adapter, manifest, or renderer work is allowed here.

## QA Issues And Fixes

1. `CaptureStatus` now matches the documented capture-result contract exactly. `src/frameproof/core/models.py` now limits capture statuses to `success`, `decode_failed`, `metadata_incomplete`, and `skipped_duplicate`, so `CaptureResult` and `CapturePoint` no longer accept clip-only values such as `partial_success` or `probe_failed`.
2. `BatchSummary` now carries the normalized batch counters required by the Stage 3 contract. `failed_count` was removed and replaced with `probe_failed_count`, `decode_failed_count`, and `skipped_count` while preserving `total_clips`, `success_count`, `partial_success_count`, and `status`.
3. Contract-level regression coverage was added. `tests/unit/core/test_models.py` now locks the exact `CaptureStatus` vocabulary, proves clip-only statuses are rejected by capture records, and verifies the required `BatchSummary` counters and non-negative validation.

## Changed Files

- `src/frameproof/core/models.py`
- `tests/unit/core/test_models.py`
- `docs/stages/stage-03-fix.md`
- `docs/reports/dev/stage-03-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation Results

- `python -m pytest tests/unit` -> PASS (`32 passed`)
- `python -m pytest` -> PASS (`38 passed`)
- `ruff check .` -> PASS
- `mypy src` -> PASS

## Re-QA Instruction

- Run a fresh Stage 3 QA session with `[Stage 3-QA]`.
- Recheck the shared-schema contract against `docs/api-contract.md`, `docs/data-inventory.md`, and `docs/architecture.md`.
- Do not start Stage 4A until Stage 3 QA returns PASS.
