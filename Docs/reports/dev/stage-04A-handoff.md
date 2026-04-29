# Stage 04A Dev Handoff

- status: complete
- run_type: fix
- stage: stage-04A
- lane: dev
- summary: Resolved the Stage 4A QA failure by making the fatal dependency-missing CLI path print explicit `dependency_missing` diagnostics with `ffmpeg` and `ffprobe` tool context, then tightened integration coverage around that user-facing output. Fresh Stage 4A QA is required before any Stage 4B work.
- source_qa_report: `docs/reports/qa/stage-04A-qa-report.md`
- latest_fix_artifact: `docs/stages/stage-04A-fix.md`
- next_recommended_prompt: `[Stage 4A-QA]`
- implementation_allowed_by_board: false
- qa_required: true

## QA Findings Resolved

- The fatal dependency-missing summary now prints an explicit per-clip diagnostic line instead of only aggregate counts and a generic fatal message.
- The CLI output now surfaces the exact state QA asked for: `dependency_missing`, `adapter=ffmpeg`, `required_tools=ffmpeg,ffprobe`, and the normalized `dependency_state`.
- The dependency-missing integration test now locks that user-facing contract so future regressions fail in CI before reaching QA.

## Updated Files

- `src/frameproof/cli.py`
- `tests/integration/test_dependency_missing.py`
- `docs/stages/stage-04A-fix.md`
- `docs/reports/dev/stage-04A-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation

- `python -m frameproof --help` -> PASS
- `python -m frameproof --input <tmp>/clip.mp4 --middle-count 1 --layout contact_sheet --output <tmp>/report.pdf --ffmpeg-path /missing/ffmpeg --ffprobe-path /missing/ffprobe --mediainfo-path /missing/mediainfo` -> PASS for expected fatal behavior (`EXIT:2`, explicit `dependency_missing` line, no PDF/CSV/JSON output)
- `python -m pytest` -> PASS (`49 passed, 1 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `command -v ffmpeg; command -v ffprobe` -> no output, exit code `1`

## Remaining Risks

- The happy-path FFmpeg integration test remains skipped on this machine because the FFmpeg toolchain is not installed locally.
- Fresh Stage 4A QA is still required.
- Stage 4B remains blocked until the new QA run returns PASS.

## Fresh Session Notes

- Use repository files only; do not rely on prior chat state.
- For re-QA, inspect `src/frameproof/cli.py`, `tests/integration/test_dependency_missing.py`, and `docs/stages/stage-04A-fix.md` first.
- The board now points at `[Stage 4A-QA]`; do not begin Stage 4B until QA passes.
