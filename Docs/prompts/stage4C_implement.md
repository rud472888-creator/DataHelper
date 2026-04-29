Metadata
Stage ID: 4C
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-04C-plan.md, docs/stage.md, docs/implement.md, docs/architecture.md, docs/data-inventory.md, docs/ui-spec.md
Required output files: Layout A renderer changes, still exporter, filename sanitizer, manifest/PDF parity tests, docs/stages/stage-04C-implement.md, docs/reports/dev/stage-04C-handoff.md, docs/implement.md
Gate condition: Layout A and PNG export behavior implemented and tested.
Next recommended prompt: [Stage 4C-QA]
Stop condition: Stop after implementation handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Implement detailed Layout A, PNG still export, filename sanitize, failed/partial clip sections, and PDF/manifest capture point parity.

Context
The spec requires Layout B as default, Layout A when detailed option is selected, PNG export only when enabled, and failed/partial clips listed in PDF and manifests.

Constraints
- Do not implement GUI.
- Do not change core adapter behavior except as required for export paths and report fields.
- PNG export must remain OFF by default.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Layout A PDF renderer: clip title, source path, metadata table, 2-5 capture frames, per-frame details, warnings/errors.
- CLI support for `--layout detail`, `--export-stills`, `--stills-dir`.
- Still exporter with sanitized paths, drop-frame semicolon handling, collision suffix, long-name hash suffix.
- Failed/partial clips PDF section.
- CSV/JSON manifest fields for image_path, requested/actual frame/time/timecode, status, warnings, errors.
- Tests for Layout A, PNG export off/on, sanitize/collision, failed section, manifest parity.
- Updated docs/implement.md and handoff.

Done when
CLI can generate Layout A and optional PNG stills, default behavior does not create stills, and tests validate parity.

Validation
Run:
- python -m frameproof --help
- python -m pytest
- ruff check .
- mypy src
If FFmpeg is available, run smoke tests for:
- `--layout contact_sheet`
- `--layout detail`
- `--export-stills`
- middle_count 0 and 3

Reporting
Document changed files, behavior changes, validation outputs, generated artifacts, and next prompt.

Update files
Update Stage 4C source/tests/docs.

Stop rule
Stop after Dev handoff. Do not run QA. Do not start Stage 4D.
