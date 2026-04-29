# Stage 01 Plan

- lane: dev
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_0_pass_verified: yes
- next_recommended_prompt: `[Stage 1-Implement]`

## Gate Verification

- Stage 0 PASS is confirmed in `docs/stage.md` (`qa_gate: pass`, `last_result: stage-00-qa-pass`) and `docs/qa.md` (`latest_verdict: PASS`, `Stage 00 verdict: PASS`).
- Stage 1 planning is therefore allowed.

## Scope

- Create the implementation plan for a minimal but real Python bootstrap that matches the repo's greenfield state and the product's CLI-first delivery path.
- Establish project metadata, package layout, CLI entrypoint shape, test/lint/typecheck wiring, and a small documentation shell only.
- Keep the bootstrap honest: the CLI may expose help, version, and basic config diagnostics, but it must not imply that scanning, probe, capture, rendering, or manifest generation already exist.
- Choose conventions that can grow into the staged architecture already described in `docs/plan.md` without forcing a rewrite during later pipeline stages.

## Non-Scope

- No scanner, grouping, adapter, probe, capture, renderer, manifest, or GUI implementation.
- No fake media-processing behavior, sample outputs, or placeholder success paths.
- No external-tool integration for FFmpeg, FFprobe, MediaInfo, BRAW, R3D, or ARRIRAW yet.
- No packaging, release automation, fixture matrix, or performance work beyond the basic dev-tool wiring.

## Evidence And Planning Basis

- The board already points to Stage 1 planning and records Stage 0 QA PASS in `docs/stage.md`.
- QA independently records Stage 0 PASS and no blocker in `docs/qa.md`.
- The product spec defines Frame Proof as a local desktop and CLI tool for clip scan, metadata extraction, representative frame capture, and PDF/manifest generation in `docs/frameproof_tech_spec_ko.md`.
- The same spec confirms CLI is part of the product surface, while scan/probe/capture/report behavior belongs to later functional work, not bootstrap.
- `docs/plan.md` already sequences delivery as CLI-first and explicitly places the Python project skeleton before the standard-format pipeline.
- Repository inspection shows orchestration docs are present, but there is still no `pyproject.toml`, `src/`, or `tests/` tree, so Stage 1 remains greenfield bootstrap work.

## Proposed File And Module Structure

Planned implementation files for the next phase:

- `pyproject.toml`
- `README.md`
- `src/frameproof/__init__.py`
- `src/frameproof/__main__.py`
- `src/frameproof/cli.py`
- `src/frameproof/settings.py`
- `tests/test_cli.py`
- `tests/test_version.py`
- `docs/stages/stage-01-implement.md`
- `docs/reports/dev/stage-01-handoff.md`
- `docs/implement.md`

Bootstrap layout rationale:

- Use a `src/` layout to avoid import-path ambiguity and to keep packaging behavior clean from the first implementation pass.
- Use the package name `frameproof` because the Stage 1 implement contract requires `python -m frameproof --help`.
- Keep the package intentionally small: `__main__.py` runs the CLI, `cli.py` owns argument parsing and command dispatch, and `settings.py` provides only real config-path or environment diagnostics needed for the bootstrap CLI.
- Defer `core/`, `adapters/`, `render/`, and `output/` packages until those responsibilities have real behavior to hold.

## Dependency Choices And Rationale

### Runtime

- Python `>=3.11`
- No third-party runtime dependencies in Stage 1

Rationale:

- The local environment is already on Python 3.11, and the repository cache state also reflects 3.11 usage.
- `argparse`, `pathlib`, and other standard-library modules are enough for a truthful bootstrap CLI.
- Avoiding runtime dependencies now keeps the shell small and reduces churn before the media pipeline shape is implemented.

### Build And Tooling

- `setuptools` as the build backend in `pyproject.toml`
- `pytest` for tests
- `ruff` for linting
- `mypy` for type checking

Rationale:

- `setuptools` keeps the packaging baseline conventional and lightweight for a greenfield Python shell.
- `pytest`, `ruff`, and `mypy` directly satisfy the Stage 1 requirement to wire tests, linting, and type checking.
- Do not add Click, Typer, Rich, or media-related libraries yet because the bootstrap CLI does not need them and later product stages may change those tradeoffs.

## Planned Touched Files In Stage 1 Implement

- `pyproject.toml`: project metadata, build backend, console/module entrypoint, and tool configuration.
- `README.md`: bootstrap usage and development commands.
- `src/frameproof/__init__.py`: package marker and version surface.
- `src/frameproof/__main__.py`: `python -m frameproof` entrypoint.
- `src/frameproof/cli.py`: help/version/config-diagnostic CLI only.
- `src/frameproof/settings.py`: real bootstrap diagnostics such as package/config path inspection, not product logic.
- `tests/test_cli.py`: CLI help and diagnostic coverage.
- `tests/test_version.py`: version and import smoke coverage.
- `docs/implement.md`, `docs/stages/stage-01-implement.md`, `docs/reports/dev/stage-01-handoff.md`: durable implementation handoff records.

## Validation Command Plan

- `python -m frameproof --help`
- `python -m frameproof --version`
- `python -m pytest`
- `ruff check .`
- `mypy src`

## Acceptance Criteria

- A real `pyproject.toml` exists and configures packaging, tests, linting, and type checking.
- `src/frameproof` is importable and `python -m frameproof --help` exits successfully.
- The CLI only exposes truthful bootstrap surfaces such as help, version, or config diagnostics; it does not claim scan/report features are implemented.
- A `tests/` tree exists with bootstrap coverage for import and CLI behavior.
- `README.md` explains the bootstrap state and developer validation commands.
- Stage 1 implementation handoff docs are written for a fresh-session worker and `docs/stage.md` advances to `[Stage 1-QA]` after implementation.

## Risks

- Package naming drift could break `python -m frameproof` if the implementation chooses a different import root.
- A too-ambitious bootstrap may accidentally start Stage 2 product work early.
- Adding convenience CLI libraries now would create avoidable dependency churn before the command surface is stable.
- The repo contains both `docs/` and `Docs/` trees; implementation work should avoid accidental duplicate edits unless a future prompt explicitly expands scope.

## Assumptions

- The lowercase `docs/` tree remains the active workflow memory because current stage files and prompts point there.
- Stage 1 implementation is allowed to create the initial Python shell but must stay short of real media-processing behavior.
- Python 3.11 is an acceptable baseline for the first bootstrap pass.
- README and test scaffolding are part of the bootstrap contract even though the product pipeline is still absent.

## Exact Next Prompt

`[Stage 1-Implement]`

## Outcome

Stage 1 planning defines a narrow bootstrap target: create a real Python package shell, CLI help/version/config diagnostics, and validation tooling, while explicitly deferring all media pipeline behavior to later stages.
