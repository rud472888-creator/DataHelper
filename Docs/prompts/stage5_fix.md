Metadata
Stage ID: 5
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-05-qa.md, docs/reports/qa/stage-05-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md, UI/PDF source/tests
Required output files: docs/stages/stage-05-fix.md, docs/reports/dev/stage-05-handoff.md, docs/implement.md, fixed source/tests as needed
Gate condition: Only Stage 5 QA issues fixed; re-QA required.
Next recommended prompt: [Stage 5-QA]
Stop condition: Stop after fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only QA-reported UI/UX refinement issues.

Context
Stage 6 is blocked until Stage 5 fresh QA returns PASS.

Constraints
- Do not add new features.
- Do not change core data contracts unless required by QA defect.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Fixed UI/PDF source/tests/artifacts.
- docs/stages/stage-05-fix.md.
- Updated docs/implement.md and handoff.

Done when
All Stage 5 QA defects are addressed and validation reruns are recorded.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- relevant visual verification commands from QA report

Reporting
Map QA defects to fixes and record next prompt [Stage 5-QA].

Update files
Update only Stage 5 files needed for QA fixes.

Stop rule
Stop after fix handoff. Do not mark PASS. Do not start Stage 6.
