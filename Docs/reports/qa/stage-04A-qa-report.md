# Stage 04A QA Report

- gate: PASS
- verdict: PASS
- stage: stage-04A
- lane: qa
- next_recommended_prompt: `[Stage 4B-Plan]`
- stage_4b_status: unblocked-by-qa

## Scope

Independent QA review of the Stage 4A standard-video CLI pipeline against:

- `docs/stages/stage-04A-plan.md`
- `docs/stages/stage-04A-implement.md`
- `docs/reports/dev/stage-04A-handoff.md`
- `docs/stage.md`
- `docs/qa.md`
- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/data-inventory.md`
- `docs/ui-spec.md`
- `src/frameproof/`
- `tests/`

This was a QA-only gate. No source files were modified. Only QA documents were updated.

## Checked Files

- `AGENTS.md`
- `docs/stage.md`
- `docs/qa.md`
- `docs/stages/stage-04A-plan.md`
- `docs/stages/stage-04A-implement.md`
- `docs/reports/dev/stage-04A-handoff.md`
- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/data-inventory.md`
- `docs/ui-spec.md`
- `src/frameproof/__main__.py`
- `src/frameproof/cli.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/core/models.py`
- `src/frameproof/core/scanner.py`
- `src/frameproof/core/clip_grouper.py`
- `src/frameproof/core/adapter_resolver.py`
- `src/frameproof/core/probe_service.py`
- `src/frameproof/core/capture_service.py`
- `src/frameproof/core/report_builder.py`
- `src/frameproof/adapters/ffmpeg_adapter.py`
- `src/frameproof/render/pdf_renderer.py`
- `src/frameproof/output/manifest_writer.py`
- `tests/test_cli.py`
- `tests/integration/conftest.py`
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/integration/test_dependency_missing.py`

## Command Results

- `python -m frameproof --help` -> PASS

```text
usage: frameproof [-h] [--version] [--input PATH] [--recursive]
                  [--no-recursive] [--middle-count {0,1,2,3}]
                  [--layout {contact_sheet}] [--output PDF_PATH]
                  [--csv CSV_PATH] [--json JSON_PATH] [--project-name NAME]
                  [--ffmpeg-path FFMPEG_PATH] [--ffprobe-path FFPROBE_PATH]
                  [--mediainfo-path MEDIAINFO_PATH]
...
```

- `python -m pytest` -> PASS

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-8.3.2, pluggy-1.6.0
collected 50 items
...
======================== 49 passed, 1 skipped in 0.60s =========================
```

- `ruff check .` -> PASS

```text
All checks passed!
```

- `mypy src` -> PASS

```text
Success: no issues found in 24 source files
```

- `command -v ffmpeg && command -v ffprobe` -> BLOCKED

```text
(no output)
EXIT:1
```

- `python -m frameproof --input /var/folders/.../tmp.IJDT8Lrpi4/clip.mp4 --middle-count 1 --layout contact_sheet --output /var/folders/.../tmp.IJDT8Lrpi4/report.pdf --ffmpeg-path /missing/ffmpeg --ffprobe-path /missing/ffprobe --mediainfo-path /missing/mediainfo` -> PASS

```text
status: partial_success
total_clips: 1
success_count: 0
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 1
dependency_missing: clip=clip.mp4 status=dependency_missing adapter=ffmpeg required_tools=ffmpeg,ffprobe dependency_state=configured_missing
fatal: batch could not produce a standard-video report

EXIT:2
missing:/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.IJDT8Lrpi4/report.pdf
missing:/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.IJDT8Lrpi4/report.csv
missing:/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.IJDT8Lrpi4/report.json
```

- `python -m frameproof --input /var/folders/.../tmp.MmPP7hPpM1 --no-recursive --middle-count 3 --layout contact_sheet --output /var/folders/.../tmp.MmPP7hPpM1/report.pdf --csv /var/folders/.../tmp.MmPP7hPpM1/report.csv --json /var/folders/.../tmp.MmPP7hPpM1/report.json` -> PASS

```text
status: partial_success
total_clips: 2
success_count: 0
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 2
pdf_path: /var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/report.pdf
csv_path: /var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/report.csv
json_path: /var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/report.json

EXIT:0
exists:/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/report.pdf
exists:/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/report.csv
exists:/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/report.json
PNG_COUNT:0
CSV_ROWS
clip_id,clip_name,logical_clip_name,source_path,format_family,adapter_name,capture_label,requested_ratio,requested_frame_index,requested_seconds,actual_frame_index,actual_seconds,actual_timecode,actual_timecode_source,image_path,status,warnings,errors
candidate-0001,clip01.braw,,/private/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/clip01.braw,braw,braw_deferred,,,,,,,,,,unsupported_format,,BRAW support is deferred in Stage 4A
candidate-0002,clip02.r3d,,/private/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/clip02.r3d,r3d,r3d_deferred,,,,,,,,,,unsupported_format,,R3D support is deferred in Stage 4A
```

