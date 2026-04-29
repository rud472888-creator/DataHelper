# Dependency Guide

Frame Proof separates standard-video tooling from proprietary RAW tooling. The repository does not bundle any of these executables.

## Standard Video

### FFmpeg

- Purpose: frame capture for standard-video formats
- CLI override: `--ffmpeg-path`
- GUI setting: `FFmpeg`
- Status expectation: required for standard-video capture

### FFprobe

- Purpose: probe metadata for standard-video formats
- CLI override: `--ffprobe-path`
- GUI setting: `FFprobe`
- Status expectation: required for standard-video probe metadata

### MediaInfo

- Purpose: optional metadata enrichment when FFprobe metadata is incomplete
- CLI override: `--mediainfo-path`
- GUI setting: `MediaInfo`
- Status expectation: optional

Example with explicit paths:

```bash
python -m frameproof \
  --input /path/to/clip.mp4 \
  --output ./artifacts/report.pdf \
  --ffmpeg-path /usr/local/bin/ffmpeg \
  --ffprobe-path /usr/local/bin/ffprobe \
  --mediainfo-path /usr/local/bin/mediainfo
```

## RAW Tooling

RAW families are routed through subprocess adapter clients. Python orchestrates the workflow, but the actual RAW probe/capture path depends on operator-supplied vendor executables.

### BRAW

- CLI override: `--braw-adapter-path`
- GUI setting: `BRAW Adapter`
- Applies to: `.braw`
- Native SDK-backed adapter in this checkout: `tools/braw_adapter`
- Native helper built from the installed SDK headers/runtime: `tools/braw_native_helper`
- Required local SDK/runtime path: `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries/BlackmagicRawAPI.framework`
- Optional environment override for the SDK libraries directory: `BLACKMAGIC_RAW_SDK_LIBRARIES`
- Optional environment override for the native helper path: `FRAMEPROOF_BRAW_NATIVE_HELPER`
- Packaging note: the repo builds/uses a local helper against the installed SDK, but does not vendor Blackmagic proprietary framework assets. Redistribution of SDK/runtime assets still requires separate license review.

### R3D

- CLI override: `--r3d-adapter-path`
- GUI setting: `R3D Adapter`
- Applies to: `.r3d`
- Native SDK-backed adapter in this checkout: `tools/r3d_adapter`
- Native helper built from the installed SDK headers/runtime: `tools/r3d_native_helper`
- Required local SDK/runtime path: `~/Applications/REDSDK/9.2.0/R3DSDKv9_2_0/Redistributable/mac/REDR3D.dylib`
- Optional environment override for the SDK libraries directory: `RED_R3D_SDK_LIBRARIES`
- Optional environment override for the native helper path: `FRAMEPROOF_R3D_NATIVE_HELPER`
- Packaging note: the repo builds/uses a local helper against the installed SDK, but does not vendor RED proprietary SDK assets. Redistribution of SDK/runtime assets still requires separate license review.

### ARRI ART CMD

- CLI override: `--arri-art-cmd-path`
- GUI setting: `ARRI ART CMD`
- Applies to: `.ari`
- Local wrapper in this checkout: `tools/art-cmd`
- Installed local ART CMD path: `~/Applications/ARRIReferenceToolCMD/1.0.0/bin/art-cmd`
- Optional environment override for the ART CMD executable: `FRAMEPROOF_ARRI_ART_CMD`
- Packaging note: ART CMD installation, licensing, and runtime behavior remain external operator responsibilities

Example with vendor paths:

```bash
python -m frameproof \
  --input /path/to/clip.braw \
  --output ./artifacts/raw-report.pdf \
  --braw-adapter-path /opt/frameproof/bin/braw_adapter
```

```bash
python -m frameproof \
  --input /path/to/clip.r3d \
  --output ./artifacts/raw-report.pdf \
  --r3d-adapter-path tools/r3d_adapter
```

```bash
python -m frameproof \
  --input /path/to/clip.ari \
  --output ./artifacts/raw-report.pdf \
  --arri-art-cmd-path tools/art-cmd
```

## GUI Dependency Screen

The GUI `Dependencies` dialog reports:

- configured path
- applies-to scope
- required state label
- resolved executable path

Current dependency-state labels:

- `available`
- `configured path missing`
- `not configured`
- `runtime startup failure`

The GUI stores these paths in its settings INI file. Saving the dialog updates future GUI launches; it does not bundle or install the tools for you.

## Config Reference And Path Conventions

The CLI runtime diagnostics use:

- environment variable: `FRAMEPROOF_CONFIG`
- default path: `~/.config/frameproof/config.toml`

Useful commands:

```bash
python -m frameproof config
python -m frameproof config --format json
FRAMEPROOF_CONFIG=/path/to/config.toml python -m frameproof config --format json
```

Reference example:

- [Docs/examples/frameproof.example.toml](Docs/examples/frameproof.example.toml)

Important: this is a documentation/reference path today. The repository does not yet prove that arbitrary batch runs automatically ingest that TOML file.

## Licensing And Distribution Limits

- FFmpeg and FFprobe bundling decisions require a packaging and license review outside the current repository evidence.
- Proprietary RAW executables and SDK assets must not be described as bundled unless redistribution rights are explicitly cleared.
- If redistribution remains restricted, the release path must continue to rely on user-configurable executable paths.

## Troubleshooting

- If `ffmpeg` or `ffprobe` cannot be resolved, standard-video clips will fail before a successful report is generated.
- If `mediainfo` is absent, standard-video runs can still succeed, but metadata enrichment may be reduced.
- If a RAW executable is not configured, only the affected RAW family should degrade to dependency-missing; other processable clips in the batch should continue.
- If a configured executable exists but fails its startup check, the GUI should show `runtime startup failure`.
