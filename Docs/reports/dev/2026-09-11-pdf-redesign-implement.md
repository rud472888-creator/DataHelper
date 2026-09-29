# DataHelper PDF redesign implementation handoff

Date: 2026-09-11

Lane: fresh Dev / Implement session. Status: IMPLEMENTED; independent QA gate is still required. This document does not declare production QA PASS.

Read on entry: `AGENTS.md`, `Docs/reports/dev/2026-09-11-pdf-redesign-plan.md`, and the explicit plan PASS in `Docs/reports/qa/2026-09-11-pdf-redesign-plan-qa.md`. Applied PDF and report-output-quality skills and their contract, Korean, pagination, pressure, and verification references. The parent had already performed the artifact marker; this worker did not repeat it.

## Changed files and ownership

- `src/frameproof/render/pdf_renderer.py`: complete replacement of the legacy coordinate/card renderer with a pure presentation projection and Platypus document story.
- `tests/unit/render/test_pdf_renderer.py`: replaced coordinate/raw-compressed-stream assertions with 32 meaningful projection, PDF extraction, path, image, public API, settings, font, and pagination tests.
- `tests/unit/render/pressure_fixtures.py`: new deterministic source-model/image fixture builder and Poppler extraction/raster/contact-sheet inspector.
- `pyproject.toml`: package both supplied TTF faces, OFL and font provenance; raise ReportLab minimum from 4.0 to 4.4 at the parent's request.
- This dated implementation report.

Parent-provided `render/fonts/DataHandlerSans-Regular.ttf`, `DataHandlerSans-Bold.ttf`, `OFL.txt`, and `README.md` were used without conversion or modification. No adapters, capture/timecode algorithms, manifest code, still exporter, DataManager, orchestrator, source media, global stage/status documents, or unrelated work were changed. No separate production helper module was added.

Frozen production renderer SHA256: `377c45573f972988e7e4397c8ed0abbcdb6ae3db102d59909e85cfb42928af7c`.

Frozen `pyproject.toml` SHA256: `aae73cb7c47361e5ae6105f131436477c91c041d9c1b26fe34ad90d55d786bb5`.

## Completed contract and final layout

The authoritative inputs remain one materialized tuple of `ReportItem`, the supplied `BatchSummary`, and `AppSettings`. `_project_report` performs presentation only; it neither probes media nor changes selection, values, order, or status.

The final story contains the full project title; local offset-aware generation time; report layout; ordered input paths; capture profile, configured middle count and frame/seconds preference; recursion/extensions; supplied summary categories; rendered item count; independently counted warning/error-bearing clips; and every capture status count. The conditional mismatch note explains when supplied totals and rendered scope differ. Missing values are `-`, zero and false remain explicit, times/ratios have three decimal places, and FPS includes its exact rational value.

Every clip keeps the full ID/name/logical name, displayed source/ordered part paths, format family and adapter; all requested media/camera/reel/TC/drop-frame metadata; every canonical capture row with requested and actual values, actual timecode provenance, duplicate target, extraction status, and durable exported still reference; all ordered report/capture warnings/errors including error code, message and nested detail. Temporary preview paths are never printed as handoff references. Missing or corrupt preview images are reported separately from extraction status.

Complete raw metadata remains present in deterministic reversible JSON key paths and typed scalar representations, including nested arrays, null, false, zero, empty mappings/lists, and the last key/value. Recognized raw path fields receive the selected path presentation policy without mutating the stored mapping. No key, message, line, or collection cap remains.

The parent requested these final refinements after inspecting integration output; they supersede only the original plan's section placement, not its data contract:

1. Put the gallery directly below clip title/status and a compact media line, ahead of the complete identity/media tables.
2. Put all raw metadata in a separately identified appendix after all clip review/evidence sections and the optional issue index. Use repeating two-column ruled key/value tables so the reader can browse all image evidence first.
3. Add prominent rendered-clip, normal-processing and warning-bearing-clip numerals. User-facing labels are `정상 처리`, `전체 클립`, and `캡처 지점`; implementation provenance appears only in the conditional scope note when necessary.
4. Include actual TC, actual frame index and actual seconds in each image caption, as well as extraction status. Missing actual values remain missing, including skipped duplicates.

