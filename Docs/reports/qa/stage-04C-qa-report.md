# Stage 04C QA Report

- gate: passed
- verdict: PASS
- stage: stage-04C
- lane: qa
- next_recommended_prompt: `[Stage 4D-Plan]`
- stage_4d_status: unblocked-by-qa

## Scope

Independent QA review of Stage 4C Layout A detail PDF rendering, PNG still export, failed or partial reporting, filename sanitization, and PDF or manifest parity against:

- `docs/stages/stage-04C-plan.md`
- `docs/stages/stage-04C-implement.md`
- `docs/reports/dev/stage-04C-handoff.md`
- `docs/ui-spec.md`
- `docs/data-inventory.md`
- `src/frameproof/`
- `tests/`

This was a QA-only gate. No product code was modified. Only QA documents were updated.

## Checked Files

- `AGENTS.md`
- `docs/qa.md`
- `docs/stages/stage-04C-plan.md`
- `docs/stages/stage-04C-implement.md`
- `docs/reports/dev/stage-04C-handoff.md`
- `docs/ui-spec.md`
- `docs/data-inventory.md`
- `src/frameproof/cli.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/core/report_builder.py`
- `src/frameproof/output/manifest_writer.py`
- `src/frameproof/output/still_exporter.py`
- `src/frameproof/render/pdf_renderer.py`
- `tests/test_cli.py`
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/unit/output/test_manifest_writer.py`
- `tests/unit/output/test_still_exporter.py`
- `tests/unit/render/test_pdf_renderer.py`

## Command Results

- `python -m pytest` -> PASS

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-8.3.2, pluggy-1.6.0
rootdir: /Users/server_jay/Desktop/DataHelper
configfile: pyproject.toml
testpaths: tests
collected 77 items
...
======================== 75 passed, 2 skipped in 2.82s =========================
```

- `ruff check .` -> PASS

```text
All checks passed!
```

- `mypy src` -> PASS

```text
Success: no issues found in 30 source files
```

- FFmpeg availability check -> live standard-video smoke BLOCKED

```text
ffmpeg=missing
ffprobe=missing
```

- `python -m frameproof --help` -> PASS

```text
usage: frameproof [-h] [--version] [--input PATH] [--recursive]
                  [--no-recursive] [--middle-count {0,1,2,3}]
                  [--layout {contact_sheet,detail}] [--output PDF_PATH]
                  [--csv CSV_PATH] [--json JSON_PATH] [--export-stills]
                  [--stills-dir PATH]
...
```

- Invalid-input CLI dependency-path check -> PASS

```text
tmpdir=/tmp/stage4c-qa-cli-1Dr2jp
exit_code=2
pdf_exists=false
csv_exists=false
json_exists=false
status: partial_success
total_clips: 1
success_count: 0
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 1
dependency_missing: clip=clip.mp4 status=dependency_missing adapter=ffmpeg required_tools=ffmpeg,ffprobe dependency_state=configured_missing
fatal: batch could not produce a report
```

- Manual Stage 4C artifact smoke via direct renderer/export/manifest calls -> PASS

```text
base_dir=/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/stage4c-qa-r55c_gnq
detail_off_stills_dir_exists=False
detail_off_layout_a=True
detail_off_failed_section=True
detail_off_requested_ratio=True
detail_off_requested_frame=True
detail_off_requested_time=True
detail_off_actual_frame=True
detail_off_actual_time=True
detail_off_actual_timecode=True
detail_off_failed_probe_clip=True
detail_off_partial_capture_issue=True
detail_off_csv_requested_ratios=['0.0', '0.5', '1.0', '']
detail_off_csv_statuses=['success', 'success', 'decode_failed', 'probe_failed']
detail_off_csv_image_paths=['', '', '', '']
detail_off_json_row_requested_ratio=0.5
detail_off_json_row_actual_timecode='01:00:01:00'
detail_off_json_failed_clip_status='probe_failed'
detail_on_exported_pngs=['.../A001_Shot_01.mov_mid1_01_00_01_00.png', '.../A001_Shot_01.mov_mid1_01_00_01_00_001.png', '.../A001_Shot_01.mov_start_01_00_00_df_12.png', '.../A001_Shot_01.mov_start_01_00_00_df_12_001.png']
detail_on_first_export={'Start': '.../A001_Shot_01.mov_start_01_00_00_df_12.png', 'Mid1': '.../A001_Shot_01.mov_mid1_01_00_01_00.png', 'End': None}
detail_on_second_export={'Start': '.../A001_Shot_01.mov_start_01_00_00_df_12_001.png', 'Mid1': '.../A001_Shot_01.mov_mid1_01_00_01_00_001.png', 'End': None}
detail_on_json_capture_image_paths=['.../A001_Shot_01.mov_start_01_00_00_df_12.png', '.../A001_Shot_01.mov_mid1_01_00_01_00.png', None]
```

## Artifact Paths

