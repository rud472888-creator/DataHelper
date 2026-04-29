# DataHelper PDF Contact Sheet Preview No-Crop Fix Report

## Summary
- status: succeeded
- vertical_crop_fixed: yes
- width_preserved: yes
- output_pdf: /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop.pdf
- output_png: /Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop-page-1.png
- output_pdf_size: 198153 bytes

## Changes
- files modified
  - /Users/server_jay/Desktop/DataHelper/src/frameproof/render/pdf_renderer.py
  - /Users/server_jay/Desktop/DataHelper/tests/unit/render/test_pdf_renderer.py
- image fit behavior change
  - Contact-sheet Start/End preview image drawing now uses `_fit_image(...)` contain/aspect-fit dimensions and `_pdf_image_reader(...)` downsampled in-memory embedding.
  - Removed contact-sheet cover-crop drawing behavior from the active preview path.
  - Contact-sheet clip density changed from 2 clips/page to 1 clip/page so the existing horizontal preview block width can be preserved while giving 16:9/3:2 frames enough vertical room to display without cropping.
  - Letterboxing inside the dark preview well is expected and accepted for no-crop behavior.

## Verification
- `python3 -m py_compile src/frameproof/render/pdf_renderer.py`: PASS
- `PYTHONPATH=src python3 -m pytest tests/unit/render/test_pdf_renderer.py -q`: PASS, 8 passed
- Real-media smoke PDF generation with both Oven Maru BRAW clips and repo-local `tools/braw_adapter`: PASS, status success, 2 clips, 2 success
- Output size check: PASS, 198153 bytes, far below 177MB class output
- First-page PNG generation via `qlmanage -t -s 1600`: PASS
- Visual first-page review: PASS, Start/End frames not vertically cut off; preview wells remain wide/readable; source summary remains folder-level (`.../001_video/260215/R#1`)

## Visual Notes
- no vertical crop confirmation
  - First-page rendered PNG shows the full vertical image composition for both Start and End previews with no top/bottom truncation.
- remaining tradeoffs such as letterboxing
  - Letterboxing is visible in the dark preview well because frames are contained instead of cover-cropped.
  - The contact sheet now flows one clip per page to preserve horizontal preview width and provide enough vertical height.

## Safety Confirmation
- source media untouched: yes
- credentials/config untouched: yes
- existing exported still PNGs untouched: yes; new smoke stills were written only under `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/no-crop-stills/`

## Next Step
- Jay should inspect `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-no-crop.pdf` and the first-page PNG preview to confirm the no-crop visual behavior.
