Metadata
Stage ID: 2
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-02-plan.md, docs/stage.md, docs/implement.md, docs/source/frameproof_tech_spec_ko.md or frameproof_tech_spec_ko.md
Required output files: docs/architecture.md, docs/api-contract.md, docs/data-inventory.md, docs/ui-spec.md, docs/release-checklist.md, docs/stages/stage-02-implement.md, docs/reports/dev/stage-02-handoff.md, docs/implement.md
Gate condition: Architecture and milestone docs completed.
Next recommended prompt: [Stage 2-QA]
Stop condition: Stop after architecture handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Write durable architecture and milestone planning documents that future fresh Codex sessions can use without chat context.

Context
The implementation must follow the spec’s adapter layer, subprocess isolation for RAW, normalized schemas, capture planner rules, PDF layout rules, GUI/CLI requirements, failure handling, performance defaults, and security/file safety rules.

Constraints
- Do not implement application code.
- Do not create fake adapters or placeholder implementation.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- docs/architecture.md with module responsibilities and data flow.
- docs/api-contract.md with adapter JSON contract and Python interfaces.
- docs/data-inventory.md with ClipInfo, CapturePoint, ReportItem, manifest columns, candidate keys, nullability, error statuses.
- docs/ui-spec.md with GUI screens, PDF Layout B/A details, visual density, empty/loading/error/success states, design tokens draft.
- docs/release-checklist.md with packaging/dependency/smoke checklist.
- docs/implement.md updated.
- docs/stages/stage-02-implement.md and docs/reports/dev/stage-02-handoff.md.

Done when
Future sessions can implement Stage 3 using only repository docs. The docs explicitly map every major v1 requirement to a module or later stage.

Validation
Run:
- test -f docs/architecture.md
- test -f docs/api-contract.md
- test -f docs/data-inventory.md
- test -f docs/ui-spec.md
- test -f docs/release-checklist.md
- grep -R "BRAW" docs/architecture.md docs/api-contract.md
- grep -R "CapturePoint" docs/data-inventory.md docs/api-contract.md
- grep -R "Layout B" docs/ui-spec.md

Reporting
Update docs/implement.md with documentation decisions, changed files, validation results, known issues, and next prompt.

Update files
Update architecture/planning docs only.

Stop rule
Stop after Dev handoff. Do not implement Stage 3 code. Do not run QA.
