# Dev Plan Report: PDF Output Refined Layout

status: PASS

workflow_id: datahelper-pdf-output-refined-layout-20260426-plan
parent_workflow_id: datahelper-pdf-output-refined-layout-20260426
lane: Dev / Plan only
created_at: 2026-04-26T17:33:31+09:00
reported_at: 2026-04-26T17:34:00+09:00

## Summary

Planning and inspection completed for the Stage 09 refined contact-sheet PDF layout. The implementation and QA prompts are concrete enough for fresh follow-on lanes. The original lane-completion blocker was limited to the worker being unable to create the required central work-log path outside its writable sandbox; that work-log was later recovered by runner-side artifact recovery and verified by Maintenance on 2026-04-26T17:50:00+09:00.

No product code, tests, adapters, or source media were modified.

## Recovered Operational Blocker

Required central work-log:

`/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-plan.md`

Original attempted prerequisite directory creation:

`mkdir -p /Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper`

Original result:

`Operation not permitted`

Maintenance verification on 2026-04-26T17:50:00+09:00 confirmed the central work-log now exists, the runner final artifact reports `expected_work_log_exists: true` and `work_log_recovered_by_runner: true`, and no other plan blocker is present in this report. This lane is therefore routeable as PASS without product-code changes.

## Inspected Files And Artifacts

- `/Users/server_jay/Desktop/DataHelper/AGENTS.md`
- `/Users/server_jay/Desktop/DataHelper/docs/stage.md`
- `/Users/server_jay/Desktop/DataHelper/Docs/stage.md`
- `/Users/server_jay/Desktop/DataHelper/docs/reports/status/current-status.md`
- `/Users/server_jay/Desktop/DataHelper/Docs/reports/status/current-status.md`
- `/Users/server_jay/Documents/Security/brain/ops/project-handoffs/datahelper/current.md`
- `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-25-contact-sheet-3-frame-previews.md`
- `/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-25-contact-sheet-3-frame-previews-qa.md`
- `/Users/server_jay/.hermes/cache/documents/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf`
- `/Users/server_jay/Documents/Security/brain/ops/devman-runs/2026-04-26/datahelper-pdf-output-refined-layout-20260426/reference-preview/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf.png`
- `/Users/server_jay/Desktop/DataHelper/src/frameproof/render/pdf_renderer.py`
- `/Users/server_jay/Desktop/DataHelper/tests/unit/render/test_pdf_renderer.py`

## Current State Observed

- Stage boards show `stage-09`, `dev-plan`, implementation not allowed until this Plan lane completes.
- Prior Stage 08 QA passed: 3-frame START/MIDDLE/END contact-sheet wells render, native BRAW adapter behavior is preserved, and source media safety was validated.
- Reference PDF is a 2-page landscape contact sheet, 608,505 bytes, with two page MediaBox entries.
- Reference preview shows two clip cards on page 1, three horizontal frame previews per clip, small caption bars, thin image borders, no large black containers, and no artificial stretching of last-page space.

## Implementation Strategy

The next Dev lane should make a narrow renderer/test change centered on the contact-sheet PDF path.

1. Replace fixed one-clip pagination with measured clip-card layout.
   - Current boundary: `src/frameproof/render/pdf_renderer.py`, `render_contact_sheet_pdf`.
   - Remove dependence on `CONTACT_CLIPS_PER_PAGE = 1` for normal page flow.
   - Add a measurement pass that computes each clip card height before drawing.
   - Pack clips top-down after the header; prefer two clips per page when the measured heights fit above the footer. If the next clip would infringe footer/bottom margin, move it to a new page.
   - Do not stretch frames or cards to consume leftover page space.

2. Replace fixed-height preview wells with image ratio-derived direct placement.
   - Current boundary: `_draw_clip_block`, `_draw_contact_preview_triptych`, `_draw_contact_preview_block`.
   - Compute `columnWidth = (availablePreviewWidth - 2 * gap) / 3`.
   - For each START/MIDDLE/END capture, compute aspect ratio from the actual image file. Use image width / image height.
   - Compute `imageHeight = columnWidth / aspectRatio`.
   - Compute frame total height as `captionBarHeight + imageHeight`.
   - Draw all three caption bars at the same y coordinate, then draw images directly below them at their own derived heights.
   - Keep natural bottom differences when aspect ratios differ; align frame tops, not bottoms.
   - Use a minimal caption bar around 24-32 PDF points with left label and right timecode.
   - Use only a 1 point stroke around the image. Do not draw a large black rounded container behind the full frame area.

