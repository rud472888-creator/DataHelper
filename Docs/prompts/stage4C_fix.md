Metadata
Stage ID: 4C
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-04C-qa.md, docs/reports/qa/stage-04C-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md, Stage 4C source/tests
Required output files: docs/stages/stage-04C-fix.md, docs/reports/dev/stage-04C-handoff.md, docs/implement.md, fixed source/tests as needed
Gate condition: Only Stage 4C QA issues fixed; re-QA required.
Next recommended prompt: [Stage 4C-QA]
Stop condition: Stop after fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only QA-reported Layout A/export/failure section issues.

Context
Stage 4D is blocked until Stage 4C fresh QA returns PASS.

Constraints
- Do not add GUI.
- Do not alter RAW adapter scope unless QA defect requires preserving existing behavior.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Fixed Stage 4C code/tests.
- docs/stages/stage-04C-fix.md.
- Updated docs/implement.md and handoff.

Done when
All QA findings are resolved or documented as blockers and validation reruns are recorded.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src

Reporting
Map QA findings to fixes and record next prompt [Stage 4C-QA].

Update files
Update only Stage 4C files needed for QA fixes.

Stop rule
Stop after fix handoff. Do not mark PASS. Do not start Stage 4D.
