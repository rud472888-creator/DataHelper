# DataHelper PDF Contact Sheet Preview No-Crop Fix Report

## Summary
- status: succeeded
- vertical_crop_fixed: yes
- width_preserved: yes
- output_pdf: /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop.pdf
- output_png: /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop-page-1.png
- output_pdf_size: 198153 bytes (0.189 MB)

## Changes
- files modified
  - Implementation changes were not modified during QA. Per dev handoff, the implementation/test files changed for this fix were:
    - /Users/server_jay/Desktop/DataHelper/src/frameproof/render/pdf_renderer.py
    - /Users/server_jay/Desktop/DataHelper/tests/unit/render/test_pdf_renderer.py
  - QA created this report only:
    - /Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-25-pdf-contact-sheet-preview-no-crop-fix-qa.md
- image fit behavior change
  - Verified current contact-sheet Start/End preview draw uses contained/aspect-fit behavior in the generated PDF output: decoded page content draws each preview image at 334.7502 x 223.3333 pt inside the preview well, matching the 6048x4032 source aspect ratio without vertical cover-crop.
  - Verified the contact sheet now flows one clip per page, preserving the wide two-column preview row while allowing enough vertical room for no-crop rendering.
  - Letterboxing/padding inside the dark preview wells is visible and acceptable for the no-crop behavior.

## Verification
- commands and pass/fail
  - `python3 -m py_compile src/frameproof/render/pdf_renderer.py`: PASS
  - `PYTHONPATH=src python3 -m pytest tests/unit/render/test_pdf_renderer.py -q`: PASS, 8 passed
  - `PYTHONPATH=src .venv/bin/python -m pytest tests/unit/render/test_pdf_renderer.py -q`: PASS, 8 passed in 0.15s
  - `.venv/bin/python -m py_compile src/frameproof/render/pdf_renderer.py`: PASS
  - Artifact existence check: PASS
    - PDF exists: /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop.pdf
    - First-page PNG exists: /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop-page-1.png
    - JSON exists: /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop.json
    - CSV exists: /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop.csv
    - no-crop still PNGs exist: 8 PNG stills under /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/no-crop-stills/
  - First-page PNG dimensions: PASS, 1600x1236
  - Previous visual parity PNG exists for comparison: PASS, 792x612
  - Source summary check in decoded PDF page streams: PASS, source is folder-level `Source: .../001_video/260215/R#1`; it is not rendered as a full file list.
  - PDF size check: PASS, 198153 bytes / 0.189 MB, far below the old 177MB-class output.

## Visual Notes
- no vertical crop confirmation
  - Visual inspection of the first-page PNG confirms both START FRAME and END FRAME previews show the full vertical composition without top/bottom cut-off.
  - The top architectural overhang and lower foreground/stone wall areas remain visible in both previews.
  - Decoded PDF geometry confirms the embedded image aspect ratio is preserved: 334.7502 / 223.3333 ~= 1.499, matching the 6048 / 4032 source ratio of 1.5.
- remaining tradeoffs such as letterboxing
  - Letterboxing/padding is visible inside the dark preview wells because frames are contained rather than cover-cropped.
  - Page flow changed to one clip per page (`Page 1 / 2`, `Page 2 / 2`) so the current two-column preview block width stays wide while vertical image content is preserved.
  - Horizontal preview width is preserved: each Start/End preview remains a wide two-column panel spanning nearly half of the clip card, consistent with the previous visual parity layout.

## Safety Confirmation
- source media untouched: yes
- credentials/config untouched: yes
- implementation code untouched by QA: yes
- QA activity was limited to reading files/artifacts, running verification commands, inspecting rendered output, and writing this QA report.

## Next Step
- Jay should inspect /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop.pdf and /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop-page-1.png to confirm the acceptable letterboxing/no-crop visual tradeoff.
