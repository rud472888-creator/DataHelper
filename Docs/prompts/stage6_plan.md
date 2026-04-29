Metadata
Stage ID: 6
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/qa.md, docs/architecture.md, docs/data-inventory.md, docs/release-checklist.md, docs/stages/stage-05-qa.md
Required output files: docs/stages/stage-06-plan.md, docs/stage.md
Gate condition: Stage 5 QA must be PASS.
Next recommended prompt: [Stage 6-Implement]
Stop condition: Stop after Stage 6 plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan hardening for tests, edge cases, security, performance, accessibility, error handling, and cleanup.

Context
The project now has core, standard pipeline, RAW clients, Layout A/B, PNG export, and GUI. Stage 6 strengthens reliability.

Constraints
- Do not implement in this phase.
- Do not add new product features.
- Prioritize spec acceptance criteria and failure modes.
- Include damaged media, short clips, non-ASCII paths, long clips, dependency missing, output write failure, and batch continuation.

Deliverables
- Hardening scope.
- Test matrix expansion.
- Security/file safety checklist.
- Performance smoke plan.
- Cleanup plan.
- Acceptance criteria.
- Next prompt.

Done when
docs/stages/stage-06-plan.md is complete and docs/stage.md points to [Stage 6-Implement].

Validation
Run:
- cat docs/qa.md
- cat docs/release-checklist.md
- find tests src docs -maxdepth 4 -type f | sort | sed -n '1,260p'

Reporting
Record Stage 5 PASS verification and hardening plan.

Update files
Update docs/stages/stage-06-plan.md and docs/stage.md.

Stop rule
Stop after planning. Do not implement hardening.
