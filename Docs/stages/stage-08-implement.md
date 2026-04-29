# Stage 08 Implement

- lane: dev
- stage: stage-08
- subphase: implement
- status: pending
- authorized_by: 재경
- orchestrated_by: 준 / Devman
- date: 2026-04-25

## Scope

Implement true/native BRAW support now that the Blackmagic RAW SDK 5.1 development package is installed on this Mac.

This is a maintenance feature stage after Stage 07 release-ready. Do not rely on hidden chat context. Use repository files and installed SDK evidence only.

## Product Requirements

- `.braw` files must be processed from actual BRAW media, not matching Proxy media.
- Extract representative frames from `.braw` itself.
- Return real metadata where available:
  - frame count
  - fps
  - duration
  - resolution
  - start timecode if available
  - camera/clip metadata where available
- Preserve existing JSON adapter contract where possible:
  - `version`
  - `probe`
  - `capture`
- Missing SDK/runtime/license must produce a clear actionable dependency error.
- Do not broaden unrelated RAW families unless necessary.
- Do not modify/delete user media files.

## SDK Paths To Inspect

Use actual installed tree; path names may differ. Start with:

```text
/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac
/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Include/BlackmagicRawAPI.h
/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Samples
/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries
/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Frameworks
/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Documentation
```

Known installed evidence:

```text
pkgutil --pkg-info com.blackmagic-design.BlackmagicRawSDK
package-id: com.blackmagic-design.BlackmagicRawSDK
version: 5.1
```

## Sample Media

Use read-only sample media:

```text
/Users/server_jay/Desktop/DataHelper/artifacts/runs/end-start-r1-braw-input/*.braw
/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app/Contents/Resources/profile.braw
```

## Expected Implementation Route

If feasible:

1. Build a production SDK-backed `braw_adapter` executable or equivalent adapter binary/script.
2. Keep it callable by DataHelper via `--braw-adapter-path`.
3. Implement/prove JSON `version`, `probe`, and `capture`.
4. Ensure capture writes stills into `staging_dir` from native BRAW decode.
5. Ensure no-proxy validation: run against a BRAW sample where matching Proxy media is not required/used.
6. Add tests and documentation for setup/runtime diagnostics.
7. Run validation gates.

Use the SDK sample source where helpful, but do not vendor proprietary SDK/framework binaries into the repo unless clearly permitted. It is acceptable to compile/link against the locally installed SDK path.

## Existing Context

Prior reports:

```text
/Users/server_jay/.hermes/profiles/devman/reports/2026-04-25-datahelper-braw-failure-investigation.md
/Users/server_jay/.hermes/profiles/devman/reports/2026-04-25-datahelper-native-braw-support.md
```

Existing adapter client:

```text
src/frameproof/adapters/braw_adapter_client.py
src/frameproof/adapters/_json_subprocess_adapter.py
```

Existing old proxy-preview artifact must not be treated as proof of native support:

```text
artifacts/bin/braw_adapter
```

## Required Dev Outputs

Write/update:

```text
Docs/stages/stage-08-implement.md
Docs/reports/dev/stage-08-handoff.md
Docs/stage.md
Docs/reports/status/current-status.md
```

The handoff must include:

- SDK paths found
- implementation details or exact blocker details
- files changed
- BRAW sample used
- tests run and results
- whether native no-proxy BRAW happy path was proven
- exact next prompt: `[Stage 8-QA]` if implementation completed, or blocker/human action if not

## Validation Expectations

At minimum, run relevant unit tests and any adapter-level smoke commands. If implementation is complete, prove native BRAW no-proxy processing using an actual `.braw` sample through the DataHelper adapter path or the adapter executable itself, and run the normal QA-relevant checks where practical:

```text
./.venv/bin/python -m pytest
./.venv/bin/ruff check .
./.venv/bin/mypy src
```

## Stop Conditions

If blocked despite SDK install, do not fake support. Produce a blocker handoff with exact command output and minimal next action.

Do not mark the stage complete without explicit implementation evidence. Do not run QA yourself.
