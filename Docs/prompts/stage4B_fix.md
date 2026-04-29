Metadata
Stage ID: 4B
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-04B-qa.md, docs/reports/qa/stage-04B-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md, RAW adapter source/tests
Required output files: docs/stages/stage-04B-fix.md, docs/reports/dev/stage-04B-handoff.md, docs/implement.md, fixed source/tests as needed
Gate condition: Only Stage 4B QA issues fixed; re-QA required.
Next recommended prompt: [Stage 4B-QA]
Stop condition: Stop after fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only QA-reported RAW adapter integration issues.

Context
Stage 4C is blocked until Stage 4B fresh QA returns PASS.

Constraints
- Do not implement Layout A, PNG export, or GUI.
- Do not fake RAW success.
- Do not expand beyond QA findings.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Fixed RAW adapter source/tests.
- docs/stages/stage-04B-fix.md.
- Updated docs/implement.md and handoff.

Done when
QA issues are resolved or documented as blockers, and validation commands rerun.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src

Reporting
Map QA defects to fixes and record re-QA requirement.

Update files
Update only Stage 4B files required by QA findings.

Stop rule
Stop after fix handoff. Do not mark PASS. Do not start Stage 4C.
