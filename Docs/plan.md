# Global Plan

## Product Goal Summary

Frame Proof PDF Generator is a local desktop and CLI tool that scans user-selected source files or folders, extracts normalized clip metadata plus representative start/middle/end frames, and generates PDF contact reports with CSV/JSON manifests for review, handoff, and delivery evidence.

The v1 product must support standard video formats through FFmpeg/FFprobe with MediaInfo fallback, and must also support RAW workflows for BRAW, R3D, and ARRIRAW through format-specific adapters. The default output is Layout B contact sheet PDF. Layout A detailed per-clip PDF is optional. PNG still export is optional and off by default.

## V1 Scope

### In Scope

- Local-only execution through CLI first, with desktop GUI delivered in a later v1 milestone.
- Scanning files, folders, and subfolders.
- Logical clip grouping, including multipart R3D grouping.
- Standard formats: MOV, MP4, MXF, AVI via FFprobe/FFmpeg with MediaInfo fallback.
- Required RAW formats: BRAW, R3D, ARRIRAW.
- Adapter-based probe and capture flow with normalized output schema.
- Capture planning for Start, Mid1-Mid3, and End using the specified rounding and fallback rules.
- Timecode priority handling: native per-frame timecode, calculated clip timecode, container metadata, then elapsed fallback.
- Layout B contact sheet PDF as the default renderer.
- Layout A detailed PDF as an optional mode.
- CSV and JSON manifests.
- Per-file failure handling with batch continuation except for fatal conditions defined in the tech spec.
- Optional PNG export, default OFF.
- Failure and warning reporting in PDF/log outputs.

### Out of Scope

- Color-critical output or grading reference generation.
- NLE, DAM, cloud, or SaaS integrations.
- OCR, subtitle extraction, waveform analysis, or scene-change frame selection.
- Checksum backup reporting.
- Image sequence support.
- ARRIRAW HDE support unless separately approved for a later milestone.

## Architecture And Module Plan

### Delivery Principle

Use a normalized core pipeline with format-specific adapters behind a stable contract:

```text
probe(input_path) -> ClipInfo
capture(input_path, CapturePlan, CaptureProfile) -> CaptureResult[]
```

RAW adapters must run in subprocess isolation. Standard video stays in the Python process through FFmpeg/FFprobe tooling.

### Planned Modules

- `app/core/scanner.py`: source discovery, recursion, extension filtering.
- `app/core/clip_grouper.py`: logical clip grouping, especially multipart R3D handling.
- `app/core/adapter_resolver.py`: select adapter by extension and metadata context.
- `app/core/probe_service.py`: execute probes and collect source metadata.
- `app/core/capture_planner.py`: compute requested capture slots and duplicate-collapse warnings.
- `app/core/capture_service.py`: run capture requests and manage staging assets.
- `app/core/metadata_normalizer.py`: convert adapter-specific payloads into shared schema.
- `app/core/timecode.py`: apply priority rules, calculated timecode, drop-frame handling, and fallback labels.
- `app/core/report_models.py`: canonical `ClipInfo`, `CapturePoint`, and `ReportItem` structures.
- `app/render/pdf_renderer.py`: shared PDF entrypoint.
- `app/render/layout_b_renderer.py`: default contact sheet layout.
- `app/render/layout_a_renderer.py`: optional detailed per-clip layout.
- `app/output/manifest_writer.py`: CSV and JSON exports.
- `app/output/still_exporter.py`: optional PNG persistence and naming rules.
- `app/config/settings.py`: CLI/GUI config loading, validation, tool-path resolution.
- `app/cli/main.py`: user-facing CLI entrypoint.
- `app/gui/`: PySide6 GUI, added after CLI pipeline stabilizes.
- `app/adapters/ffmpeg_adapter.py`: standard-format probe/capture path.
- `app/adapters/mediainfo_fallback.py`: standard-format metadata fallback.
- `app/adapters/braw_adapter_client.py`: subprocess client for BRAW native tool.
- `app/adapters/r3d_adapter_client.py`: subprocess client for R3D native tool.
- `app/adapters/arriraw_art_adapter_client.py`: subprocess client for ARRI Reference Tool CMD.
- `native/`: vendor-specific native adapter binaries or wrappers delivered in milestone order.

### Data Contract Priorities

