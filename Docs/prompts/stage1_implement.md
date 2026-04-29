Metadata
Stage ID: 1
Sub-phase: Implement
Lane: Dev
Required input files: AGENTS.md, docs/stages/stage-01-plan.md, docs/stage.md, docs/implement.md, docs/source/frameproof_tech_spec_ko.md or frameproof_tech_spec_ko.md
Required output files: pyproject.toml, src/frameproof/, tests/, README.md, docs/stages/stage-01-implement.md, docs/reports/dev/stage-01-handoff.md, docs/implement.md
Gate condition: Real project shell created and validation commands run.
Next recommended prompt: [Stage 1-QA]
Stop condition: Stop after implementation handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Implement the Greenfield Bootstrap.

Context
Create a minimal, real, testable Python app shell for Frame Proof without pretending that media processing is complete.

Constraints
- Do not implement full scanner/adapter/PDF pipeline yet.
- CLI may expose `--help` and version/config diagnostics only.
- Do not create fake media processing behavior.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- pyproject.toml with project metadata and dev dependencies.
- src/frameproof package with importable app shell.
- CLI entrypoint that supports help/version without claiming unimplemented features.
- tests directory with bootstrap tests.
- README.md bootstrap section.
- docs/implement.md updated with required fields.
- docs/stages/stage-01-implement.md.
- docs/reports/dev/stage-01-handoff.md.

Done when
- `python -m frameproof --help` works.
- Tests/lint/typecheck commands are configured and run.
- No unimplemented core feature is falsely presented as complete.
- docs/stage.md shows Stage 1 Implement complete and next prompt [Stage 1-QA].

Validation
Run:
- python -m frameproof --help
- python -m pytest
- ruff check .
- mypy src

Reporting
Document changed files, why they changed, implementation decisions, command outputs, known issues, and next prompt in docs/implement.md and stage handoff.

Update files
Update project bootstrap files and Stage 1 implementation docs.

Stop rule
Stop after writing the Dev handoff. Do not run QA or start Stage 2.
