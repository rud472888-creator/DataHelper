# Stage 01 Implement

- lane: dev
- subphase: implement
- status: complete
- scope_boundary: bootstrap-shell-only
- next_recommended_prompt: `[Stage 1-QA]`

## Delivered Scope

- Created the first real Python project shell for Frame Proof with packaging metadata and a `src/` package layout.
- Added a truthful CLI surface that supports help, version, and config diagnostics only.
- Added bootstrap tests that verify importability and CLI behavior without pretending media processing exists.
- Updated the Stage 1 delivery records so a fresh QA or Dev worker can continue from repository files only.

## Changed Files And Reasons

- `pyproject.toml` defines project metadata, build settings, console entrypoint, and test/lint/typecheck configuration.
- `README.md` explains the bootstrap boundary, supported commands, and validation workflow.
- `frameproof/__init__.py` and `frameproof/__main__.py` provide a repo-root shim so `python -m frameproof` works before installation.
- `src/frameproof/__about__.py` centralizes the package version.
- `src/frameproof/__init__.py` exposes package metadata from the installable source tree.
- `src/frameproof/__main__.py` enables module execution from the installable package.
- `src/frameproof/cli.py` implements the honest bootstrap CLI surface.
- `src/frameproof/settings.py` implements real config-path diagnostics instead of fake processing behavior.
- `tests/test_cli.py` verifies help, version, default config behavior, and env override behavior.
- `tests/test_package.py` verifies package metadata export and runtime snapshot shape.
- `scripts/orchestrator_watch.py` drops an unused import so the required repo-wide lint run passes cleanly.
- `docs/implement.md` records the Stage 1 implementation state and validation evidence.
- `docs/stage.md` advances the board to fresh QA for Stage 1.
- `docs/reports/status/current-status.md` mirrors the board state for the repo status report.
- `docs/reports/dev/stage-01-handoff.md` captures the Stage 1 Dev handoff.

## Implementation Decisions

- Kept runtime dependencies at zero because the bootstrap CLI only needs standard-library behavior.
- Used a `src/` package for the installable project but added a repo-root shim because the stage contract requires `python -m frameproof` to work before any install step.
- Limited the CLI to `--help`, `--version`, and `config` diagnostics so the bootstrap remains truthful about missing scan, adapter, capture, and PDF features.
- Implemented config diagnostics around real environment and filesystem state only: config source, resolved path, path existence, working directory, and Python executable.

## Data/API/State Ownership Changes

- Introduced the first application runtime contract: `RuntimeSnapshot` in `src/frameproof/settings.py`.
- Package metadata ownership now lives in `src/frameproof/__about__.py`.
- CLI ownership now lives in `src/frameproof/cli.py`, while repo execution compatibility lives in the root `frameproof/` shim.
- Workflow state ownership remains documentary in `docs/stage.md`, `docs/implement.md`, and `docs/reports/`.

## UI Behavior Notes

- The only product-facing behavior in Stage 1 is a CLI shell.
- The CLI explicitly states that media scanning, frame capture, and PDF generation are not implemented in this stage.
- `config` diagnostics report current runtime state only; they do not simulate project settings or probe unavailable features.

## Validation Results

- `python -m frameproof --help` -> PASS; usage shows only `config` plus the statement that media scanning, frame capture, and PDF generation are not implemented in this stage.
- `python -m pytest` -> PASS; 6 tests passed in 0.15s.
- `ruff check .` -> PASS; run with `PATH="$PWD/.venv/bin:$PATH"` because `ruff` is installed in the repo virtualenv but not on the base shell PATH. Output: `All checks passed!`
- `mypy src` -> PASS; run with `PATH="$PWD/.venv/bin:$PATH"` because `mypy` is installed in the repo virtualenv but not on the base shell PATH. Output: `Success: no issues found in 5 source files`

## Blockers And Known Gaps

- Stage 1 is not QA-passed yet; a fresh QA run is still required before Stage 2 work.
- No scanner, adapter, capture, manifest, or PDF pipeline exists yet by design.
- No persisted config loader exists yet; the current `config` command is limited to diagnostics about the resolved config path.