- Normalize every adapter response into the tech spec schema before rendering or manifest writing.
- Preserve requested capture intent and actual capture result separately.
- Preserve adapter name, status, warnings, and errors per clip and per capture.
- Keep PDF and manifest outputs derived from the same `ReportItem` data so QA can compare them directly.

## Staged Delivery Breakdown

### Stage 00 Planning Completion

Stage 00 plan work is completed by this document set. No implementation or QA claim is made here. The next legal subphase after this plan run is `Docs/stages/stage-00-implement.md`.

### Milestone M1 - Core Standard Pipeline

Goal: prove the end-to-end architecture on standard video before RAW integration.

Deliverables:

- Python project skeleton and core modules.
- Scanner, clip grouping baseline, adapter resolver.
- FFprobe/FFmpeg standard adapter with MediaInfo fallback.
- Normalized schema and capture planner.
- Timecode handling for standard formats and fallback labeling.
- Layout B PDF renderer.
- CSV and JSON manifest generation.
- CLI entrypoint and config loading.
- Per-file failure continuation behavior for standard formats.

Exit expectation:

- Standard MOV/MP4/MXF/AVI clips can be scanned, probed, captured, rendered, and logged through one pipeline.

### Milestone M2 - RAW Adapter Integration

Goal: attach required RAW support without changing the normalized contract.

Deliverables:

- BRAW subprocess adapter client and native adapter contract.
- R3D subprocess adapter client with multipart grouping integration.
- ARRIRAW subprocess adapter client through ARRI Reference Tool CMD.
- Dependency detection and degraded-mode handling when some adapters are unavailable.
- RAW-specific timecode and metadata normalization.
- RAW sample validation path for probe, capture, and report inclusion.

Exit expectation:

- BRAW, R3D, and ARRIRAW all work through the same `ReportItem` output model and batch jobs continue on per-file failures.

### Milestone M3 - Layout A And GUI

Goal: add optional output and operator usability without destabilizing the core pipeline.

Deliverables:

- Layout A detailed per-clip renderer using existing report data.
- Optional PNG export flow with sanitized filenames and collision handling.
- PySide6 GUI with source/output selection, layout choice, middle count, export toggles, and dependency status.
- Progress table and failure presentation tied to existing core statuses.
- Settings persistence.

Exit expectation:

- GUI is a thin shell around the same CLI/core pipeline. Layout B remains default; Layout A and PNG export remain optional.

### Milestone M4 - Packaging And QA

Goal: harden the product for release-quality local use.

Deliverables:

- macOS and Windows packaging strategy.
- External dependency path setup and validation UX.
- Regression fixture matrix aligned to the tech spec.
- Visual PDF QA and manifest comparison checks.
- Performance profiling and concurrency tuning.
- Release-readiness review against section 21.3 acceptance criteria.

Exit expectation:

- v1 release candidate is verified against all required format, layout, and failure-handling gates.

## Recommended Implementation Order And Dependencies

1. Establish package layout, report schema, capture planner, and shared status enums first.
2. Implement the standard-video pipeline next: scanner, resolver, FFprobe/FFmpeg adapter, MediaInfo fallback, timecode handling, manifest writing, and Layout B rendering.
3. Add CLI configuration and batch orchestration once the standard path can generate one full report.
4. Integrate RAW adapters one at a time behind the same JSON contract: BRAW first, R3D second, ARRIRAW third.
5. Add dependency detection and degraded-mode behavior before GUI work so missing tools do not block standard formats.
6. Add Layout A as a renderer variant over existing `ReportItem` data.
7. Add optional PNG export by changing persistence policy, not capture semantics.
8. Add the GUI after the CLI pipeline is stable and testable.
9. Finish packaging, fixture expansion, and release QA last.

Key dependency notes:

- Layout renderers depend on normalized `ReportItem` stability.
- RAW adapters depend on the finalized probe/capture JSON contract.
- GUI depends on stable settings, orchestration, and status reporting.
- Packaging depends on confirmed external dependency path handling and licensing constraints.

## Test Strategy And Acceptance Gates

### Stage Gates

- Plan gate: durable planning artifacts written, board updated, next legal subphase set to implement.
- Implement gate: code exists for the milestone scope, tests added where practical, and a dev handoff records exactly what was built.
- QA gate: only a QA worker can mark PASS or FAIL. No stage advances on dev assertion alone.
- Fix gate: only scope admitted by the latest failing QA report may be changed.

