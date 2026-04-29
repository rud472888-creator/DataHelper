# Stage 03 Implement

- lane: dev
- stage: stage-03
- subphase: implement
- status: complete
- scope_boundary: reusable-foundation-layer-only
- next_recommended_prompt: `[Stage 3-QA]`

## Delivered Scope

- Implemented the Stage 3 reusable foundation layer under `src/frameproof/core/`, `src/frameproof/config/`, and `src/frameproof/adapters/`.
- Added durable typed schemas and enums for clip metadata, capture planning, capture results, report items, adapter errors, dependency states, and timecode sources.
- Implemented the pure capture planner covering `middle_count` `0` through `3`, frame-count priority, `floor(x + 0.5)` rounding, duration fallback, and duplicate preservation for short clips.
- Implemented foundation-level timecode parsing and display helpers for native, calculated, container-metadata, and elapsed-fallback labels with nullable drop-frame handling.
- Added the Stage 3 config model and kept the bootstrap `frameproof.settings` import path working through a compatibility wrapper.
- Added unit tests for core models, planner, timecode utilities, settings, and adapter base contracts.

## Changed Files And Reasons

- `src/frameproof/core/models.py` defines the normalized Stage 3 data layer and validation rules.
- `src/frameproof/core/capture_planner.py` implements deterministic capture-slot planning.
- `src/frameproof/core/timecode.py` implements reusable timecode parsing, formatting, and fallback logic.
- `src/frameproof/core/__init__.py` re-exports the public core surface.
- `src/frameproof/config/settings.py` defines the Stage 3 configuration and runtime diagnostics model.
- `src/frameproof/settings.py` preserves the bootstrap compatibility import path.
- `src/frameproof/adapters/base.py` defines the `ProbeAdapter` and `CaptureAdapter` protocols.
- `tests/unit/core/test_models.py` locks schema and status edge cases.
- `tests/unit/core/test_capture_planner.py` locks planner rules and short-clip duplicate behavior.
- `tests/unit/core/test_timecode.py` locks calculated and fallback timecode behavior.
- `tests/unit/config/test_settings.py` locks settings validation and compatibility wrapper behavior.
- `tests/unit/adapters/test_base.py` locks the adapter base contract and side-effect-free import behavior.
- `docs/implement.md`, `docs/stage.md`, and `docs/reports/status/current-status.md` were updated for durable handoff state.
- `docs/stages/stage-03-implement.md` and `docs/reports/dev/stage-03-handoff.md` were added to complete the missing Dev artifacts.

## Implementation Decisions

- Used standard-library dataclasses and enums for the foundation layer rather than adding new runtime dependencies.
- Kept planner and timecode utilities pure so later stages can reuse them without filesystem or subprocess coupling.
- Preserved duplicate-collapsed capture slots as explicit records instead of deleting them for short clips.
- Kept the Stage 1 bootstrap CLI intact by routing configuration ownership through `src/frameproof/config/settings.py` and re-exporting from `src/frameproof/settings.py`.
- Did not implement FFmpeg capture, PDF rendering, manifest writing, or RAW subprocess execution in this stage.

## Validation Results

- `python -m pytest tests/unit` -> PASS (`29 passed`)
- `python -m pytest` -> PASS (`35 passed`)
- `ruff check .` -> PASS
- `mypy src` -> PASS

## Blockers And Known Gaps

- No blocking Stage 3 implementation defects were found in this run.
- Stage 3 still requires a fresh QA pass before Stage 4A work begins.
- Timecode derivation intentionally degrades to warnings or elapsed fallback when the inputs do not support honest frame-accurate calculation.

## Fresh Session Notes

- Stage 3 QA should validate the foundation modules and tests directly from repository files.
- Stage 4A should reuse the Stage 3 models, planner, timecode utilities, and settings layer rather than creating parallel abstractions.
- The next legal prompt is `[Stage 3-QA]`.
