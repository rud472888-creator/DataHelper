Metadata
Stage ID: 4D
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-04D-qa.md, docs/reports/qa/stage-04D-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md, GUI source/tests
Required output files: docs/stages/stage-04D-fix.md, docs/reports/dev/stage-04D-handoff.md, docs/implement.md, fixed source/tests as needed
Gate condition: Only Stage 4D QA issues fixed; re-QA required.
Next recommended prompt: [Stage 4D-QA]
Stop condition: Stop after fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only QA-reported GUI/settings/progress issues.

Context
Stage 5 is blocked until Stage 4D fresh QA returns PASS.

Constraints
- Do not add new feature scope.
- Do not rewrite core architecture.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Fixed GUI/settings/progress source/tests.
- docs/stages/stage-04D-fix.md.
- Updated docs/implement.md and handoff.

Done when
Every QA issue is resolved or documented as blocker and validation reruns are recorded.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- relevant GUI smoke/manual checks from QA report

Reporting
Map QA findings to fixes and record next prompt [Stage 4D-QA].

Update files
Update only Stage 4D files needed for QA fixes.

Stop rule
Stop after fix handoff. Do not mark PASS. Do not start Stage 5.
