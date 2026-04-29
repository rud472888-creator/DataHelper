Metadata
Stage ID: 3
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-03-plan.md, docs/stage.md, docs/implement.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md
Required output files: src/frameproof/core/, src/frameproof/adapters/base.py, tests/unit/, docs/stages/stage-03-implement.md, docs/reports/dev/stage-03-handoff.md, docs/implement.md
Gate condition: Foundation logic implemented and unit-tested.
Next recommended prompt: [Stage 3-QA]
Stop condition: Stop after implementation handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Implement the reusable foundation layer for Frame Proof.

Context
The source spec defines ClipInfo, CapturePoint, ReportItem, capture planning rules, timecode priorities, status values, adapter interface, settings validation, and manifest data needs.

Constraints
- Do not implement FFmpeg capture or PDF rendering yet unless Stage 3 plan explicitly includes a minimal pure foundation utility needed by later stages.
- Do not fake adapter support.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Typed schemas for ClipInfo, CapturePoint, ReportItem, status enums, adapter result/error payloads.
- Capture planner implementing middle_count 0/1/2/3, frame_count priority, floor(x + 0.5) rounding, duration fallback, short clip duplicate tracking.
- Timecode utility for display formatting, elapsed fallback, calculated label, drop-frame flag handling at foundation level.
- Settings/config model with paths and adapter settings.
- Adapter base interface with probe/capture contract.
- Unit tests for core rules.
- Updated docs/implement.md and handoff.

Done when
Foundation modules are importable, unit tests cover planner/timecode/schema/settings edge cases, and validation passes.

Validation
Run:
- python -m pytest tests/unit
- python -m pytest
- ruff check .
- mypy src

Reporting
Update docs/implement.md with current stage/sub-phase, changed files, implementation decisions, validation results, known issues, QA status, latest handoff, next prompt, assumptions, and manual verification steps.

Update files
Update foundation source files, unit tests, and Stage 3 implementation docs.

Stop rule
Stop after Dev handoff. Do not run QA. Do not start Stage 4A.
