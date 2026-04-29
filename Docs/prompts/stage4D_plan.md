Metadata
Stage ID: 4D
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/qa.md, docs/architecture.md, docs/ui-spec.md, docs/stages/stage-04C-qa.md
Required output files: docs/stages/stage-04D-plan.md, docs/stage.md
Gate condition: Stage 4C QA must be PASS.
Next recommended prompt: [Stage 4D-Implement]
Stop condition: Stop after Stage 4D plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan PySide6 GUI, settings persistence, dependency screen, progress table, and start/cancel flow.

Context
The GUI must reuse the existing CLI/core pipeline and must not create a parallel architecture.

Constraints
- Do not implement in this phase.
- Do not redesign core pipeline.
- Include empty/loading/error/success states and dependency_missing UX.
- Include test and manual verification strategy.

Deliverables
- GUI scope.
- Module/file plan.
- State ownership and threading/process strategy.
- Settings persistence plan.
- Acceptance criteria.
- Validation plan.
- Next prompt.

Done when
docs/stages/stage-04D-plan.md is complete and docs/stage.md points to [Stage 4D-Implement].

Validation
Run:
- cat docs/qa.md
- grep -R "PySide6" docs/ui-spec.md docs/architecture.md
- grep -R "Progress" docs/ui-spec.md

Reporting
Record Stage 4C PASS verification and plan.

Update files
Update docs/stages/stage-04D-plan.md and docs/stage.md.

Stop rule
Stop after planning. Do not implement GUI.
