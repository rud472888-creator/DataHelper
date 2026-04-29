# DataHelper Stage 09 Implement Lane - PDF Output Refined Layout

workflow_id: datahelper-pdf-output-refined-layout-20260426-implement
parent_workflow_id: datahelper-pdf-output-refined-layout-20260426
repo: /Users/server_jay/Desktop/DataHelper
lane: Dev / Implement
created_at: 2026-04-26T17:34:00+09:00

You are a fresh Codex worker in the Dev Implement lane. Do not use hidden prior chat context. Use repository files and this prompt only.

## Hard Boundaries

- Implement only the refined contact-sheet PDF layout described here.
- Do not launch QA or Fix workers. Devman will route the next lane.
- Do not self-validate as final acceptance. Your verification can support Dev handoff, but only a later independent QA lane can accept the workflow.
- Preserve BRAW/native adapter behavior and source-media safety.
- Do not copy or modify original media.
- Do not add dependencies unless explicitly requested by Devman.
- Keep diffs small and focused.

## Required Reads

1. `/Users/server_jay/Desktop/DataHelper/AGENTS.md`
2. `/Users/server_jay/Desktop/DataHelper/docs/stage.md` and `/Users/server_jay/Desktop/DataHelper/Docs/stage.md`
3. `/Users/server_jay/Desktop/DataHelper/docs/reports/status/current-status.md` and `/Users/server_jay/Desktop/DataHelper/Docs/reports/status/current-status.md`
4. `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-plan.md`
5. `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-25-contact-sheet-3-frame-previews.md`
6. `/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-25-contact-sheet-3-frame-previews-qa.md`
7. Reference PDF: `/Users/server_jay/.hermes/cache/documents/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf`
8. Reference preview PNG: `/Users/server_jay/Documents/Security/brain/ops/devman-runs/2026-04-26/datahelper-pdf-output-refined-layout-20260426/reference-preview/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf.png`

## Required Outputs

Write the implementation report:

`/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-implement.md`

The first 120 lines of the report must include exactly one of:

- `status: PASS`
- `status: FAIL`
- `status: BLOCKED`

Write the implementation work-log:

`/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-implement.md`

If the central work-log path is not writable, report `status: BLOCKED` and include the exact permission error. Do not silently substitute a different path.

## Goal

Refine the contact-sheet PDF so each clip card displays START / MIDDLE / END frames horizontally with full uncropped images, minimal caption bars, no large black dead containers, auto-measured card heights, and page packing that fits two normal clips per page where possible.

## User Requirements

Frame layout:

- Inside one clip card, place START / MIDDLE / END frames horizontally in 3 columns.
- Never crop any image; always show the full image.
- Frame boxes must not use fixed height.
- Compute frame image height from the image's actual aspect ratio:
  - `imageHeight = columnWidth / aspectRatio`
  - `aspectRatio = imagePixelWidth / imagePixelHeight`
- Frame total height is `captionBarHeight + imageHeight`.
- Replace contain/crop fixed boxes with direct image placement based on image ratio-derived height.
- The three frames may have different aspect ratios. They must start at the same y coordinate, and bottom height differences should remain naturally visible.
- Clip card height must be auto-calculated as `max(frameTotalHeight) + metadata + padding`.
- Prefer 2 clips per page when possible.
- If footer/bottom would be infringed, move the next clip to the next page.
- If only 1 clip remains on the last page, do not stretch/enlarge frames artificially.

Visual design:

- Remove large black frame containers and unnecessary vertical whitespace.
- Caption bar should be minimal, about 24-32 PDF points, with left label and right timecode.
- Use only a 1 point border around images.
- Avoid excessive navy boxes, large rounded cards, and AI-template-style badges.
- Status badges should be small and secondary.

Verification criteria:

- No crop.
- No black dead/empty container area.
- Natural layout for different image aspect ratios.
- 2 clips per page where possible.
- No text/image overlap.
- Last page single clip is not artificially enlarged.

## Likely Code Area

- `src/frameproof/render/pdf_renderer.py`
- `tests/unit/render/test_pdf_renderer.py`

Current implementation facts from the Plan lane:

- `CONTACT_CLIPS_PER_PAGE = 1` makes normal contact sheets one clip per page.
- `render_contact_sheet_pdf` computes a single fixed `block_height` per page before drawing.
- `_draw_clip_block` computes `preview_h` from remaining fixed card height.
- `_draw_contact_preview_block` draws a full dark rounded frame container, then aspect-fits the image inside it, leaving padding/dead area.
- `_fit_image` currently fits within `max_width`/`max_height`; the refined contact sheet should use direct ratio-derived image height instead of fixed-height contain wells.

