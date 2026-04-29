# Stage 08 QA

- lane: qa
- stage: stage-08
- subphase: qa
- status: pending
- authorized_by: 재경
- orchestrated_by: 준 / Devman
- date: 2026-04-25

## Scope

Validate Stage 08 true/native BRAW support in a fresh QA-only session. Do not modify implementation code. Do not silently fix defects.

## Required Inputs

Read repository state and handoff files first:

```text
Docs/stage.md
Docs/reports/status/current-status.md
Docs/stages/stage-08-implement.md
Docs/reports/dev/stage-08-handoff.md
```

Also inspect prior context if needed:

```text
/Users/server_jay/.hermes/profiles/devman/reports/2026-04-25-datahelper-braw-failure-investigation.md
/Users/server_jay/.hermes/profiles/devman/reports/2026-04-25-datahelper-native-braw-support.md
```

## QA Requirements

PASS only if all are true:

- `.braw` is processed from native BRAW media, not matching Proxy media.
- Representative stills are extracted from actual `.braw` via SDK-backed path.
- JSON adapter contract works for `version`, `probe`, and `capture`.
- Real/sample BRAW metadata is returned where available: frame count, fps, duration, resolution, start timecode if available, camera/clip metadata where available.
- Missing SDK/runtime/license behavior produces clear actionable dependency errors.
- Existing DataHelper `--braw-adapter-path` integration remains compatible.
- No unrelated RAW families were broadened unnecessarily.
- No user media files were modified/deleted.
- Tests and docs are adequate.

## Required Sample Proof

Use read-only real/sample BRAW media, preferably without relying on matching Proxy media:

```text
/Users/server_jay/Desktop/DataHelper/artifacts/runs/end-start-r1-braw-input/*.braw
/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app/Contents/Resources/profile.braw
```

## Required QA Outputs

Write/update:

```text
Docs/reports/qa/stage-08-qa-report.md
Docs/stage.md
Docs/reports/status/current-status.md
```

The QA report must include:

- verdict: PASS or FAIL
- SDK/runtime paths verified
- BRAW sample used
- exact commands run and results
- whether native no-proxy BRAW happy path was proven
- defects if any
- exact next recommended prompt

## Validation Commands

Run relevant adapter smoke commands and the normal gate checks where practical:

```text
./.venv/bin/python -m pytest
./.venv/bin/ruff check .
./.venv/bin/mypy src
./.venv/bin/python -m frameproof --help
QT_QPA_PLATFORM=offscreen ./.venv/bin/python -m frameproof.gui --smoke-test
```

If any gate cannot be run, record the exact blocker and decide FAIL unless it is clearly outside Stage 08 acceptance criteria.

## Stop Conditions

Do not change code. If acceptance criteria are not met, write FAIL and identify the next `[Stage 8-Fix]` scope.
