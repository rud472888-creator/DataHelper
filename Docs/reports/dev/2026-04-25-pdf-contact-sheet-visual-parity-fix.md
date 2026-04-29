# DataHelper PDF Contact Sheet Visual Parity Fix Report

## Summary
- status: succeeded
- previews_enlarged: yes
- source_summary_fixed: yes
- output_pdf: `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-visual-parity.pdf`
- output_pdf_size: 54,124 bytes
- visual_reference_used: `/Users/server_jay/.hermes/cache/documents/doc_fcd515a9277a_nearby-two-contact-sheet-redesign.pdf` and `/tmp/datahelper_pdf_ref/page-1.png`

## Changes
- files modified
  - `src/frameproof/render/pdf_renderer.py`
  - `tests/unit/render/test_pdf_renderer.py`
  - `docs/reports/dev/2026-04-25-pdf-contact-sheet-visual-parity-fix.md`
  - `/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-25/devman/2026-04-25-datahelper-pdf-contact-sheet-visual-parity-fix.md`
- preview sizing/layout changes
  - Reduced page margin, header height, footer height, and inter-card gap to give the two clip cards more vertical space.
  - Compressed the clip-card metadata area so the lower Start/End preview area receives the priority.
  - Kept the two-clip-per-page structure for the smoke case while making each clip card taller and closer to the reference proportions.
  - Changed contact-sheet preview image embedding to an in-memory cover-fit crop so actual frames fill the dark Start/End preview wells instead of appearing as small centered thumbnails.
  - Increased contact-sheet embedded image quality/cap from 1,200px/82 JPEG quality to 1,600px/86 while keeping PDF size far below the old 177MB class output.
- source summary logic changes
  - `settings.input.paths` now collapse file inputs to their parent directories before summary display.
  - Inputs sharing one parent now show the shared folder only, e.g. `.../001_video/260215/R#1`, without listing individual BRAW file paths.
  - Multiple unrelated roots now show the first compact root plus `+N more sources`.
  - Header source text remains width-ellipsized and no longer duplicates a long source summary near page/badge text.

## Verification
- commands and pass/fail
  - `.venv/bin/python -m py_compile src/frameproof/render/pdf_renderer.py`: PASS
  - `.venv/bin/python -m pytest tests/unit/render/test_pdf_renderer.py`: PASS, 7 passed
  - `.venv/bin/python -m frameproof --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151557_C002.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151601_C003.braw' --no-recursive --middle-count 2 --layout contact_sheet --project-name 'Oven Maru PDF Visual Parity' --export-stills --stills-dir artifacts/qa/pdf-redesign-2026-04-25/stills-visual-parity --output artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-visual-parity.pdf --csv artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-visual-parity.csv --json artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-visual-parity.json --braw-adapter-path tools/braw_adapter`: PASS, status success, 2 clips, 2 successes, 0 failed/skipped
  - `sips -s format png artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-visual-parity.pdf --out artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-visual-parity-page-1.png`: PASS
  - `.venv/bin/python -m pytest tests/integration/test_native_braw_adapter.py`: PASS, 2 passed
  - `stat -f '%z bytes %N' artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-visual-parity.pdf`: PASS, 54,124 bytes

## Visual Comparison Notes
- what now matches the reference better
  - Start/End preview blocks now use the same dark header-bar and large image-below structure, with the actual frames cover-fitted into the preview area.
  - The two clip cards have more usable image area and less vertical space spent on metadata.
  - Header badge/source/page placement is cleaner and closer to the reference, with compact source and page information on the right.
  - Source display is folder-level and no longer exposes or collides with every input file path.
- remaining differences
  - The generated frame content is dark and preview-only; color/exposure should not be judged from the PDF.
  - End timecodes remain calculated where the adapter provides calculated values.
  - The PDF uses ReportLab built-in Helvetica rather than a custom embedded UI font.
  - The PNG comparison artifact was rendered with macOS `sips`, so it is suitable as a quick visual check rather than a color-critical render.

## Safety Confirmation
- source media untouched
- credentials/config untouched
- existing exported still PNGs untouched; this run wrote new smoke stills only under `artifacts/qa/pdf-redesign-2026-04-25/stills-visual-parity/`

## Next Step
- Jay should inspect `/Users/server_jay/Desktop/DataHelper/artifacts/qa/pdf-redesign-2026-04-25/contact-sheet-redesign-visual-parity.pdf` against the reference PDF, especially first-page Start/End frame size and the header Source line.
