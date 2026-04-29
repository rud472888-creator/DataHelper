Metadata
Stage ID: 4A
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-04A-plan.md, docs/stage.md, docs/implement.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md, docs/ui-spec.md
Required output files: src/frameproof/core/scanner.py, src/frameproof/core/clip_grouper.py, src/frameproof/adapters/ffmpeg_adapter.py, src/frameproof/core/probe_service.py, src/frameproof/core/capture_service.py, src/frameproof/render/pdf_renderer.py, src/frameproof/output/manifest_writer.py, CLI files, tests/integration/, docs/stages/stage-04A-implement.md, docs/reports/dev/stage-04A-handoff.md, docs/implement.md
Gate condition: Standard video CLI E2E pipeline works.
Next recommended prompt: [Stage 4A-QA]
Stop condition: Stop after implementation handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Implement the Standard Video CLI Pipeline for MOV/MP4/MXF/AVI and other FFmpeg/FFprobe-compatible standard video files.

Context
The pipeline should scan inputs, group clips where applicable, resolve the FFmpeg adapter, probe metadata, plan Start/Mid/End captures, capture frames, normalize metadata, render Layout B PDF, and write CSV/JSON manifests.

Constraints
- Do not implement BRAW/R3D/ARRIRAW adapter clients in this sprint.
- Do not implement GUI.
- Do not fake video outputs. Use FFmpeg/FFprobe when available and dependency_missing/error statuses when missing.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- Recursive scanner with extension filtering.
- Standard clip grouping baseline.
- Adapter resolver for standard video formats.
- FFprobe metadata probe with MediaInfo fallback only if configured and available.
- FFmpeg capture implementation for requested frames/timestamps.
- Capture service that records requested/actual capture data.
- Layout B PDF renderer with header, clip blocks, thumbnail labels, footer disclaimer, failed/partial section if applicable.
- CSV/JSON manifest writer.
- CLI options for input, recursive, middle-count, layout contact_sheet, output, csv, json.
- Integration tests using synthetic video if FFmpeg is available; otherwise dependency_missing behavior tests.
- Updated docs/implement.md and Dev handoff.

Done when
A standard video input can produce PDF, CSV, and JSON through CLI, and validation commands pass or dependency-missing behavior is explicitly tested.

Validation
Run:
- python -m frameproof --help
- python -m pytest tests/unit tests/integration
- python -m pytest
- ruff check .
- mypy src
If FFmpeg is installed, also generate a tiny synthetic video and run a CLI smoke test that writes PDF/CSV/JSON.

Reporting
Record all changed files, design decisions, command outputs, generated artifacts, known issues, and next prompt.

Update files
Update Stage 4A source, tests, docs/implement.md, docs/stages/stage-04A-implement.md, and docs/reports/dev/stage-04A-handoff.md.

Stop rule
Stop after Dev handoff. Do not run QA. Do not start Stage 4B.
