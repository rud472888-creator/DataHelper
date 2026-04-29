Metadata
Stage ID: 0
Sub-phase: QA
Lane: QA
Required input files: AGENTS.md, docs/stage.md, docs/plan.md, docs/implement.md, docs/qa.md, docs/documentation.md, docs/prompt.md, docs/stages/stage-00-plan.md, docs/stages/stage-00-implement.md, docs/reports/dev/stage-00-handoff.md
Required output files: docs/stages/stage-00-qa.md, docs/reports/qa/stage-00-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 1.
Next recommended prompt: [Stage 1-Plan] if PASS, otherwise [Stage 0-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Independently verify that Stage 0 durable memory and orchestration docs are complete and faithful to the source spec.

Context
QA is isolated from Dev. Do not trust the Dev handoff without checking actual files.

Constraints
- Do not implement or fix anything.
- Only write QA report files and docs/qa.md.
- Fail the stage if source-of-truth is missing, durable docs are incomplete, next prompt is unclear, or QA gate rules are absent.
- Do not proceed to Stage 1 without PASS.

Deliverables
- docs/stages/stage-00-qa.md
- docs/reports/qa/stage-00-qa-report.md
- docs/qa.md updated with Stage 0 verdict

Done when
- QA report includes PASS or FAIL.
- Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness.
- Any FAIL includes exact fix items and states that Stage 1 is blocked.

Validation
Run:
- find docs -maxdepth 3 -type f | sort
- grep -R "Stage 0" docs/stage.md docs/implement.md docs/qa.md
- test -f AGENTS.md
- test -f docs/reports/dev/stage-00-handoff.md

Reporting
Write an evidence-based QA report. Include checked files, command results, issues, verdict, and next recommended prompt.

Update files
Update only docs/stages/stage-00-qa.md, docs/reports/qa/stage-00-qa-report.md, and docs/qa.md.

Stop rule
Stop after QA. Do not modify implementation files. Do not start Stage 1.
