Metadata
Stage ID: 3
Sub-phase: QA
Lane: QA
Required input files: docs/stages/stage-03-plan.md, docs/stages/stage-03-implement.md, docs/reports/dev/stage-03-handoff.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md, src/frameproof/core/, src/frameproof/adapters/base.py, tests/unit/
Required output files: docs/stages/stage-03-qa.md, docs/reports/qa/stage-03-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 4A.
Next recommended prompt: [Stage 4A-Plan] if PASS, otherwise [Stage 3-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Validate Stage 3 foundation implementation against the source spec and architecture docs.

Context
QA must independently inspect code, tests, docs, and command results.

Constraints
- Do not modify source code.
- Only write QA docs.
- Fail if capture planner rounding, short clip duplicates, middle_count validation, schema fields, adapter base contract, or timecode fallback rules are missing or incorrect.

Deliverables
- Stage 3 QA report.
- docs/qa.md update.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Any category failure means overall FAIL.

Validation
Run:
- python -m pytest tests/unit
- python -m pytest
- ruff check .
- mypy src
- grep -R "floor" src/frameproof tests || true
- grep -R "duplicate_of" src/frameproof tests
- grep -R "dependency_missing" src/frameproof docs

Reporting
Document evidence, command outputs, defects, and exact next prompt.

Update files
Update only docs/stages/stage-03-qa.md, docs/reports/qa/stage-03-qa-report.md, docs/qa.md.

Stop rule
Stop after QA. Do not fix issues. Do not start Stage 4A.
