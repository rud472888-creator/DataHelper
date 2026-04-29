Metadata
Stage ID: 2
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-02-qa.md, docs/reports/qa/stage-02-qa-report.md, docs/qa.md, docs/stage.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md, docs/ui-spec.md, docs/release-checklist.md
Required output files: docs/stages/stage-02-fix.md, docs/reports/dev/stage-02-handoff.md, docs/implement.md, updated architecture docs as needed
Gate condition: Only Stage 2 QA issues fixed; re-QA required.
Next recommended prompt: [Stage 2-QA]
Stop condition: Stop after fix handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix Stage 2 architecture/documentation issues found by QA.

Context
Stage 3 cannot start until Stage 2 fresh QA returns PASS.

Constraints
- Do not implement application code.
- Do not expand product scope beyond the source spec.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Updated docs resolving QA findings.
- docs/stages/stage-02-fix.md.
- Updated docs/implement.md and docs/reports/dev/stage-02-handoff.md.

Done when
All QA issues have exact resolution notes and Stage 2 is ready for fresh QA rerun.

Validation
Run the relevant grep/file checks from Stage 2 QA and document results.

Reporting
Map every QA issue to a fix or blocker. Record next prompt [Stage 2-QA].

Update files
Update only Stage 2 documentation and handoff files needed for QA fixes.

Stop rule
Stop after fix handoff. Do not mark PASS. Do not start Stage 3.
