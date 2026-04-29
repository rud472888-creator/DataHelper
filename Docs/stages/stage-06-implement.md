# Stage 06 Implement

- lane: dev
- subphase: implement
- status: complete
- source_plan: `docs/stages/stage-06-plan.md`
- next_recommended_prompt: `[Stage 6-QA]`

## Scope Delivered

- Added early output-target validation so invalid PDF/manifest/stills/staging targets fail before scan/probe work begins.
- Added structured batch-level fatal output metadata and cleanup of partial PDF/manifest artifacts when terminal output stages fail.
- Hardened still-export filename handling for non-ASCII names and traversal-style inputs while keeping collision-safe filenames inside the configured stills root.
- Expanded automated coverage for all supported `middle_count` values, invalid input, short clips, non-ASCII paths, output-write failure, manifest parity, dependency-missing continuation, damaged-media continuation, scanner Unicode paths, and default staging isolation.
- Updated GUI/manual smoke guidance for Stage 6 reliability, long-warning readability, and quick GUI smoke startup.

## Hardening Decisions

1. Output validation now happens before scan/probe/capture work. This keeps fatal output-path issues cheap and deterministic while preserving the existing per-clip failure model.
2. Structured fatal metadata is limited to batch-level terminal failures. The public clip/capture status vocabulary stays unchanged to preserve report, manifest, and GUI parity.
3. Stage 6 keeps the one-pipeline contract intact. No alternate GUI path, no new feature flags, and no new concurrency subsystem were added.
4. Default staging remains app-owned and outside the source tree unless the operator explicitly overrides it. Stage 6 documents that policy and locks it with unit coverage.

## Changed Files

- `src/frameproof/core/batch_runner.py`
- `src/frameproof/output/still_exporter.py`
- `src/frameproof/cli.py`
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/integration/test_dependency_missing.py`
- `tests/test_cli.py`
- `tests/unit/core/test_batch_runner.py`
- `tests/unit/core/test_scanner.py`
- `tests/unit/output/test_manifest_writer.py`
- `tests/unit/output/test_still_exporter.py`
- `tests/manual/gui_smoke_checklist.md`
- `docs/stages/stage-06-implement.md`
- `docs/reports/dev/stage-06-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation Results

- `python -m pytest` -> PASS (`95 passed, 9 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `python -m frameproof --input <unsupported.txt> --output <unsupported.pdf>` -> PASS (`returncode=2`, invalid-input smoke)
- `python -m frameproof --input <clip.braw> --output <raw.pdf>` -> PASS (`returncode=2`, RAW dependency-missing smoke)
- `python -m frameproof --input <broken.mp4> --output <standard.pdf> --ffmpeg-path /missing/ffmpeg --ffprobe-path /missing/ffprobe --mediainfo-path /missing/mediainfo` -> PASS (`returncode=2`, standard dependency-missing smoke)
- `python -m frameproof.gui --help` -> PASS
- `python -m frameproof.gui --smoke-test` -> PASS

## Accessibility And Responsiveness Notes

- The Stage 5 desktop layout remains the active GUI baseline; Stage 6 adds manual checks for long warning text, degraded mixed batches, and quick smoke startup without changing the established layout.
- `python -m frameproof.gui --smoke-test` succeeds in this session, but Qt logs a fallback-font warning when `IBM Plex Sans` is unavailable.

## Remaining Risks

- ffmpeg-backed success-path CLI smoke for valid standard-video media remains blocked in this environment because `ffmpeg`/`ffprobe` are unavailable locally; the corresponding integration tests are present and skipped.
- Full live GUI manual validation still depends on a host with a working desktop Qt runtime.

## Exact Next Prompt

`[Stage 6-QA]`

## Outcome

Stage 6 hardening implementation is complete. Fresh QA should now verify the new failure handling, mixed-batch behavior, Unicode path handling, and manual GUI reliability checks without relying on hidden session state.
