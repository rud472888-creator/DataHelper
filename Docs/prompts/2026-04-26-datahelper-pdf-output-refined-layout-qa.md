# DataHelper Stage 09 QA Lane - PDF Output Refined Layout

workflow_id: datahelper-pdf-output-refined-layout-20260426-qa
parent_workflow_id: datahelper-pdf-output-refined-layout-20260426
repo: /Users/server_jay/Desktop/DataHelper
lane: QA / Validation only
created_at: 2026-04-26T17:34:00+09:00

You are a fresh Codex worker in the QA lane. Do not use hidden prior chat context. Use repository files and this prompt only.

## Hard Boundaries

- Validation only.
- Do not modify implementation code, tests, adapters, prompts, source media, or product configuration.
- Do not silently fix implementation.
- You may write only the QA report, central QA work-log, and QA artifacts/previews needed for validation.
- Preserve BRAW/native adapter behavior and source-media safety.
- Do not copy or modify original media.
- Return explicit PASS or FAIL in the QA report. Use BLOCKED only if validation cannot be performed due to missing artifacts, permissions, or unavailable required environment.

## Required Reads

1. `/Users/server_jay/Desktop/DataHelper/AGENTS.md`
2. `/Users/server_jay/Desktop/DataHelper/docs/stage.md` and `/Users/server_jay/Desktop/DataHelper/Docs/stage.md`
3. `/Users/server_jay/Desktop/DataHelper/docs/reports/status/current-status.md` and `/Users/server_jay/Desktop/DataHelper/Docs/reports/status/current-status.md`
4. Plan report: `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-plan.md`
5. Implementation report: `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-26-pdf-output-refined-layout-implement.md`
6. Prior dev report: `/Users/server_jay/Desktop/DataHelper/docs/reports/dev/2026-04-25-contact-sheet-3-frame-previews.md`
7. Prior QA report: `/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-25-contact-sheet-3-frame-previews-qa.md`
8. Reference PDF: `/Users/server_jay/.hermes/cache/documents/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf`
9. Reference preview PNG: `/Users/server_jay/Documents/Security/brain/ops/devman-runs/2026-04-26/datahelper-pdf-output-refined-layout-20260426/reference-preview/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf.png`

## Required Outputs

Write the QA report:

`/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-26-pdf-output-refined-layout-qa.md`

The first 120 lines of the report must include exactly one of:

- `status: PASS`
- `status: FAIL`
- `status: BLOCKED`

Write the QA work-log:

`/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-26/datahelper/2026-04-26-pdf-output-refined-layout-qa.md`

If the central work-log path is not writable, report `status: BLOCKED` and include the exact permission error. Do not silently substitute a different path.

## Acceptance Criteria

QA may return PASS only if all required criteria are verified:

- Contact-sheet clip cards place START / MIDDLE / END frames horizontally in 3 columns.
- Images are not cropped; each frame shows the full image.
- Image height is derived from actual image aspect ratio using the effective column width.
- The three frame tops align at the same y coordinate.
- Mixed aspect ratios retain naturally different bottom y positions; bottoms are not forced equal by a fixed-height container.
- There are no large black dead/empty containers around preview images.
- Caption bars are minimal, approximately 24-32 PDF points, with left label and right timecode.
- Image border is thin, about 1 point.
- Two normal clips fit on a page where possible.
- If a next clip would infringe footer/bottom margin, it moves to the next page.
- A single clip on the final page is not stretched/enlarged to fill unused space.
- No text/image overlap is visible.
- Status badges are small and secondary.
- Existing START/MIDDLE/END middle-selection behavior remains intact.
- Native BRAW adapter behavior is preserved.
- Original `.braw` source media are not copied into artifacts.

## Required Validation

1. Inspect repo state and implementation report.
   - Confirm implementation report exists and has a Dev PASS before running full QA. If it is missing or not PASS, return QA BLOCKED or FAIL as appropriate.

2. Run static/test verification:
   - `python -m compileall src/frameproof/render/pdf_renderer.py`
   - `python -m pytest tests/unit/render/test_pdf_renderer.py -q`
   - `python -m pytest tests/unit/render/test_pdf_renderer.py tests/integration/test_native_braw_adapter.py -q`

3. Inspect implementation without modifying it:
   - Verify measurement/page-packing helpers exist or equivalent logic is present.
   - Verify preview drawing no longer uses a fixed-height black rounded container for the whole image area.
   - Verify direct image placement uses actual aspect ratio-derived height.

4. Generate validation artifacts if environment permits:
   - Use at least three clips so QA can validate two clips on page 1 and one clip on the last page.
   - Prefer real valid `.braw` sample media if available, excluding `._*.braw`.
   - Use `--layout contact_sheet`, `--middle-count 2`, and `--braw-adapter-path tools/braw_adapter`.
   - Write QA artifacts under a QA-specific artifact directory, for example:
     `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-output-refined-layout-2026-04-26/`

5. Generate or inspect a rendered preview:
   - Use Quick Look if common PDF renderers are unavailable:
     `qlmanage -t -s 1200 -o <preview-dir> <pdf-path>`
   - Compare visually against the reference preview:
     `/Users/server_jay/Documents/Security/brain/ops/devman-runs/2026-04-26/datahelper-pdf-output-refined-layout-20260426/reference-preview/doc_c1363320ac6b_contact-sheet-3-frame-refined.pdf.png`

6. Source-media safety:
   - Scan QA artifact directory and confirm there are zero copied `.braw` files.
   - Confirm QA did not modify source media.

## PASS / FAIL Guidance

Return PASS only when tests pass, generated/inspected output satisfies all visual/layout criteria, native BRAW behavior is preserved, and source-media safety is verified.

Return FAIL if implementation runs but violates any acceptance criterion, including crop, black dead containers, one-clip-per-page for normal clips, stretched last-page single clip, overlap, adapter regression, or copied source media.

Return BLOCKED if required files/artifacts are missing, implementation report is absent, required paths are unwritable, or the environment cannot perform enough validation to make a defensible PASS/FAIL judgment.

## Report Content Requirements

The QA report must include:

- verdict line as described above;
- scope statement saying QA made no implementation changes;
- implementation report inspected;
- commands run and results;
- generated QA artifacts and preview paths;
- visual/layout findings mapped to each acceptance criterion;
- native BRAW adapter result;
- source-media safety result;
- exact failure evidence or blocker details if not PASS.

The QA work-log must include:

- workflow id;
- commands run;
- artifacts generated;
- validation evidence;
- blocker details if any.
