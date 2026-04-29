# Frame Proof Architecture

This document is the Stage 2 implementation architecture for Frame Proof v1. It defines the single shared pipeline that later stages must extend. CLI, GUI, standard-video processing, RAW processing, PDF rendering, still export, and manifest writing all reuse the same core contracts. No later stage should introduce a second pipeline or a GUI-only code path.

## Architectural Principles

- Keep one normalized domain model across all formats: `ClipInfo`, `CapturePoint`, `ReportItem`, batch summary, and settings.
- Keep adapter-specific logic behind the adapter boundary. RAW vendor SDK behavior must never leak into the shared planner, renderer, or UI layers.
- Run BRAW, R3D, and ARRIRAW processing in subprocesses. Python owns orchestration, validation, normalization, caching, rendering, manifests, and UI state only.
- Prefer file-level fault isolation. A clip failure becomes a `ReportItem` error or warning unless the batch hits a documented fatal stop condition.
- Preserve requested-versus-actual capture data through every layer so PDF, CSV, JSON, and GUI progress all report the same facts.

## Runtime Topology

```text
CLI / GUI
  -> settings + request validation
  -> scan session
  -> scanner
  -> clip_grouper
  -> adapter_resolver
  -> dependency_inspector
  -> probe_service
  -> metadata_normalizer
  -> capture_planner
  -> capture_service
  -> report_builder
  -> pdf_renderer
  -> still_exporter
  -> manifest_writer
  -> batch_result / progress events
```

RAW path:

```text
Python core
  -> raw adapter client
  -> native subprocess executable
  -> JSON stdout/stderr contract
  -> normalized response back into Python
```

## Module Responsibilities

| Module | Responsibility | Key inputs | Key outputs | Planned stage |
|---|---|---|---|---|
| `src/frameproof/core/scanner.py` | Expand input paths, recurse folders, filter supported extensions, preserve path ordering | settings input paths | file candidates | Stage 4A |
| `src/frameproof/core/clip_grouper.py` | Collapse file candidates into logical clips, especially multi-part R3D | file candidates | clip candidates | Stage 4A, Stage 4B for R3D rules |
| `src/frameproof/core/adapter_resolver.py` | Choose adapter by extension and metadata hints | clip candidate, dependency state | adapter selection | Stage 4A |
| `src/frameproof/core/dependency_inspector.py` | Detect tool paths, version visibility, missing dependencies, per-format availability | settings adapter paths | dependency report | Stage 4A, Stage 4B, Stage 4D |
| `src/frameproof/core/probe_service.py` | Run probe through the selected adapter and capture raw metadata/errors | adapter, clip candidate | raw probe payload | Stage 4A |
| `src/frameproof/core/metadata_normalizer.py` | Convert raw probe payloads into `ClipInfo` with source labels and warnings | raw probe payload | `ClipInfo` | Stage 3 |
| `src/frameproof/core/capture_planner.py` | Calculate Start/Mid/End requested positions using frame-count priority and duration fallback | `ClipInfo`, `middle_count` | capture plan | Stage 3 |
| `src/frameproof/core/capture_service.py` | Execute captures, manage temp images, record actual positions/timecode/status | adapter, capture plan | capture results | Stage 4A |
| `src/frameproof/core/timecode.py` | Parse and format timecode, drop-frame display, calculated labels, elapsed fallback | clip timing fields | display strings and warnings | Stage 3 |
| `src/frameproof/core/report_builder.py` | Assemble `ReportItem` objects and batch summary from clip + capture results | `ClipInfo`, capture results | `ReportItem` list | Stage 4A |
| `src/frameproof/rendering/pdf_renderer.py` | Render Layout B and Layout A using one report model | `ReportItem` list, settings | PDF file | Layout B Stage 4A, Layout A Stage 4C |
| `src/frameproof/rendering/still_exporter.py` | Persist optional PNG stills with sanitized file names and collision suffixes | capture results, settings | exported PNG paths | Stage 4C |
| `src/frameproof/output/manifest_writer.py` | Write CSV and JSON manifests from the same `ReportItem` data used by PDF | batch report | manifest files | Stage 4A |
| `src/frameproof/config/settings.py` | Load CLI/GUI config, validate paths/options, expose resolved runtime config | CLI args, GUI form state, config file | validated settings | Stage 3 |
| `src/frameproof/adapters/base.py` | Shared adapter protocols, status enums, request/response models | normalized inputs | adapter contracts | Stage 3 |
| `src/frameproof/adapters/ffmpeg_adapter.py` | Standard video probe/capture using FFprobe, FFmpeg, MediaInfo fallback | clip candidate | raw probe and capture payloads | Stage 4A |
| `src/frameproof/adapters/braw_adapter_client.py` | Python client for `BRAW` subprocess probe/capture | clip candidate, capture plan | raw JSON payloads | Stage 4B |
| `src/frameproof/adapters/r3d_adapter_client.py` | Python client for R3D subprocess probe/capture and logical clip awareness | logical clip candidate | raw JSON payloads | Stage 4B |
| `src/frameproof/adapters/arriraw_art_adapter_client.py` | Python client for ARRI Reference Tool based probe/capture | clip candidate | raw JSON payloads | Stage 4B |
| `src/frameproof/cli.py` | Command-line entrypoint, batch start, progress output, non-zero exit rules | CLI args | batch run | Stage 4A expands Stage 1 shell |
| `src/frameproof/gui/` | Desktop UI that drives the same batch services as CLI | settings + user actions | progress UI + batch run | Stage 4D |

