# Stage 04B QA

- lane: qa
- stage: stage-04B
- verdict: PASS
- gate: passed
- next_recommended_prompt: `[Stage 4C-Plan]`
- stage_4c_status: unblocked-by-qa

## Summary

Independent QA re-ran Stage 4B in a fresh session against the Stage 4B plan, implementation handoff, architecture, API contract, current RAW adapter sources, and current tests. The required command suite passes, RAW adapters resolve to real subprocess-backed clients instead of deferred success paths, missing RAW dependencies surface as structured `dependency_missing` results, malformed subprocess JSON is normalized into structured probe failures, and RAW adapter code stays subprocess-isolated without direct vendor SDK imports into Python. No real vendor binaries are installed in this environment, so optional live-tool smoke remains blocked here; under that constraint, the required graceful-failure path was verified directly with a real CLI RAW-only batch and an adapter-crash smoke.

## Evidence Checked

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

## Validation Results

- `python -m pytest` -> PASS (`63 passed, 1 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `grep -R "subprocess" src/frameproof/adapters docs/api-contract.md` -> PASS (RAW adapter source hits are limited to the subprocess-backed client layers and the contract doc)
- `grep -R "dependency_missing" src/frameproof tests docs` -> PASS (normalized dependency-missing vocabulary is present in source, tests, and docs)
- `ffmpeg=missing`, `ffprobe=missing`, `mediainfo=missing`, `braw_adapter=missing`, `r3d_adapter=missing`, `art-cmd=missing`, `arri_art_cmd=missing` -> BLOCKED for optional real-tool smoke; graceful missing-dependency behavior was validated instead
- `python -m frameproof --input <tmp>/clip.braw --input <tmp>/A001_C001_001.R3D --input <tmp>/clip.ari --middle-count 1 --layout contact_sheet --output <tmp>/report.pdf --csv <tmp>/report.csv --json <tmp>/report.json` -> PASS (`EXIT:2`, explicit `dependency_missing` diagnostics for `braw_adapter`, `r3d_adapter`, and `arri_art_cmd`; no PDF/CSV/JSON written)
- `python - <<'PY' ... BRAWAdapterClient crash smoke ... PY` -> PASS (`{'probe_ok': False, 'probe_status': 'probe_failed', 'probe_error': 'probe_failed', 'capture_status': 'decode_failed', 'capture_error': 'probe_failed'}`)

## Evaluation

- Spec fidelity / product depth: PASS. RAW routing now resolves `.braw`, `.r3d`, and `.ari` to real adapter clients instead of Stage 4A deferrals, matching [src/frameproof/core/adapter_resolver.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/core/adapter_resolver.py:45), the Stage 4B plan, and the architecture contract.
- Functionality: PASS. Shared dependency inspection returns `not_configured`, `configured_missing`, and `runtime_error` states for RAW tools, and probe execution converts unavailable adapters into structured `dependency_missing` results before touching media, as shown in [src/frameproof/core/dependency_inspector.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/core/dependency_inspector.py:96) and [src/frameproof/core/probe_service.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/core/probe_service.py:46).
- Visual design / UX clarity: PASS for current scope. This stage is backend and CLI-facing only, and the CLI now prints actionable dependency diagnostics naming the RAW adapter and dependency state during the fatal zero-processable-files path.
- Code quality / maintainability: PASS. BRAW and R3D share one subprocess transport in [src/frameproof/adapters/_json_subprocess_adapter.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/adapters/_json_subprocess_adapter.py:43), ARRIRAW stays isolated in its own ART CMD client at [src/frameproof/adapters/arriraw_art_adapter_client.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/adapters/arriraw_art_adapter_client.py:33), and R3D grouping stays conservative and deterministic in [src/frameproof/core/clip_grouper.py](/Users/server_jay/Desktop/DataHelper/src/frameproof/core/clip_grouper.py:48).
- Accessibility / responsiveness: PASS for current scope. No GUI surface changed, and the CLI path remains deterministic and non-interactive.
- Validation completeness: PASS for this environment. The full automated suite passed, missing-dependency CLI behavior was verified directly, malformed JSON behavior is covered by unit tests, runtime-error dependency checks are covered by unit tests, and a manual subprocess-crash smoke confirmed structured error normalization even without vendor binaries installed locally.

## Findings

1. No blocking defects were found in the Stage 4B QA scope.
2. Residual risk: real vendor-runtime smoke for actual `BRAW`, R3D, and ARRI tools remains environment-blocked on this machine because none of those executables are installed or configured.

## Gate Decision

PASS. Stage 4B satisfies the QA gate in this session.

Exact next recommended prompt: `[Stage 4C-Plan]`

Stop after QA.
