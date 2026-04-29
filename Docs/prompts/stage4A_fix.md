Metadata
Stage ID: 4A
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-04A-qa.md, docs/reports/qa/stage-04A-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md, Stage 4A source/tests
Required output files: docs/stages/stage-04A-fix.md, docs/reports/dev/stage-04A-handoff.md, docs/implement.md, fixed source/tests as needed
Gate condition: Only Stage 4A QA issues fixed; re-QA required.
Next recommended prompt: [Stage 4A-QA]
Stop condition: Stop after fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only QA-reported Standard Video CLI Pipeline issues.

Context
Stage 4B is blocked until Stage 4A fresh QA returns PASS.

Constraints
- Do not add RAW adapter features.
- Do not add GUI.
- Do not expand beyond QA findings.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Fixed Stage 4A code/tests.
- docs/stages/stage-04A-fix.md.
- Updated docs/implement.md and handoff.

Done when
All Stage 4A QA issues are fixed or documented as blockers and validation commands are rerun.

Validation
Run relevant failed QA commands plus:
- python -m pytest
- ruff check .
- mypy src

Reporting
Map QA defects to fixes and record re-QA requirement.

Update files
Update only Stage 4A files needed to fix QA findings.

Stop rule
Stop after fix handoff. Do not mark PASS. Do not start Stage 4B.