## Shared Flow

### 1. Intake

- CLI or GUI builds one validated settings object.
- Scanner enumerates file candidates from selected files or folders.
- Clip grouper turns file candidates into logical clips.
- Adapter resolver assigns one adapter and one dependency state per logical clip.

### 2. Probe

- Probe service invokes the chosen adapter.
- Standard formats probe in-process through tool wrappers.
- RAW formats probe through subprocess adapter clients only.
- Metadata normalizer converts adapter payloads into `ClipInfo`.
- Probe failures become `ReportItem` seeds with `probe_failed`, `dependency_missing`, `unsupported_format`, or `metadata_incomplete`.

### 3. Capture Planning

- Capture planner receives normalized `ClipInfo`.
- It always creates Start and End slots.
- It inserts `Mid1` to `Mid3` according to `middle_count`.
- It uses `frame_count` first.
- It falls back to duration math when `frame_count` is missing or untrusted.
- It records duplicate collapse for short clips instead of deleting slots.

### 4. Capture Execution

- Capture service executes adapter captures in the requested slot order.
- Each slot preserves requested ratio, requested frame or seconds, and actual frame or seconds.
- RAW adapters return timecode or frame metadata when available.
- Standard adapter results may need calculated or elapsed fallback labels.
- Temp image paths remain internal until still export or PDF rendering consumes them.

### 5. Output

- Report builder produces one `ReportItem` per logical clip.
- PDF renderer builds Layout B by default and Layout A when the detailed-report option is selected.
- Manifest writer writes CSV and JSON from the same `ReportItem` collection.
- Still exporter is off by default and only persists PNG files when enabled.
- Batch result aggregates counts for success, partial success, probe failure, decode failure, and skipped items.

## Subprocess Isolation Rules

These rules are mandatory for BRAW, R3D, and ARRIRAW:

- Python must not import vendor SDK bindings directly.
- Adapter subprocesses communicate with Python only through documented JSON request and response envelopes.
- The client process treats non-zero exit, invalid JSON, timeout, or stderr-only failures as adapter errors and maps them into normalized status values.
- A RAW subprocess crash must fail that clip only unless the batch has zero processable files left.
- Concurrency for each RAW capture lane stays at `1` by default.
- Temporary files produced by subprocesses must be created inside an app-owned staging directory, never beside source media.

