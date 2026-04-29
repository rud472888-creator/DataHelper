# Stage 04B QA Report

- gate: PASS
- verdict: PASS
- stage: stage-04B
- lane: qa
- next_recommended_prompt: `[Stage 4C-Plan]`
- stage_4c_status: unblocked-by-qa

## Scope

Independent QA review of Stage 4B RAW adapter support against:

- `docs/stages/stage-04B-plan.md`
- `docs/stages/stage-04B-implement.md`
- `docs/reports/dev/stage-04B-handoff.md`
- `docs/architecture.md`
- `docs/api-contract.md`
- `src/frameproof/`
- `tests/`

This was a QA-only gate. No product code was modified. Only QA documents were updated.

## Checked Files

- `AGENTS.md`
- `docs/qa.md`
- `docs/stages/stage-04B-plan.md`
- `docs/stages/stage-04B-implement.md`
- `docs/reports/dev/stage-04B-handoff.md`
- `docs/architecture.md`
- `docs/api-contract.md`
- `src/frameproof/cli.py`
- `src/frameproof/core/adapter_resolver.py`
- `src/frameproof/core/clip_grouper.py`
- `src/frameproof/core/dependency_inspector.py`
- `src/frameproof/core/probe_service.py`
- `src/frameproof/core/capture_service.py`
- `src/frameproof/core/report_builder.py`
- `src/frameproof/adapters/_json_subprocess_adapter.py`
- `src/frameproof/adapters/braw_adapter_client.py`
- `src/frameproof/adapters/r3d_adapter_client.py`
- `src/frameproof/adapters/arriraw_art_adapter_client.py`
- `tests/integration/test_raw_dependency_missing.py`
- `tests/unit/adapters/test_braw_adapter_client.py`
- `tests/unit/adapters/test_r3d_adapter_client.py`
- `tests/unit/adapters/test_arriraw_art_adapter_client.py`
- `tests/unit/core/test_dependency_inspector.py`
- `tests/unit/core/test_clip_grouper.py`

## Command Results

- `python -m pytest` -> PASS

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-8.3.2, pluggy-1.6.0
collected 64 items
...
======================== 63 passed, 1 skipped in 3.87s =========================
```

- `ruff check .` -> PASS

```text
All checks passed!
```

- `mypy src` -> PASS

```text
Success: no issues found in 29 source files
```

- `grep -R "subprocess" src/frameproof/adapters docs/api-contract.md` -> PASS

```text
src/frameproof/adapters/arriraw_art_adapter_client.py:import subprocess
src/frameproof/adapters/_json_subprocess_adapter.py:import subprocess
src/frameproof/adapters/r3d_adapter_client.py:from frameproof.adapters._json_subprocess_adapter import JsonSubprocessAdapterClient
src/frameproof/adapters/braw_adapter_client.py:from frameproof.adapters._json_subprocess_adapter import JsonSubprocessAdapterClient
docs/api-contract.md:- One subprocess JSON envelope for every RAW adapter client.
```

- `grep -R "dependency_missing" src/frameproof tests docs` -> PASS

```text
src/frameproof/core/models.py:    DEPENDENCY_MISSING = "dependency_missing"
src/frameproof/adapters/arriraw_art_adapter_client.py:            return _dependency_missing_probe(candidate, availability)
tests/integration/test_raw_dependency_missing.py:def test_cli_reports_dependency_missing_for_raw_only_batch_when_braw_adapter_is_unconfigured(tmp_path: Path) -> None:
docs/api-contract.md:  "status": "dependency_missing",
docs/stages/stage-04B-plan.md:- Missing RAW dependencies produce truthful `dependency_missing` results and never fabricate probe or capture success.
```

- RAW dependency environment check -> BLOCKED for real-tool smoke

```text
ffmpeg=missing
ffprobe=missing
mediainfo=missing
braw_adapter=missing
r3d_adapter=missing
art-cmd=missing
arri_art_cmd=missing
```

- `python -m frameproof --input <tmp>/clip.braw --input <tmp>/A001_C001_001.R3D --input <tmp>/clip.ari --middle-count 1 --layout contact_sheet --output <tmp>/report.pdf --csv <tmp>/report.csv --json <tmp>/report.json` -> PASS

```text
status: partial_success
total_clips: 3
success_count: 0
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 3
dependency_missing: clip=A001_C001_001.R3D status=dependency_missing adapter=r3d_adapter required_tools=r3d_adapter dependency_state=not_configured
dependency_missing: clip=clip.ari status=dependency_missing adapter=arriraw_art_adapter required_tools=arri_art_cmd dependency_state=not_configured
dependency_missing: clip=clip.braw status=dependency_missing adapter=braw_adapter required_tools=braw_adapter dependency_state=not_configured
fatal: batch could not produce a report

