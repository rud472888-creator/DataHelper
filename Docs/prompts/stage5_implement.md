Metadata
Stage ID: 5
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-05-plan.md, docs/stage.md, docs/implement.md, docs/ui-spec.md
Required output files: UI/PDF refinement source changes, visual verification artifacts/tests, docs/stages/stage-05-implement.md, docs/reports/dev/stage-05-handoff.md, docs/implement.md, updated docs/ui-spec.md as needed
Gate condition: UI/UX refinements implemented without feature scope expansion.
Next recommended prompt: [Stage 5-QA]
Stop condition: Stop after implementation handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Refine PDF and GUI UX for clarity, accessibility, density, error/warning communication, and verification artifacts.

Context
The spec requires Layout B contact sheet readability, Layout A detailed clarity, preview-only disclaimer, progress states, dependency status, failed/partial visibility, and clear timecode display.

Constraints
- Do not add new features outside Stage 5 plan.
- Do not change data contracts unless required to display existing information correctly.
- Do not remove existing tests or reduce coverage.
- If Playwright is feasible for a PDF/HTML visual harness, add or run it. If not feasible, document why and provide PySide6/PDF visual verification artifacts.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- PDF Layout B/A visual refinements for header/footer, density, thumbnail labels, warnings, disclaimer.
- GUI UX refinements for controls, progress, dependency screen, error/success states.
- Accessibility/responsiveness improvements where applicable.
- Visual verification artifacts or tests, including Playwright if feasible for a visual harness.
- Updated docs/ui-spec.md if design decisions changed.
- Updated docs/implement.md and handoff.

Done when
Visual UX acceptance criteria are met, existing functionality remains intact, and verification artifacts are documented.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- visual artifact generation command if available
- Playwright command if a visual harness exists or was created
- GUI smoke/manual checklist where environment permits

Reporting
Document refinements, before/after notes where possible, command outputs, screenshots/artifacts, limitations, and next prompt.

Update files
Update UI/PDF source, tests/artifacts, docs/ui-spec.md, docs/implement.md, stage implement doc, and handoff.

Stop rule
Stop after Dev handoff. Do not run QA. Do not start Stage 6.
