Metadata
Stage ID: 6
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-06-plan.md, docs/stage.md, docs/implement.md, docs/architecture.md, docs/data-inventory.md, docs/release-checklist.md
Required output files: expanded tests, hardening fixes, security/performance docs or scripts, docs/stages/stage-06-implement.md, docs/reports/dev/stage-06-handoff.md, docs/implement.md
Gate condition: Hardening scope implemented and validated.
Next recommended prompt: [Stage 6-QA]
Stop condition: Stop after implementation handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Implement hardening improvements and expanded tests.

Context
Stage 6 should improve reliability and acceptance readiness without adding new product features.

Constraints
- Do not add unplanned features.
- Do not relax tests to pass.
- Do not remove required behavior.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Expanded tests for middle_count 0/1/2/3, short clips, invalid input, dependency missing, output write failure, non-ASCII paths, filename sanitize, manifest parity, batch continuation.
- Security/file safety improvements for read-only source handling, path traversal prevention, output path validation.
- Error handling cleanup for structured statuses.
- Performance/concurrency defaults documented and enforced where applicable.
- Accessibility/responsiveness checks or documented constraints.
- Updated docs/implement.md and handoff.

Done when
Full regression suite passes or blockers are clearly documented, and hardening acceptance criteria are met.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- CLI smoke tests documented in Stage 6 plan
- GUI smoke/manual checks if environment permits

Reporting
Document changed files, hardening decisions, validation outputs, remaining known issues, and next prompt.

Update files
Update source/tests/docs relevant to Stage 6 hardening.

Stop rule
Stop after Dev handoff. Do not run QA. Do not start Stage 7.
