# Stage 07 QA

- lane: qa
- stage: stage-07
- verdict: PASS
- gate: passed
- next_recommended_prompt: none
- release_status: release-ready

## Summary

Independent QA re-ran Stage 7 in a fresh session against `README.md`, `Docs/setup-guide.md`, `Docs/dependency-guide.md`, `Docs/architecture-note.md`, `Docs/release-checklist.md`, `Docs/reports/final/final-report.md`, `Docs/stages/stage-07-plan.md`, `Docs/stages/stage-07-implement.md`, `Docs/reports/dev/stage-07-handoff.md`, `pyproject.toml`, and the current `tests/` tree. The Stage 7 gate clears in the current repository state: `python -m frameproof --help`, `python -m frameproof config`, `python -m frameproof config --format json`, `python -m pytest`, `ruff check .`, `mypy src`, `python -m frameproof.gui --help`, and `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` all passed; README-linked documents exist; the documented dependency-missing smoke remained explicit and left no stray artifacts; and the final report stays honest about external-tool limits, known issues, and backlog.

The remaining happy-path media-processing gaps are documented host constraints rather than hidden release claims. `ffmpeg`, `ffprobe`, and vendor RAW executables are not present on this host, so the standard-video and proprietary RAW success-path README examples were inspected rather than executed. That does not block the Stage 7 docs gate because the README, setup guide, dependency guide, release checklist, and final report all disclose those exact prerequisites and do not present blocked smoke as completed evidence.

## Evidence Checked

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
- `tests/`
- `tests/manual/gui_smoke_checklist.md`

## Validation Results

- `python -m frameproof --help` -> PASS
- `python -m frameproof config` -> PASS (`config_source: default`, `config_exists: False`)
- `python -m frameproof config --format json` -> PASS
- `python -m pytest` -> PASS (`95 passed, 9 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS (`Success: no issues found in 43 source files`)
- `python -m frameproof.gui --help` -> PASS
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS
- README-linked document existence check -> PASS (`missing_count: 0`)
- dependency-diagnostic smoke -> PASS (`EXIT:2`, explicit `dependency_missing`, no PDF/CSV/JSON artifacts left behind)

## Coverage Observations

- The prompt metadata listed `source/tests` as a required input path, but the repository test tree is `tests/`; there is no `source/tests` path in the current checkout.
- README command blocks were handled as required by the prompt:
- the module entrypoint, config diagnostics, GUI help, and GUI smoke commands were executed directly
- the interactive GUI launch command was inspected rather than run because it is a manual desktop workflow
- the standard-video and detailed-report CLI examples were inspected rather than run because this host lacks `ffmpeg` and `ffprobe`
- the console-script entrypoints were inspected in `pyproject.toml` under `[project.scripts]`; a fresh clean-install rerun was not fully reproducible in this sandbox because network access is restricted and the temporary validation venv could not fetch the declared build requirements
- `ffmpeg`, `ffprobe`, and `mediainfo` are absent on this host, matching the release checklist and final report claims that dependency-backed success-path smoke was not proven here.

## Evaluation

- Spec fidelity / product depth: PASS. The release docs match the implemented CLI, GUI, dependency, output, config-diagnostics, and known-limits surfaces described in Stage 7 planning and handoff.
- Functionality: PASS. All required validation commands passed, the dependency-missing smoke behaved as documented, and no README-linked doc target was missing.
- Visual design / UX clarity: PASS. The release-facing docs are readable, task-oriented, and consistent with the already-passing Stage 5/6 GUI QA baseline and the current offscreen GUI smoke.
- Code quality / maintainability: PASS. Stage 7 is docs-only, does not overstate implementation, and keeps release-facing guidance aligned to durable repo behavior rather than hidden session knowledge.
- Accessibility / responsiveness: PASS. No Stage 7 implementation changed the GUI, the prior accessibility/responsiveness gate remains passing in `Docs/qa.md`, and current offscreen GUI startup still succeeds.
- Validation completeness: PASS. Every required gate command was run in this session, every README-linked document was verified, and the remaining README smoke commands were either executed or explicitly inspected with host blockers documented.

## Defects

No blocking Stage 7 defects were reproduced in the current repository state.

## Residual Risks

- Release readiness on a host with real media still depends on installing `ffmpeg` and `ffprobe` for standard-video work.
- Proprietary RAW happy-path validation still depends on operator-supplied executables, runtime support, and license clearance.
- Fresh-install console-script verification was inspected rather than fully rerun because the sandboxed QA host cannot fetch missing build requirements during temp-venv reproduction.

## Gate Decision

PASS. Stage 07 satisfies the final QA gate and the project may be marked release-ready.

Exact next recommended prompt: none

Stop after QA.
