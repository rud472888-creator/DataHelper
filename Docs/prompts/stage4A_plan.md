Metadata
Stage ID: 4A
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/qa.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md, docs/ui-spec.md, docs/stages/stage-03-qa.md
Required output files: docs/stages/stage-04A-plan.md, docs/stage.md
Gate condition: Stage 3 QA must be PASS.
Next recommended prompt: [Stage 4A-Implement]
Stop condition: Stop after Stage 4A plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan the Standard Video CLI Pipeline sprint.

Context
This sprint should implement scanner, standard format adapter using FFprobe/FFmpeg, probe/capture services, Layout B PDF renderer, CSV/JSON manifest writer, and CLI E2E flow for standard video formats.

Constraints
- Do not plan RAW native adapter implementation in this sprint.
- Do not implement GUI in this sprint.
- Plan real E2E behavior, not mock-only behavior.
- Include sample/synthetic media strategy.

Deliverables
- Stage 4A module scope.
- Touched files.
- Acceptance criteria.
- Validation commands.
- Failure handling rules.
- Test fixture strategy.
- Next prompt.

Done when
docs/stages/stage-04A-plan.md fully defines the sprint and docs/stage.md points to [Stage 4A-Implement].

Validation
Run:
- cat docs/qa.md
- cat docs/stage.md
- find src tests docs -maxdepth 4 -type f | sort | sed -n '1,220p'

Reporting
Document Stage 3 PASS verification and plan.

Update files
Update docs/stages/stage-04A-plan.md and docs/stage.md.

Stop rule
Stop after planning. Do not implement Stage 4A.
