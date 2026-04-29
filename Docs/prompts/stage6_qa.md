Metadata
Stage ID: 6
Sub-phase: QA
Lane: QA
Required input files: docs/stages/stage-06-plan.md, docs/stages/stage-06-implement.md, docs/reports/dev/stage-06-handoff.md, docs/release-checklist.md, source/tests
Required output files: docs/stages/stage-06-qa.md, docs/reports/qa/stage-06-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 7.
Next recommended prompt: [Stage 7-Plan] if PASS, otherwise [Stage 6-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Validate hardening, regression stability, security/file safety, edge cases, and acceptance readiness.

Context
QA should be strict. Any missing required acceptance behavior is FAIL.

Constraints
- Do not modify source code.
- Only write QA docs.
- Fail if tests are superficial, errors are unstructured, source files can be modified, path traversal is possible, batch failure behavior violates spec, or acceptance criteria are not covered.

Deliverables
- Stage 6 QA report.
- docs/qa.md update.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Overall PASS only if all categories pass.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- documented CLI smoke tests
- inspect path sanitization and output validation code
- verify tests cover short clips, dependency missing, manifest parity, export on/off, failed files, and middle_count values

Reporting
Include command outputs, coverage observations, defects, verdict, and next prompt.

Update files
Update only docs/stages/stage-06-qa.md, docs/reports/qa/stage-06-qa-report.md, docs/qa.md.

Stop rule
Stop after QA. Do not fix issues. Do not start Stage 7 unless PASS.
