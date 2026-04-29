status: PASS

# QA Report: PDF Output Refined Layout

workflow_id: datahelper-pdf-output-refined-layout-20260426-qa
parent_workflow_id: datahelper-pdf-output-refined-layout-20260426
lane: QA / Validation only
reported_at: 2026-04-26T18:40:00+09:00

## Verdict

QA validation checks completed successfully. The original lane blocker was limited to the required central QA work-log write from the worker sandbox; that work-log was later recovered by runner-side artifact recovery and verified by Maintenance on 2026-04-26T18:49:14+09:00, so this QA lane is routeable as PASS.

Exact permission error:

`touch: /Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-qa.md: Operation not permitted`

Required central work-log path, later recovered by runner-side artifact recovery:

`/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-qa.md`

QA made no implementation changes. QA wrote only this report and generated QA-owned validation artifacts under:

`/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-output-refined-layout-2026-04-26/`

## Required Reads

Inspected:

- `/Users/server_jay/Desktop/DataHelper/AGENTS.md`
- `/Users/server_jay/Desktop/DataHelper/docs/stage.md`
- `/Users/server_jay/Desktop/DataHelper/Docs/stage.md`
- `/Users/server_jay/Desktop/DataHelper/docs/reports/status/current-status.md`
- `/Users/server_jay/Desktop/DataHelper/Docs/reports/status/current-status.md`
- `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-plan.md`
- `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-implement.md`
- `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-25-contact-sheet-3-frame-previews.md`
- `/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-25-contact-sheet-3-frame-previews-qa.md`
- `/Users/server_jay/.hermes/cache/documents/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf`
- `/Users/server_jay/Documents/Security/brain/ops/devman-runs/2026-04-26/datahelper-pdf-output-refined-layout-20260426/reference-preview/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf.png`

Implementation report inspected:

- `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-implement.md`
- Dev report verdict: PASS.

## Commands Run

1. `python -m compileall src/frameproof/render/pdf_renderer.py`
   - Result: PASS, exit code 0.

2. `python -m pytest tests/unit/render/test_pdf_renderer.py -q`
   - Result: PASS, `15 passed in 2.47s`.

3. `python -m pytest tests/unit/render/test_pdf_renderer.py tests/integration/test_native_braw_adapter.py -q`
   - Result: PASS, `17 passed in 3.97s`.

4. Central work-log write check:
   - Command: `mkdir -p /Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper && touch /Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-qa.md`
   - Result: BLOCKER, `Operation not permitted`.

5. Real-media QA smoke:
   - Command used three valid `.braw` inputs from `/Volumes/HOTDRIVE/06.15`, excluding AppleDouble `._*.braw`, with `--layout contact_sheet`, `--middle-count 2`, and `--braw-adapter-path tools/braw_adapter`.
   - Result: PASS, exit code 0.
   - CLI summary: success, `total_clips: 3`, `success_count: 3`, all failure/skipped counts 0.

6. Preview generation:
   - `qlmanage -t -s 1200 -o artifacts/qa/pdf-output-refined-layout-2026-04-26/preview artifacts/qa/pdf-output-refined-layout-2026-04-26/contact-sheet-refined-qa.pdf`
   - Result: failed with `sandbox initialization failed: invalid data type of path filter; expected pattern, got boolean`.
   - Fallback: `sips -s format png artifacts/qa/pdf-output-refined-layout-2026-04-26/contact-sheet-refined-qa.pdf --out artifacts/qa/pdf-output-refined-layout-2026-04-26/preview/contact-sheet-refined-qa-sips.png`
   - Result: PASS, produced a 792 x 612 PNG preview.

## Generated QA Artifacts

- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-output-refined-layout-2026-04-26/contact-sheet-refined-qa.pdf`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-output-refined-layout-2026-04-26/contact-sheet-refined-qa.csv`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-output-refined-layout-2026-04-26/contact-sheet-refined-qa.json`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-output-refined-layout-2026-04-26/preview/contact-sheet-refined-qa-sips.png`

Reference preview inspected for comparison:

