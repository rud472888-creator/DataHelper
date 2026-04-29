# Stage 04A Fix

- lane: dev
- subphase: fix
- status: complete
- source_qa_report: `docs/reports/qa/stage-04A-qa-report.md`
- next_recommended_prompt: `[Stage 4A-QA]`

## Fix Scope

- Fix only the Stage 4A QA-reported fatal dependency-missing CLI summary defect.
- Keep Stage 4A limited to the existing standard-video CLI pipeline. No RAW adapter work, GUI work, or broader output changes are allowed here.

## QA Issues And Fixes

1. The fatal standard-video dependency-missing path now exposes the missing dependency state directly in CLI output. `src/frameproof/cli.py` now prints a `dependency_missing:` diagnostic line for each affected clip, including the clip name, `status=dependency_missing`, `adapter=ffmpeg`, `required_tools=ffmpeg,ffprobe`, and the normalized `dependency_state` already produced by the probe layer.
2. Regression coverage now locks the user-facing dependency diagnosis. `tests/integration/test_dependency_missing.py` was tightened so the Stage 4A dependency-missing smoke path must keep surfacing `dependency_missing`, `ffmpeg`, `ffprobe`, and `configured_missing` while still exiting `2` and suppressing PDF/CSV/JSON output.

## Changed Files

- `src/frameproof/cli.py`
- `tests/integration/test_dependency_missing.py`
- `docs/stages/stage-04A-fix.md`
- `docs/reports/dev/stage-04A-handoff.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`

## Validation Results

- `python -m frameproof --help` -> PASS
- `python -m frameproof --input <tmp>/clip.mp4 --middle-count 1 --layout contact_sheet --output <tmp>/report.pdf --ffmpeg-path /missing/ffmpeg --ffprobe-path /missing/ffprobe --mediainfo-path /missing/mediainfo` -> PASS for expected fatal behavior (`EXIT:2`, explicit `dependency_missing` line printed, PDF/CSV/JSON absent)
- `python -m pytest` -> PASS (`49 passed, 1 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `command -v ffmpeg; command -v ffprobe` -> no output, exit code `1`

## Re-QA Instruction

- Run a fresh Stage 4A QA session with `[Stage 4A-QA]`.
- Recheck the fatal dependency-missing CLI path and confirm the user-facing output now includes `dependency_missing`, `adapter=ffmpeg`, `required_tools=ffmpeg,ffprobe`, and the dependency state.
- Do not begin Stage 4B until the new Stage 4A QA run returns PASS.
