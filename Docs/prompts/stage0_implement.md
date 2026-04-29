Metadata
Stage ID: 0
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-00-plan.md, frameproof_tech_spec_ko.md or docs/source/frameproof_tech_spec_ko.md
Required output files: AGENTS.md, docs/stage.md, docs/plan.md, docs/implement.md, docs/qa.md, docs/documentation.md, docs/prompt.md, docs/stages/stage-00-implement.md, docs/reports/dev/stage-00-handoff.md
Gate condition: Durable memory skeleton created; no product functionality implemented.
Next recommended prompt: [Stage 0-QA]
Stop condition: Stop after Stage 0 documentation implementation and Dev handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Create the durable repository memory and orchestration documentation needed to run the rest of the project in isolated Codex sessions.

Context
Stage 0 freezes the target and working memory. The project is assumed Greenfield unless existing repository evidence proves otherwise.

Constraints
- Do not implement product features.
- Do not create fake app code or mock pipelines.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.
- Copy or reference the source spec into docs/source only if it exists in the repo.
- Preserve source-of-truth language and avoid silently changing requirements.

Deliverables
- AGENTS.md with project execution rules, lane isolation, no-resume rule, no-placeholder rule, and QA gate rules.
- docs/stage.md as the orchestrator status board.
- docs/plan.md with milestone overview.
- docs/implement.md initialized with mandatory handoff fields.
- docs/qa.md initialized as QA source of truth.
- docs/documentation.md initialized for user/developer docs tracking.
- docs/prompt.md initialized for prompt inventory.
- docs/stages/stage-00-implement.md with implementation details.
- docs/reports/dev/stage-00-handoff.md with complete Dev handoff.

Done when
- Required docs exist.
- docs/stage.md clearly says Stage 0 Implement complete and next prompt is [Stage 0-QA].
- docs/implement.md includes: Current stage/sub-phase, lane, completed functionality, changed files and why, implementation decisions, data/API/state ownership changes, UI behavior notes, validation commands/results, known issues/blockers, QA status by stage, latest QA verdict/report, latest Dev handoff path, next recommended prompt, assumptions, manual verification steps, future fresh Dev session notes.

Validation
Run:
- find docs -maxdepth 3 -type f | sort
- test -f AGENTS.md
- test -f docs/stage.md
- test -f docs/implement.md
- test -f docs/qa.md

Reporting
Record changed files, reasons, validation results, blockers, and next prompt in docs/stages/stage-00-implement.md and docs/reports/dev/stage-00-handoff.md.

Update files
Update AGENTS.md and docs/*.md only. Do not add product implementation code.

Stop rule
Stop after writing the Dev handoff. Do not run QA or proceed to Stage 1.
