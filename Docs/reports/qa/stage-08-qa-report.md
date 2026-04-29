# Stage 08 QA Report

- verdict: PASS
- run_type: qa
- stage: stage-08
- lane: qa
- checked_at: 2026-04-25 01:40:45 KST
- qa_scope: Independent validation of SDK-backed native BRAW support. No implementation code was modified.

## SDK / Runtime Paths Verified

- Blackmagic RAW SDK package: `com.blackmagic-design.BlackmagicRawSDK`, version `5.1`
- SDK libraries: `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries`
- Runtime framework: `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries/BlackmagicRawAPI.framework`
- Adapter: `/Users/server_jay/Desktop/DataHelper/tools/braw_adapter`
- Native helper: `/Users/server_jay/Desktop/DataHelper/tools/braw_native_helper`

## BRAW Sample Used

- `/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app/Contents/Resources/profile.braw`
- File existed and was treated read-only during QA.
- Repo sample glob `/Users/server_jay/Desktop/DataHelper/artifacts/runs/end-start-r1-braw-input/*.braw` had no matching files in this checkout, so QA used the installed Blackmagic sample.

## Native No-Proxy BRAW Happy Path

Proven. The adapter reported `native_no_proxy: true`, used the Blackmagic SDK libraries and repo native helper, probed actual `.braw` metadata, and captured PNG stills from the `.braw` file itself. DataHelper CLI integration through `--braw-adapter-path /Users/server_jay/Desktop/DataHelper/tools/braw_adapter` generated PDF/CSV/JSON outputs and exported PNG stills without requiring or matching Proxy media.

Observed probe metadata for `profile.braw`:

```text
codec: blackmagic_raw_native_sdk
format_family: braw
frame_count: 4
fps_num/fps_den: 60/1
duration_seconds: 0.0666667
resolution: 4608x2592
start_timecode: 00:00:00:00
blackmagic_raw_metadata examples: clip.manufacturer=Blackmagic Design, frame0.sensor_rate=1 1
```

Observed native capture outputs:

```text
/tmp/stage08-qa-adapter.CPNq6j/adapter-capture/01_first_0.png
/tmp/stage08-qa-adapter.CPNq6j/adapter-capture/02_last_3.png
/tmp/stage08-qa.4A3sz9/stills/profile.braw/profile.braw_start_00_00_00_00.png
/tmp/stage08-qa.4A3sz9/stills/profile.braw/profile.braw_end_00_00_00_03_calculated.png
```

## Commands Run and Results

### Prerequisite / SDK evidence

```text
pwd
pkgutil --pkg-info com.blackmagic-design.BlackmagicRawSDK || true
ls -l "/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app/Contents/Resources/profile.braw" tools/braw_adapter tools/braw_native_helper 2>&1
```

Result:

```text
/Users/server_jay/Desktop/DataHelper
package-id: com.blackmagic-design.BlackmagicRawSDK
version: 5.1
volume: /
location: /
install-time: 1777047150
profile.braw exists, size 13688932, executable/readable
/tools/braw_adapter exists and executable
/tools/braw_native_helper exists and executable
```

### Full test gate

```text
./.venv/bin/python -m pytest
```

Result:

```text
106 passed in 8.21s
```

### Ruff gate

```text
./.venv/bin/ruff check .
```

Result:

```text
All checks passed!
```

### Mypy gate

```text
./.venv/bin/mypy src
```

Result:

```text
Success: no issues found in 43 source files
```

### CLI help gate

```text
./.venv/bin/python -m frameproof --help >/tmp/stage08_help.txt
```

Result: exit code 0.

### GUI smoke gate

```text
QT_QPA_PLATFORM=offscreen ./.venv/bin/python -m frameproof.gui --smoke-test
```

Result: exit code 0. Qt emitted non-fatal font/propagateSizeHints warnings only.

### Adapter JSON contract smoke

Correct contract key is `command`.

```text
tools/braw_adapter < JSON command=version
```

Result:

```json
{"request_id":"qa-version","ok":true,"adapter_name":"braw_adapter","adapter_version":"2.0.0-native-sdk","status":"success","metadata_raw":{"native_no_proxy":true,"sdk_libraries_path":"/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries","native_helper":"/Users/server_jay/Desktop/DataHelper/tools/braw_native_helper"}}
```

```text
tools/braw_adapter < JSON command=probe input.source_path=/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app/Contents/Resources/profile.braw
```

