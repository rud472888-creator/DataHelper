# DataHelper PDF redesign - Fix handoff

Date: 2026-09-11. Lane: fresh Dev / Fix. Status: fixes complete; independent Re-QA PASS remains required.

Read `AGENTS.md`, the dated implementation handoff, and the explicit first QA FAIL. Applied PDF and report-output-quality skills. The parent had already run the artifact marker; this lane did not repeat it.

## Scope and changes

Only the two reported P2 layout defects were fixed. The authoritative supplied `ReportItem` sequence, `BatchSummary`, and `AppSettings` remain unchanged; all data fields, ordering, path policies, image behavior, public APIs, fonts, dimensions, and visual styling retain the implemented contract. No adapters, models, DataManager, orchestrator, global documents, package configuration, or deployment payloads were edited.

- `src/frameproof/render/pdf_renderer.py:239-284`: running furniture is drawn at page end. The document records the first and last meaningful section on each page, ignoring spacers, rules, and page-break controls. A fresh section opening replaces preceding-page context; continuation content inherits the active section; mixed pages show both endpoint contexts. The full project title's fit check reserves the actual running-context width plus separation.
- `src/frameproof/render/pdf_renderer.py:464-475`: message scope labels and error-detail keys use `keepWithNext`. Their following Paragraph remains splittable, including a scalar longer than a page. The entire error/group is never wrapped in an indivisible unit.
- `tests/unit/render/test_pdf_renderer.py:37-106`: ten added rendered-PDF cases cover both layouts, exact opening/continuation/mixed headers, decorative flowables, issue-index and appendix boundaries, report/capture scope labels, short detail `1`, and a multipage detail value with its final sentinel. All ten reproduced the original defects before the production changes.

Frozen renderer SHA256: `5aa5bab5d1d33c313430d78f2f6d8a6eb60f77d966787d2c3d2dff35bbda73f3`.

## Verification

Commands run from `/Users/ijaegyeong/Documents/data_handler/DataHelper`:

```sh
.venv/bin/python -m pytest tests/unit/render/test_pdf_renderer.py -q -k 'running_headers or message_labels' --tb=short
.venv/bin/python -m pytest tests/unit/render/test_pdf_renderer.py -q
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src/frameproof/render/pdf_renderer.py tests/unit/render/test_pdf_renderer.py tests/unit/render/pressure_fixtures.py
.venv/bin/python -m mypy src/frameproof/render/pdf_renderer.py
PYTHONPATH=src .venv/bin/python tests/unit/render/pressure_fixtures.py artifacts/qa/pdf-redesign-2026-09-11 --inspect
```

Results: targeted **10 passed**; renderer **42 passed in 3.50s**; full suite **175 passed in 18.49s**; Ruff and mypy passed. After strengthening the header assertion from suffix matching to exact normalized header equality, the ten targeted cases and Ruff passed again; production bytes did not change.

Rebuilt all eight pressure PDFs and their layout/raw extraction, info/font inventory, bbox XML, page rasters, and overview sheets under:

`/Users/ijaegyeong/Documents/data_handler/DataHelper/artifacts/qa/pdf-redesign-2026-09-11/`

Page counts remain unchanged: Korean full evidence **7/11**, issues overflow **75/94**, image/capture edges **19/26**, pagination/paths **14/14** (contact/detail). All **260 pages** rendered; the regenerated `artifact-inventory.json` reports **zero bbox boundary violations**. A coordinate-filtered check of each page's final body line found **zero stranded detail/scope labels**, saved in `fix-inspection/boundary-audit.json` with section-opening and long-tail context evidence.

Generated 25 additional 1600px page rasters with `pdftoppm -f N -l N -singlefile -scale-to 1600 -png` in `fix-inspection/`. Visually inspected these 17 pages:

- Korean full contact **2, 4** and detail **2, 6**: first and later clip header/body identities agree.
- Issues contact **7, 8**: page 7 ends with the complete `false` leaf; page 8 starts with `detail $["nested"]["list"][0]` immediately followed by `1`. Capture scope remains adjacent to its first warning.
- Issues detail **10, 11**: long-message tail, detail leaves, and Capture Start scope remain readable and connected.
- Issues contact **54, 55, 56, 60, 61** and detail **72, 73, 74, 78**: issue-index opening/continuation, appendix opening, repeated raw headers, multipage raw-value tail, and mixed appendix context agree with visible content. Contact page 61 correctly says `부록 · 클립 002 / 부록 · 클립 003`.

No visual defect remained in the inspected scope. Korean glyphs and body wrapping remain legible. Existing data/manifest, path, flags, image, font, oversized-row, and complete-tail checks all passed. Original failed QA extractions/rasters and `independent-qa/audit.py` were left untouched; this lane did not rerun that script because its default output location would overwrite the earlier QA evidence.

`fix-inspection/freeze-sha256.json` records the final production/test/fixture fingerprints, eight PDF hashes, and inventory hash. The previous wheel and installed-app payload were not rebuilt in this lane. The parent owns fresh Re-QA and subsequent approved packaging/deployment; this handoff is not a QA verdict.
