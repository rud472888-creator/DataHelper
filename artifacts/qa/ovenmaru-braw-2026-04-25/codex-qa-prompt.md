# Fresh Codex QA Task: DataHelper Oven Maru BRAW QA

You are an isolated QA worker for the local DataHelper repository.

Repository: `/Users/server_jay/Desktop/DataHelper`
Target media folder: `/Volumes/HOTDRIVE/오븐마루`
Known sample BRAW: `/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151557_C001.braw`
Preferred artifact output directory: `/Users/server_jay/Desktop/DataHelper/artifacts/qa/ovenmaru-braw-2026-04-25/`

Hard rules:
- QA only. Do not modify product source code, tests, OpenClaw/Hermes config, credentials, or bindings.
- Do not delete, move, rename, or alter source media.
- Do not write outputs into HOTDRIVE except if DataHelper explicitly requires it; prefer repo-local artifacts under the preferred output directory.
- Do not print or preserve credentials, tokens, API keys, account emails, or connection strings. Redact as `[REDACTED]` if encountered.
- Use real `.braw` files only. Ignore AppleDouble/resource-fork files named `._*.braw`.

Required QA work:
1. Inspect DataHelper documented CLI/test workflow from repo files.
2. Verify Blackmagic RAW SDK/native adapter availability where relevant.
3. Run normal repo tests relevant to BRAW/DataHelper if available and non-destructive.
4. Run DataHelper against at least the known sample BRAW. If practical and safe, include a tiny subset of nearby real BRAW clips from the same folder.
5. Verify expected outputs according to current feature set: report/PDF/CSV/JSON/stills/metadata, as applicable.
6. Distinguish explicitly: true native BRAW SDK path vs proxy/preview/fallback behavior vs metadata-incomplete behavior vs outright failure.
7. Capture command names, cwd, exit codes, output artifact paths, and concise evidence.
8. Confirm generated artifacts exist and are non-empty when the run claims success.
9. If failure occurs, classify as repo-code bug, missing dependency/SDK/runtime, media-specific issue, or operational/environment issue.
10. If this is an operational blocker suitable for Maintenance, write a blocker handoff under `/Users/server_jay/services/maintenance-agent/workspace/inbox/devman-blockers/`; otherwise do not escalate.

Required reports to write:
1. `/Users/server_jay/Desktop/DataHelper/docs/reports/qa/2026-04-25-ovenmaru-braw-qa.md`
2. `/Users/server_jay/Documents/Security/brain/ops/work-logs/2026-04-25/devman/2026-04-25-datahelper-ovenmaru-braw-qa.md`

Use exactly this report structure in both files:

# DataHelper Oven Maru BRAW QA Report

## Summary
- status: PASS / FAIL / PARTIAL / BLOCKED
- real_braw_processed: yes/no
- native_braw_sdk_path: yes/no/unknown
- fallback_or_proxy_used: yes/no/unknown
- sample_count:
- output_dir:

## Commands Run
- command, cwd, exit_code, concise result

## Media Samples
- paths tested, size/duration/metadata if available

## Outputs Verified
- artifact paths and non-empty checks

## Findings
- concise bullets

## Failure / Blocker Classification
- only if not PASS

## Recommendation
- next action for Jun/Jay

Final response should be short and include PASS/FAIL/PARTIAL/BLOCKED plus the two report paths. Do not include secrets.