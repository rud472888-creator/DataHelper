# Frame Proof

Frame Proof is a local CLI and desktop GUI for generating clip-review PDFs plus CSV/JSON manifests from source media without modifying the source files. The current application ships one shared processing pipeline for CLI and GUI runs: scan, probe, capture-plan, capture, PDF render, optional still export, and manifest writing all use the same core services.

## What It Handles Today

- Standard video inputs through the FFmpeg adapter flow: `.mov`, `.mp4`, `.mxf`, `.avi`
- RAW-family routing through subprocess adapter clients: `.braw`, `.r3d`, `.ari`
- PDF layouts:
  - `contact_sheet` = Layout B, the default
  - `detail` = Layout A
- Manifests:
  - CSV and JSON are written by default beside the PDF unless you override their paths
- Optional PNG still export
- GUI dependency inspection and persisted GUI settings

## Install

Frame Proof requires Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

After installation, both module and console-script entrypoints are available:

```bash
python -m frameproof --help
frameproof --help
python -m frameproof.gui --help
frameproof-gui --help
```

See [Docs/setup-guide.md](Docs/setup-guide.md) for first-run validation, smoke commands, and GUI startup guidance.

## Quick Start

Show the CLI and runtime diagnostics:

```bash
python -m frameproof --help
python -m frameproof config
python -m frameproof config --format json
```

Create the default contact-sheet PDF plus default CSV/JSON manifests:

```bash
python -m frameproof \
  --input /path/to/clip-or-folder \
  --output ./artifacts/contact-sheet.pdf \
  --layout contact_sheet \
  --middle-count 3
```

Create the detailed PDF and export PNG stills:

```bash
python -m frameproof \
  --input /path/to/clip.mp4 \
  --output ./artifacts/detail-report.pdf \
  --layout detail \
  --middle-count 0 \
  --export-stills \
  --stills-dir ./artifacts/detail-stills
```

Launch the GUI:

```bash
python -m frameproof.gui --help
QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test
python -m frameproof.gui
```

## Output Examples

For an output PDF path such as `./artifacts/contact-sheet.pdf`, Frame Proof can produce:

- `./artifacts/contact-sheet.pdf`
- `./artifacts/contact-sheet.csv`
- `./artifacts/contact-sheet.json`
- `./artifacts/detail-stills/*.png` when `--export-stills` is enabled

The CLI prints a terminal summary with batch status counts and any generated output paths:

- `status`
- `success_count`, `partial_success_count`, `probe_failed_count`, `decode_failed_count`
- `pdf_path`, `csv_path`, `json_path`
- `fatal_code`, `fatal_stage`, `fatal_reason` on batch-level fatal stops

## Dependencies

Standard-video success paths depend on external tools:

- `ffmpeg`: required for standard-video capture
- `ffprobe`: required for standard-video probe metadata
- `mediainfo`: optional metadata enrichment where available

RAW-family paths depend on operator-supplied vendor executables:

- BRAW adapter executable (this checkout includes `tools/braw_adapter`, backed by a native helper built against the locally installed Blackmagic RAW SDK 5.1)
- R3D adapter executable
- ARRI ART CMD executable

These tools are not bundled by this repository. See [Docs/dependency-guide.md](Docs/dependency-guide.md) for CLI flags, GUI path configuration, and licensing constraints.

## Config Reference

`python -m frameproof config` reports the resolved config-path convention and whether a config file exists. The example TOML at [Docs/examples/frameproof.example.toml](Docs/examples/frameproof.example.toml) shows the current settings shape and `FRAMEPROOF_CONFIG` path convention.

Important: the example TOML is a reference document, not proof that arbitrary pipeline runs already auto-load that TOML. Today, batch runs are driven by CLI flags or GUI state.

## Docs Map

- [Docs/setup-guide.md](Docs/setup-guide.md)
- [Docs/dependency-guide.md](Docs/dependency-guide.md)
- [Docs/architecture-note.md](Docs/architecture-note.md)
- [Docs/release-checklist.md](Docs/release-checklist.md)
- [Docs/reports/final/final-report.md](Docs/reports/final/final-report.md)
- [tests/manual/gui_smoke_checklist.md](tests/manual/gui_smoke_checklist.md)

## Known Limitations

- This repository does not bundle FFmpeg, FFprobe, MediaInfo, or proprietary RAW executables.
- Proprietary RAW support depends on operator-supplied tools and any required licenses or runtime libraries.
- The generated PDF is a review artifact. It is not a color-critical grading reference.
- Full GUI operator validation requires a working desktop Qt runtime; `--smoke-test` only proves startup and shutdown.
- The documented config example is a schema/reference artifact, not a proven end-to-end config-driven batch-run path.
