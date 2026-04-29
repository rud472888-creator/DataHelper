Metadata
Stage ID: 4B
Sub-phase: Implement
Lane: Dev
Required input files: docs/stages/stage-04B-plan.md, docs/stage.md, docs/implement.md, docs/architecture.md, docs/api-contract.md, docs/data-inventory.md
Required output files: src/frameproof/adapters/braw_adapter_client.py, src/frameproof/adapters/r3d_adapter_client.py, src/frameproof/adapters/arriraw_art_adapter_client.py, dependency detection files, tests for RAW contracts, docs/stages/stage-04B-implement.md, docs/reports/dev/stage-04B-handoff.md, docs/implement.md
Gate condition: RAW adapter clients and dependency detection implemented without fake support.
Next recommended prompt: [Stage 4B-QA]
Stop condition: Stop after implementation handoff.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Implement BRAW, R3D, and ARRIRAW adapter clients and dependency detection.

Context
RAW adapters must be subprocess-isolated. The actual vendor SDK tools may be absent. The correct behavior when absent is dependency_missing, not fake success.

Constraints
- Do not bundle or import proprietary SDKs directly.
- Do not create mock-only RAW support in production code.
- Test doubles are allowed only in tests and must be clearly isolated.
- Do not use placeholders as a substitute for required functionality. Do not leave TODOs for core behavior. Do not hardcode fake data unless explicitly required as seed/demo data. Do not implement only a visual shell while skipping required state, validation, API, persistence, or interaction logic. Do not mark work complete if any acceptance criterion is unimplemented. Do not skip relevant empty/loading/error/success states. Do not create parallel architecture when the repository already has established patterns. Do not use previous Codex session history, transcript, or resume output. Write a complete Dev handoff report so future fresh Dev sessions can continue from repository files only.

Deliverables
- BRAW client supporting probe/capture subprocess JSON contract.
- R3D client supporting probe/capture subprocess JSON contract and multi-part logical grouping hooks.
- ARRIRAW ART CMD client supporting configured path, metadata export command contract, capture/process command contract where possible.
- Dependency checker for FFmpeg, FFprobe, MediaInfo, BRAW adapter, R3D adapter, ARRI ART CMD.
- CLI/config exposure for adapter paths if not already present.
- Contract fixture tests using temporary executable test doubles.
- Tests for missing dependency and malformed JSON errors.
- Updated docs/implement.md and handoff.

Done when
RAW client code is real subprocess integration, missing dependencies are reported per file/format, and tests verify contract behavior without pretending vendor tools are present.

Validation
Run:
- python -m pytest tests/unit tests/integration
- python -m pytest
- ruff check .
- mypy src
If any real RAW adapter binary is configured in the environment, run a smoke dependency check and document the result.

Reporting
Document changed files, dependency assumptions, command results, known blockers for proprietary SDKs, and next prompt.

Update files
Update RAW adapter client files, dependency checker, tests, docs/implement.md, stage implement doc, and handoff.

Stop rule
Stop after Dev handoff. Do not run QA. Do not start Stage 4C.