`/Users/server_jay/Documents/Security/brain/ops/devman-runs/2026-04-26/datahelper-pdf-output-refined-layout-20260426/reference-preview/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf.png`

## Implementation Inspection

Renderer inspection found equivalent refined layout logic in `src/frameproof/render/pdf_renderer.py`:

- `_image_aspect_ratio`, `_measure_contact_frame`, `_measure_contact_preview`, `_measure_contact_clip_card`, and `_pack_contact_pages` are present.
- `_measure_contact_frame` derives `image_height = column_width / aspect_ratio`.
- `_draw_contact_preview_block` draws caption and image directly, uses `drawImage(..., frame.image_width, frame.image_height, preserveAspectRatio=False)`, and applies a 1 point image border.
- The contact-sheet preview path does not use a fixed-height black rounded container around the whole image area.
- `_pack_contact_pages` moves a card to the next page when the next measured height would exceed usable page height.

## Visual And Layout Findings

- START / MIDDLE / END in 3 horizontal columns: verified in rendered preview and PDF drawing stream. Page 1 has START/MIDDLE/END at x positions 113.0, 309.6667, and 506.3333 for both clip cards.
- Images not cropped / full image shown: verified by geometry for BRAW stills. Source aspect is 6048x2520, and drawn frames are 186.6667 x 77.7778, matching the source ratio.
- Image height derived from actual aspect ratio: verified by code inspection and PDF geometry.
- Frame tops align: verified. For each row, all three images share the same top y coordinate.
- Mixed aspect ratios retain natural bottom positions: covered by unit test `test_triptych_draws_mixed_aspect_images_from_same_top_y` and measurement helper inspection.
- No large black dead/empty containers: verified in rendered preview and by `_draw_contact_preview_block`; black fill is limited to 24 point caption bars.
- Caption bars minimal: verified at 24 PDF points in code and PDF geometry.
- Image border thin: verified code sets line width 1 before drawing image border.
- Two normal clips fit on a page: verified in rendered preview and PDF stream. Page 1 contains `A001_06151426_C001.braw` and `A001_06151426_C002.braw`.
- Next clip moves to next page when needed: verified. Page 2 contains only `A001_06151433_C003.braw`.
- Final-page single clip not stretched: verified by PDF geometry. Page 2 image dimensions are the same 186.6667 x 77.7778 as page 1.
- No text/image overlap: no overlap visible in the rendered first-page preview; PDF geometry has separate card, metadata, status, caption, image, and footer bands.
- Status badges small/secondary: verified visually; status badges are compact.
- Existing middle-selection behavior intact: tests passed and generated manifest has `Start`, `Mid1`, `Mid2`, `End` for each clip while PDF header reports `Middle preview: 1 of 2`.
- Native BRAW adapter behavior preserved: combined integration test passed; real-media manifest shows adapter `braw_adapter`, codec `blackmagic_raw_native_sdk`, and all captures successful.
- Original `.braw` source media not copied into artifacts: artifact scan found 0 `.braw` files under the QA artifact directory.

## Native BRAW Adapter Result

Real-media manifest evidence:

- `A001_06151426_C001.braw`: adapter `braw_adapter`, codec `blackmagic_raw_native_sdk`, 4 successful captures.
- `A001_06151426_C002.braw`: adapter `braw_adapter`, codec `blackmagic_raw_native_sdk`, 4 successful captures.
- `A001_06151433_C003.braw`: adapter `braw_adapter`, codec `blackmagic_raw_native_sdk`, 4 successful captures.

## Source-Media Safety

QA did not enable still export, did not copy original media, and did not modify source media. Artifact scan result:

`find artifacts/qa/pdf-output-refined-layout-2026-04-26 -type f -name '*.braw' -print | wc -l`

Result: `0`

Checked source-media paths remained on `/Volumes/HOTDRIVE/06.15/` and were only read by the native adapter.

## Blocker

The central QA work-log path was not writable from this lane, but the durable runner recovered the required work-log and Maintenance verified it on 2026-04-26T18:49:14+09:00. Compile, unit, integration, real-media smoke, preview fallback, layout inspection, BRAW adapter validation, and source-media safety checks all passed.
