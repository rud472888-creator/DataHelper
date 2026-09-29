# Compact PDF density implementation handoff

Date: 2026-09-11. Lane: fresh Dev / Implement. Status: implementation complete; independent implementation QA is required before delivery. The density plan and explicit plan-QA PASS were read before implementation. PDF and report-output-quality skills were applied; the already-completed artifact marker was not repeated.

## Result and contract

Nine ordinary clips now occupy **3 total pages in both layouts**, with three complete clips on every page including page 1. The frozen parent baseline is 20 contact / 34 detail pages. Ten ordinary clips and ten pressure clips occupy four pages; the last page contains clip 010 and no empty trailing page. Empty input intentionally produces one empty-state page.

The supplied `ReportItem` iterable is materialized once and remains the source of truth; clip/capture order, original values, capture selection, and supplied `BatchSummary` stay unchanged. PDF is a compact projection: identity/status, normalized format/codec/resolution/fps/duration/size/camera/TC/path metadata, aspect-fit previews, every supplied capture's request/actual position/TC/source/state, duplicate target, and bounded messages. Raw metadata and structured error-detail dumps are intentionally absent. There is no cover, issue index, appendix, repeated evidence section, or overflow page.

Both layouts use horizontal rows. Portrait A4 retains 75pt for the integrated intro and 222pt per clip; landscape Letter uses 64pt and 150pt. Metadata sits beside previews/timing, and messages use the complete row width. Portrait can use two message lines; landscape places error and warning excerpts side by side when both exist. This measured adjustment preserves useful warning/error prose at the required density. Contact previews show Start/nearest-to-0.5 Mid/End; detail shows every supplied capture. Preview caps are 49pt/43pt high, without cropping or stretching. Bundled fonts are preserved; body text is 8.3pt and supporting/timing text is 8pt. Every field is measured before visible `…(축약)` elision; final row/intro heights are checked before drawing.

Capture states and TC sources use explicit footer mappings. Missing preview availability never changes extraction state. Successful clips with warnings retain `success` and receive bold teal issue emphasis. Message counts include report/capture lists and are explicitly described as stored records including duplicates. Capture-scoped error excerpts precede warning excerpts and retain location/code. Path policy applies before elision, including known paths in messages; source literal markup is escaped without removing closing slashes. No companion availability or completeness claims are made.

`include_summary_page` remains accepted and selects the fuller integrated summary; `include_failed_section` adds optional inline issue-count emphasis. Neither creates a separate section/page, and neither hides essential failures/messages. Public renderer functions, dispatch, page sizes, settings/models/adapters, font assets, CSV/JSON writers, output flags and filenames were not edited. Existing and concurrent changes outside this lane were preserved.

## Verification

- `.venv/bin/python -m pytest tests/unit/render/test_pdf_renderer.py -q`: **31 passed**. Tests replace superseded raw-completeness expectations with actual PDF density, captured source values/order versus manifests, zero-capture identity, failure/duplicate/missing states, useful warnings, bounded Korean/path/markup cases, both flags/layouts, no-companion omissions, summary mismatch, font embedding and page dimensions. Image precedence/orientation/aspect fit and representative-Mid tie ordering remain covered.
- `.venv/bin/python -m pytest`: **164 passed in 14.66s**, including CLI/integration, manifest/output and all renderer tests.
- `.venv/bin/python -m ruff check src tests`: **PASS**.
- `.venv/bin/python -m mypy src`: **PASS**, 43 source files.
- `git diff --check`: **PASS**.
- `.venv/bin/python ../.pipeline/pdf-density-qa/compare_density.py after`: contact/detail **3 pages each** from the identical parent fixture. Before artifacts were retained.
- `../DataManager/.venv/bin/python ../.pipeline/pdf-density-qa/audit_density.py after`: **PASS**, three ordered IDs per page, every actual TC, required codec/fps, minimum 8pt, no appendix, zero page-bounds violations.
- `.venv/bin/python tests/unit/render/density_fixtures.py artifacts/qa/pdf-density-2026-09-11`: six pressure/density PDFs generated. Fixture covers 2/3/4/5 captures, 9/10 clips, long Korean title/phrase, mixed identifier, portrait/panorama/EXIF frames, missing/corrupt previews, failed capture and duplicate target, successful clip warnings, zero/missing values, oversized name/path/prose, literal markup, split count, and companion-disabled output.
- All eight final PDFs (six fixture PDFs plus two parent comparison PDFs) were inspected programmatically with pypdf/Poppler: minimum **8pt**, embedded regular/bold Korean fonts, expected page counts, **zero bounding-box violations**. Text, font inventories, PDF hashes and all-page 150dpi rasters are durable below.
- Personally inspected all six final parent comparison pages and all eight final pressure/no-companion pages at 150dpi, including first-page three clips, five-capture rows, errors/long Korean, literal markup, zero capture, portrait/EXIF handling and clip 010 final page. No clipped text, overlaps, broken Korean or distorted previews were found. Additional ten-ordinary-clip PDFs were count/text/bounds checked; their identical ordinary row geometry and final-page layout are covered by the inspected comparison/pressure files.

Parent separately reports a four-MP4/MOV, two-replica orchestration E2E PASS with two-page report outputs at this exact renderer hash; evidence is `../.pipeline/pdf-density-qa/workflow-results.json`. This lane did not perform app deployment or claim independent QA PASS.

## Durable artifacts and frozen sources

Base comparison: `/Users/ijaegyeong/Documents/data_handler/.pipeline/pdf-density-qa/DEBUG-DATA-nine-clips-before-contact_sheet.pdf` and `DEBUG-DATA-nine-clips-before-detail.pdf`; final comparisons use the same names with `after`. Baseline/new counts and independent audit JSON are in that directory.

Pressure artifacts: `/Users/ijaegyeong/Documents/data_handler/DataHelper/artifacts/qa/pdf-density-2026-09-11/`. PDFs use `DEBUG-DATA-{nine-clips,ten-clips,pressure-no-companions}-{contact_sheet,detail}.pdf`. `DEBUG-DATA-source-fixtures.json` is the supplied model snapshot. `artifact-inventory.json` records each final PDF hash, count, minimum text size and raster directory; `raster/<PDF-stem>/page-N.png` contains 150dpi pages. Neighboring `.txt`, `.bbox.html` and `.fonts.txt` files preserve extraction evidence.

Frozen SHA-256 inputs for independent QA:

- Renderer `src/frameproof/render/pdf_renderer.py`: `8e2854f0740d3214ffde478a590cdf957af09d47521dff7ac404637b4fce0f9f`.
- Renderer tests: `888039016915c7d8488036176ea33bf0bbee1d31655453763aa9ad111aef26c9`.
- New density fixture: `c29e558253b476b07d03130753881ecc3a9c2c6f3a18d2c0e030c41ef2fe02e7`.
- Parent `density-source-fixtures.json`: `14af478446d837b5da1afa888ead25c1adea1c5c350bc43813ea03cc86cd9a12`.
- Pressure source snapshot: `eef25044faefe2b4277f817bdf6b1c5ba28ca6e7c2e3c6195c3c83e41dabd0c5`.

This lane changed only the renderer, its unit tests, new focused density fixture, this handoff, and generated density evidence. Fresh QA should independently verify the frozen source/artifact hashes and compact contract, then return explicit PASS/FAIL. Raw metadata/detail omission and marked abbreviation are accepted scope, not missing-evidence defects under the superseded full-evidence design.
