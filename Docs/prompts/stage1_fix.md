Metadata
Stage ID: 1
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-01-qa.md, docs/reports/qa/stage-01-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md
Required output files: docs/stages/stage-01-fix.md, docs/reports/dev/stage-01-handoff.md, docs/implement.md, docs/stage.md
Gate condition: Only Stage 1 QA issues fixed; re-QA required.
Next recommended prompt: [Stage 1-QA]
Stop condition: Stop after fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only QA-reported Stage 1 bootstrap issues.

Context
Stage 1 cannot pass until fresh QA returns PASS.

Constraints
- Do not add Stage 2 architecture work.
- Do not implement media pipeline features.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Fixed bootstrap files.
- docs/stages/stage-01-fix.md.
- Updated docs/implement.md.
- Updated docs/reports/dev/stage-01-handoff.md.
- docs/stage.md pointing back to [Stage 1-QA].

Done when
Every QA issue is resolved or documented as a blocker, and validation commands are rerun.

Validation
Run the failed Stage 1 QA commands again, plus:
- python -m frameproof --help
- python -m pytest
- ruff check .
- mypy src

Reporting
Document exact QA issue mapping, fixes, validation outputs, and re-QA instruction.

Update files
Update only files needed for Stage 1 QA fixes.

Stop rule
Stop after fix handoff. Do not mark PASS. Do not proceed to Stage 2.
