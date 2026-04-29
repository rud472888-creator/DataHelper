# DataHelper Stage 09 Plan / Inspection Lane - PDF Output Refined Layout

workflow_id: datahelper-pdf-output-refined-layout-20260426-plan
parent_workflow_id: datahelper-pdf-output-refined-layout-20260426
repo: /Users/server_jay/Desktop/DataHelper
lane: Dev / Plan only
created_at: 2026-04-26T17:33:31+09:00

You are a fresh Codex worker in the Dev Plan lane. Do not use hidden prior chat context. Use repository files and this prompt only.

## Hard boundaries
- This is a planning/inspection lane only. Do not modify product code in `src/`, tests, adapters, or source media.
- You may write only the required plan report, central work-log, and implementation/QA prompt files named below.
- Do not launch Dev/QA/Fix workers. Devman will route the next lane.
- Preserve BRAW/native adapter behavior and source-media safety; do not copy or modify original media.

## Read first
1. `/Users/server_jay/Desktop/DataHelper/AGENTS.md`
2. `/Users/server_jay/Desktop/DataHelper/docs/stage.md` and `/Users/server_jay/Desktop/DataHelper/Docs/stage.md`
3. `/Users/server_jay/Desktop/DataHelper/docs/reports/status/current-status.md` and `/Users/server_jay/Desktop/DataHelper/Docs/reports/status/current-status.md`
4. `/Users/server_jay/Documents/Security/brain/ops/project-handoffs/datahelper/current.md`
5. Existing contact-sheet reports:
   - `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-25-contact-sheet-3-frame-previews.md`
   - `/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-25-contact-sheet-3-frame-previews-qa.md`
6. Reference PDF:
   - `/Users/server_jay/.hermes/cache/documents/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf`
   - Devman inspection preview: `/Users/server_jay/Documents/Security/brain/ops/devman-runs/2026-04-26/datahelper-pdf-output-refined-layout-20260426/reference-preview/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf.png`

## Devman reference inspection already performed
- `pdfinfo` is not installed.
- `mdls` showed PDF size 608,505 bytes.
- Byte-level PDF scan found 2 `/Type /Page` entries, `/Count 2`, and two `MediaBox [0 0 791.3793103448276 611.3793103448276]` entries.
- Quick Look thumbnail command generated `/Users/server_jay/Documents/Security/brain/ops/devman-runs/2026-04-26/datahelper-pdf-output-refined-layout-20260426/reference-preview/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf.png`.
- Vision inspection found a landscape contact sheet with header + footer, two clip cards per page, three horizontal START/MIDDLE/END frame previews per clip, minimal dark caption bars, thin image borders, small status badges, no large black containers, and unused last-page space not stretched.

## User requirements to convert into implementable plan
Frame layout:
- Inside one clip card, place START / MIDDLE / END frames horizontally in 3 columns.
- Never crop any image; always show the full image.
- Frame boxes must not use fixed height. Compute height from the image's actual aspect ratio.
- Use `imageHeight = columnWidth / aspectRatio`.
- Frame total height = `captionBarHeight + imageHeight`.
- Replace contain/crop fixed boxes with direct image placement based on image ratio-derived height.
- The three frames may have different aspect ratios; they must start at the same y coordinate, and bottom height differences should remain naturally visible.
- Clip card height must be auto-calculated as `max(frameTotalHeight) + metadata + padding`.
- Prefer 2 clips per page when possible, but if footer/bottom would be infringed, move the next clip to the next page.
- If only 1 clip remains on the last page, do not stretch/enlarge frames artificially.

Visual design:
- Remove large black frame containers and unnecessary vertical whitespace.
- Caption bar should be minimal, about 24-32 px; show left label and right timecode.
- Use only a 1 px border around images.
- Avoid excessive navy boxes, large rounded cards, and AI-template-style badges.
- Status badges should be small; success/warning should be secondary information.

Verification criteria:
- No crop.
- No black dead/empty container area.
- Natural layout for different image aspect ratios.
- 2 clips per page where possible.
- No text/image overlap.
- Last page single clip is not artificially enlarged.

## Likely implementation area
- `src/frameproof/render/pdf_renderer.py`
- `tests/unit/render/test_pdf_renderer.py`
- Any existing contact-sheet PDF layout helpers.

## Required outputs
1. Plan report: `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-plan.md`
   - First 120 lines must include exactly one of: `status: PASS`, `status: FAIL`, or `status: BLOCKED`.
   - Include inspected files, implementation strategy, exact code/test boundaries, expected implement report/work-log paths, expected QA report/work-log paths, and blockers if any.
2. Central work-log: `/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-plan.md`
3. Implementation prompt file for the next Dev lane: `/Users/server_jay/Desktop/DataHelper/docs/prompts/2026-04-26-datahelper-pdf-output-refined-layout-implement.md`
   - Must be self-contained, require fresh worker state, and include exact expected report/work-log paths:
     - report: `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-implement.md`
     - work-log: `/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-implement.md`
   - Must instruct implementation worker to write `status: PASS|FAIL|BLOCKED` in the report.
   - Must prohibit QA self-validation as final acceptance.
4. QA prompt file for later fresh QA lane: `/Users/server_jay/Desktop/DataHelper/docs/prompts/2026-04-26-datahelper-pdf-output-refined-layout-qa.md`
   - Must be self-contained and validation-only.
   - Must include exact expected report/work-log paths:
     - report: `/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-26-pdf-output-refined-layout-qa.md`
     - work-log: `/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-qa.md`
   - Must prohibit implementation changes by QA.

## Success condition for this plan lane
Return PASS only if the implementation and QA prompts are concrete enough for Devman to launch the next legal implementation lane without hidden context.
