# Release Checklist

This is the Stage 7 release-wrap checklist for the current repository state. It records what is complete in the repo, what was validated on this host, and what remains conditional on external tooling or licensing.

## Release State

- repository documentation wrap-up: complete
- release-wrap Dev handoff: complete
- baseline validation commands on this host: complete
- standard-video success-path smoke on this host: blocked by missing `ffmpeg` and `ffprobe`
- proprietary RAW success-path smoke on this host: blocked by missing vendor executables and licensing evidence
- release readiness: not fully verified on this host

## Packaging And Distribution

- complete: Python package install path is documented for local source installs
- complete: console-script and module entrypoints are documented
- open: packaged macOS/Windows installer strategy is still backlog
- open: FFmpeg/FFprobe bundling decision still requires license review
- open: proprietary RAW redistribution rights are unresolved and must not be implied as bundled

## Dependency Checklist

### Standard Dependencies

- complete: Python runtime requirement documented
- complete: `ffmpeg` requirement documented for standard-video capture
- complete: `ffprobe` requirement documented for standard-video probe metadata
- complete: `mediainfo` documented as optional metadata enrichment
- complete: GUI dependency dialog behavior documented

### RAW Dependencies

- complete: BRAW adapter path guidance documented
- complete: R3D adapter path guidance documented
- complete: ARRI ART CMD path guidance documented
- complete: user-supplied runtime-library/license expectation documented
- blocked on host: no live BRAW/R3D/ARRI executable validation was possible in this session

## Security And File Safety

- complete: release docs state that source media remains read-only
- complete: release docs state that default staging is app-owned and outside the source tree unless overridden
- complete: known limitations and troubleshooting sections avoid claiming network upload or source-side writes
- carried forward from prior implementation/testing: output filename sanitization, manifest/write cleanup, and still-export path hardening remain part of the validated Stage 6 baseline

## Smoke Commands

### Commands validated on this host

```bash
python -m frameproof --help
python -m frameproof config
python -m frameproof config --format json
python -m pytest
ruff check .
mypy src
python -m frameproof.gui --help
QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test
```

### Standard-video success-path smoke command

Run this on a host where `ffmpeg` and `ffprobe` are installed and a real local sample clip exists:

```bash
python -m frameproof \
  --input /path/to/sample.mp4 \
  --output ./artifacts/smoke/contact-sheet.pdf \
  --layout contact_sheet \
  --middle-count 3
```

Expected evidence:

- PDF exists
- default CSV and JSON manifests exist beside the PDF
- CLI summary reports a truthful success or partial-success batch status

### Dependency-diagnostic smoke command

```bash
python -m frameproof \
  --input /path/to/sample.mp4 \
  --output ./artifacts/smoke/dependency-missing.pdf \
  --ffmpeg-path /missing/ffmpeg \
  --ffprobe-path /missing/ffprobe \
  --mediainfo-path /missing/mediainfo
```

Expected evidence:

- non-zero exit
- explicit failure text
- no leftover PDF/CSV/JSON artifacts

### GUI smoke commands

```bash
python -m frameproof.gui --help
QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test
```

For full interactive validation, also use:

- [tests/manual/gui_smoke_checklist.md](tests/manual/gui_smoke_checklist.md)

## Regression And Verification Baseline

- complete on this host: automated tests via `python -m pytest`
- complete on this host: lint via `ruff check .`
- complete on this host: typing via `mypy src`
- complete in repository docs: CLI/GUI/config/dependency surfaces now match the implemented code paths
- blocked on host: ffmpeg-backed happy-path artifact generation
- blocked on host: vendor RAW executable smoke

## Known External Risks

- proprietary RAW redistribution terms may still block bundling
- preview color can differ from grading-reference color
- full GUI operator validation still depends on a working desktop Qt runtime
- packaged executable discovery may differ by OS from source-checkout behavior

## Exit Decision

Stage 7 Dev implementation is complete for documentation and handoff scope. QA should verify the updated release docs, baseline validation evidence, and the honesty of the unresolved environment/tooling limits in a fresh session.
