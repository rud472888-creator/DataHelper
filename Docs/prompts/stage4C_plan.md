Metadata
Stage ID: 4C
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/qa.md, docs/architecture.md, docs/data-inventory.md, docs/ui-spec.md, docs/stages/stage-04B-qa.md
Required output files: docs/stages/stage-04C-plan.md, docs/stage.md
Gate condition: Stage 4B QA must be PASS.
Next recommended prompt: [Stage 4C-Implement]
Stop condition: Stop after Stage 4C plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan Layout A, PNG still export, filename sanitize, failed/partial clips sections, and PDF/manifest parity improvements.

Context
Layout B exists from Stage 4A. Stage 4C adds detailed per-clip reporting and export behavior.

Constraints
- Do not implement GUI.
- Do not change RAW adapter scope except to consume existing ReportItem data.
- Ensure PNG export is OFF by default.

Deliverables
- Renderer/export scope.
- Acceptance criteria for Layout A, export_stills, stills_dir, sanitize, collision suffix, failed section.
- Tests and validation plan.
- Next prompt.

Done when
docs/stages/stage-04C-plan.md is complete and docs/stage.md points to [Stage 4C-Implement].

Validation
Run:
- cat docs/qa.md
- grep -R "Layout A" docs/ui-spec.md
- grep -R "Export still" docs/ui-spec.md docs/data-inventory.md

Reporting
Document Stage 4B PASS verification and plan.

Update files
Update docs/stages/stage-04C-plan.md and docs/stage.md.

Stop rule
Stop after planning. Do not implement Stage 4C.
