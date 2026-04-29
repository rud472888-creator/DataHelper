# Final Report

- stage: stage-07
- lane: dev
- subphase: implement
- release_readiness_state: not fully verified on this host
- next_recommended_prompt: `[Stage 7-QA]`

## Implemented Scope

- Replaced the bootstrap README with release-facing product, install, usage, output, dependency, and limitation guidance.
- Added a fresh-user setup guide for CLI and GUI startup, smoke commands, config diagnostics, and repo-local tool invocation.
- Added a dependency guide covering FFmpeg, FFprobe, MediaInfo, BRAW, R3D, and ARRI ART CMD path configuration plus licensing constraints.
- Added a release-facing architecture note that explains the shared pipeline and failure model without duplicating the full architecture spec.
- Added a reference TOML example for settings shape and `FRAMEPROOF_CONFIG` path conventions.
- Finalized the release checklist with exact smoke commands, host validation evidence, and unresolved blockers.
- Updated the Stage 7 implementation and Dev handoff records for fresh-session QA continuation.

## Files Changed

- `README.md`
- `Docs/setup-guide.md`
- `Docs/dependency-guide.md`
- `Docs/architecture-note.md`
- `Docs/release-checklist.md`
- `Docs/examples/frameproof.example.toml`
- `Docs/reports/final/final-report.md`
- `Docs/stages/stage-07-implement.md`
- `Docs/reports/dev/stage-07-handoff.md`
- `Docs/implement.md`
- `Docs/stage.md`
- `Docs/reports/status/current-status.md`

## Validation Summary

- `python -m frameproof --help` -> success
- `python -m frameproof config` -> success (`config_source: default`, `config_exists: False`, resolved path `/Users/server_jay/.config/frameproof/config.toml`)
- `python -m frameproof config --format json` -> success
- `python -m pytest` -> success (`95 passed, 9 skipped`)
- `ruff check .` -> success (`All checks passed!`)
- `mypy src` -> success (`Success: no issues found in 43 source files`)
- `python -m frameproof.gui --help` -> success
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> success
- README link verification -> success (`missing_count: 0`)
- dependency-diagnostic CLI smoke -> expected non-zero (`returncode: 2`, no PDF/CSV/JSON artifacts left behind)

## Smoke Evidence

### Run on this host

- CLI help and config diagnostics
- repository test, lint, and typecheck suite
- GUI help
- offscreen GUI smoke startup
- dependency-diagnostic CLI smoke with an empty `.mp4` and intentionally missing FFmpeg/FFprobe paths

### Blocked on this host

- ffmpeg-backed standard-video success-path smoke
  - blocker: `command -v ffmpeg` and `command -v ffprobe` both returned no executable path in this environment
- proprietary RAW success-path smoke
  - blocker: vendor executables and licensing/runtime evidence are not present in this environment

## Known Issues

- FFmpeg and FFprobe are external dependencies and were not available on this host for live success-path artifact generation.
- Proprietary RAW tooling is not bundled and remains subject to operator installation, runtime setup, and license constraints.
- Preview PDFs are review artifacts and may not match grading-reference color.
- Full GUI operator validation still requires a working desktop Qt runtime beyond `--smoke-test`.
- The example TOML documents settings shape and config-path conventions only; current repository evidence still centers pipeline execution on CLI flags and GUI state.

## Backlog

- Define packaged installer/distribution strategy for macOS and Windows.
- Decide and document FFmpeg/FFprobe bundling after license review.
- Validate dependency-enabled standard-video smoke on a host with FFmpeg/FFprobe installed.
- Validate BRAW, R3D, and ARRIRAW happy paths on hosts with the required vendor tools and licenses.
- If config-driven batch execution becomes a product requirement, implement and verify real TOML ingestion for pipeline runs instead of diagnostics-only path reporting.

## Release Readiness

Frame Proof is documentation-complete for the Stage 7 Dev scope, but release readiness is not fully proven on this host. The repository-level docs, tests, lint, typing, CLI help/config diagnostics, and GUI smoke all ran, but the environment did not include FFmpeg/FFprobe or proprietary RAW executables, so successful dependency-backed media-processing smoke could not be demonstrated here.

## QA Handoff Note

Fresh QA should verify:

- the new release docs match the actual CLI, GUI, and dependency surfaces
- every README-linked document exists
- the release checklist and final report are honest about blocked success-path smoke on this host
- the next prompt remains `[Stage 7-QA]`
