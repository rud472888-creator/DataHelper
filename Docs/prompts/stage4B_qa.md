Metadata
Stage ID: 4B
Sub-phase: QA
Lane: QA
Required input files: docs/stages/stage-04B-plan.md, docs/stages/stage-04B-implement.md, docs/reports/dev/stage-04B-handoff.md, docs/architecture.md, docs/api-contract.md, RAW adapter source/tests
Required output files: docs/stages/stage-04B-qa.md, docs/reports/qa/stage-04B-qa-report.md, docs/qa.md
Gate condition: QA verdict PASS required before Stage 4C.
Next recommended prompt: [Stage 4C-Plan] if PASS, otherwise [Stage 4B-Fix]
Stop condition: Stop after QA report.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Validate RAW adapter clients, dependency detection, and error behavior.

Context
QA must ensure RAW support is honest: real subprocess contracts when configured, dependency_missing when absent, no fake production success.

Constraints
- Do not modify code.
- Only write QA docs.
- Fail if adapter clients return success without an executable dependency.
- Fail if malformed JSON, subprocess crash, or missing binary is not converted to structured errors.
- Fail if RAW client design imports vendor SDKs into the Python process.

Deliverables
- Stage 4B QA report.
- docs/qa.md update.

Done when
Report evaluates Spec fidelity/product depth, Functionality, Visual design/UX clarity, Code quality/maintainability, Accessibility/responsiveness, and Validation completeness. Overall PASS only if all categories pass.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- grep -R "subprocess" src/frameproof/adapters docs/api-contract.md
- grep -R "dependency_missing" src/frameproof tests docs
- inspect adapter clients for direct vendor SDK imports
If real RAW tools are present, run dependency check smoke and optional sample clip smoke. If not present, verify graceful dependency_missing behavior.

Reporting
Include evidence, command outputs, dependency environment, defects, and next prompt.

Update files
Update only docs/stages/stage-04B-qa.md, docs/reports/qa/stage-04B-qa-report.md, docs/qa.md.

Stop rule
Stop after QA. Do not fix issues. Do not start Stage 4C unless PASS.
