Metadata
Stage ID: 1
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/plan.md, docs/implement.md, docs/qa.md, docs/source/frameproof_tech_spec_ko.md or frameproof_tech_spec_ko.md
Required output files: docs/stages/stage-01-plan.md, docs/stage.md
Gate condition: Stage 0 QA must be PASS.
Next recommended prompt: [Stage 1-Implement]
Stop condition: Stop after Stage 1 plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan the Greenfield Bootstrap for the Frame Proof repository.

Context
No existing codebase was provided. Stage 1 should create a minimal but real Python project shell with CLI help, test/lint/typecheck wiring, package layout, and docs skeleton.

Constraints
- Do not implement product pipeline features in planning.
- Do not start coding.
- Do not proceed if Stage 0 QA is not PASS in docs/qa.md or docs/stage.md.
- Reuse existing repository patterns if any are discovered, but otherwise assume Greenfield.

Deliverables
- Stage 1 scope and non-scope.
- Proposed file/module structure.
- Dependency choices and rationale.
- Validation command plan.
- Acceptance criteria.
- Risks and assumptions.
- Exact next prompt.

Done when
docs/stages/stage-01-plan.md documents bootstrap scope, touched files, validation plan, and next prompt.

Validation
Run:
- cat docs/stage.md
- cat docs/qa.md
- find . -maxdepth 3 -type f | sort | sed -n '1,160p'

Reporting
Record whether Stage 0 PASS is verified. If not, block Stage 1.

Update files
Update docs/stages/stage-01-plan.md and docs/stage.md only.

Stop rule
Stop after planning. Do not implement bootstrap.
