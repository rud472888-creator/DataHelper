Metadata
Stage ID: 4C
Sub-phase: QA
Lane: QA
Required input files: docs/stages/stage-04C-plan.md, docs/stages/stage-04C-implement.md, docs/reports/dev/stage-04C-handoff.md, docs/ui-spec.md, docs/data-inventory.md, Stage 4C source/tests
Required output files: docs/stages/stage-04C-qa.md, docs/reports/qa/stage-04C-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 4D.
Next recommended prompt: [Stage 4D-Plan] if PASS, otherwise [Stage 4C-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Validate Layout A, PNG export, failed sections, filename sanitize, and PDF/manifest parity.

Context
QA must check actual behavior and artifacts, not just tests.

Constraints
- Do not modify implementation.
- Only write QA docs.
- Fail if PNG stills are created when export is OFF.
- Fail if Layout A lacks required per-frame details.
- Fail if failed/partial clips are absent from PDF/manifest behavior.

Deliverables
- Stage 4C QA report.
- docs/qa.md update.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Overall PASS only if all categories pass.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
If FFmpeg is available:
- create/run standard video smoke for contact_sheet and detail
- run with export_stills false and verify no stills directory is created
- run with export_stills true and verify filenames are sanitized
- inspect CSV/JSON for requested/actual capture fields
- verify failed/partial section behavior with an intentionally invalid input

Reporting
Include command outputs, artifact paths, visual/manifest findings, defects, verdict, and next prompt.

Update files
Update only docs/stages/stage-04C-qa.md, docs/reports/qa/stage-04C-qa-report.md, docs/qa.md.

Stop rule
Stop after QA. Do not fix issues. Do not start Stage 4D unless PASS.
