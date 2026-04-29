# Stage 01 Fix

- lane: dev
- subphase: fix
- status: complete-with-blocker
- source_qa_report: `docs/reports/qa/stage-01-qa-report.md`
- next_recommended_prompt: `[Stage 1-QA]`

## Fix Scope

- Fix only the Stage 1 QA-reported bootstrap validation-path issues.
- Keep Stage 1 limited to the truthful package and CLI bootstrap. No Stage 2 architecture or media-pipeline work is allowed here.

## QA Issues And Fixes

1. Documentation fidelity issue resolved. `README.md` no longer presents `ruff check .` and `mypy src` as universally runnable commands from every fresh repository shell. It now distinguishes the PATH-dependent commands from the repo-local `.venv/bin/ruff check .` and `.venv/bin/mypy src` equivalents.
2. Command-availability blocker investigated and documented. The repository content itself is clean because `.venv/bin/ruff check .` and `.venv/bin/mypy src` both pass, but the exact QA commands still fail in the shared fresh shell with `command not found`. This fix run could not expose new `ruff` and `mypy` executables on PATH from inside the repository scope.

## Changed Files

- `README.md`
- `docs/implement.md`
- `docs/stages/stage-01-fix.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`
- `docs/reports/dev/stage-01-handoff.md`

## Validation Results

- `python -m frameproof --help` -> PASS
- `python -m pytest` -> PASS
- `ruff check .` -> FAIL (`zsh:1: command not found: ruff`)
- `mypy src` -> FAIL (`zsh:1: command not found: mypy`)
- `.venv/bin/ruff check .` -> PASS (`All checks passed!`)
- `.venv/bin/mypy src` -> PASS (`Success: no issues found in 5 source files`)

## Blocker Detail

- The fresh shared shell used in this session resolves `python` and `pytest` from a non-repo environment and does not expose the repo `.venv/bin` directory on PATH.
- The repository already contains working `ruff` and `mypy` executables under `.venv/bin`, so the failure is command discovery rather than lint or type errors.
- This session could not publish new executables into any writable PATH directory, so the exact Stage 1 QA commands remain blocked outside the repo-local `.venv/bin/...` path.

## Re-QA Instruction

- Run a fresh Stage 1 QA session with `[Stage 1-QA]`.
- Recheck the exact commands `python -m frameproof --help`, `python -m pytest`, `ruff check .`, and `mypy src`.
- If the raw `ruff` and `mypy` commands still fail, treat the remaining issue as an environment/PATH blocker rather than a bootstrap code defect.
