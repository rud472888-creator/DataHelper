# DataHelper PDF redesign - independent QA

Date: 2026-09-11
Lane: fresh QA session; read-only production review
Result: **FAIL - first implementation QA; two layout defects require a fresh Fix and Re-QA.**

No production or test file was changed by this lane. This verdict applies to renderer SHA256 `377c45573f972988e7e4397c8ed0abbcdb6ae3db102d59909e85cfb42928af7c`, the final 260-page pressure artifact set, and the source fingerprints in `artifacts/qa/pdf-redesign-2026-09-11/independent-qa/audit-results.json`. The source fingerprints remained identical during the final audit. Later edits invalidate this acceptance scope. Data/content checks pass; they do not override the failed layout gate.

## Findings in severity order

### P2 - A new clip page retains the preceding clip's running header

`DEBUG-DATA-korean-full-evidence-contact.pdf`, page 4, contains the heading `002 / ...TAIL-002.mov`, identity `clip-002`, and that clip's frames, while its top-right running header says `클립 001`. The corresponding detail first-clip page 2 still says `보고서 개요`. Other section transitions inherit the same timing problem. The prominent body identity is correct and all data remains present, but the page carries conflicting clip context, which weakens standalone page review and handoff.

Cause: `src/frameproof/render/pdf_renderer.py:260` draws `self.section_name` in `onPage`, before `afterFlowable` updates it at lines 266-269. Fix the page-context timing or use a truthful neutral section label; preserve correct continuation-page context. Do not merely change the clip body heading or source ordering.

Independent evidence: `artifacts/qa/pdf-redesign-2026-09-11/independent-qa/full-contact-4.png` (1600-pixel raster), the corresponding independent `.raw.txt` and `.bbox.html` extraction, and original page 4. Re-QA must check the first clip, a later clip, issue-index transition, raw appendix transition, and continuation pages in both layouts.

### P2 - An error-detail key is stranded on the preceding page

`DEBUG-DATA-issues-overflow-contact.pdf`, page 7, ends with `detail $["nested"]["list"][0]`. Its short value `1` appears alone at the top of page 8. The first raw audit leaf of the next page has no visible key beside it. The full source value is preserved, but this breaks a small semantic key/value unit and makes the error evidence harder to interpret at a page boundary.

Cause: `src/frameproof/render/pdf_renderer.py:455` and `:456` append key and value as unrelated Paragraphs without a keep relationship. Keep each detail label with at least the first line of its value, while retaining splitting for a value longer than a page. Apply the same semantic-heading check to the `Report messages` and `Capture <label>` scope labels at line 449.

Independent evidence: `artifacts/qa/pdf-redesign-2026-09-11/independent-qa/issues-contact-07.png` and `issues-contact-08.png` (1800-pixel rasters). `pdftotext -f 7 -l 8 -layout` independently reproduces the boundary. Re-QA must verify this exact fixture, scope labels, and long-value continuation in both layouts.

These are presentation defects, not missing source data, decoder failures, or checksum failures. No additional data-fidelity blocker was found.

## Contract and code inspection

Read `AGENTS.md`, the 2026-09-11 redesign plan, and its plan-QA addendum approving frames near clip headings plus the ordered raw appendix. Applied the PDF and report-output-quality skills and their gate, data contract, PDF, Korean, verification, and pressure references. The parent's artifact marker was not repeated.

Authoritative input remains the materialized supplied `ReportItem` tuple, supplied `BatchSummary`, and `AppSettings`. The renderer does not probe footage, reorder items, synthesize capture rows, or change timecode/capture logic. Code inspection covered the renderer, model validations, settings, manifest writer, fixture builder, tests, font assets, and package-data declaration.

Verified the complete contract:

- Full project/clip/logical names, ID, source and ordered parts, family/adapter, source scope/settings, local offset-aware generation time, layout and missing-value legend.
- Container/codec, exact bytes, seconds, frame count, rational and decimal fps, dimensions, camera make/model/ID, reel, stored start/end TC and its source/drop-frame flag. Missing values remain distinct from zero/false.
- Every supplied capture label/status, requested ratio/frame/seconds, actual frame/seconds/TC/source, duplicate target, and exported still reference. Temporary image paths are not printed as durable references. The fixtures deliberately make requested and actual positions differ.
- Item `Report messages` and capture-scoped warnings/errors remain complete and ordered, with error code, full message and all detail leaves. Successful clips with messages contribute to the separate warning/error counts; unsuccessful status totals are not relabeled as warning totals.
- All raw metadata keys/leaves, typed values, nested objects/lists, empty collections, null, long values and final sentinels survive in deterministic ordered appendices. Markup-looking source text is escaped. Every main clip appears before the raw appendix.
- Public dispatcher and direct layout functions retain their signatures and layout sizes. Full/basename/hidden paths, summary/index booleans, empty documents, mismatched supplied summaries, duplicate and zero-capture entries are exercised by the independent test run. Source mappings remain unmodified. Manifest source ordering includes the zero-capture identity row.
- Contact selects Start/nearest-to-middle/End; all captures remain in the evidence table. Detail shows all images. Gallery captions include actual TC/frame/seconds. Missing/corrupt previews explicitly report their availability independently of extraction success. Portrait, panorama, EXIF rotation, 1x1 and large images retain aspect fit and all asymmetric edge markers.

