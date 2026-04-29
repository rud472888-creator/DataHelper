Metadata
Stage ID: 4B
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/qa.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md, docs/stages/stage-04A-qa.md
Required output files: docs/stages/stage-04B-plan.md, docs/stage.md
Gate condition: Stage 4A QA must be PASS.
Next recommended prompt: [Stage 4B-Implement]
Stop condition: Stop after Stage 4B plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan RAW adapter integration and dependency detection.

Context
BRAW, R3D, and ARRIRAW require adapter clients using vendor SDK binaries or ARRI Reference Tool CMD via subprocess. The repository must not fake RAW support if dependencies are missing.

Constraints
- Do not implement in this phase.
- Do not bundle proprietary SDKs.
- Do not pretend RAW capture works without configured binaries.
- Include R3D multi-part grouping strategy and JSON contract tests.

Deliverables
- Scope for BRAW, R3D, ARRIRAW adapter clients.
- Dependency detection plan.
- Error/status handling plan.
- Test strategy for dependency_missing, contract fixtures, and optional real samples.
- Acceptance criteria.
- Next prompt.

Done when
docs/stages/stage-04B-plan.md is complete and docs/stage.md points to [Stage 4B-Implement].

Validation
Run:
- cat docs/qa.md
- grep -R "BRAW" docs/architecture.md docs/api-contract.md
- grep -R "R3D" docs/architecture.md docs/api-contract.md
- grep -R "ARRIRAW" docs/architecture.md docs/api-contract.md

Reporting
Document Stage 4A PASS verification, risks, and plan.

Update files
Update docs/stages/stage-04B-plan.md and docs/stage.md.

Stop rule
Stop after planning. Do not implement RAW clients.
