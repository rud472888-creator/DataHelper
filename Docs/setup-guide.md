# Setup Guide

This guide is for a fresh developer or operator starting from a clean checkout.

## Requirements

- Python 3.11 or newer
- A shell that can create and activate a virtual environment
- For standard-video success-path runs: `ffmpeg` and `ffprobe`
- For GUI use: a working PySide6/Qt runtime on the local host

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

If your shell does not automatically expose repo-local tools on `PATH`, use:

```bash
.venv/bin/ruff check .
.venv/bin/mypy src
```

## First Commands To Run

```bash
python -m frameproof --help
python -m frameproof config
python -m frameproof config --format json
python -m frameproof.gui --help
QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test
```

What these commands prove:

- `--help` confirms the package entrypoint is importable.
- `config` confirms the runtime diagnostics surface works and shows the resolved config path.
- GUI `--help` confirms the GUI entrypoint is importable.
- GUI `--smoke-test` confirms the app can create, show, and close a window without starting a batch.

## CLI Workflow

Use the CLI when you want a scripted batch run.

Basic contact-sheet run:

```bash
python -m frameproof \
  --input /path/to/media \
  --output ./artifacts/contact-sheet.pdf \
  --layout contact_sheet \
  --middle-count 3
```

Detailed report with still export:

```bash
python -m frameproof \
  --input /path/to/media \
  --output ./artifacts/detail.pdf \
  --layout detail \
  --middle-count 0 \
  --export-stills \
  --stills-dir ./artifacts/stills
```

Notes:

- `--output` is required for pipeline runs.
- CSV and JSON manifests are enabled by default.
- If `--csv` or `--json` is omitted, Frame Proof uses the PDF stem.
- `--recursive` is on by default for directory inputs.
- `--middle-count` accepts `0` through `3`.

## GUI Workflow

Use the GUI when you want dependency inspection, persisted settings, and interactive run control.

```bash
python -m frameproof.gui
```

Or after installation:

```bash
frameproof-gui
```

The GUI stores settings in an INI file. You can override the path:

```bash
python -m frameproof.gui --settings-file /path/to/frameproof-gui.ini
```

The default settings location is chosen from the Qt app-config location, then `~/.frameproof/frameproof-gui.ini`, then a temp directory fallback.

## Smoke Commands

### Always-available baseline

These are the baseline smoke checks that do not require a sample media toolchain:

```bash
python -m frameproof --help
python -m frameproof config
python -m frameproof config --format json
python -m frameproof.gui --help
QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test
```

### Standard-video success path

Run this only on a host where `ffmpeg` and `ffprobe` are installed and you have a real local `.mov`, `.mp4`, `.mxf`, or `.avi` clip:

```bash
python -m frameproof \
  --input /path/to/sample.mp4 \
  --output ./artifacts/smoke/contact-sheet.pdf \
  --layout contact_sheet \
  --middle-count 3
```

Then confirm:

- the PDF exists
- the default CSV and JSON manifests exist beside it
- the CLI prints `status: success` or `status: partial_success` truthfully for the batch

### Dependency-diagnostic smoke

If standard-video tools are missing, you can still verify the failure path stays explicit:

```bash
python -m frameproof \
  --input /path/to/standard-video.mp4 \
  --output ./artifacts/smoke/dependency-missing.pdf \
  --ffmpeg-path /missing/ffmpeg \
  --ffprobe-path /missing/ffprobe \
  --mediainfo-path /missing/mediainfo
```

Expected behavior:

- non-zero exit
- explicit `dependency_missing`/fatal output
- no PDF, CSV, or JSON artifact left behind

## Test And Static Analysis

Run the repository validation set:

```bash
python -m pytest
ruff check .
mypy src
```

## Config Diagnostics

Frame Proof currently exposes config-path diagnostics rather than a proven config-driven batch-run loader.

Useful commands:

```bash
python -m frameproof config
python -m frameproof config --format json
FRAMEPROOF_CONFIG=/path/to/config.toml python -m frameproof config --format json
```

Reference settings shape:

- [Docs/examples/frameproof.example.toml](Docs/examples/frameproof.example.toml)

## Troubleshooting

- If `python -m frameproof --help` fails, reinstall with `python -m pip install -e '.[dev]'`.
- If `ruff` or `mypy` is not found, use `.venv/bin/ruff` and `.venv/bin/mypy`.
- If GUI `--smoke-test` fails, verify the local Qt runtime and try `QT_QPA_PLATFORM=offscreen`.
- If standard-video pipeline runs fail immediately, check `ffmpeg` and `ffprobe` availability first.
- If RAW inputs show dependency-missing states, configure the vendor executable paths in the CLI flags or GUI `Dependencies` dialog.
