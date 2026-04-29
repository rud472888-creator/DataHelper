Metadata
Stage ID: 0
Sub-phase: Fix
Lane: Dev
Required input files: docs/stages/stage-00-qa.md, docs/reports/qa/stage-00-qa-report.md, docs/qa.md, docs/stage.md, docs/implement.md
Required output files: docs/stages/stage-00-fix.md, docs/reports/dev/stage-00-handoff.md, docs/implement.md, docs/stage.md
Gate condition: Only QA-reported Stage 0 issues fixed; re-QA required.
Next recommended prompt: [Stage 0-QA]
Stop condition: Stop after fixes and Dev handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Fix only the Stage 0 issues identified by QA.

Context
Stage 0 is blocked until fresh QA returns PASS.

Constraints
- Do not implement product functionality.
- Do not expand scope beyond QA findings.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Corrected Stage 0 docs.
- docs/stages/stage-00-fix.md with each QA issue and fix.
- Updated docs/implement.md.
- Updated docs/reports/dev/stage-00-handoff.md.
- docs/stage.md showing next prompt [Stage 0-QA].

Done when
- Every QA issue has a documented resolution or justified blocker.
- No new scope has been added.
- Same-stage QA rerun is explicitly required.

Validation
Run the exact relevant checks from the QA report and document results.

Reporting
Record fixes, changed files, validation results, and re-QA instruction.

Update files
Update only files necessary to resolve Stage 0 QA findings.

Stop rule
Stop after writing the fix handoff. Do not mark PASS. Do not proceed to Stage 1.
