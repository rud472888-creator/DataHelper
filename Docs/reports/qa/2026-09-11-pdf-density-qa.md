# PDF density implementation QA

Date: 2026-09-11. Lane: fresh independent QA. Result: **PASS**.

No material issues found against the approved compact contract: three complete clip rows per full page, starting on page 1, and no appendix. Read repository `AGENTS.md`, the September 11 density plan, its explicit plan-QA PASS, and the implementation handoff. Raw metadata and structured error-detail dumps are deliberately omitted by this revision; the superseded full-PDF contract was not reapplied. No production or test fixes were made.

## Independently verified artifacts

Verified the final renderer SHA-256 is `8e2854f0740d3214ffde478a590cdf957af09d47521dff7ac404637b4fce0f9f`. The renderer test, density fixture, parent source snapshot, and supplemental source snapshot hashes also match the implementation handoff. They were checked again after the audit. Exact paths and hashes, including all eight PDF hashes, are recorded in [audit-results.json](../../../artifacts/qa/pdf-density-2026-09-11/independent-qa/audit-results.json).

| Frozen PDF family | Contact pages | Detail pages | Clip rows by page |
| --- | ---: | ---: | --- |
| Parent nine-clips-before baseline | 20 | 34 | Baseline page count only |
| Parent nine-clips-after | 3 | 3 | 3 / 3 / 3 |
| Supplemental nine-clips | 3 | 3 | 3 / 3 / 3 |
| Supplemental ten-clips | 4 | 4 | 3 / 3 / 3 / 1 |
| Supplemental pressure-no-companions | 4 | 4 | 3 / 3 / 3 / 1 |

The parent final PDFs are `../.pipeline/pdf-density-qa/DEBUG-DATA-nine-clips-after-{contact_sheet,detail}.pdf`. Supplemental PDFs are in `artifacts/qa/pdf-density-2026-09-11/`. The independent audit opens the actual PDF files and reads expected values from the saved `density-source-fixtures.json` and `DEBUG-DATA-source-fixtures.json`; it imports no production renderer or presentation projection to construct expectations.

Across all eight final PDFs, all **28 pages and 244 capture rows** passed checks for ordered clip IDs, complete ordinary names, clip status, report/capture warning and error counts, normalized format/container/codec, resolution, fps rational/decimal, duration/frame count/byte size, camera/reel, stored TC/source/drop-frame values, adapter, basename source display, logical name where different, and split count. Every supplied capture retained its label/order, state, requested and actual frame/seconds, ratio, actual TC/source, and duplicate target. Real requested/actual differences and elapsed fallback remain visible. Zero-capture identity records remain present.

The two main PDFs retain the useful success warning `start_timecode_missing - 시작 타임코드 수동 확인 필요`, beyond the `DEBUG DATA` prefix. Pressure clip 004 visibly remains `partial_success`; Mid2 is `실패` with `decode_failed` and a useful instruction to check source media, while End is `중복` targeting Start with absent actual values. The capture-scoped warning is visible alongside error content, with counts `외 3건` and `외 1건`. In detail, missing Mid1 preview is clearly labeled `파일 없음` while capture state remains normal. Corrupt Mid2 preview is labeled `이미지 읽기 실패`. This distinguishes preview availability from extraction status.

Pressure clip 007 preserves `probe_failed`, `0 bytes`, `0.000 s`, missing metadata markers, and zero captures. Clip 009 retains the complete frozen warning string, including literal `<b>literal message</b>` and its closing slash, plus the different logical name and two-part count. Oversized identity preserves `IDENTITY-FINAL-SUFFIX.mov` with visible `축약`. There is no appendix, issue index, raw sentinel, structured-detail sentinel, private-path prefix, or invented CSV/JSON companion destination in pressure output.

## Rendering and regression checks

Fresh Poppler extraction and pypdf font inspection report an **8pt minimum text size** in every final PDF. Used regular and bold DataHandlerSans fonts are embedded with Unicode mappings. Korean text is extractable. Word bounding checks found **zero violations** against the reserved page margins across all 28 pages.

Re-rasterized the main and pressure PDFs directly at 150 dpi into the independent evidence directory. Personally inspected all **six main pages** and pressure **pages 2, 3, and 4 in both layouts** (12 pages total), not a montage. All main pages have three complete, readable rows including page 1. Five-capture rows, portrait/panorama/EXIF-oriented previews, failure placeholders, Korean warning lines, literal markup, zero-capture row, abbreviation boundaries, and the last clip 010 are legible. No text/image overlap, clipped critical state, orphan message label, distorted preview, or blank trailing page was found. Running header clip ranges and page numbers match content. The final one-row page is the expected remainder.

Ran `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/unit/render/test_pdf_renderer.py -q -p no:cacheprovider --basetemp=artifacts/qa/pdf-density-2026-09-11/independent-qa/pytest`: **31 passed in 2.93s**. This includes both summary/issue flags, FULL/BASENAME/HIDDEN message-path policies, literal escaping, manifest order including zero-capture records, compact omissions, empty input/summary mismatch, preview precedence/orientation, representative Mid selection, public dispatch, and page dimensions. Test log: [pytest-renderer.txt](../../../artifacts/qa/pdf-density-2026-09-11/independent-qa/pytest-renderer.txt).

The independent audit script and fresh extraction/font/bounds evidence are under `artifacts/qa/pdf-density-2026-09-11/independent-qa/`; its result is PASS. This QA did not rerun the full application suite, lint/type checks, or real-media orchestration; the implementation handoff and parent integration evidence cover those separately. App installation/signing remains parent-owned and is not claimed by this report.

This PASS clears the implementation QA gate for the exact renderer hash above. This lane wrote only this report and its own `independent-qa/` evidence. Frozen sources/PDFs, application source/tests, stage/status files, and other workers' changes were preserved. The artifact marker was not repeated.