## State Ownership

| Concern | Owning layer |
|---|---|
| Tool path discovery | settings + dependency inspector |
| Supported-format routing | adapter resolver |
| Raw adapter request serialization | adapter client |
| Requested capture math | capture planner |
| Actual capture facts | adapter response + capture service |
| Timecode display label | timecode utility |
| Report status and warnings | report builder |
| PDF layout choice | validated settings |
| Manifest row generation | manifest writer |
| GUI progress row state | batch progress events derived from report state |

## Failure Model

Per-clip failures continue unless one of the fatal batch-stop rules is hit:

- output path is not writable
- PDF renderer hits a fatal error
- the user cancels
- every relevant adapter dependency is missing and zero files are processable

All other failures must stay attached to clip or capture records. The renderer and manifest writer must expose:

- `success`
- `partial_success`
- `probe_failed`
- `decode_failed`
- `unsupported_format`
- `dependency_missing`
- `metadata_incomplete`
- `skipped_duplicate`

## Concurrency Defaults

| Work type | Default concurrency | Notes |
|---|---:|---|
| scanner | 1 | preserve deterministic file ordering |
| standard probe | 4 | bounded by external tool cost |
| standard capture | 2 | avoid overloading decode and disk IO |
| BRAW capture | 1 | subprocess isolation + GPU/SDK stability |
| R3D capture | 1 | subprocess isolation + multi-part clip stability |
| ARRIRAW capture | 1 | ART CMD cost and staging overhead |
| PDF render | 1 | single ordered document build |

## Output Contracts

- Layout B is the default PDF mode and must be complete before Layout A work begins.
- Layout A is a renderer variant over the same `ReportItem` model, not a second report pipeline.
- CSV and JSON manifests must include the same requested and actual capture facts shown in the PDF.
- PNG export changes persistence policy only. It must not change capture selection or image generation logic.
- Shared-path privacy is controlled by report settings, not by a second report builder.

## Requirement Map

| Requirement | Module or subsystem | Delivery stage |
|---|---|---|
| Standard video support via FFprobe, FFmpeg, MediaInfo fallback | `ffmpeg_adapter.py`, `probe_service.py`, `capture_service.py` | Stage 4A |
| BRAW support | `braw_adapter_client.py` + native `BRAW` executable | Stage 4B |
| R3D support with multi-part grouping | `clip_grouper.py`, `r3d_adapter_client.py` | Stage 4B |
| ARRIRAW support through ART CMD | `arriraw_art_adapter_client.py` | Stage 4B |
| Normalized schemas | `metadata_normalizer.py`, `adapters/base.py`, `core/models.py` | Stage 3 |
| Capture planner rules | `capture_planner.py` | Stage 3 |
| Timecode priority and display rules | `timecode.py` | Stage 3 |
| Layout B PDF | `pdf_renderer.py` | Stage 4A |
| Layout A PDF | `pdf_renderer.py` detailed variant | Stage 4C |
| CSV/JSON manifest | `manifest_writer.py` | Stage 4A |
| PNG still export | `still_exporter.py` | Stage 4C |
| GUI and dependency screen | `gui/` + dependency inspector | Stage 4D |
| Failure section and partial-clip reporting | `report_builder.py`, `pdf_renderer.py`, `manifest_writer.py` | Stage 4C |
| File safety and path sanitization | `settings.py`, `still_exporter.py`, `manifest_writer.py` | Stage 3 foundation + Stage 4C |
| Packaging and dependency setup | release workflow docs + installer work | Stage 7 |

## Stage 3 Entry Guidance

Stage 3 should implement only the reusable foundation layer:

- typed schemas and enums
- settings/config model
- adapter base contracts
- capture planner
- timecode utility
- unit tests for the above

Stage 3 must not implement FFmpeg capture, PDF rendering, GUI screens, or RAW subprocess execution beyond interface scaffolding required by the base contracts.
