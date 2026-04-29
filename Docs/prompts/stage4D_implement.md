Metadata
Stage ID: 4D
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-04D-plan.md, docs/stage.md, docs/implement.md, docs/architecture.md, docs/ui-spec.md
Required output files: src/frameproof/gui/, GUI tests/checklist, settings persistence files, docs/stages/stage-04D-implement.md, docs/reports/dev/stage-04D-handoff.md, docs/implement.md
Gate condition: GUI implemented using existing pipeline.
Next recommended prompt: [Stage 4D-QA]
Stop condition: Stop after implementation handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Implement the PySide6 GUI and settings/progress behavior.

Context
The GUI must provide source selector, output selector, middle frame count selector, layout selector, export still PNGs checkbox, start button, progress table, and dependency check screen.

Constraints
- Reuse the existing core pipeline.
- Do not create a separate GUI-only media processing pipeline.
- Do not fake progress; report actual pipeline state where available.
- If GUI tests cannot fully run headless, create executable smoke/manual verification docs and test what can be automated.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- PySide6 main window.
- Dependency check screen/status.
- Settings persistence for paths, layout, middle_count, export_stills, adapter paths.
- Progress table with clip, format, probe, capture, PDF, warning columns.
- Start/cancel behavior wired to core pipeline or a documented controller abstraction.
- GUI entrypoint.
- Automated tests where practical plus manual verification checklist.
- Updated docs/implement.md and handoff.

Done when
GUI can be launched, settings persist, dependency status is visible, and the existing pipeline can be started from GUI without parallel implementation.

Validation
Run:
- python -m pytest
- ruff check .
- mypy src
- python -m frameproof --help
- python -m frameproof.gui --help or documented GUI launch command
If headless GUI launch is possible, run a smoke launch test.

Reporting
Document changed files, state ownership, validation results, manual verification steps, known issues, and next prompt.

Update files
Update GUI source/tests/docs and Stage 4D handoff.

Stop rule
Stop after Dev handoff. Do not run QA. Do not start Stage 5.
