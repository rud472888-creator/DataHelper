Metadata
Stage ID: 7
Sub-phase: Plan
Lane: Dev
Required input files: AGENTS.md, docs/stage.md, docs/qa.md, docs/release-checklist.md, docs/implement.md, docs/stages/stage-06-qa.md
Required output files: docs/stages/stage-07-plan.md, docs/stage.md
Gate condition: Stage 6 QA must be PASS.
Next recommended prompt: [Stage 7-Implement]
Stop condition: Stop after Stage 7 plan.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Plan release wrap-up documentation and final handoff.

Context
Stage 7 should make the repository usable by a fresh developer/user: README, setup guide, dependency guide, config example, architecture note, deployment checklist, smoke tests, known issues, backlog, final report.

Constraints
- Do not add new product features.
- Do not hide unresolved proprietary SDK limitations.
- Do not mark release-ready unless smoke commands and docs are accurate.

Deliverables
- Release docs scope.
- Setup/smoke validation plan.
- Known issues/backlog plan.
- Final report plan.
- Next prompt.

Done when
docs/stages/stage-07-plan.md is complete and docs/stage.md points to [Stage 7-Implement].

Validation
Run:
- cat docs/qa.md
- cat docs/release-checklist.md
- find . -maxdepth 3 -type f | sort | sed -n '1,260p'

Reporting
Record Stage 6 PASS verification and release wrap-up plan.

Update files
Update docs/stages/stage-07-plan.md and docs/stage.md.

Stop rule
Stop after planning. Do not implement release docs.