## Implementation Strategy

1. Add small pure helper functions in `pdf_renderer.py`:
   - image size/aspect ratio helper using PIL and `ImageOps.exif_transpose` where appropriate;
   - frame measurement helper returning caption height, image width, image height, and total height;
   - clip-card measurement helper returning the full card height from metadata/header/status/padding plus `max(frameTotalHeight)`;
   - page packing helper that assigns measured clip cards to pages without stretching.

2. Update `render_contact_sheet_pdf`:
   - Measure clip cards before drawing.
   - Compute pages by packing cards top-down between header and footer.
   - Prefer two normal clips per page naturally by compact metadata and ratio-derived image heights.
   - Keep total page count accurate, including optional failed section.
   - Do not stretch the final page item.

3. Update clip-card drawing:
   - Draw compact card chrome and metadata.
   - Keep status badge/bar small.
   - Use measured card height instead of page-sliced fixed height.
   - Pass measured frame layout to preview drawing so draw and measure agree.

4. Update preview drawing:
   - Draw each of START/MIDDLE/END in a column.
   - Caption bars share the same top y.
   - Draw image immediately below caption bar using `imageHeight = columnWidth / aspectRatio`.
   - Draw a 1 point image border.
   - Do not draw a large dark rounded container behind the whole frame.
   - For missing/failed capture images, draw a small neutral placeholder at the measured image area without implying crop.

5. Preserve existing behavior:
   - Keep `_start_middle_end_captures` semantics.
   - Keep `_pdf_image_reader` compression/downsampling and source-media safety.
   - Keep detail PDF layout behavior unless a shared helper change requires compatibility.
   - Preserve BRAW native adapter behavior and tests.

## Test Requirements

Update `tests/unit/render/test_pdf_renderer.py` with focused tests. Prefer pure-helper tests for geometry, plus a generated-PDF smoke test.

Required coverage:

- two normal 16:9 clip cards fit on one regular contact-sheet page;
- three normal 16:9 clip cards produce two regular pages with the third card not stretched;
- frame measurement uses actual image aspect ratio and computes `imageHeight = columnWidth / aspectRatio`;
- mixed aspect ratio frames share the same top y and have naturally different bottoms;
- preview draw path uses direct image placement and a 1 point image border, not a fixed-height black container;
- existing START/MIDDLE/END labels and middle-selection behavior remain intact;
- existing source summary behavior remains intact;
- no-crop behavior is asserted by draw dimensions matching image ratio.

Acceptable techniques:

- Add a small fake canvas or monkeypatch helpers to capture `drawImage`, `rect`, and text coordinates.
- Inspect pure helper return values rather than parsing binary PDF content when possible.
- Keep PDF text extraction tests only for text labels/page smoke.

## Verification Commands

Run, at minimum:

`python -m compileall src/frameproof/render/pdf_renderer.py`

`python -m pytest tests/unit/render/test_pdf_renderer.py -q`

`python -m pytest tests/unit/render/test_pdf_renderer.py tests/integration/test_native_braw_adapter.py -q`

If real BRAW sample media is available, run a smoke generation with at least three valid `.braw` inputs, excluding AppleDouble `._*.braw`, using:

- `--layout contact_sheet`
- `--middle-count 2`
- `--braw-adapter-path tools/braw_adapter`

Then generate a Quick Look preview PNG if available:

`qlmanage -t -s 1200 -o <preview-dir> <pdf-path>`

Verify:

- Generated PDF/CSV/JSON are non-empty.
- Native BRAW adapter remains `braw_adapter` / `blackmagic_raw_native_sdk` where applicable.
- No `.braw` files were copied into artifact directories.
- Preview visually matches the refined reference: two clips per page where possible, compact caption bars, no large black containers, no crop, no overlap.

## Report Content Requirements

The implementation report must include:

- verdict line as described above;
- files changed;
- implementation summary;
- tests and commands run with results;
- generated artifacts, if any;
- source-media safety statement;
- remaining risks or blockers;
- explicit statement that final acceptance is deferred to independent QA.

The work-log must include:

- workflow id;
- commands run;
- files changed;
- verification evidence;
- any blockers or permission issues.
