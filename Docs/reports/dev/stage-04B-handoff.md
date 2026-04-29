# Stage 04B Dev Handoff

- status: complete
- run_type: implement
- stage: stage-04B
- lane: dev
- summary: Implemented real RAW adapter routing, shared dependency inspection, subprocess-backed `BRAW` and R3D JSON clients, ARRIRAW ART CMD integration, conservative R3D grouping, and the required Stage 4B regression coverage. Fresh Stage 4B QA is required before any Stage 4C work.
- source_plan_artifact: `docs/stages/stage-04B-plan.md`
- latest_implement_artifact: `docs/stages/stage-04B-implement.md`
- next_recommended_prompt: `[Stage 4B-QA]`
- implementation_allowed_by_board: false
- qa_required: true

## Delivered Against Plan

- RAW adapter selection is no longer deferred for `.braw`, `.r3d`, and `.ari`.
- Missing RAW dependencies now surface as truthful `dependency_missing` results with dependency name, required tools, and dependency state.
- BRAW and R3D use a shared subprocess JSON contract with request round-trip validation and malformed JSON handling.
- ARRIRAW uses configured ART CMD probe/capture commands without bundling or importing proprietary SDKs.
- R3D grouping now collapses same-directory numeric parts into one ordered logical candidate.

## Updated Files

- `src/frameproof/cli.py`
- `src/frameproof/core/adapter_resolver.py`
- `src/frameproof/core/clip_grouper.py`
- `src/frameproof/core/dependency_inspector.py`
- `src/frameproof/core/probe_service.py`
- `src/frameproof/core/__init__.py`
- `src/frameproof/adapters/__init__.py`
- `src/frameproof/adapters/_json_subprocess_adapter.py`
- `src/frameproof/adapters/braw_adapter_client.py`
- `src/frameproof/adapters/r3d_adapter_client.py`
- `src/frameproof/adapters/arriraw_art_adapter_client.py`
- `src/frameproof/adapters/ffmpeg_adapter.py`
- `tests/unit/adapters/test_base.py`
- `tests/unit/adapters/test_ffmpeg_adapter.py`
- `tests/unit/adapters/test_braw_adapter_client.py`
- `tests/unit/adapters/test_r3d_adapter_client.py`
- `tests/unit/adapters/test_arriraw_art_adapter_client.py`
- `tests/unit/core/test_clip_grouper.py`
- `tests/unit/core/test_dependency_inspector.py`
- `tests/integration/test_dependency_missing.py`
- `tests/integration/test_raw_dependency_missing.py`
- `tests/test_cli.py`
- `docs/implement.md`
- `docs/stages/stage-04B-implement.md`
- `docs/reports/dev/stage-04B-handoff.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation

- `python -m pytest tests/unit tests/integration` -> PASS (`56 passed, 1 skipped`)
- `python -m pytest` -> PASS (`63 passed, 1 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `env | rg 'FRAMEPROOF|BRAW|R3D|ARRI'` -> no output, exit code `1`

## Remaining Risks

- No real proprietary RAW binary was configured here, so vendor-runtime smoke coverage is still pending on a tool-enabled workstation.
- `tests/integration/test_cli_standard_pipeline.py` remains skipped locally because `ffmpeg` and `ffprobe` are absent.
- QA should verify the fatal all-dependency-missing batch behavior still matches expectations for mixed and RAW-only inputs.

## Fresh Session Notes

- Use repository files only; do not rely on prior chat state.
- For Stage 4B QA, inspect `src/frameproof/core/dependency_inspector.py`, `src/frameproof/core/adapter_resolver.py`, `src/frameproof/core/clip_grouper.py`, and the three RAW adapter client files first.
- The board now points at `[Stage 4B-QA]`; do not begin Stage 4C until QA passes.