## Independent commands and results

From `/Users/ijaegyeong/Documents/data_handler/DataHelper`:

```sh
.venv/bin/python -m pytest tests/unit/render/test_pdf_renderer.py -q
.venv/bin/python -m pytest
.venv/bin/python artifacts/qa/pdf-redesign-2026-09-11/independent-qa/audit.py
```

- Focused final renderer tests: **32 passed in 3.33s**, no skips. `independent-qa/focused-tests-final.log`.
- Full DataHelper suite: **165 passed in 16.45s**, no skips. `independent-qa/full-suite-final.log`. Includes unchanged output/manifest and still-export behavior.
- Independent content/bounds audit: **PASS, 8 PDFs, 260 pages, zero content failures**, `independent-qa/audit-results.json` and `audit-console.log`.

The audit reads the saved JSON fixtures without regenerating or changing them, freshly runs `pdftotext -raw`, `pdfinfo`, `pdffonts` and `pdftotext -bbox-layout`, and checks every clip/capture sequence, every capture column's ordered values, identity/media values, full warnings/errors/details, and every raw leaf within its own appendix clip segment. Fixture path display is the configured `basename`; recognized stored source paths are independently transformed before comparison. Repeating page furniture/table headers are removed only for continuous long-value comparisons. Source fingerprints, PDF hashes and per-file totals are retained. No page has an empty content body or text outside the checked page bounds. Bounds alone cannot detect the two semantic layout defects above.

## Artifact inventory and visual inspection

All files below are under `artifacts/qa/pdf-redesign-2026-09-11/`. Each has the original `.txt`, `.raw.txt`, `.info.txt`, `.fonts.txt`, `.bbox.html`, all page rasters, and overview sheets. Independent fresh extractions are under `independent-qa/`.

| Fixture | Contact pages | Detail pages |
| --- | ---: | ---: |
| `DEBUG-DATA-korean-full-evidence` | 7 | 11 |
| `DEBUG-DATA-issues-overflow` | 75 | 94 |
| `DEBUG-DATA-capture-and-image-edges` | 19 | 26 |
| `DEBUG-DATA-pagination-and-paths` | 14 | 14 |
| Total | 115 | 145 |

The frozen set is **260 pages**, superseding the earlier 249-page implementation snapshot. Original inventory and raster counts were checked against freshly read PDFs.

Viewed all **16 overview sheets**, covering every page of all 8 PDFs. The sheets show the first/last pages, raw appendices, long-warning/long-raw continuations, missing/corrupt/zero-capture outputs, multi-page issue indexes and pagination. Readable-resolution inspection additionally covered full-evidence contact pages 1, 3 and 4; detail pages 2, 3 and 5; image-edges contact page 8; and independent 1800-pixel issues-contact pages 7-8. These establish the cover hierarchy, Korean body/table typography, metadata/capture tables, landscape/portrait/panorama/rotated image fit, corrupt and skipped placeholders, actual-position captions, and both reported defects. No overlap, clipped essential field, missing Korean glyph, or mid-word ordinary Korean prose break was seen in these readable-resolution pages. Long filenames may wrap within the identifier as allowed.

`pdffonts` confirms embedded/subset/Unicode-mapped DataHandlerSans Regular and Bold in all eight PDFs. The independent ZIP inspection in `independent-qa/wheel-font-check.json` confirms both TTFs, OFL and provenance README are packaged and byte-identical to checkout assets. The package declares `reportlab>=4.5` for `splitInRow` support.

## Boundaries and next gate

This is a synthetic renderer QA gate. It does not verify real-camera footage, full-stream decoding, cross-replica equality, color accuracy, live pipeline runs, app bundling/signing, or deployment. Parent owns pipeline/package integration. No pipeline run or source-footage mutation was performed. The dated implementation handoff had not yet appeared when this first FAIL was written; it must be read by fresh Re-QA along with the Fix handoff. No extra adversarial PDFs were generated after the two reproducible layout blockers were confirmed.

Required next step: a fresh bounded Fix lane resolves the two findings, regenerates pressure PDFs/extractions/rasters, records its new source fingerprint and handoff, and a fresh Re-QA lane returns explicit PASS/FAIL. This report does not authorize stage advancement.
