Metadata
Stage ID: 7
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-07-qa.md, docs/reports/qa/stage-07-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md, release docs/source/tests as relevant
Required output files: docs/stages/stage-07-fix.md, docs/reports/dev/stage-07-handoff.md, docs/implement.md, fixed docs/source/tests as needed
Gate condition: Only Stage 7 QA issues fixed; re-QA required.
Next recommended prompt: [Stage 7-QA]
Stop condition: Stop after fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only final release QA issues.

Context
Release-ready status is blocked until Stage 7 fresh QA returns PASS.

Constraints
- Do not add new product features.
- Do not hide unresolved issues.
- Do not overclaim proprietary SDK support.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Fixed release docs/source/tests as required.
- docs/stages/stage-07-fix.md.
- Updated docs/implement.md and handoff.

Done when
All Stage 7 QA issues are resolved or documented as blockers and validation reruns are recorded.

Validation
Run:
- python -m frameproof --help
- python -m pytest
- ruff check .
- mypy src
- relevant documented smoke checks from QA report

Reporting
Map QA issues to fixes and record next prompt [Stage 7-QA].

Update files
Update only files required by Stage 7 QA findings.

Stop rule
Stop after fix handoff. Do not mark release-ready. Re-run Stage 7 QA in a fresh session.
