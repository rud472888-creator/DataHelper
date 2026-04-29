Metadata
Stage ID: 5
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/qa.md, docs/ui-spec.md, docs/stages/stage-04D-qa.md
Required output files: docs/stages/stage-05-plan.md, docs/stage.md
Gate condition: Stage 4D QA must be PASS.
Next recommended prompt: [Stage 5-Implement]
Stop condition: Stop after Stage 5 plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan UI/UX refinement for PDF layouts and GUI.

Context
Stage 5 focuses on visual clarity, user feedback, accessibility/responsiveness, report density, and verification artifacts. PySide6 is desktop UI, so Playwright applies only to web/HTML/PDF visual harness if present or created; PySide6 itself should use screenshot/manual/pytest-qt checks.

Constraints
- Do not add new product features.
- Do not change core behavior except to improve UX clarity.
- Include Playwright verification for any HTML/PDF visual harness if feasible.
- Include manual verification checklist for PySide6 desktop UX.

Deliverables
- Refinement scope.
- Visual acceptance criteria.
- Accessibility/responsiveness checklist.
- Playwright or alternative visual verification plan.
- Next prompt.

Done when
docs/stages/stage-05-plan.md is complete and docs/stage.md points to [Stage 5-Implement].

Validation
Run:
- cat docs/qa.md
- cat docs/ui-spec.md
- find docs src tests -maxdepth 4 -type f | sort | sed -n '1,240p'

Reporting
Document Stage 4D PASS verification and plan.

Update files
Update docs/stages/stage-05-plan.md and docs/stage.md.

Stop rule
Stop after planning. Do not implement refinements.