- `python -m frameproof --input /var/folders/.../tmp.rs5SDZIds4/clip01.braw --middle-count 0 --layout contact_sheet --output /var/folders/.../tmp.rs5SDZIds4/report.pdf` -> PASS

```text
status: partial_success
total_clips: 1
success_count: 0
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 1
pdf_path: /var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.rs5SDZIds4/report.pdf
csv_path: /var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.rs5SDZIds4/report.csv
json_path: /var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.rs5SDZIds4/report.json

EXIT:0
exists:/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.rs5SDZIds4/report.pdf size=3124
exists:/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.rs5SDZIds4/report.csv size=451
exists:/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.rs5SDZIds4/report.json size=1729
PNG_COUNT:0
```

## Evidence

### CLI contract and batch behavior

- [src/frameproof/cli.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/cli.py:155) exposes the Stage 4A CLI contract required by the plan and UI spec: `--input`, recursion flags, `--middle-count`, `--layout contact_sheet`, `--output`, and manifest-path overrides.
- [src/frameproof/cli.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/cli.py:241) correctly treats the all-standard, dependency-missing case as a fatal batch stop with exit code `2`, matching the Stage 4A failure rules.
- [src/frameproof/cli.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/cli.py:324) now emits explicit dependency diagnostics, and the smoke run confirmed the fatal lane surfaces `dependency_missing`, `adapter=ffmpeg`, `required_tools=ffmpeg,ffprobe`, and `dependency_state=configured_missing` while still suppressing PDF/CSV/JSON output.
- The deferred RAW smoke runs confirmed non-fatal per-file failures do not abort the whole batch: reports were still produced at `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/report.pdf`, `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/report.csv`, and `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.MmPP7hPpM1/report.json`.
- The default-output smoke run confirmed that when `--csv` and `--json` are omitted, the CLI derives `report.csv` and `report.json` beside the requested PDF and leaves PNG export disabled by default.

### Output behavior

- The raw-only default-output smoke run wrote derived manifest paths beside the requested PDF at `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.rs5SDZIds4/report.csv` and `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/tmp.rs5SDZIds4/report.json`, and all three artifacts were non-empty, matching [docs/ui-spec.md](/Users/server_jay/Desktop/DataHelper/docs/ui-spec.md:47).
- The same run created no `.png` files in the output directory, which is consistent with the documented default still-export-off behavior in [docs/ui-spec.md](/Users/server_jay/Desktop/DataHelper/docs/ui-spec.md:52).
- The unsupported-format CSV and JSON outputs preserved the same normalized clip rows and explicit `unsupported_format` status instead of silently dropping failed candidates, aligning with the fault-isolation rule in [docs/architecture.md](/Users/server_jay/Desktop/DataHelper/docs/architecture.md:10).

### Environment block note

- `ffmpeg` and `ffprobe` are not callable in this session, so the prompt-required real synthetic-video CLI sweep for `--middle-count 0`, `1`, `2`, and `3` cannot be executed locally here.
- That environment gap is not a Stage 4A product defect in this QA run because the prompt explicitly allows dependency-missing validation when FFmpeg is absent. The blocking requirement in this session is that missing dependencies must be reported clearly, and the current CLI satisfies that requirement.

## Evaluation

- Spec fidelity / product depth: PASS. The Stage 4A CLI contract, fatal dependency behavior, manifest defaults, and deferred-format isolation match the plan and shared docs for the environment actually available in this session.
- Functionality: PASS. Exit codes, artifact suppression, batch continuation, and default output behavior all match the Stage 4A contract under current environment constraints.
- Visual design / UX clarity: PASS. The CLI now exposes actionable dependency diagnostics and output paths directly.
- Code quality / maintainability: PASS. The Stage 4A implementation follows the shared architecture and keeps failures normalized through one report model.
- Accessibility / responsiveness: PASS for current scope. No GUI or responsive surface was modified in this stage.
- Validation completeness: PASS for this blocked-media environment. Full standard-video FFmpeg E2E validation is still environment-blocked locally, but the required dependency-missing path was verified directly and the full automated suite passes.

## Defects

- Blocking defects:
1. None in the current QA scope.

- Non-blocking observations:
1. The full FFmpeg-backed happy-path Stage 4A smoke validation remains environment-blocked here because `ffmpeg` and `ffprobe` are not installed or not on `PATH`.
2. A fresh local synthetic-video CLI sweep for `--middle-count 0`, `1`, `2`, and `3` should still be run on a tool-enabled machine if later stages want new manual happy-path evidence in addition to the automated coverage already present in `tests/integration/test_cli_standard_pipeline.py`.

## Verdict

PASS. Stage 4A satisfies the QA gate in this session.

Exact next recommended prompt: `[Stage 4B-Plan]`

Stop after QA.
