Metadata
Stage ID: 7
Sub-phase: QA
Lane: QA
Required input files: README.md, docs/setup-guide.md, docs/dependency-guide.md, docs/architecture-note.md, docs/release-checklist.md, docs/reports/final/final-report.md, docs/stages/stage-07-plan.md, docs/stages/stage-07-implement.md, docs/reports/dev/stage-07-handoff.md, source/tests
Required output files: docs/stages/stage-07-qa.md, docs/reports/qa/stage-07-qa-report.md, docs/qa.md, docs/stage.md
Gate condition: Final QA verdict PASS required for release-ready status.
Next recommended prompt: None if PASS, otherwise [Stage 7-Fix]
Stop condition: Stop after final QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Final release readiness QA.

Context
QA must verify docs, smoke commands, final report, known issues, dependency caveats, and regression suite.

Constraints
- Do not modify implementation.
- Only write QA/status docs.
- Fail if README/setup instructions are not reproducible, dependency limitations are hidden, smoke commands fail without documented blocker, or final report overclaims completion.

Deliverables
- Stage 7 QA report.
- docs/qa.md update.
- docs/stage.md updated to release-ready only if PASS.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Overall PASS only if all categories pass.

Validation
Run:
- python -m frameproof --help
- python -m pytest
- ruff check .
- mypy src
- run or inspect each README smoke command
- verify docs referenced by README exist
- verify docs/reports/final/final-report.md lists known issues and backlog honestly

Reporting
If PASS, set docs/stage.md to project_status=release-ready. If FAIL, block release and list exact fixes.

Update files
Update only docs/stages/stage-07-qa.md, docs/reports/qa/stage-07-qa-report.md, docs/qa.md, and docs/stage.md.

Stop rule
Stop after QA. Do not fix issues.