Both public layout entry points and dispatcher signatures are unchanged. Contact remains A4 portrait; detail remains landscape Letter. The cover setting controls the dedicated opening page break while retaining essential scope/counts. Empty input produces one intentional empty-report page for the tested settings, including a mismatched supplied summary. The failed-section setting controls only the repeated non-success index; inline evidence remains. PDF document properties include the full title, `Data Handler` author, `DataHelper` creator and sampled-frame subject without injected source paths.

Visual system: white page, graphite text, one deep teal accent and thin rules; 42pt side margins, 52pt top and 45pt bottom reserves; 29pt cover, 17pt clip title, 14pt section title, 9pt body/13.5pt leading and 8pt supporting labels. Embedded regular/bold Data Handler Sans covers Korean and Latin consistently. Normal prose keeps word boundaries; oversized identifiers and path tokens can break without truncation. All source markup is escaped before Paragraph creation.

Images are read from the exported reference before the temporary path, EXIF-oriented and aspect-fit. Preview-size JPEG data is embedded with quality 86 and a 1600px cap. Contact uses Start / the nearest-to-0.5 middle (tuple order breaks ties) / End, with an explicit unconfigured-middle label. Detail shows every capture image. Gallery rows are bounded indivisible tables; the first gallery stays with its title/status context. The full capture table is retained for all images, including unavailable previews.

## Fixtures and artifacts

All durable fixture artifacts are under:

`/Users/ijaegyeong/Documents/data_handler/DataHelper/artifacts/qa/pdf-redesign-2026-09-11/`

Source models were authored and saved **before** production implementation using the builder's `--sources-only` option. `DEBUG-DATA-source-fixtures.json` preserves all model fields; `images/` contains synthetic edge-marked landscape, portrait, panorama, tiny, large, EXIF-rotated, corrupt and missing-reference examples. Debug markers appear in fixture names, titles and source-model content; there is no automatic production debug inference.

Final PDFs and page counts:

| Fixture | Contact | Detail |
|---|---:|---:|
| `DEBUG-DATA-korean-full-evidence` | 7 | 11 |
| `DEBUG-DATA-issues-overflow` | 75 | 94 |
| `DEBUG-DATA-capture-and-image-edges` | 19 | 26 |
| `DEBUG-DATA-pagination-and-paths` | 14 | 14 |

PDF filenames append `-contact.pdf` or `-detail.pdf` to the fixture name. The long issue fixture intentionally has 17 clips, repeated scoped messages, and single values spanning multiple pages; its large page count reflects preserved stress data.

For each final PDF the same directory contains `.txt` (layout extraction), `.raw.txt` (drawing-order extraction), `.info.txt`, `.fonts.txt`, `.bbox.html`, and numbered overview `-sheet-XX.png` files. `raster/<PDF-stem>/page-N.png` contains **every** page; representative fixtures use a 1300px maximum dimension, long issue fixtures 700px. `artifact-inventory.json` lists final page counts, font inventories and page-boundary violations. The inspector clears its previous generated page rasters before each run to avoid stale page-count evidence.

Extra 1500px inspection images are named `inspect-issues-overflow-contact-page-{7,54,55,58,60}.png` and `inspect-issues-overflow-detail-page-78.png`. They show the long-message final sentinel, issue-index continuation, repeated raw table headers, long raw continuation, and final raw sentinel.

Path-mode, flag matrix, empty/mismatched summary, and single oversized identity/export-reference cases are also reproduced by the renderer test file, using temporary artifact directories. Their settings/source creation is explicit in that file. The oversized row test uses a 1200-repeat Korean path token and proves both final references survive without LayoutError.

The parent retains responsibility for the synthetic pipeline replay and integration artifacts. This worker did not run a newly authorized copy operation, re-probe the parent sample, or claim real-camera, full-stream, checksum, color, or cross-replica validation.

## Commands and results

All commands below were run from `/Users/ijaegyeong/Documents/data_handler/DataHelper` unless noted otherwise.