EXIT:2
```

- `python - <<'PY' ... BRAWAdapterClient subprocess-crash smoke ... PY` -> PASS

```text
{'probe_ok': False, 'probe_status': 'probe_failed', 'probe_error': 'probe_failed', 'capture_status': 'decode_failed', 'capture_error': 'probe_failed'}
```

## Evidence

### RAW routing and dependency honesty

- [src/frameproof/core/adapter_resolver.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/core/adapter_resolver.py:45) routes `.braw`, `.r3d`, and `.ari` to concrete adapter clients rather than deferring them as unsupported.
- [src/frameproof/core/dependency_inspector.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/core/dependency_inspector.py:96) defines explicit RAW dependency checks for `braw_adapter`, `r3d_adapter`, and `arri_art_cmd`, and [src/frameproof/core/dependency_inspector.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/core/dependency_inspector.py:216) runs lightweight startup checks that can yield `runtime_error` instead of false success.
- [src/frameproof/core/probe_service.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/core/probe_service.py:46) converts unavailable adapters into normalized `dependency_missing` probe results with dependency detail before probe execution starts.
- [tests/unit/core/test_dependency_inspector.py](/Users/server_jay/Desktop/DataHelper/tests/unit/core/test_dependency_inspector.py:16) locks `not_configured`, [tests/unit/core/test_dependency_inspector.py](/Users/server_jay/Desktop/DataHelper/tests/unit/core/test_dependency_inspector.py:24) locks `configured_missing`, and [tests/unit/core/test_dependency_inspector.py](/Users/server_jay/Desktop/DataHelper/tests/unit/core/test_dependency_inspector.py:38) locks `runtime_error` for invalid RAW version responses.

### Subprocess isolation and error normalization

- [docs/architecture.md](/Users/server_jay/Desktop/DataHelper/docs/architecture.md:14) requires RAW execution to remain subprocess-isolated, and the import audit showed the RAW client modules only import stdlib and Frame Proof modules, not vendor SDK bindings.
- [src/frameproof/adapters/_json_subprocess_adapter.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/adapters/_json_subprocess_adapter.py:129) runs BRAW and R3D through subprocesses, maps missing executables to `dependency_missing`, maps timeouts to `timeout`, and maps empty or malformed stdout to structured `invalid_response` or `probe_failed` results rather than uncaught exceptions.
- [src/frameproof/adapters/_json_subprocess_adapter.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/adapters/_json_subprocess_adapter.py:59) and [src/frameproof/adapters/_json_subprocess_adapter.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/adapters/_json_subprocess_adapter.py:91) normalize both probe and capture transport failures into typed domain results.
- [src/frameproof/adapters/arriraw_art_adapter_client.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/adapters/arriraw_art_adapter_client.py:48) keeps ARRIRAW on a subprocess shell-out path, [src/frameproof/adapters/arriraw_art_adapter_client.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/adapters/arriraw_art_adapter_client.py:98) rejects missing or malformed metadata JSON as `invalid_response`, and [src/frameproof/adapters/arriraw_art_adapter_client.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/adapters/arriraw_art_adapter_client.py:151) maps capture-time tool failures into structured per-slot results.
- [tests/unit/adapters/test_braw_adapter_client.py](/Users/server_jay/Desktop/DataHelper/tests/unit/adapters/test_braw_adapter_client.py:50) verifies JSON request/response round-tripping for BRAW, [tests/unit/adapters/test_braw_adapter_client.py](/Users/server_jay/Desktop/DataHelper/tests/unit/adapters/test_braw_adapter_client.py:105) locks malformed JSON probe handling, [tests/unit/adapters/test_r3d_adapter_client.py](/Users/server_jay/Desktop/DataHelper/tests/unit/adapters/test_r3d_adapter_client.py:107) locks adapter-declared capture-time `dependency_missing`, and [tests/unit/adapters/test_arriraw_art_adapter_client.py](/Users/server_jay/Desktop/DataHelper/tests/unit/adapters/test_arriraw_art_adapter_client.py:99) locks malformed ARRIRAW metadata-export JSON handling.

### R3D grouping and batch behavior

- [src/frameproof/core/clip_grouper.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/core/clip_grouper.py:48) groups only same-directory `.R3D` stems that match the conservative `base_digits` suffix pattern and sorts them numerically.
- [tests/unit/core/test_clip_grouper.py](/Users/server_jay/Desktop/DataHelper/tests/unit/core/test_clip_grouper.py:20) locks numeric part ordering, and [tests/unit/core/test_clip_grouper.py](/Users/server_jay/Desktop/DataHelper/tests/unit/core/test_clip_grouper.py:34) locks the no-cross-directory-merge rule.
- [tests/unit/adapters/test_r3d_adapter_client.py](/Users/server_jay/Desktop/DataHelper/tests/unit/adapters/test_r3d_adapter_client.py:52) verifies the grouped `part_files` list is passed through the JSON request and that the logical clip name survives probe normalization.
- [tests/integration/test_raw_dependency_missing.py](/Users/server_jay/Desktop/DataHelper/tests/integration/test_raw_dependency_missing.py:8) locks the raw-only fatal CLI path for missing BRAW dependencies, and the direct CLI smoke in this QA run confirmed the same behavior for mixed RAW-family inputs with all RAW tools absent locally.

## Evaluation

- Spec fidelity / product depth: PASS. The Stage 4B implementation matches the documented subprocess-only RAW design, dependency-state vocabulary, and conservative R3D grouping rules.
- Functionality: PASS. Required command suite passes, missing dependencies surface truthfully, malformed JSON is rejected cleanly, and subprocess crash behavior is normalized into structured results.
- Visual design / UX clarity: PASS for current scope. This stage is not a GUI delivery, and the CLI dependency diagnostics are explicit and actionable.
- Code quality / maintainability: PASS. Shared subprocess transport removes duplication between BRAW and R3D while keeping ARRIRAW isolated where its CLI contract differs.
- Accessibility / responsiveness: PASS for current scope. No accessibility-facing UI changed, and the CLI remains scriptable and deterministic.
- Validation completeness: PASS for this environment. Real vendor-binary smoke is blocked because the tools are not installed here, but the required graceful-failure path, runtime-error path, malformed JSON path, and crash path were all validated with automated or direct evidence.

## Defects

- Blocking defects:
1. None in the current QA scope.

- Non-blocking observations:
1. Real vendor-runtime smoke for actual `BRAW`, R3D, and ARRI tools remains unverified on this machine because those executables are absent from `PATH` and not configured.
2. The subprocess-crash path is validated in this QA run by direct smoke, but there is not yet an explicit committed unit test dedicated to that exact transport failure mode.

## Verdict

PASS. Stage 4B satisfies the QA gate in this session.

Exact next recommended prompt: `[Stage 4C-Plan]`

Stop after QA.
