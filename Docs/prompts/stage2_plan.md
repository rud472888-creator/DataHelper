Metadata
Stage ID: 2
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/qa.md, docs/plan.md, docs/implement.md, docs/source/frameproof_tech_spec_ko.md or frameproof_tech_spec_ko.md
Required output files: docs/stages/stage-02-plan.md, docs/stage.md
Gate condition: Stage 1 QA must be PASS.
Next recommended prompt: [Stage 2-Implement]
Stop condition: Stop after Stage 2 plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan architecture and milestone documentation before building core functionality.

Context
The spec requires adapter-based architecture, common schema, capture planning, timecode rules, PDF layouts, GUI/CLI, manifests, error handling, and RAW subprocess isolation.

Constraints
- Do not implement architecture in code yet.
- Do not proceed if Stage 1 QA is not PASS.
- Do not invent unsupported product scope.
- Preserve source spec decisions.

Deliverables
Plan documentation for:
- Architecture doc.
- API/adapter contract.
- Data inventory and schemas.
- UI spec and design tokens.
- Release checklist.
- Test strategy.
- Milestone breakdown for Stage 3 through Stage 7.

Done when
docs/stages/stage-02-plan.md lists scope, touched docs, risks, assumptions, acceptance criteria, validation plan, and next prompt.

Validation
Run:
- cat docs/stage.md
- cat docs/qa.md
- find docs -maxdepth 3 -type f | sort

Reporting
Document Stage 1 PASS verification and Stage 2 plan.

Update files
Update docs/stages/stage-02-plan.md and docs/stage.md.

Stop rule
Stop after planning. Do not write architecture docs yet.
