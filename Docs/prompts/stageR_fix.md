Metadata
Stage ID: R
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-R-qa.md, docs/reports/qa/stage-R-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md
Required output files: docs/stages/stage-R-fix.md, docs/reports/dev/stage-R-handoff.md, corrected durable docs if needed
Gate condition: Only Stage R QA issues fixed; re-QA required.
Next recommended prompt: [Stage R-QA]
Stop condition: Stop after recovery fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only recovery QA issues in durable memory.

Context
Recovery cannot be trusted until Stage R fresh QA returns PASS.

Constraints
- Do not modify product source.
- Do not mark any stage PASS without a matching QA PASS report.
- Do not advance the project.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Corrected recovery docs.
- docs/stages/stage-R-fix.md.
- docs/reports/dev/stage-R-handoff.md.

Done when
All Stage R QA findings are resolved or documented as blockers, and next prompt is [Stage R-QA].

Validation
Run:
- cat docs/stage.md
- cat docs/qa.md
- find docs/stages docs/reports -maxdepth 2 -type f | sort

Reporting
Map recovery QA issues to fixes and record re-QA requirement.

Update files
Update only durable docs needed for recovery QA fixes.

Stop rule
Stop after fix handoff. Do not mark recovery PASS. Do not run the recovered project prompt.
