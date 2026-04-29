# Dev Implement Report: PDF Output Refined Layout

status: PASS

workflow_id: datahelper-pdf-output-refined-layout-20260426-implement
parent_workflow_id: datahelper-pdf-output-refined-layout-20260426
lane: Dev / Implement
created_at: 2026-04-26T17:34:00+09:00
reported_at: 2026-04-26T17:58:00+09:00

## Verdict

Implementation code and verification completed. The original lane blocker was limited to the required central work-log write from the worker sandbox; that work-log was later recovered by runner-side artifact recovery and verified by Maintenance on 2026-04-26T18:32:43+09:00, so this Dev lane is routeable as PASS.

Exact permission error:

`touch: /Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-implement.md: Operation not permitted`

Required central work-log path, later recovered by runner-side artifact recovery:

`/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-implement.md`

## Files Changed

- `src/frameproof/render/pdf_renderer.py`
- `tests/unit/render/test_pdf_renderer.py`
- `docs/reports/dev/2026-04-26-pdf-output-refined-layout-implement.md`

## Implementation Summary

- Replaced fixed one-clip contact-sheet pagination with measured clip-card layout and top-down page packing.
- Added pure contact-sheet measurement helpers for image aspect ratio, frame geometry, card height, and page packing.
- Contact preview frames now render START / MIDDLE / END horizontally with direct image placement.
- Image height is derived from actual image aspect ratio: `imageHeight = columnWidth / aspectRatio`.
- Removed the large fixed-height dark preview wells from the contact-sheet path.
- Caption bars are compact at 24 PDF points.
- Images receive a 1 point border and are not cropped.
- Mixed aspect ratios share the same top y coordinate and keep naturally different bottom positions.
- Clip cards auto-size from metadata/status chrome plus the tallest measured frame.
- Normal 16:9 clips pack two per page where measured geometry allows.
- Last-page cards are not stretched to consume remaining page space.
- Existing START/MIDDLE/END selection semantics, source summary behavior, `_pdf_image_reader` compression/downsampling, and native BRAW adapter behavior were preserved.

## Tests And Commands Run

- `python -m compileall src/frameproof/render/pdf_renderer.py`
  - Result: PASS.
- `python -m pytest tests/unit/render/test_pdf_renderer.py -q`
  - Result: PASS, `15 passed in 2.53s`.
- `python -m pytest tests/unit/render/test_pdf_renderer.py tests/integration/test_native_braw_adapter.py -q`
  - Result: PASS, `17 passed in 4.00s`.

## Real-Media Smoke

Command used three valid `.braw` inputs from `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1`, excluding AppleDouble `._*.braw` files, with:

- `--layout contact_sheet`
- `--middle-count 2`
- `--braw-adapter-path tools/braw_adapter`

Result:

- `status: success`
- `total_clips: 3`
- `success_count: 3`
- `partial_success_count: 0`
- `probe_failed_count: 0`
- `decode_failed_count: 0`
- `skipped_count: 0`

Generated artifacts:

- `artifacts/dev/pdf-output-refined-layout-2026-04-26/contact-sheet-refined-implement.pdf` - 105 KB, 2 pages.
- `artifacts/dev/pdf-output-refined-layout-2026-04-26/contact-sheet-refined-implement.csv` - 3.0 KB.
- `artifacts/dev/pdf-output-refined-layout-2026-04-26/contact-sheet-refined-implement.json` - 17 KB.

Manifest evidence:

- `A001_02151700_C017.braw`: adapter `braw_adapter`, codec `blackmagic_raw_native_sdk`, status `success`, 4 captures.
- `A001_02151704_C018.braw`: adapter `braw_adapter`, codec `blackmagic_raw_native_sdk`, status `success`, 4 captures.
- `A001_02151705_C019.braw`: adapter `braw_adapter`, codec `blackmagic_raw_native_sdk`, status `success`, 4 captures.

PDF text evidence:

- `START`: present.
- `MIDDLE`: present.
- `END`: present.
- `Middle preview: 1 of 2`: present.
- `Original media untouched`: present.
- `PREVIEW ONLY`: present.

Quick Look preview generation was attempted with:

`qlmanage -t -s 1200 -o artifacts/dev/pdf-output-refined-layout-2026-04-26/preview artifacts/dev/pdf-output-refined-layout-2026-04-26/contact-sheet-refined-implement.pdf`

Result: failed in the worker sandbox with:

`sandbox initialization failed: invalid data type of path filter; expected pattern, got boolean`

Fallback raster tools were unavailable:

- `pdftoppm`: not found.
- `magick`: not found.
- Python modules `fitz`, `pypdfium2`, and `pdf2image`: not installed.

## Source-Media Safety

No original media was copied or modified. Artifact scan found zero `.braw` files under:

`artifacts/dev/pdf-output-refined-layout-2026-04-26`

The smoke run did not enable exported stills.

## Remaining Risks Or Blockers

- RECOVERED: central work-log path was not writable from the worker sandbox, but the runner recovered the required work-log artifact and Maintenance verified it on 2026-04-26T18:32:43+09:00.
- Visual raster preview could not be generated in this worker because Quick Look failed and common PDF raster tools are unavailable.
- Final acceptance is deferred to the independent QA lane. This Dev lane does not self-validate final acceptance.
