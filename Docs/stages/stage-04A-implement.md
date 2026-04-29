# Stage 04A Implement

- lane: dev
- stage: stage-04A
- subphase: implement
- status: complete
- scope_boundary: standard-video-cli-pipeline
- next_recommended_prompt: `[Stage 4A-QA]`

## Delivered Scope

- Implemented recursive standard-video scanning and deterministic extension filtering.
- Implemented conservative Stage 4A clip grouping with one logical clip per standard video file.
- Implemented standard adapter resolution to the FFmpeg adapter while leaving RAW-family formats visibly deferred.
- Wired probe, capture, report build, PDF render, and manifest writing into the real CLI batch path.
- Added Stage 4A unit and integration coverage for both happy-path and dependency-missing behavior.

## Changed Files And Reasons

- `src/frameproof/cli.py` fixed broken imports, completed the Stage 4A orchestration path, and narrowed capture execution safely for strict typing.
- `src/frameproof/adapters/ffmpeg_adapter.py` fixed protocol and frame-rate parsing typing issues without changing the intended runtime behavior.
- `src/frameproof/core/models.py` now accepts zero-capture report items so failed and dependency-missing candidates remain visible in reporting.
- `src/frameproof/render/pdf_renderer.py` adds the mypy import treatment required for `reportlab`.
- `tests/test_cli.py` now asserts the real Stage 4A CLI contract.
- `tests/unit/core/test_scanner.py`, `tests/unit/core/test_report_builder.py`, and `tests/unit/adapters/test_ffmpeg_adapter.py` lock the new Stage 4A behaviors.
- `tests/integration/` now contains the required Stage 4A integration harness and tests.

## Implementation Decisions

- Reused the existing Stage 3 foundation models, planner, and timecode helpers rather than adding a second Stage 4A-only schema.
- Allowed zero-capture `ReportItem` records because truthful probe/dependency failure reporting requires visible failed clips even when no frames were captured.
- Kept the FFmpeg happy-path test conditional on real tool availability and made dependency-missing coverage mandatory so Stage 4A still verifies in tool-less environments.
- Did not implement RAW native adapter clients, GUI work, Layout A, or still export because those remain outside this stage boundary.

## Validation Results

- `python -m frameproof --help` -> PASS
- `python -m pytest tests/unit tests/integration` -> PASS (`42 passed, 1 skipped`)
- `python -m pytest` -> PASS (`49 passed, 1 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS

## Generated Artifacts

- No persistent runtime artifacts were checked into the repository during this run.
- The real FFmpeg smoke artifacts were not generated because `ffmpeg` and `ffprobe` were not available on `PATH` in this environment.

## Blockers And Known Gaps

- The happy-path integration test is skipped until FFmpeg tools are installed locally.
- Stage 4A now requires fresh QA; no additional Dev work is pending in this phase.

## Fresh Session Notes

- Run `[Stage 4A-QA]` next.
- If QA runs on a machine with FFmpeg installed, it should also execute the real synthetic-video happy-path and smoke flow.
