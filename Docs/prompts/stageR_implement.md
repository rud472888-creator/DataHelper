Metadata
Stage ID: R
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-R-plan.md, docs/stage.md, docs/qa.md, docs/implement.md, docs/reports/
Required output files: docs/stages/stage-R-implement.md, docs/reports/dev/stage-R-handoff.md, corrected durable docs if needed
Gate condition: Durable memory inconsistencies repaired; no product code changed.
Next recommended prompt: Determined by recovery state, usually the blocked stage QA/Fix/Plan prompt.
Stop condition: Stop after recovery handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Repair durable-memory inconsistencies identified in Stage R Plan.

Context
This is documentation recovery only. It is not a feature implementation phase.

Constraints
- Do not modify product source unless the recovery plan explicitly identifies docs-only generated metadata stored in source, which should be rare.
- Do not mark any stage PASS unless a QA report says PASS.
- Do not skip failed QA.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Corrected docs/stage.md, docs/implement.md, docs/qa.md, or stage docs if inconsistent.
- docs/stages/stage-R-implement.md.
- docs/reports/dev/stage-R-handoff.md.

Done when
Durable docs consistently identify current stage/sub-phase, latest QA verdict, and next recommended prompt.

Validation
Run:
- cat docs/stage.md
- cat docs/qa.md
- find docs/stages docs/reports -maxdepth 2 -type f | sort

Reporting
Document each inconsistency and correction.

Update files
Update only durable documentation required for recovery.

Stop rule
Stop after recovery handoff. Do not proceed to the recommended next prompt.
