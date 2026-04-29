Metadata
Stage ID: 2
Sub-phase: QA
Lane: QA
Required input files: docs/stage.md, docs/qa.md, docs/stages/stage-02-plan.md, docs/stages/stage-02-implement.md, docs/reports/dev/stage-02-handoff.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md, docs/ui-spec.md, docs/release-checklist.md, source spec
Required output files: docs/stages/stage-02-qa.md, docs/reports/qa/stage-02-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 3.
Next recommended prompt: [Stage 3-Plan] if PASS, otherwise [Stage 2-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Validate that architecture and milestone docs are complete, coherent, and faithful to the source spec.

Context
This is a documentation QA gate. No product code should be required.

Constraints
- Do not fix docs.
- Only write QA outputs.
- Fail if required v1 features are missing from architecture, adapter contracts are vague, RAW dependency handling is fake/unsafe, or QA gates are not clear.

Deliverables
- Stage 2 QA report with PASS/FAIL.
- docs/qa.md updated.

Done when
The report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Overall verdict is PASS only if all categories pass.

Validation
Run:
- grep -R "subprocess" docs/architecture.md docs/api-contract.md
- grep -R "Layout A" docs/ui-spec.md
- grep -R "Layout B" docs/ui-spec.md
- grep -R "drop-frame" docs/architecture.md docs/data-inventory.md
- grep -R "dependency_missing" docs/api-contract.md docs/data-inventory.md
- grep -R "Stage 3" docs/stage.md docs/plan.md docs/architecture.md

Reporting
Cite exact missing/mismatched docs sections and provide fix instructions if FAIL.

Update files
Update only docs/stages/stage-02-qa.md, docs/reports/qa/stage-02-qa-report.md, docs/qa.md.

Stop rule
Stop after QA. Do not start Stage 3.
