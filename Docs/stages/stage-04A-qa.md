# Stage 04A QA

- lane: qa
- stage: stage-04A
- verdict: PASS
- gate: passed
- next_recommended_prompt: `[Stage 4B-Plan]`
- stage_4b_status: unblocked-by-qa

## Summary

Independent QA re-ran the Stage 4A standard-video CLI pipeline in a fresh session against the Stage 4A plan, implementation handoff, architecture, API contract, data inventory, UI spec, current source, current tests, and the required command output. The required command suite passes, the fatal standard-video dependency-missing lane now exits `2`, prints an explicit `dependency_missing` diagnostic naming `ffmpeg` and `ffprobe`, and suppresses PDF/CSV/JSON output as required. `ffmpeg` and `ffprobe` are not installed in this environment, so full happy-path standard-video artifact generation is environment-blocked here; under that constraint, QA also confirmed that non-fatal deferred RAW-family files do not abort the batch, PDF/CSV/JSON outputs are still generated, default manifest derivation works, and PNG export is off by default.

## Evidence Checked

- `AGENTS.md`
- `docs/stage.md`
- `docs/qa.md`
- `docs/stages/stage-04A-plan.md`
- `docs/stages/stage-04A-implement.md`
- `docs/reports/dev/stage-04A-handoff.md`
- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/data-inventory.md`
- `docs/ui-spec.md`
- `src/frameproof/__main__.py`
- `src/frameproof/cli.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/core/models.py`
- `src/frameproof/core/scanner.py`
- `src/frameproof/core/clip_grouper.py`
- `src/frameproof/core/adapter_resolver.py`
- `src/frameproof/core/probe_service.py`
- `src/frameproof/core/capture_service.py`
- `src/frameproof/core/report_builder.py`
- `src/frameproof/adapters/ffmpeg_adapter.py`
- `src/frameproof/render/pdf_renderer.py`
- `src/frameproof/output/manifest_writer.py`
- `tests/test_cli.py`
- `tests/integration/conftest.py`
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/integration/test_dependency_missing.py`

## Validation Results

- `python -m frameproof --help` -> PASS
- `python -m pytest` -> PASS (`49 passed, 1 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `command -v ffmpeg && command -v ffprobe` -> BLOCKED (`EXIT:1`, no output; full FFmpeg-backed standard-video E2E is not runnable on this machine)
- `python -m frameproof --input /tmp/.../clip.mp4 --middle-count 1 --layout contact_sheet --output /tmp/.../report.pdf --ffmpeg-path /missing/ffmpeg --ffprobe-path /missing/ffprobe --mediainfo-path /missing/mediainfo` -> PASS (`EXIT:2`, explicit `dependency_missing` line printed, no PDF/CSV/JSON written)
- `python -m frameproof --input /tmp/... --no-recursive --middle-count 3 --layout contact_sheet --output /tmp/.../report.pdf --csv /tmp/.../report.csv --json /tmp/.../report.json` -> PASS (`EXIT:0`, PDF/CSV/JSON written for deferred-format batch, CSV and JSON rows agree on `unsupported_format`, `PNG_COUNT:0`)
- `python -m frameproof --input /tmp/.../clip01.braw --middle-count 0 --layout contact_sheet --output /tmp/.../report.pdf` -> PASS (`EXIT:0`, default `report.csv` and `report.json` derived beside the PDF, all outputs non-empty, `PNG_COUNT:0`)

## Evaluation

- Spec fidelity / product depth: PASS. The Stage 4A CLI contract, fatal dependency handling, manifest defaults, and deferred-format isolation match the Stage 4A plan and UI/API requirements for the environment available in this session.
- Functionality: PASS. Fatal standard-video dependency loss is surfaced clearly and suppresses outputs; non-fatal per-file failures continue the batch and still produce report artifacts.
- Visual design / UX clarity: PASS. The CLI now surfaces actionable dependency diagnostics and output paths directly.
- Code quality / maintainability: PASS. The Stage 4A pipeline stays within the shared architecture, reuses one normalized report model, and keeps non-fatal RAW deferrals isolated.
- Accessibility / responsiveness: PASS for current scope. The CLI surface is simple, deterministic, and non-interactive; no GUI or responsive surface is in scope for Stage 4A.
- Validation completeness: PASS for this blocked-media environment. Full FFmpeg-backed standard-video artifact generation remains blocked locally because `ffmpeg` and `ffprobe` are absent, but the prompt-required dependency-missing path was validated and documented, and the required automated suite passes.

## Findings

1. No blocking defects were found in the current QA scope.
2. Residual risk: the real FFmpeg/FFprobe synthetic-video CLI sweep for `--middle-count 0`, `1`, `2`, and `3` remains environment-blocked on this machine and should be rerun later on a tool-enabled workstation if Stage 4B wants fresh local happy-path artifact evidence beyond automated coverage.

## Gate Decision

PASS. Stage 4A satisfies the QA gate in this session.

Exact next recommended prompt: `[Stage 4B-Plan]`

Stop after QA.
