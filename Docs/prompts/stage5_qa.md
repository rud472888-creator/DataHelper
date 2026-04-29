Metadata
Stage ID: 5
Sub-phase: QA
Lane: QA
Required input files: docs/stages/stage-05-plan.md, docs/stages/stage-05-implement.md, docs/reports/dev/stage-05-handoff.md, docs/ui-spec.md, UI/PDF source/tests/artifacts
Required output files: docs/stages/stage-05-qa.md, docs/reports/qa/stage-05-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 6.
Next recommended prompt: [Stage 6-Plan] if PASS, otherwise [Stage 5-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Validate UI/UX refinements independently.

Context
QA must inspect PDF/GUI visual clarity, accessibility/responsiveness, visual verification evidence, and regression status.

Constraints
- Do not modify implementation.
- Only write QA docs.
- Fail if visual improvements break required functionality.
- Fail if no credible visual verification is provided.
- If Playwright is not applicable, verify the rationale and alternative desktop/PDF verification.

Deliverables
- Stage 5 QA report.
- docs/qa.md update.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Overall PASS only if all categories pass.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- run visual artifact generation if available
- run Playwright visual harness if present
- inspect generated PDF artifacts or documented screenshots/checklist
- verify Layout B/A include preview-only disclaimer and required fields

Reporting
Include visual findings, command outputs, artifacts, defects, verdict, and next prompt.

Update files
Update only docs/stages/stage-05-qa.md, docs/reports/qa/stage-05-qa-report.md, docs/qa.md.

Stop rule
Stop after QA. Do not fix issues. Do not start Stage 6 unless PASS.
