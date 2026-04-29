Metadata
Stage ID: 3
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/qa.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md, docs/stages/stage-02-qa.md
Required output files: docs/stages/stage-03-plan.md, docs/stage.md
Gate condition: Stage 2 QA must be PASS.
Next recommended prompt: [Stage 3-Implement]
Stop condition: Stop after Stage 3 plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan the Foundation Build: schemas, settings, capture planner, timecode helpers, adapter base interfaces, status/error model, and unit tests.

Context
Foundation code must enable later standard video, RAW adapters, PDF rendering, manifests, and GUI without parallel architecture.

Constraints
- Do not implement in this phase.
- Do not proceed if Stage 2 QA is not PASS.
- Keep scope limited to reusable foundation logic, not end-to-end media processing.

Deliverables
- Module/file plan.
- Acceptance criteria.
- Unit test plan.
- Edge cases for short clips, frame_count vs duration, rounding, VFR, drop-frame flags, dependency_missing statuses.
- Next prompt.

Done when
docs/stages/stage-03-plan.md is complete and docs/stage.md points to [Stage 3-Implement].

Validation
Run:
- cat docs/qa.md
- cat docs/stage.md
- find src docs tests -maxdepth 4 -type f | sort | sed -n '1,200p'

Reporting
Record scope, touched files, risk, acceptance criteria, validation commands.

Update files
Update docs/stages/stage-03-plan.md and docs/stage.md.

Stop rule
Stop after planning. Do not implement foundation code.