### Core Verification Tracks

- Unit and component tests for capture planning, rounding, duplicate-collapse warnings, timecode formatting, filename sanitization, and schema normalization.
- Integration tests for standard-format probe/capture/manifest/PDF flow.
- Adapter contract tests for RAW subprocess request and response handling.
- Golden or structural PDF checks for Layout B and Layout A output stability.
- Manifest-to-PDF consistency checks so actual capture points and statuses align.

### Acceptance Gates Derived From Tech Spec Section 21.3

- Standard support gate: MOV, MP4, MXF, and AVI sample sets succeed through probe, capture, PDF, and manifest generation.
- RAW support gate: BRAW, R3D, and ARRIRAW each pass at least three sample clips through probe, capture, and PDF generation.
- Capture-shape gate: `middle_count` values 0, 1, 2, and 3 generate stable layouts without breakage.
- Layout-default gate: Layout B is the default export path.
- Layout-option gate: selecting detailed mode produces Layout A output.
- PNG-default gate: PNG export is OFF by default.
- PNG-option gate: enabling PNG export writes sanitized stills to the requested directory.
- Timecode-fallback gate: missing timecode is labeled as `N/A` or elapsed fallback, and calculated values are clearly marked.
- Batch-resilience gate: one file failure does not stop remaining files unless a fatal condition from section 17.3 is hit.
- Auditability gate: PDF and manifests record actual capture points, statuses, warnings, and adapter names.

### Fatal Conditions To Preserve

- Output path is not writable.
- PDF renderer hits a fatal error.
- User cancels the run.
- No processable files remain because all relevant dependencies are missing.

## Key Risks And Mitigations

- RAW SDK redistribution limits may block bundled delivery.
  Mitigation: treat vendor SDKs and ARRI tools as externally installed dependencies with configurable paths.

- RAW preview color may be mistaken for color-critical output.
  Mitigation: keep preview-only labeling in the PDF footer and avoid claiming grading accuracy anywhere in the UI.

- Last-frame seeking can fail on some codecs or containers.
  Mitigation: prefer frame-count indexing where reliable and use the spec epsilon fallback for duration-based end capture.

- Multipart R3D grouping can produce duplicate or missing logical clips.
  Mitigation: isolate grouping logic early and validate against multipart fixture coverage before broader RAW rollout.

- ARRIRAW processing may be slow for large batches.
  Mitigation: keep ARRIRAW concurrency at 1, expose progress, and leave room for cache introduction without changing the adapter contract.

- Incomplete timecode metadata can create misleading report output.
  Mitigation: centralize timecode-source labeling and never collapse calculated or elapsed fallback into native timecode presentation.

- RAW SDK or GPU crashes could terminate the whole app.
  Mitigation: keep RAW adapters in subprocess isolation and treat adapter crashes as per-file failures whenever possible.

## Repo-Specific Assumptions And Open Decisions

### Current Repo Assumptions

- The repository currently contains delivery-orchestration docs and scripts, but no application implementation baseline yet.
- Stage 00 implement work must create the initial project structure rather than extend existing product code.
- Repository markdown files are the durable workflow memory, so each future stage must keep `Docs/` and existing `docs/` mirrors synchronized.

### Open Decisions That Shape Implementation

- Final Python package root and naming convention are not yet established; Stage 00 implement should choose one and use it consistently.
- Test fixture storage location is not yet defined; implement work should create a stable convention for lightweight fixtures and documented external sample dependencies.
- Packaging format for macOS and Windows is deferred to M4, but path-resolution strategy for external tools should be designed early.
- ARRIRAW HDE remains outside v1 unless a later approved plan expands the scope.

### Non-Blocking Questions For The Next Worker

- What minimal fixture set can be committed now versus documented as externally supplied due to proprietary sample restrictions?
- Should the first implementation pass include CLI-only packaging scaffolding, or defer all packaging setup until M4?
- Which PDF font strategy will satisfy Korean and ASCII text needs without complicating early milestone delivery?

## Stage 00 Outcome

Stage 00 planning is complete once this file and the paired board/report artifacts are written. The next legal subphase is a fresh dev-lane implementation run using `Docs/stages/stage-00-implement.md`, constrained by this plan and the Stage 00 handoff.