- Detail PDF or manifest smoke with still export OFF:
- `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/stage4c-qa-r55c_gnq/artifacts/detail-off.pdf`
- `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/stage4c-qa-r55c_gnq/artifacts/detail-off.csv`
- `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/stage4c-qa-r55c_gnq/artifacts/detail-off.json`
- Detail PDF or manifest smoke with still export ON:
- `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/stage4c-qa-r55c_gnq/artifacts/detail-on.pdf`
- `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/stage4c-qa-r55c_gnq/artifacts/detail-on.csv`
- `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/stage4c-qa-r55c_gnq/artifacts/detail-on.json`
- Exported stills root:
- `/var/folders/qd/7zm7z5r5107cmhvc8ph6n79w0000gn/T/stage4c-qa-r55c_gnq/artifacts/stills-on`
- Invalid-input CLI evidence:
- `/tmp/stage4c-qa-cli-1Dr2jp/cli.out`
- `/tmp/stage4c-qa-cli-1Dr2jp/cli.err`

## Evidence

### `Layout A` detail fidelity is restored

- `docs/ui-spec.md:204-223` requires `Layout A` to show `label`, `requested_ratio`, `requested frame/time`, `actual frame/time`, and `actual timecode`.
- `src/frameproof/render/pdf_renderer.py:259-291` renders all of those per-frame detail lines directly from `CapturePoint`, including `Requested ratio`.
- `tests/unit/render/test_pdf_renderer.py:71-143` now asserts `Requested ratio: 0.500` in the rendered PDF text.
- The direct detail-PDF artifact smoke confirmed the rendered output contains:
- `Layout A / detail`
- `Requested ratio: 0.500`
- `Requested frame: 24`
- `Requested time: 1.000s`
- `Actual frame: 24`
- `Actual time: 1.000s`
- `Timecode: 01:00:01:00`

### Still-export behavior matches the Stage 4C gate

- `docs/stages/stage-04C-plan.md:204-210` requires still export to remain off by default and to use sanitized deterministic paths when enabled.
- `src/frameproof/output/still_exporter.py:15-41` exports only captures with real temp PNGs and leaves missing or failed captures as `None`.
- `src/frameproof/output/still_exporter.py:44-69` sanitizes separators, `:`, and `;`, and `src/frameproof/output/still_exporter.py:95-117` adds `_001` collision suffixes without overwriting the first export.
- `tests/unit/output/test_still_exporter.py:50-89` covers drop-frame sanitization, fallback sanitization, collision suffixes, and the no-output path when images are missing.
- The direct artifact smoke confirmed:
- no stills directory is created when export is off
- filenames include `_df_` for drop-frame timecode
- repeated exports produce `_001` collision suffixes
- decode-failed captures do not create fake PNGs and keep `End: None`

### PDF and manifest parity is intact for partial and failed clips

- `docs/stages/stage-04C-plan.md:157-182` requires manifest fields and failed-clip handling to stay aligned with the shared `ReportItem` data.
- `src/frameproof/output/manifest_writer.py:13-68` preserves `requested_ratio`, requested and actual capture facts, exported `image_path`, and clip-level failure rows when no captures exist.
- `src/frameproof/output/manifest_writer.py:118-166` preserves the same capture facts in the JSON clip payloads.
- `tests/unit/output/test_manifest_writer.py:52-146` verifies exported image-path parity, stills-off parity, and failure rows without captures.
- `src/frameproof/render/pdf_renderer.py:418-477` keeps the dedicated `Failed / Partial Clips` section and includes capture issue summaries plus warning or error detail.
- The direct artifact smoke confirmed:
- the PDF contains `Failed / Partial Clips`
- the partial clip shows `Capture issues: End=decode_failed`
- the failed clip remains visible as `broken.mov [probe_failed]`
- CSV stills-off `image_path` values stay empty
- JSON stills-off `image_path` values stay `null`
- JSON and CSV both preserve `requested_ratio` and the failed clip row

### Invalid-input behavior remains truthful

- The explicit invalid-input CLI run with missing FFmpeg tools exited `2`, reported `dependency_missing`, and produced no PDF, CSV, or JSON outputs.
- This matches the expected fatal dependency-missing path for an all-standard batch and does not regress the Stage 4C gate.

## Evaluation

- Spec fidelity / product depth: PASS. The current `Layout A` artifact contains the full required per-frame detail set and the failed-section behavior the spec calls for.
- Functionality: PASS. Export-off, export-on, sanitization, collision handling, and failed or partial reporting all behaved as required in inspected artifacts.
- Visual design / UX clarity: PASS. The detail PDF exposes the intended requested-versus-actual context and keeps degraded clips visible instead of hiding them.
- Code quality / maintainability: PASS. The output surfaces remain driven by shared report data and the regression tests now pin the previously missing field.
- Accessibility / responsiveness: PASS for current scope. This stage is limited to CLI and PDF output, and the verified layouts remain readable.
- Validation completeness: PASS within environment constraints. The required command suite passed, direct artifacts were inspected, and the FFmpeg-only smoke path was explicitly conditional rather than mandatory.

## Defects

- Blocking defects: none
- Non-blocking observations:
1. Live FFmpeg or FFprobe smoke for real standard-video CLI runs remains unavailable on this machine because both executables are missing from `PATH`.

## Verdict

PASS. Stage 4C satisfies the QA gate in this session.

Exact next recommended prompt: `[Stage 4D-Plan]`

Stop after QA.
