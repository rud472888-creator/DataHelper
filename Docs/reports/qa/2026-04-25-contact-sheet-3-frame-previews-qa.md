# QA Report: Contact Sheet 3-Frame Previews

- status: succeeded
- verdict: PASS
- workflow_id: datahelper-contact-sheet-3-frame-previews-20260425
- qa_completed_at: 2026-04-25 22:09 KST
- qa_scope: independent validation only; no implementation code changed

## Summary
Independent QA validation passed. The contact-sheet PDF clip card renders three preview wells labeled START, MIDDLE, and END; the preview images are contained/aspect-fit with visible padding and no apparent cropping; metadata/status/warnings are readable; the source summary is folder-level; `--middle-count 2` generated two middle captures while the contact sheet selected one middle preview for display; native BRAW adapter behavior remains intact; no original BRAW source files were copied into QA artifacts.

## Files Changed
Implementation code changed by QA: none.

QA wrote/created only validation artifacts and this report:
- `/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-25-contact-sheet-3-frame-previews-qa.md`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-3-frame-preview-qa.pdf`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-3-frame-preview-qa.csv`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-3-frame-preview-qa.json`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/ql-qa-preview/contact-sheet-3-frame-preview-qa.pdf.png`

## Verification Results

### 1. Python compile for changed renderer module
Command:
`python -m compileall src/frameproof/render/pdf_renderer.py`

Result: PASS, exit code 0.

### 2. Renderer unit tests and BRAW/native adapter integration test
Command:
`python -m pytest tests/unit/render/test_pdf_renderer.py tests/integration/test_native_braw_adapter.py -q`

Result: PASS.
Output:
`11 passed in 1.81s`

### 3. Real-media CLI smoke: PDF/CSV/JSON generation
Command used three valid `.braw` inputs from `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1`, excluding AppleDouble `._*.braw` files, with:
- `--layout contact_sheet`
- `--middle-count 2`
- `--braw-adapter-path tools/braw_adapter`

Input files:
- `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151705_C019.braw`
- `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151704_C018.braw`
- `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151700_C017.braw`

Result: PASS, exit code 0.
CLI summary:
- `status: success`
- `total_clips: 3`
- `success_count: 3`
- `partial_success_count: 0`
- `probe_failed_count: 0`
- `decode_failed_count: 0`
- `skipped_count: 0`

Generated output sizes:
- PDF: 200,563 bytes
- CSV: 3,075 bytes
- JSON: 17,487 bytes
- first-page PNG preview from Quick Look: 279,506 bytes

PDF size assessment: PASS. The 3-clip contact sheet PDF is about 201 KB, not huge.

### 4. PDF text/content checks
Result: PASS.

Validated text in generated QA PDF:
- `START`: present
- `MIDDLE`: present
- `END`: present
- `Middle preview: 1 of 2`: present
- folder-level source summary `001_video/260215/R#1`: present
- `Original media untouched`: present
- `PREVIEW ONLY`: present

### 5. `--middle-count` behavior and renderer selection
Result: PASS.

Generated JSON manifest shows each real-media clip had four captures from `--middle-count 2`:
- `Start`, requested ratio `0.0`
- `Mid1`, requested ratio `0.3333333333333333`
- `Mid2`, requested ratio `0.6666666666666666`
- `End`, requested ratio `1.0`

The PDF/contact sheet renders one middle well and reports `Middle preview: 1 of 2`, confirming the renderer selects one representative middle preview while respecting generated middle captures.

### 6. BRAW native adapter behavior
Result: PASS.

Integration test passed. Real-media JSON also confirmed:
- adapter: `braw_adapter`
- codec: `blackmagic_raw_native_sdk`
- all captures successful for all three clips

This preserves native BRAW adapter behavior and does not indicate proxy-based behavior.

### 7. Source-media safety / no source copying
Result: PASS.

QA did not enable exported stills and did not copy original `.braw` media. Artifact scan result:
- `.braw` files under `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/`: 0
- `.braw` directories under that artifact tree: 4 existing still-directory names from earlier artifact organization; these are directories only, not copied source media files.

Source media stat was read-only during QA. The checked source `.braw` files remain at their original paths on `/Volumes/HOTDRIVE`.

## Visual Notes
Visual validation was performed from:
`/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/ql-qa-preview/contact-sheet-3-frame-preview-qa.pdf.png`

Observed first-page preview:
- The clip card clearly displays three horizontal preview wells labeled `START`, `MIDDLE`, and `END`.
- The preview images are aspect-fit/contained inside dark wells with visible letterboxing/padding and no apparent crop/cover behavior.
- Clip metadata is readable, including clip name, timecode range, format, decoder, resolution, frame rate/duration, and status.
- Status/warning area is readable and shows successful state/no clip-level warnings or errors.
- Header source summary is folder-level: `.../001_video/260215/R#1`, not a per-file list.
- Header reports `Middle preview: 1 of 2`, matching the `--middle-count 2` smoke run.

## Issues Encountered
- `pdftoppm`, ImageMagick `magick`, and Python PDF raster libraries were not available, so first-page PNG preview generation used macOS `qlmanage`, which succeeded.
- No blocking issues.

## Safe Next Step
Accept this workflow as QA PASS. Safe next step: merge/advance the workflow, preserving the generated QA report and artifacts for audit.