3. Auto-calculate clip card height.
   - Card height should be metadata/header/status/padding plus `max(frameTotalHeight)`.
   - Keep metadata/status compact enough to allow two normal 16:9 clips per landscape letter page, matching the reference.
   - If a card is unusually tall due to image aspect ratio, page-break before it when needed.
   - If a single card is taller than the usable page, keep a deterministic fallback that fits inside the page without cropping, preferably by scaling the three columns down uniformly for that card and recording the behavior in tests.

4. Preserve existing behavior outside refined layout.
   - Do not change capture selection semantics: `_start_middle_end_captures` should continue selecting START, representative MIDDLE, and END.
   - Preserve `_pdf_image_reader` downsampling/compression and source-media safety.
   - Preserve native BRAW adapter paths and do not copy or modify original media.
   - Avoid new dependencies.

## Exact Code Boundaries

Expected code changes:

- `src/frameproof/render/pdf_renderer.py`
  - Add small pure helpers for image dimension/aspect ratio, frame measurement, clip-card measurement, and page packing.
  - Update contact-sheet rendering to measure before drawing.
  - Update contact preview drawing to use direct image placement with ratio-derived heights and no dead container area.
  - Update header copy only if needed to reflect two-clips-per-page page flow.

Do not change:

- BRAW adapter code under `tools/` or native integration paths.
- Capture extraction code.
- Source media files or source-media copying behavior.
- Detail PDF layout unless a shared helper must remain compatible.

## Exact Test Boundaries

Expected test changes:

- `tests/unit/render/test_pdf_renderer.py`
  - Add or update unit coverage for:
    - two normal 16:9 clips fitting on one contact-sheet page;
    - three normal clips producing two regular pages without stretching the third;
    - frame measurement deriving image height from actual image aspect ratio;
    - mixed aspect ratios sharing the same top y and retaining different bottom y values;
    - no fixed black container rectangles larger than the image/caption frame in the preview block, to the extent feasible by monkeypatching a fake canvas or helper output;
    - no-crop behavior by asserting drawn image dimensions match `columnWidth` and `columnWidth / aspectRatio`.
  - Keep existing START/MIDDLE/END label, middle-selection, source-summary, PDF text, and fit/downsample tests.

Optional but useful:

- Add pure-helper tests rather than brittle binary PDF parsing where possible.
- Add a generated-PDF smoke test that counts page markers or text distribution for three clips.

## Verification Requirements For Implementation Lane

Minimum implementation verification:

- `python -m compileall src/frameproof/render/pdf_renderer.py`
- `python -m pytest tests/unit/render/test_pdf_renderer.py -q`
- `python -m pytest tests/unit/render/test_pdf_renderer.py tests/integration/test_native_braw_adapter.py -q`
- Generate a small contact-sheet PDF with at least three clips and `--middle-count 2` if real BRAW sample media is available in the worker environment.
- Produce or inspect a Quick Look preview PNG when macOS `qlmanage` is available.
- Confirm no `.braw` source media files were copied into artifacts.

## Expected Follow-On Reports

Implementation report:

`/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-implement.md`

Implementation work-log:

`/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-implement.md`

QA report:

`/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-26-pdf-output-refined-layout-qa.md`

QA work-log:

`/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-qa.md`

## Prompt Files Written

- `/Users/server_jay/Desktop/DataHelper/docs/prompts/2026-04-26-datahelper-pdf-output-refined-layout-implement.md`
- `/Users/server_jay/Desktop/DataHelper/docs/prompts/2026-04-26-datahelper-pdf-output-refined-layout-qa.md`

## Remaining Risks

- Visual QA depends on available PDF rasterization tooling. Prior lanes used Quick Look because common PDF tools were missing.
- Binary PDF inspection is brittle; implementation should expose pure measurement helpers so geometry can be verified without relying only on rendered previews.
- The central work-log path must be created by a process with write permission outside this worker sandbox before Devman can treat this plan lane as fully complete.
