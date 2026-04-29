Metadata
Stage ID: 1
Sub-phase: QA
Lane: QA
Required input files: AGENTS.md, docs/stage.md, docs/stages/stage-01-plan.md, docs/stages/stage-01-implement.md, docs/reports/dev/stage-01-handoff.md, pyproject.toml, src/frameproof/, tests/
Required output files: docs/stages/stage-01-qa.md, docs/reports/qa/stage-01-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 2.
Next recommended prompt: [Stage 2-Plan] if PASS, otherwise [Stage 1-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Independently validate the Greenfield Bootstrap.

Context
Check actual repository state, not just Dev claims.

Constraints
- Do not modify source code.
- Only write QA files.
- Fail if CLI help is broken, package is not importable, tests/lint/typecheck fail without documented acceptable blocker, docs/implement.md lacks mandatory handoff fields, or unimplemented product functionality is misrepresented as complete.

Deliverables
- QA report with PASS/FAIL.
- docs/qa.md updated.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Any category failure means overall FAIL.

Validation
Run:
- python -m frameproof --help
- python -m pytest
- ruff check .
- mypy src
- find src tests docs -maxdepth 4 -type f | sort

Reporting
Include command outputs, evidence, defects, and exact next recommended prompt.

Update files
Update only docs/stages/stage-01-qa.md, docs/reports/qa/stage-01-qa-report.md, and docs/qa.md.

Stop rule
Stop after QA. Do not fix issues. Do not proceed to Stage 2 unless PASS is documented.
