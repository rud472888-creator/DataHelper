Metadata
Stage ID: R
Sub-phase: Plan
Lane: Dev
Required input files: docs/stage.md, docs/plan.md, docs/implement.md, docs/documentation.md, docs/qa.md, docs/stages/, docs/reports/
Required output files: docs/stages/stage-R-plan.md, docs/stage.md
Gate condition: Recovery plan identifies exact current stage/sub-phase and gate state.
Next recommended prompt: Determined by recovery plan.
Stop condition: Stop after recovery plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Recover the current project state from durable repository files only.

Context
Use Stage R when context is lost, a previous session was interrupted, or docs/stage.md is inconsistent.

Constraints
- Do not implement or fix product code.
- Do not infer from chat history.
- Do not advance past any stage without QA PASS.
- Identify the safest next prompt.

Deliverables
- Current stage/sub-phase.
- Latest PASS/FAIL QA verdicts by stage.
- Missing docs or inconsistent state.
- Recommended next prompt.
- Recovery risks.

Done when
docs/stages/stage-R-plan.md and docs/stage.md clearly state the current gate and next prompt.

Validation
Run:
- find docs -maxdepth 4 -type f | sort
- cat docs/stage.md
- cat docs/qa.md
- ls docs/stages
- ls docs/reports/dev docs/reports/qa || true

Reporting
Document evidence for the recovered state.

Update files
Update docs/stages/stage-R-plan.md and docs/stage.md only.

Stop rule
Stop after recovery planning. Do not implement, QA, or fix.
