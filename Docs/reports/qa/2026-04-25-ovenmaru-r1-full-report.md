# DataHelper Oven Maru R#1 Full Report — 2026-04-25

status: succeeded

target folder:
/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1

valid clip count: 19
ignored AppleDouble/resource-fork .braw count: 19

output artifact directory:
/Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25

output artifacts:
- /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.pdf — 1,308,844 bytes
- /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.csv — 30,697 bytes
- /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.json — 134,287 bytes
- /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet-page-1.png — 246,538 bytes
- /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/stills — dir, 76 PNG stills, 1,876,094,144 bytes
- /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/run_frameproof.sh — 2,796 bytes
- /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/frameproof-run.log — 523 bytes

DataHelper command used:
```bash
#!/usr/bin/env bash
set -o pipefail
cd /Users/server_jay/Desktop/DataHelper
PYTHONPATH=src python3.11 -m frameproof --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151557_C001.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151557_C002.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151601_C003.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151603_C004.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151606_C005.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151610_C006.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151611_C007.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151612_C008.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151614_C009.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151615_C010.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151616_C011.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151616_C012.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151618_C013.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151646_C014.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151653_C015.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151658_C016.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151700_C017.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151704_C018.braw' --input '/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151705_C019.braw' --no-recursive --layout contact_sheet --middle-count 2 --export-stills --stills-dir /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/stills --braw-adapter-path tools/braw_adapter --project-name 'Oven Maru R#1 Full' --output /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.pdf --csv /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.csv --json /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.json 2>&1 | tee /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/frameproof-run.log
exit ${PIPESTATUS[0]}
```

DataHelper command result:
- exit code: 0 — PASS
- stdout/stderr log: /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/frameproof-run.log

DataHelper summary output:
```text
status: success
total_clips: 19
success_count: 19
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 0
pdf_path: /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.pdf
csv_path: /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.csv
json_path: /Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.json
```

verification results:
- target folder exists: PASS
- valid `.braw` enumeration excluding `._*.braw`: PASS (19 valid clips)
- PDF existence/non-empty: PASS (1,308,844 bytes)
- CSV existence/non-empty: PASS (30,697 bytes; 77 rows including header)
- JSON existence/non-empty/parseable: PASS (134,287 bytes)
- JSON total clips / success count: PASS (19 total / 19 success)
- JSON status: PASS (success)
- still export: PASS (76 PNG stills across 19 clip directories)
- first-page PNG preview generation: PASS (/Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet-page-1.png; 246,538 bytes)
- first-page visual sanity: PASS (readable contact sheet; header source summary is folder-level `.../001_video/260215/R#1`)
- native BRAW SDK path: PASS (`--braw-adapter-path tools/braw_adapter`; adapter counts {'braw_adapter': 19}; codec counts {'blackmagic_raw_native_sdk': 19})
- fallback status: no fallback observed; all clips decoded via `blackmagic_raw_native_sdk`
- relevant renderer smoke tests: PASS (`PYTHONPATH=src python3.11 -m pytest tests/unit/render/test_pdf_renderer.py -q` → 8 passed)

valid clip file sizes:
- A001_02151557_C001.braw: 4,150,917,734 bytes
- A001_02151557_C002.braw: 4,668,886,254 bytes
- A001_02151601_C003.braw: 3,508,517,094 bytes
- A001_02151603_C004.braw: 3,392,374,894 bytes
- A001_02151606_C005.braw: 2,157,215,378 bytes
- A001_02151610_C006.braw: 5,270,915,966 bytes
- A001_02151611_C007.braw: 1,951,878,682 bytes
- A001_02151612_C008.braw: 2,395,767,450 bytes
- A001_02151614_C009.braw: 2,075,459,542 bytes
- A001_02151615_C010.braw: 2,286,903,774 bytes
- A001_02151616_C011.braw: 2,446,685,023 bytes
- A001_02151616_C012.braw: 4,961,311,419 bytes
- A001_02151618_C013.braw: 1,829,477,795 bytes
- A001_02151646_C014.braw: 5,316,049,947 bytes
- A001_02151653_C015.braw: 10,666,596,851 bytes
- A001_02151658_C016.braw: 7,978,489,877 bytes
- A001_02151700_C017.braw: 8,026,127,169 bytes
- A001_02151704_C018.braw: 6,251,319,209 bytes
- A001_02151705_C019.braw: 10,237,520,497 bytes

important warnings/errors:
- None from DataHelper run: JSON warnings/errors are empty for all 19 clips.
- The source folder contains 19 AppleDouble/resource-fork sidecar files (`._*.braw`); they were intentionally excluded by passing only the 19 valid clip inputs.
- No source media was mutated, moved, deleted, renamed, transcoded, rewrapped, or copied into artifacts.

safe next step for Jun/Jay:
- Review `/Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet.pdf` and optionally `/Users/server_jay/Desktop/DataHelper/artifacts/reports/ovenmaru-r1-full-2026-04-25/ovenmaru-r1-full-contact-sheet-page-1.png` for first-page visual confirmation. If acceptable, this report set is ready to use/share from the artifact directory.