```sh
PYTHONPATH=src .venv/bin/python tests/unit/render/pressure_fixtures.py artifacts/qa/pdf-redesign-2026-09-11 --sources-only
.venv/bin/python -m pytest tests/unit/render/test_pdf_renderer.py -q
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src/frameproof/render/pdf_renderer.py tests/unit/render/test_pdf_renderer.py tests/unit/render/pressure_fixtures.py
.venv/bin/python -m mypy src/frameproof/render/pdf_renderer.py
PYTHONPATH=src .venv/bin/python tests/unit/render/pressure_fixtures.py artifacts/qa/pdf-redesign-2026-09-11 --inspect
```

Final full-suite result: **165 passed in 16.19s**, including all **32 renderer cases**. Ruff: **All checks passed**. Mypy: **Success: no issues found in 1 source file**. Earlier failing assertions were corrected for typed JSON quote escaping and extraction order, and a page-number regex was corrected to avoid concatenating the following clip number. The final production revision has no failing tests. Existing CSV/JSON and still-export tests remained unchanged and passed within the full suite.

Actual output checks cover PDF headers, page size, full document title, embedded regular/bold TrueType subsets with Unicode maps, Korean title and prose extraction, complete tail identifiers and sentinels, all four TC-source enums, explicit false/null/zero, markup-looking source strings, missing/corrupt images, zero-capture identity, success-with-warning counting, all path modes in both layouts, all summary/index flag combinations, supplied summary mismatch, oversized table rows, and unique Page N numbering.

An actual PDF extraction test isolates each clip's capture-evidence section and compares the ordered `(clip_id, capture_label)` rows with `build_manifest_rows(items)`, including the zero-capture identity row. A separate pure-projection test confirms the same order and preserves missing duplicate actual values.

Poppler rendered **all 260 final pages**. The bbox audit found **0 words outside the reserved page-boundary region**. The audit is a boundary check, not a substitute for visual inspection. Overview sheets were inspected for all main fixture pages and long issue pages; full-resolution inspection covered both covers, first clip/gallery, capture table, appendix, placeholders, portrait/panorama/rotated frames, issue continuation, and long-value tails. Frames remain uncropped/unstretched, Korean text renders without missing-glyph blocks, and long content continues with intact tail values. No accidental fully blank page was observed.

Wheel packaging was checked using the bundled runtime:

```sh
/Users/ijaegyeong/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip wheel --no-deps --no-build-isolation --wheel-dir artifacts/qa/pdf-redesign-2026-09-11/wheel .
```

Final wheel: `wheel/frameproof-0.1.0-py3-none-any.whl`, SHA256 `ddcf354e6b9f8b73e9cb6b47e2c97a6abb8c26a84c06b69a36a07380e5ed0aff`. The archived renderer bytes were compared with the frozen checkout; both supplied TTFs and OFL are present. The wheel was extracted into `/private/tmp/datahelper-pdf-installed-wheel`. A separate Python process run from `/private/tmp` with only that package directory first on `PYTHONPATH` rendered Korean contact/detail reports, asserting `renderer.__file__` was inside the extracted wheel. Its font directory resolved inside the wheel rather than the checkout/system fonts. Outputs: `wheel-smoke/DEBUG-DATA-installed-contact_sheet.pdf` and `wheel-smoke/DEBUG-DATA-installed-detail.pdf`.

## Known limitations and next gate

No known data-loss, status-substitution, path-policy, embedded-font, API, or source-modification defect remains in the checked cases. Independent QA must still make its own acceptance decision.

Two visible polish limitations were explicitly reported to the parent at the production freeze:

- The running header is drawn before the page's story, so the first page of a new clip/appendix may retain the preceding section name. The body heading correctly identifies the new section and following continuation pages identify the current section.
- In the long issue fixture, an individual error-detail key label can end one page while its scalar value begins the next (for example contact page 7 to 8). All keys/values remain present; this small semantic unit can be kept together more tightly in a future Fix lane if QA requires it.

Shorter metadata groups and bounded image rows may leave deliberate whitespace. Complete raw metadata and long scoped messages produce more pages than the truncated baseline; no truncation is used to force a target page count. Arbitrary non-JSON custom Python objects inside raw mappings are displayed using their string representation; the tested authoritative payload uses JSON-like scalars, mappings and lists.

The parent should run the fresh independent QA gate against the frozen renderer fingerprint, integrate its orchestrator replay evidence, and rebuild/deploy only the approved app PDF payloads. QA must not silently fix code or treat this implementation handoff as QA PASS.
