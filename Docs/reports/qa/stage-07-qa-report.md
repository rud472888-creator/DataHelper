# Stage 07 QA Report

- gate: passed
- verdict: PASS
- stage: stage-07
- lane: qa
- next_recommended_prompt: none
- release_status: release-ready

## Scope

Independent QA review of Stage 7 release readiness against:

- `README.md`
- `Docs/setup-guide.md`
- `Docs/dependency-guide.md`
- `Docs/architecture-note.md`
- `Docs/release-checklist.md`
- `Docs/reports/final/final-report.md`
- `Docs/stages/stage-07-plan.md`
- `Docs/stages/stage-07-implement.md`
- `Docs/reports/dev/stage-07-handoff.md`
- `pyproject.toml`
- `tests/`

This was a QA-only gate. No implementation files were modified. Only QA/status documents were updated.

## Checked Files

- `AGENTS.md`
- `README.md`
- `Docs/setup-guide.md`
- `Docs/dependency-guide.md`
- `Docs/architecture-note.md`
- `Docs/release-checklist.md`
- `Docs/reports/final/final-report.md`
- `Docs/stages/stage-07-plan.md`
- `Docs/stages/stage-07-implement.md`
- `Docs/reports/dev/stage-07-handoff.md`
- `Docs/qa.md`
- `Docs/stage.md`
- `Docs/reports/status/current-status.md`
- `pyproject.toml`
- `tests/test_cli.py`
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/integration/test_dependency_missing.py`
- `tests/integration/test_raw_dependency_missing.py`
- `tests/test_package.py`
- `tests/unit/gui/test_main_window.py`
- `tests/manual/gui_smoke_checklist.md`

## Command Results

- `python -m frameproof --help` -> PASS

```text
usage: frameproof [-h] [--version] [--input PATH] [--recursive]
                  [--no-recursive] [--middle-count {0,1,2,3}]
                  [--layout {contact_sheet,detail}] [--output PDF_PATH]
                  [--csv CSV_PATH] [--json JSON_PATH] [--export-stills]
                  [--stills-dir PATH] [--project-name NAME]
                  [--ffmpeg-path FFMPEG_PATH] [--ffprobe-path FFPROBE_PATH]
                  [--mediainfo-path MEDIAINFO_PATH] [--braw-adapter-path PATH]
                  [--r3d-adapter-path PATH] [--arri-art-cmd-path PATH]
```

- `python -m frameproof config` -> PASS

```text
Frame Proof runtime diagnostics
config_source: default
config_path: /Users/server_jay/.config/frameproof/config.toml
config_exists: False
working_directory: /Users/server_jay/Desktop/DataHelper
python_executable: /Users/server_jay/.pyenv/versions/3.11.9/bin/python3.11
```

- `python -m frameproof config --format json` -> PASS

```json
{
  "config_exists": false,
  "config_path": "/Users/server_jay/.config/frameproof/config.toml",
  "config_source": "default",
  "python_executable": "/Users/server_jay/.pyenv/versions/3.11.9/bin/python3.11",
  "working_directory": "/Users/server_jay/Desktop/DataHelper"
}
```

- `python -m pytest` -> PASS

```text
======================== 95 passed, 9 skipped in 2.76s =========================
```

- `ruff check .` -> PASS

```text
All checks passed!
```

- `mypy src` -> PASS

```text
Success: no issues found in 43 source files
```

- `python -m frameproof.gui --help` -> PASS

```text
usage: python -m frameproof.gui [-h] [--settings-file PATH] [--smoke-test]

