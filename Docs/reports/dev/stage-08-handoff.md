# Stage 08 Dev Handoff

- status: complete
- run_type: implement
- stage: stage-08
- lane: dev
- summary: Implemented a Blackmagic RAW SDK-backed BRAW adapter path using a repo-local JSON adapter script and native helper compiled against the installed Blackmagic RAW SDK 5.1. Native no-proxy BRAW probe/capture was proven with a real `.braw` sample.
- source_prompt: `Docs/stages/stage-08-implement.md`
- latest_implement_artifact: `Docs/stages/stage-08-implement.md`
- next_recommended_prompt: `[Stage 8-QA]`
- qa_required: true

## SDK Paths Found

- `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac`
- `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Include/BlackmagicRawAPI.h`
- `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Include/BlackmagicRawAPIDispatch.cpp`
- `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries/BlackmagicRawAPI.framework`
- `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Samples/ExtractFrame/ExtractFrame.cpp`
- `/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Samples/ExtractMetadata/ExtractMetadata.cpp`

Package evidence:

```text
pkgutil --pkg-info com.blackmagic-design.BlackmagicRawSDK
package-id: com.blackmagic-design.BlackmagicRawSDK
version: 5.1
volume: /
location: /
```

## Implementation Details

- Added `tools/braw_native_helper.cpp`, a native helper based on Blackmagic RAW SDK sample patterns.
- Compiled `tools/braw_native_helper` locally with `clang++` against the installed SDK headers and `BlackmagicRawAPIDispatch.cpp`.
- Added `tools/braw_adapter`, an executable JSON stdin/stdout adapter preserving DataHelper's existing `version`, `probe`, and `capture` subprocess contract.
- `probe` uses the SDK helper to open the `.braw` directly and return native metadata including frame count, fps, duration, resolution, start timecode, and available Blackmagic metadata.
- `capture` decodes requested BRAW frame indices to PNG files in the provided `staging_dir` using the SDK helper.
- The adapter reports actionable `dependency_missing` errors if the helper or Blackmagic SDK libraries/framework path is missing.
- The adapter does not search for, require, or use matching Proxy media.
- The repo does not vendor Blackmagic proprietary framework assets; it links/runs against the locally installed SDK/runtime.

## Files Changed

- `README.md`
- `Docs/dependency-guide.md`
- `Docs/stage.md`
- `Docs/reports/status/current-status.md`
- `Docs/stages/stage-08-implement.md`
- `Docs/stages/stage-08-qa.md`
- `Docs/reports/dev/stage-08-handoff.md`
- `tests/integration/test_native_braw_adapter.py`
- `tools/braw_adapter`
- `tools/braw_native_helper.cpp`
- `tools/braw_native_helper`

## BRAW Sample Used

Primary native no-proxy proof sample:

```text
/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app/Contents/Resources/profile.braw
```

Observed native probe values:

```text
frame_count: 4
fps: 60
resolution: 4608x2592
duration_seconds: 0.0666667
start_timecode: 00:00:00:00
codec: blackmagic_raw_native_sdk
```

## Native No-Proxy Happy Path Evidence

Adapter-level smoke:

```text
tools/braw_adapter version -> ok=true, native_no_proxy=true
tools/braw_adapter probe profile.braw -> ok=true, frame_count=4, fps=60, resolution=4608x2592
tools/braw_adapter capture profile.braw -> ok=true, wrote PNG stills for frame 0 and frame 3
```

DataHelper CLI smoke:

```text
./.venv/bin/python -m frameproof \
  --input '/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app/Contents/Resources/profile.braw' \
  --output "$tmp/native-braw.pdf" \
  --braw-adapter-path "$PWD/tools/braw_adapter" \
  --middle-count 0 \
  --export-stills \
  --stills-dir "$tmp/stills"
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
```

Output proof:

```text
native-braw.pdf generated
native-braw.csv generated
native-braw.json generated
exported stills generated under stills/profile.braw/
```

## Tests Run

Focused tests:

```text
./.venv/bin/python -m pytest tests/unit/adapters/test_braw_adapter_client.py tests/integration/test_native_braw_adapter.py
4 passed in 2.74s
```

Full test suite:

```text
./.venv/bin/python -m pytest
106 passed in 9.51s
```

Lint/type gates:

```text
./.venv/bin/ruff check .
All checks passed!

./.venv/bin/mypy src
Success: no issues found in 43 source files
```

## Native No-Proxy BRAW Happy Path Proven

Yes. A real `.braw` file was opened, probed, and decoded through the Blackmagic RAW SDK-backed helper/adapter path. Matching Proxy media was not used or required.

## Remaining Risks / QA Notes

- The helper binary is built locally against the installed SDK. If moved to another Mac, rebuild it or provide a matching executable and SDK/runtime installation.
- Redistribution of Blackmagic SDK/runtime assets remains a packaging/legal review item; the repo does not vendor those assets.
- QA should independently rerun adapter-level and DataHelper CLI smoke before PASS.

## Exact Next Prompt

`[Stage 8-QA]`

Stop after Dev handoff. Independent QA is required before claiming Stage 08 complete.
