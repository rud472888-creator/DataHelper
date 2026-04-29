Metadata
Stage ID: 4D
Sub-phase: QA
Lane: QA
Required input files: docs/stages/stage-04D-plan.md, docs/stages/stage-04D-implement.md, docs/reports/dev/stage-04D-handoff.md, docs/ui-spec.md, GUI source/tests
Required output files: docs/stages/stage-04D-qa.md, docs/reports/qa/stage-04D-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 5.
Next recommended prompt: [Stage 5-Plan] if PASS, otherwise [Stage 4D-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Validate GUI, settings persistence, dependency screen, progress UX, and pipeline reuse.

Context
QA must check that the GUI is not just a visual shell and does not bypass the CLI/core pipeline.

Constraints
- Do not modify source code.
- Only write QA docs.
- Fail if GUI lacks required controls, cannot persist settings, hides dependency_missing states, or implements a parallel pipeline.

Deliverables
- Stage 4D QA report.
- docs/qa.md update.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Overall PASS only if all categories pass.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- inspect GUI modules for core pipeline reuse
- run GUI smoke/manual checklist if environment allows
- verify settings persistence files/logic
- verify dependency screen behavior through tests or documented inspection

Reporting
Include command outputs, GUI observations, screenshots if available, defects, verdict, and next prompt.

Update files
Update only docs/stages/stage-04D-qa.md, docs/reports/qa/stage-04D-qa-report.md, docs/qa.md.

Stop rule
Stop after QA. Do not fix issues. Do not start Stage 5 unless PASS.
