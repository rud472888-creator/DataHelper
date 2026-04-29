Metadata
Stage ID: 6
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-06-qa.md, docs/reports/qa/stage-06-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md, source/tests
Required output files: docs/stages/stage-06-fix.md, docs/reports/dev/stage-06-handoff.md, docs/implement.md, fixed source/tests as needed
Gate condition: Only Stage 6 QA issues fixed; re-QA required.
Next recommended prompt: [Stage 6-QA]
Stop condition: Stop after fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only QA-reported hardening issues.

Context
Stage 7 is blocked until Stage 6 fresh QA returns PASS.

Constraints
- Do not add new product features.
- Do not weaken validation.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Fixed hardening source/tests.
- docs/stages/stage-06-fix.md.
- Updated docs/implement.md and handoff.

Done when
All Stage 6 QA findings are resolved or documented as blockers and validation reruns are recorded.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- relevant smoke/security checks from QA report

Reporting
Map QA issues to fixes and record next prompt [Stage 6-QA].

Update files
Update only Stage 6 files required by QA findings.

Stop rule
Stop after fix handoff. Do not mark PASS. Do not start Stage 7.