Launch the Frame Proof PySide6 GUI.
```

- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS

```text
[no output]
```

- README-linked document existence audit -> PASS

```text
Docs/setup-guide.md OK
Docs/dependency-guide.md OK
Docs/examples/frameproof.example.toml OK
Docs/setup-guide.md OK
Docs/dependency-guide.md OK
Docs/architecture-note.md OK
Docs/release-checklist.md OK
Docs/reports/final/final-report.md OK
tests/manual/gui_smoke_checklist.md OK
```

- dependency-diagnostic smoke -> PASS

```text
status: partial_success
total_clips: 1
success_count: 0
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 1
dependency_missing: clip=empty.mp4 status=dependency_missing adapter=ffmpeg required_tools=ffmpeg,ffprobe dependency_state=configured_missing
fatal: batch could not produce a report
EXIT_CODE=2
/tmp/frameproof-stage7-qa-smoke.3G6bem/empty.mp4
```

## README Smoke Audit

- Install block (`python3 -m venv .venv`, `source .venv/bin/activate`, `python -m pip install --upgrade pip`, `python -m pip install -e '.[dev]'`) -> INSPECTED. A fresh temp-venv reproduction was attempted, but this sandboxed host cannot fetch the declared build requirements (`setuptools>=69`, `wheel`) because network access is restricted.
- Module entrypoint block (`python -m frameproof --help`, `python -m frameproof.gui --help`) -> PASS.
- Console-script block (`frameproof --help`, `frameproof-gui --help`) -> INSPECTED via `pyproject.toml` `[project.scripts]`. The current host has a stale `.venv/bin/frameproof` wrapper and no `frameproof-gui` wrapper on `PATH`, which is not reliable evidence for or against a fresh install because the install block could not be rerun to completion in this sandbox.
- Config diagnostics block (`python -m frameproof config`, `python -m frameproof config --format json`) -> PASS.
- Standard-video happy-path example -> INSPECTED. Options and paths match the current CLI surface, but execution is blocked on this host because `ffmpeg` and `ffprobe` are absent.
- Detailed-report plus still-export example -> INSPECTED. Options match the current CLI surface, but execution is blocked on this host for the same external-tool reason.
- GUI launch block (`python -m frameproof.gui`) -> INSPECTED. Interactive desktop launch is a manual flow; the required `--help` and offscreen `--smoke-test` commands both passed.

## Coverage Observations

- The prompt metadata listed `source/tests` as a required input path, but the repository uses `tests/`.
- `tests/integration/test_cli_standard_pipeline.py` remains the regression coverage for standard-video happy-path artifact generation; those tests are skipped here because `ffmpeg` and `ffprobe` are missing locally.
- `tests/integration/test_dependency_missing.py` and `tests/integration/test_raw_dependency_missing.py` provide direct coverage for the explicit failure-path behavior documented in the README and setup guide.
- The final report includes known issues and backlog items for packaging, dependency-enabled smoke, proprietary RAW validation, and config-driven execution limits, and those claims match the repository evidence inspected in this session.

## Evaluation

- Spec fidelity / product depth: PASS. The docs accurately describe the shared pipeline, output contract, dependency model, config-diagnostics limitation, and known release caveats already established in the repository.
- Functionality: PASS. Required commands passed, dependency-missing behavior stayed explicit, and linked docs are present.
- Visual design / UX clarity: PASS. Release-facing documentation is coherent and usable, and no Stage 7 change regressed the previously passing GUI communication baseline.
- Code quality / maintainability: PASS. Stage 7 makes no implementation changes, keeps release guidance aligned to durable evidence, and avoids overclaiming unsupported packaging or dependency behavior.
- Accessibility / responsiveness: PASS. The current GUI still passes the required offscreen smoke, and prior GUI accessibility/responsiveness evidence remains intact in the durable QA ledger.
- Validation completeness: PASS. All mandatory validation commands were run. Remaining README commands were inspected where host constraints or interactivity made execution unsuitable, and those limits are disclosed rather than hidden.

## Defects

No blocking Stage 7 defects were reproduced.

## Residual Risks

- Happy-path standard-video generation remains host-dependent on `ffmpeg` and `ffprobe`.
- Proprietary RAW happy-path validation remains host-dependent on vendor tools, runtime support, and licensing.
- Fresh-install console-script execution was not end-to-end reproven in a clean temp venv because the sandboxed host could not satisfy the declared build requirements without network access.

## Gate Decision

PASS. The release docs, validation evidence, dependency caveats, and final report are sufficient for release-ready status.

Exact next recommended prompt: none

Stop after QA.
