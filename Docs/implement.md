# Implementation Ledger

Use this file as the durable Dev handoff ledger.
Every implement and fix run must leave enough detail for a fresh worker to continue without chat history.

## Current Stage Context

- current_stage: stage-07
- current_subphase: implement-complete
- lane: dev
- status: Stage 7 Dev implementation and release-wrap handoff are complete. Fresh QA is required next.
- latest_qa_verdict: PASS for stage-06
- latest_qa_report: `Docs/reports/qa/stage-06-qa-report.md`
- latest_dev_handoff: `Docs/reports/dev/stage-07-handoff.md`
- next_recommended_prompt: `[Stage 7-QA]`

## Completed Functionality

- The release-facing documentation now matches the current repository behavior instead of the original bootstrap-shell message.
- Fresh-user setup instructions now cover editable install, dev-tool invocation, CLI help/config diagnostics, GUI help, and offscreen GUI smoke startup.
- Dependency guidance now documents FFmpeg, FFprobe, MediaInfo, BRAW, R3D, and ARRI ART CMD path configuration through both CLI flags and the GUI dependency dialog.
- A release-facing architecture note now explains the single shared pipeline, RAW subprocess isolation, and the failure model in operator-facing language.
- A reference TOML example now documents the current settings shape and `FRAMEPROOF_CONFIG` path convention without overclaiming full config-driven pipeline execution.
- The release checklist and final report now record exact validation commands, blocked smoke conditions, known issues, backlog, and the honest release-readiness state for this host.

## Changed Files And Why

- `README.md` now presents the actual product surface, install path, CLI/GUI usage, outputs, docs map, and known limitations.
- `Docs/setup-guide.md` documents environment setup, first commands, smoke commands, and troubleshooting.
- `Docs/dependency-guide.md` documents external tool expectations, CLI overrides, GUI settings, and licensing/distribution limits.
- `Docs/architecture-note.md` translates the full architecture into release-facing guidance.
- `Docs/release-checklist.md` now acts as the actionable Stage 7 release-wrap checklist with command references and blocker disclosure.
- `Docs/examples/frameproof.example.toml` shows the current settings schema and config-path convention.
- `Docs/reports/final/final-report.md` records implemented scope, validation, known issues, backlog, and release readiness.
- `Docs/stages/stage-07-implement.md` records the Stage 7 implementation outcome.
- `Docs/reports/dev/stage-07-handoff.md` is the Dev-to-QA handoff artifact.
- `Docs/stage.md` and `Docs/reports/status/current-status.md` advance the delivery board to the QA handoff state.

## Implementation Decisions

- Kept Stage 7 docs-only. No product features, adapters, packaging code, or installer behavior were added.
- Documented proprietary RAW support as operator-supplied and licensing-constrained only; no bundled support claim was introduced.
- Kept the config example explicitly non-authoritative for pipeline execution because the current CLI evidence is runtime diagnostics plus flag-driven runs.
- Marked release readiness as not fully verified on this host rather than collapsing environment blockers into a false-ready statement.

## Data/API/State Ownership Changes

- No runtime ownership changed in Stage 7. This session updated documentation and delivery state only.
- Delivery-state ownership moved forward through `Docs/stage.md`, `Docs/reports/status/current-status.md`, `Docs/stages/stage-07-implement.md`, and `Docs/reports/dev/stage-07-handoff.md`.

## Validation Commands And Results

- `python -m frameproof --help` -> success
- `python -m frameproof config` -> success (`config_source: default`, `config_exists: False`, resolved path `/Users/server_jay/.config/frameproof/config.toml`)
- `python -m frameproof config --format json` -> success
- `python -m pytest` -> success (`95 passed, 9 skipped`)
- `ruff check .` -> success (`All checks passed!`)
- `mypy src` -> success (`Success: no issues found in 43 source files`)
- `python -m frameproof.gui --help` -> success
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> success
- README-linked docs existence check -> success (`missing_count: 0`)
- dependency-diagnostic CLI smoke -> expected non-zero (`returncode: 2`, no PDF/CSV/JSON artifacts)

## Smoke And Manual Notes

- Standard-video success-path smoke is documented but was not executable on this host because `command -v ffmpeg` and `command -v ffprobe` returned no executable path.
- Proprietary RAW happy-path smoke is documented but was not executable on this host because vendor executables and licensing/runtime evidence are not present here.
- GUI interactive/manual validation beyond `--smoke-test` is still governed by `tests/manual/gui_smoke_checklist.md` and requires a working desktop Qt runtime.

## Known Issues And Limitations

- Release readiness is not fully proven on this host because dependency-backed media-processing smoke could not be run here.
- Proprietary RAW redistribution, packaging, and licensing remain unresolved external constraints.
- Preview PDFs are not color-critical references.
- The example TOML documents config shape and path conventions, but it should not be treated as proof of automated config-driven batch execution.

## Manual Verification Steps

- On a host with `ffmpeg` and `ffprobe`, run the documented standard-video smoke command from `README.md` or `Docs/release-checklist.md` and confirm the PDF plus default manifests are generated.
- On a host with the required vendor tools, run the documented RAW CLI examples and confirm the affected format family no longer reports dependency-missing.
- Run the interactive GUI checklist in `tests/manual/gui_smoke_checklist.md` on a machine with a working desktop Qt runtime.

## Future Fresh Dev Session Notes

- Use repository files only; do not rely on hidden session history.
- Start with `Docs/stages/stage-07-implement.md`, `Docs/reports/dev/stage-07-handoff.md`, `Docs/reports/final/final-report.md`, and `Docs/release-checklist.md`.
- The next legal prompt is `[Stage 7-QA]`.
