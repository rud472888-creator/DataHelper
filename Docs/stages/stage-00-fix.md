# Stage 00 Fix

- lane: dev
- subphase: fix
- status: complete
- source_qa_report: `docs/reports/qa/stage-00-qa-report.md`
- next_recommended_prompt: `[Stage 0-QA]`

## Fix Scope

- Fix only the four documentation gaps called out in the failing Stage 0 QA report.
- Keep Stage 0 docs-only and avoid any product implementation or unrelated document churn.

## QA Issues And Fixes

1. `docs/stages/stage-00-plan.md` was only a stub. It now records the Stage 0 source spec path, scope, planned touched files, risks, assumptions, acceptance criteria, validation plan, and historical next prompt.
2. `docs/stages/stage-00-implement.md` was only a stub. It now records the actual Stage 0 docs-only implementation scope, changed files and reasons, implementation decisions, ownership notes, validation results, blockers, and next prompt.
3. `docs/implement.md` was missing mandatory Stage 0 handoff fields. It now includes current stage/subphase, lane, completed functionality, changed files and reasons, implementation decisions, data/API/state ownership changes, UI behavior notes, validation commands/results, known blockers, QA status by stage, latest QA verdict/report, latest Dev handoff path, next prompt, assumptions, manual verification steps, and fresh-session notes.
4. `docs/stage.md` still pointed to the fix run as the next step. It now records the post-fix board state and routes the repository to a fresh `[Stage 0-QA]` rerun.

## Changed Files

- `docs/stages/stage-00-plan.md`
- `docs/stages/stage-00-implement.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`
- `docs/stages/stage-00-fix.md`
- `docs/reports/dev/stage-00-handoff.md`

## Validation Results

- `find docs -maxdepth 3 -type f | sort` -> PASS
- `grep -R "Stage 0" docs/stage.md docs/implement.md docs/qa.md` -> PASS
- `test -f AGENTS.md` -> PASS
- `test -f docs/reports/dev/stage-00-handoff.md` -> PASS
- `test -f pyproject.toml` -> expected absent, exit 1
- `test -d src` -> expected absent, exit 1
- `test -d tests` -> expected absent, exit 1

## Re-QA Instruction

- Run a fresh Stage 0 QA session with `[Stage 0-QA]`.
- Do not start Stage 1 unless QA returns PASS.
