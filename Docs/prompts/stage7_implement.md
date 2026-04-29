Metadata
Stage ID: 7
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-07-plan.md, docs/stage.md, docs/implement.md, docs/architecture.md, docs/release-checklist.md, docs/qa.md
Required output files: README.md, config examples, docs/setup-guide.md, docs/dependency-guide.md, docs/architecture-note.md, docs/release-checklist.md, docs/reports/final/final-report.md, docs/stages/stage-07-implement.md, docs/reports/dev/stage-07-handoff.md, docs/implement.md
Gate condition: Release wrap-up docs and smoke commands completed.
Next recommended prompt: [Stage 7-QA]
Stop condition: Stop after implementation handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Complete release wrap-up documentation, examples, smoke commands, known issues, backlog, and final handoff.

Context
The project needs setup instructions for CLI/GUI, external dependencies, RAW adapter paths, FFmpeg/FFprobe/MediaInfo, proprietary SDK limitations, PDF/manifest generation, and troubleshooting.

Constraints
- Do not add product features.
- Do not claim bundled RAW SDK support unless actually implemented and legally available.
- Do not mark unresolved blockers as solved.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- README.md with product overview, install, CLI examples, GUI launch, output examples, dependency notes.
- docs/setup-guide.md.
- docs/dependency-guide.md for FFmpeg/FFprobe/MediaInfo/BRAW/R3D/ARRI ART CMD paths.
- docs/architecture-note.md.
- docs/release-checklist.md finalized.
- config example file for project settings.
- docs/reports/final/final-report.md with implemented scope, validation summary, known issues, backlog, release readiness.
- docs/implement.md and Stage 7 handoff.

Done when
A fresh user/developer can install, run help, understand dependencies, run smoke tests, and understand known limitations from repository docs.

Validation
Run:
- python -m frameproof --help
- python -m pytest
- ruff check .
- mypy src
- execute documented smoke command if dependencies allow
- verify all docs referenced in README exist

Reporting
Document docs changed, validation outputs, final known issues, release readiness state, and next prompt.

Update files
Update release docs, examples, final report, docs/implement.md, and handoff.

Stop rule
Stop after Dev handoff. Do not run QA. Do not mark final PASS.
