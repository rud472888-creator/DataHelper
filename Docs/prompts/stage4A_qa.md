Metadata
Stage ID: 4A
Sub-phase: QA
Lane: QA
Required input files: docs/stages/stage-04A-plan.md, docs/stages/stage-04A-implement.md, docs/reports/dev/stage-04A-handoff.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md, docs/ui-spec.md, Stage 4A source/tests
Required output files: docs/stages/stage-04A-qa.md, docs/reports/qa/stage-04A-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 4B.
Next recommended prompt: [Stage 4B-Plan] if PASS, otherwise [Stage 4A-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Independently validate the Standard Video CLI Pipeline.

Context
QA must verify actual CLI behavior, generated artifacts, PDF/manifest consistency, and failure handling.

Constraints
- Do not modify source code.
- Only write QA report files.
- Fail if output PDF/CSV/JSON cannot be generated for a standard test video when dependencies are available.
- Fail if missing dependencies are not reported clearly.
- Fail if one file failure aborts the whole batch except for spec-defined fatal conditions.

Deliverables
- Stage 4A QA report.
- docs/qa.md update.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Overall PASS only if all categories pass.

Validation
Run:
- python -m frameproof --help
- python -m pytest
- ruff check .
- mypy src
If FFmpeg is available:
- create a tiny synthetic video fixture
- run CLI with --middle-count 0, 1, 2, and 3 where practical
- verify PDF/CSV/JSON files exist
- verify manifest has requested_ratio and actual capture fields
- verify PNG export is not created by default
If FFmpeg is not available:
- verify dependency_missing behavior and document that full E2E media validation is blocked.

Reporting
Include commands, outputs, generated artifact paths, defects, and exact next prompt.

Update files
Update only docs/stages/stage-04A-qa.md, docs/reports/qa/stage-04A-qa-report.md, docs/qa.md.

Stop rule
Stop after QA. Do not fix issues. Do not start Stage 4B unless PASS.
