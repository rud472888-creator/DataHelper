Metadata
Stage ID: R
Sub-phase: QA
Lane: QA
Required input files: docs/stages/stage-R-plan.md, docs/stages/stage-R-implement.md, docs/reports/dev/stage-R-handoff.md, docs/stage.md, docs/qa.md, docs/implement.md, docs/stages/, docs/reports/
Required output files: docs/stages/stage-R-qa.md, docs/reports/qa/stage-R-qa-report.md, docs/qa.md
Gate condition: Recovery state verified.
Next recommended prompt: The recovered next prompt if PASS, otherwise [Stage R-Fix]
Stop condition: Stop after recovery QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Validate that recovery correctly identifies the project state and does not violate QA gates.

Context
QA must verify that no stage advanced without PASS and that next recommended prompt is safe.

Constraints
- Do not modify source code.
- Only write QA docs.
- Fail if docs/stage.md conflicts with docs/qa.md or latest stage reports.
- Fail if any QA FAIL stage is marked as passed.

Deliverables
- Stage R QA report.
- docs/qa.md updated with recovery QA verdict.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Overall PASS only if durable state is coherent and gate-safe.

Validation
Run:
- cat docs/stage.md
- cat docs/qa.md
- find docs/stages docs/reports -maxdepth 2 -type f | sort
- inspect latest QA reports for PASS/FAIL and compare to docs/stage.md

Reporting
Document recovered state, evidence, defects, verdict, and next prompt.

Update files
Update only docs/stages/stage-R-qa.md, docs/reports/qa/stage-R-qa-report.md, docs/qa.md.

Stop rule
Stop after QA. Do not fix issues or run the recovered next prompt.
