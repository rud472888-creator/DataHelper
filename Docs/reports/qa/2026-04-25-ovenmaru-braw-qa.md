# DataHelper Oven Maru BRAW QA Report

## Summary
- status: PASS
- real_braw_processed: yes
- native_braw_sdk_path: yes
- fallback_or_proxy_used: no
- sample_count: 3
- output_dir: /Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/

## Commands Run
- `.venv/bin/python --version`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: Python 3.11.9.
- `.venv/bin/python -m frameproof --help`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: CLI exposes `--input`, `--output`, `--layout`, manifests, still export, and `--braw-adapter-path`.
- `.venv/bin/python -m frameproof config --format json`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: config diagnostics worked; no config file present at the default path.
- `printf ... | tools/braw_adapter`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: adapter version succeeded with `adapter_version=2.0.0-native-sdk`, `native_no_proxy=true`, helper `tools/braw_native_helper`, SDK libraries `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries`.
- `.venv/bin/python -m pytest tests/integration/test_native_braw_adapter.py -q`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: 2 passed.
- `.venv/bin/python -m pytest tests/integration/test_raw_dependency_missing.py tests/integration/test_cli_standard_pipeline.py tests/test_cli.py -q`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: 16 passed.
- `printf ... | tools/braw_adapter | tee artifacts/qa/ovenmaru-braw-2026-04-25/adapter-probe-sample.json`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: known sample probed successfully through native BRAW SDK path.
- `.venv/bin/python -m frameproof --input /Volumes/HOTDRIVE/.../A001_02151557_C001.braw --output artifacts/qa/ovenmaru-braw-2026-04-25/sample-contact-sheet.pdf --layout contact_sheet --middle-count 0 --export-stills --stills-dir artifacts/qa/ovenmaru-braw-2026-04-25/stills --braw-adapter-path tools/braw_adapter`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: `status: success`, `total_clips: 1`, `success_count: 1`.
- `.venv/bin/python -m frameproof --input /Volumes/HOTDRIVE/.../A001_02151557_C002.braw --input /Volumes/HOTDRIVE/.../A001_02151601_C003.braw --output artifacts/qa/ovenmaru-braw-2026-04-25/nearby-two-contact-sheet.pdf --layout contact_sheet --middle-count 0 --braw-adapter-path tools/braw_adapter`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: `status: success`, `total_clips: 2`, `success_count: 2`.
- `find artifacts/qa/ovenmaru-braw-2026-04-25 -type f -maxdepth 3 -print0 | xargs -0 stat -f '%z %N'`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: generated artifacts are present and non-empty.
- `file artifacts/qa/ovenmaru-braw-2026-04-25/*.pdf artifacts/qa/ovenmaru-braw-2026-04-25/*.csv artifacts/qa/ovenmaru-braw-2026-04-25/*.json`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: PDFs, CSVs, and JSON files identified with expected file types.
- `find artifacts/qa/ovenmaru-braw-2026-04-25/stills -type f -name '*.png' -print0 | xargs -0 file`, cwd `/Users/server_jay/Desktop/DataHelper`, exit_code 0, result: exported stills are 6048x4032 PNG images.

## Media Samples
- `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151557_C001.braw`, size 4,150,917,734 bytes, mtime Feb 15 17:57:22 2026, probe: 585 frames, 19.5195 seconds, 6048x4032, start timecode `15:57:02:19`, codec `blackmagic_raw_native_sdk`, metadata complete.
- `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151557_C002.braw`, size 4,668,886,254 bytes, mtime Feb 15 17:58:17 2026, manifest: 635 frames, 21.1878 seconds, 6048x4032, start timecode `15:57:55:07`, codec `blackmagic_raw_native_sdk`.
- `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151601_C003.braw`, size 3,508,517,094 bytes, mtime Feb 15 18:02:00 2026, manifest: 555 frames, 18.5185 seconds, 6048x4032, start timecode `16:01:40:21`, codec `blackmagic_raw_native_sdk`.
- AppleDouble/resource-fork files named `._*.braw` were not used.

## Outputs Verified
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/adapter-probe-sample.json`, 801 bytes, non-empty JSON.
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/sample-contact-sheet.pdf`, 92,780,865 bytes, non-empty PDF.
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/sample-contact-sheet.csv`, 930 bytes, non-empty CSV.
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/sample-contact-sheet.json`, 3,926 bytes, non-empty JSON with `status=success`, `total_clips=1`, `success_count=1`.
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/stills/A001_02151557_C001.braw/A001_02151557_C001.braw_start_15_57_02_19.png`, 27,371,340 bytes, non-empty 6048x4032 PNG.
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/stills/A001_02151557_C001.braw/A001_02151557_C001.braw_end_15_57_22_03_calculated.png`, 26,386,734 bytes, non-empty 6048x4032 PNG.
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/nearby-two-contact-sheet.pdf`, 185,280,617 bytes, non-empty PDF.
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/nearby-two-contact-sheet.csv`, 1,132 bytes, non-empty CSV.
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/nearby-two-contact-sheet.json`, 6,678 bytes, non-empty JSON with `status=success`, `total_clips=2`, `success_count=2`.

## Findings
- PASS: DataHelper processed three real Oven Maru `.braw` clips through the native Blackmagic RAW SDK path.
- PASS: The adapter and manifests identify codec `blackmagic_raw_native_sdk`; adapter diagnostics report `native_no_proxy=true`.
- PASS: No proxy or fallback behavior was observed in the adapter probe or CLI outputs.
- PASS: The known sample produced PDF, CSV, JSON, and exported PNG stills; the adjacent two-clip subset produced PDF, CSV, and JSON.
- PASS: Relevant BRAW/DataHelper tests passed: 18 total tests across native adapter, raw dependency handling, CLI standard pipeline, and CLI behavior.
- Note: The repository documents that `FRAMEPROOF_CONFIG` is diagnostics-only for batch runs; CLI flags were used for the BRAW adapter path as documented.

## Failure / Blocker Classification
- N/A (PASS; no failure or operational blocker). No Maintenance blocker handoff was written.

## Recommendation
- Jun/Jay can treat the current host as BRAW-native capable for this repo and media set. Keep using `--braw-adapter-path tools/braw_adapter` for CLI runs, and retain the installed Blackmagic RAW SDK/runtime plus `tools/braw_native_helper` together for future QA or operator runs.
