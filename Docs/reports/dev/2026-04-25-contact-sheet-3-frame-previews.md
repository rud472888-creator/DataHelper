# Dev Report: Contact Sheet 3-Frame Previews

- status: succeeded
- workflow_id: datahelper-contact-sheet-3-frame-previews-20260425
- completed_at: 2026-04-25 22:05 KST

## Summary
Implemented/verified the contact sheet renderer so each clip card displays three preview wells: START, MIDDLE, END. The preview images are drawn with contain/aspect-fit sizing using the existing `_fit_image` and compressed `_pdf_image_reader` path, preserving the prior PDF-size guard.

## Files Changed
- `src/frameproof/render/pdf_renderer.py`
  - Contact sheet clip block now renders a 3-column preview triptych.
  - Added/kept middle-selection helper that picks a middle capture nearest requested ratio 0.5, preferring middle-labeled captures and preserving Start/End detection.
  - Maintains folder-level source summary via `_input_summary` / `_source_root`.
  - Keeps preview embedding downsampled/compressed to avoid huge PDFs.
- `tests/unit/render/test_pdf_renderer.py`
  - Added/kept coverage for START/MIDDLE/END labels.
  - Added/kept coverage for middle preview selection under `--middle-count` > 1.
  - Added/kept source summary folder-level behavior and aspect-fit sizing checks.
- `docs/reports/dev/2026-04-25-contact-sheet-3-frame-previews.md`
- `/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-25/devman/2026-04-25-datahelper-contact-sheet-3-frame-previews.md`

## Artifacts Generated
Under `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/`:
- `contact-sheet-3-frame-preview.pdf` — 200,507 bytes
- `contact-sheet-3-frame-preview.csv` — 3,075 bytes
- `contact-sheet-3-frame-preview.json` — 17,487 bytes
- `contact-sheet-3-frame-preview-page-1.png` — 346,667 bytes

No `.braw` source media files were copied into artifacts.

## Verification Results
- Python compile for changed renderer module:
  - Command: `python -m compileall src/frameproof/render/pdf_renderer.py`
  - Result: passed
- Renderer unit tests and native BRAW adapter integration test:
  - Command: `python -m pytest tests/unit/render/test_pdf_renderer.py tests/integration/test_native_braw_adapter.py -q`
  - Result: `11 passed in 1.81s`
- Real-media CLI smoke with 3 valid `.braw` files excluding `._*.braw`:
  - Input files:
    - `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151705_C019.braw`
    - `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151704_C018.braw`
    - `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151700_C017.braw`
  - Command used `--layout contact_sheet --middle-count 2 --braw-adapter-path tools/braw_adapter`
  - Result:
    - `status: success`
    - `total_clips: 3`
    - `success_count: 3`
    - `partial_success_count: 0`
    - `probe_failed_count: 0`
    - `decode_failed_count: 0`
    - `skipped_count: 0`
- Output non-empty checks:
  - PDF: 200,507 bytes
  - CSV: 3,075 bytes
  - JSON: 17,487 bytes
  - PNG preview: 346,667 bytes
- PDF text check:
  - `START`: present
  - `MIDDLE`: present
  - `END`: present
  - `.../001_video/260215/R#1`: present
  - `Middle preview: 1 of 2`: present
- Source-media safety check:
  - `*.braw` files under QA artifact directory: 0

## Visual Notes
First-page PNG preview confirms:
- Three labeled wells appear horizontally: START, MIDDLE, END.
- Images are contained/aspect-fit with dark padding/letterboxing, not cropped/cover-filled.
- Clip metadata remains readable: format, decoder, resolution, frame rate/duration, timecode, status, warning/status bar.
- Source summary remains folder-level: `.../001_video/260215/R#1`.
- Header reports `Middle preview: 1 of 2`, matching the smoke run with `--middle-count 2` while rendering the safest single middle preview.

## Middle Selection Logic
The renderer receives a tuple of capture points rather than a dedicated single middle still. The safe minimal logic is:
1. Detect Start by a start-prefixed label, falling back to the first capture.
2. Detect End by an end-prefixed label, falling back to the last capture.
3. For Middle, prefer remaining captures whose label starts with `mid` or `middle`.
4. Select the candidate closest to requested ratio `0.5`.

This respects existing `--middle-count` behavior by using the generated middle captures and choosing the central representative for the contact sheet.

## Safe Next Step
Run independent QA from a fresh QA lane and require explicit QA PASS before treating the workflow as accepted.
