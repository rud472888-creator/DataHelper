# Stage 04C Implement

- lane: dev
- stage: stage-04C
- subphase: implement
- status: complete
- scope_boundary: layout-a-detail-renderer-and-png-still-export-parity
- next_recommended_prompt: `[Stage 4C-QA]`

## Delivered Scope

- Preserved `Layout B` as the default PDF mode and kept the shared report pipeline intact.
- Hardened exported still naming and path safety for separators, colon, drop-frame semicolon, fallback names, collisions, and long clip-derived names.
- Expanded `Layout A` capture cards to show requested frame/time, actual frame/time, actual timecode, and per-capture notes from warnings or errors.
- Improved the PDF failed/partial section to include adapter name, clip status, capture issue labels, and capture-level warning/error detail.
- Preserved manifest parity by keeping CSV and JSON capture facts aligned with the finalized `ReportItem` collection used by PDF output.
- Added regression coverage for still-export safety, manifest parity with still export off, and detailed PDF capture diagnostics.

## Changed Files And Reasons

- `src/frameproof/output/still_exporter.py` hardens sanitized component generation, including sanitized fallbacks.
- `src/frameproof/render/pdf_renderer.py` improves Layout A capture detail presentation, capture issue visibility, and failed/partial summaries.
- `tests/unit/output/test_still_exporter.py` locks filename safety and exported directory shape.
- `tests/unit/output/test_manifest_writer.py` locks partial manifest parity when no exported stills exist.
- `tests/unit/render/test_pdf_renderer.py` locks detailed PDF capture facts plus capture-level warnings/errors.
- `tests/integration/test_cli_standard_pipeline.py` locks default no-stills image-path behavior in CSV and JSON outputs.

## Implementation Decisions

- Reused the existing Stage 4A/4B pipeline instead of adding a renderer-only or manifest-only side path.
- Kept still-export image persistence post-capture and adapter-agnostic.
- Kept manifest `image_path` mapped to exported paths only so default runs do not expose staging paths.
- Preferred making failed/partial summaries more truthful rather than broadening clip status vocabulary.

## Validation Results

- `python -m frameproof --help` -> PASS
- `python -m pytest` -> PASS (`75 passed, 2 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- FFmpeg smoke runs -> BLOCKED (`ffmpeg` and `ffprobe` unavailable in this environment)

## Generated Artifacts

- No persistent runtime artifacts were checked into the repository during this run.
- No FFmpeg-backed smoke export artifacts were generated because FFmpeg is unavailable here.

## Blockers And Known Gaps

- No functional Stage 4C Dev blocker remains.
- Optional FFmpeg smoke verification remains environment-blocked until `ffmpeg` and `ffprobe` are installed.
- Fresh QA is required before any subsequent stage work.

## Fresh Session Notes

- Run `[Stage 4C-QA]` next.
- QA should verify still-export safety, detailed PDF capture facts, failed/partial summary truthfulness, and default no-stills manifest behavior from repository files and the recorded validation outputs.