Result:

```json
{"ok":true,"status":"success","clip":{"clip_name":"profile.braw","format_family":"braw","codec":"blackmagic_raw_native_sdk","frame_count":4,"duration_seconds":0.0666667,"fps_num":60,"fps_den":1,"width":4608,"height":2592,"start_timecode":"00:00:00:00","metadata_complete":true},"metadata_raw":{"sdk":"Blackmagic RAW SDK","native_no_proxy":true,"blackmagic_raw_metadata":{"clip.manufacturer":"Blackmagic Design","frame0.sensor_rate":"1 1"}}}
```

```text
tools/braw_adapter < JSON command=capture frames 0 and 3, options.staging_dir=/tmp/stage08-qa-adapter.CPNq6j/adapter-capture
```

Result:

```text
rc=0, ok=true, status=success
captures: first frame 0 -> /tmp/stage08-qa-adapter.CPNq6j/adapter-capture/01_first_0.png
captures: last frame 3 -> /tmp/stage08-qa-adapter.CPNq6j/adapter-capture/02_last_3.png
metadata_raw.native_no_proxy=true
```

### Missing dependency behavior

```text
FRAMEPROOF_BRAW_NATIVE_HELPER=/tmp/stage08-qa-adapter.CPNq6j/missing-helper tools/braw_adapter < JSON command=probe profile.braw
```

Result:

```json
{"ok":false,"status":"dependency_missing","errors":[{"code":"dependency_missing","message":"Blackmagic RAW SDK-backed adapter is unavailable. Install Blackmagic RAW SDK 5.1 for macOS and ensure /Users/server_jay/Desktop/DataHelper/tools/braw_native_helper exists and /Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries is readable. Detail: native helper not found: /tmp/stage08-qa-adapter.CPNq6j/missing-helper"}]}
```

This is actionable.

### DataHelper `--braw-adapter-path` integration smoke

```text
TMPDIR=/tmp/stage08-qa.4A3sz9
./.venv/bin/python -m frameproof \
  --input "/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app/Contents/Resources/profile.braw" \
  --output "$TMPDIR/native-braw.pdf" \
  --braw-adapter-path "$PWD/tools/braw_adapter" \
  --middle-count 0 \
  --export-stills \
  --stills-dir "$TMPDIR/stills"
```

Result:

```text
status: success
total_clips: 1
success_count: 1
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 0
pdf_path: /tmp/stage08-qa.4A3sz9/native-braw.pdf
csv_path: /tmp/stage08-qa.4A3sz9/native-braw.csv
json_path: /tmp/stage08-qa.4A3sz9/native-braw.json
```

Generated stills:

```text
/tmp/stage08-qa.4A3sz9/stills/profile.braw/profile.braw_start_00_00_00_00.png
/tmp/stage08-qa.4A3sz9/stills/profile.braw/profile.braw_end_00_00_00_03_calculated.png
```

JSON output clip fields confirmed native BRAW metadata and successful captures.

## Acceptance Checklist

- Actual `.braw` processed from native BRAW media, not matching Proxy media: PASS
- Representative PNG stills extracted via SDK-backed path: PASS
- JSON adapter `version`, `probe`, `capture` works: PASS
- Metadata includes frame count/fps/duration/resolution/start timecode where available: PASS
- Camera/clip metadata where available included: PASS (`clip.manufacturer` observed)
- Missing dependency error is actionable: PASS
- `--braw-adapter-path` integration works: PASS
- No unrelated RAW broadening observed: PASS (`BRAWAdapterClient.format_families = (braw,)`; no implementation changes made by QA)
- No user media modified/deleted: PASS (QA wrote only temp outputs under `/tmp` and workflow markdown files)
- Tests/docs adequate for Stage 08: PASS

## Defects / Issues

None blocking.

QA note: an exploratory adapter call using `action` instead of the documented/implemented `command` key returned `invalid_request`; rerunning with `command` proved the expected adapter contract. This is not a defect in Stage 08 acceptance.

## Files Modified by QA

- `/Users/server_jay/Desktop/DataHelper/Docs/reports/qa/stage-08-qa-report.md`
- `/Users/server_jay/Desktop/DataHelper/Docs/stage.md`
- `/Users/server_jay/Desktop/DataHelper/Docs/reports/status/current-status.md`

## Exact Next Recommended Prompt

`[Stage 09-Plan]`
