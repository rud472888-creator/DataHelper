# Stage 07 Implement

- lane: dev
- subphase: implement
- status: complete
- source_plan: `Docs/stages/stage-07-plan.md`
- next_recommended_prompt: `[Stage 7-QA]`

## Scope Delivered

- Rewrote `README.md` to describe the current product rather than the bootstrap shell.
- Added `Docs/setup-guide.md` with install, validation, CLI, GUI, config, and smoke guidance.
- Added `Docs/dependency-guide.md` with executable-path overrides, GUI dependency dialog coverage, and licensing limits.
- Added `Docs/architecture-note.md` to summarize the shared pipeline and failure model for release readers.
- Added `Docs/examples/frameproof.example.toml` as a reference for settings shape and config-path conventions.
- Finalized `Docs/release-checklist.md` with exact commands, host evidence, and unresolved blockers.
- Added `Docs/reports/final/final-report.md` and the Stage 7 durable handoff records.

## Documentation Decisions

1. The release docs stay aligned to implemented behavior only. They do not claim bundled FFmpeg, bundled proprietary RAW tooling, or a completed packaged-installer story.
2. The config example is labeled as a reference artifact because the current CLI evidence shows runtime config-path diagnostics, not a proven generic TOML-driven batch-run workflow.
3. The release-readiness statement is conditional. This host validated the repo baseline, but it could not prove live success-path media processing without FFmpeg/FFprobe or vendor RAW tools.
4. The docs keep the one-pipeline architecture intact and avoid implying a separate GUI processing path.

## Changed Files

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

## Validation Results

- `python -m frameproof --help` -> success
- `python -m frameproof config` -> success (`config_source: default`, `config_exists: False`)
- `python -m frameproof config --format json` -> success
- `python -m pytest` -> success (`95 passed, 9 skipped`)
- `ruff check .` -> success (`All checks passed!`)
- `mypy src` -> success (`Success: no issues found in 43 source files`)
- `python -m frameproof.gui --help` -> success
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> success
- README-linked doc existence check -> success (`missing_count: 0`)
- dependency-diagnostic CLI smoke -> expected non-zero (`returncode: 2`, no PDF/CSV/JSON artifacts)

## Remaining Risks

- ffmpeg-backed success-path smoke remains blocked on this host because `command -v ffmpeg` and `command -v ffprobe` returned no executable path.
- Proprietary RAW success-path smoke remains blocked on this host because vendor executables and licensing evidence are unavailable.
- Full GUI operator validation still depends on a working desktop runtime beyond the offscreen smoke path.

## Exact Next Prompt

`[Stage 7-QA]`

## Outcome

Stage 7 Dev implementation is complete for the release-wrap documentation and handoff scope. The next fresh session should be QA only.
