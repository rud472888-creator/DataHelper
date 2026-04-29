# Stage 03 Plan

- lane: dev
- stage: stage-03
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_2_pass_verified: yes
- risk_level: moderate
- next_recommended_prompt: `[Stage 3-Implement]`

## Gate Verification

- `docs/qa.md` records `latest_verdict: PASS`, `latest_gate: passed`, and `next_recommended_prompt: [Stage 3-Plan]`.
- `docs/stages/stage-02-qa.md` records `verdict: PASS`, `gate: passed`, and `stage_3_status: unblocked-by-qa`.
- At session start, `docs/stage.md` recorded `last_result: stage-02-qa-pass`, `qa_gate: pass`, and `implementation_allowed: true`; this plan updates the board to point at `[Stage 3-Implement]`.
- Stage 3 planning is therefore allowed, but this phase remains docs-only and must stop before implementation.

## Scope

- Plan the reusable Stage 3 foundation layer only: typed schemas, status and error model, settings/config model, capture planner, timecode helpers, adapter base interfaces, and unit-test coverage.
- Define a file and module layout that matches the Stage 2 architecture and can be reused unchanged by later standard-video, RAW, manifest, PDF, and GUI stages.
- Preserve requested-versus-actual capture facts as first-class data so later renderers, manifests, and progress UI consume one shared model.
- Keep the plan aligned with the current repository state, which still contains only the Stage 1 bootstrap CLI and diagnostics helpers.
- Update the stage board so the next legal step is a fresh Stage 3 implementation session.

## Non-Scope

- No Python implementation in this phase.
- No FFmpeg probe or capture integration.
- No RAW subprocess client implementation beyond planning the shared interfaces they will use.
- No PDF rendering, still export, manifest writing, scanner, clip grouping, or GUI work.
- No end-to-end media processing or fake adapter behavior.
- No new runtime dependencies are planned; the foundation should use the standard library and the existing dev-tool chain unless a later approved change says otherwise.

## Evidence And Planning Basis

- `docs/architecture.md` defines Stage 3 as the reusable foundation layer and assigns `capture_planner.py`, `timecode.py`, `config/settings.py`, and `adapters/base.py` to this stage.
- `docs/api-contract.md` fixes the Python adapter protocols plus the required shared types: `ClipCandidate`, `ClipInfo`, `CapturePlan`, `CaptureRequest`, `CaptureResult`, `ProbeResult`, `ReportItem`, `AdapterError`, `BatchStatus`, `ClipStatus`, `CaptureStatus`, and `AdapterDependencyState`.
- `docs/data-inventory.md` fixes the normalized entity fields, nullability rules, status vocabulary, and invariants that Stage 3 constructors must enforce.
- The current source tree only has the Stage 1 bootstrap shell: `src/frameproof/cli.py` and `src/frameproof/settings.py`. Stage 3 therefore needs to add the real foundation packages without breaking the bootstrap CLI surface or inventing parallel architecture.

## Touched Files In This Phase

- `docs/stages/stage-03-plan.md`
- `docs/stage.md`

## Planned Module And File Layout For Stage 3 Implement

### Core package

- `src/frameproof/core/__init__.py`
- `src/frameproof/core/models.py`
- `src/frameproof/core/capture_planner.py`
- `src/frameproof/core/timecode.py`

`src/frameproof/core/models.py` should be the durable home for the shared Stage 3 data layer. Use typed standard-library models plus enums rather than introducing a new dependency. The file should define:

- `ClipCandidate`
- `ClipInfo`
- `CaptureRequest`
- `CapturePlan`
- `CapturePoint`
- `CaptureResult`
- `ProbeResult`
- `ReportItem`
- `BatchSummary`
- `CaptureProfile`
- `AdapterError`
- `BatchStatus`
- `ClipStatus`
- `CaptureStatus`
- `AdapterDependencyState`
- `TimecodeSource`

Constructor and validation rules should directly encode the Stage 2 docs:

- reject `ClipInfo` records where both `frame_count` and `duration_seconds` are null
- require `fps_num` and `fps_den` to be provided together or omitted together
- require each capture record to preserve requested position data
- keep `metadata_raw`, `warnings`, and `errors` non-null, defaulting to empty collections
- keep status and source names exactly aligned with `docs/api-contract.md` and `docs/data-inventory.md`

### Capture planner

- `src/frameproof/core/capture_planner.py`

This module should stay pure and deterministic. It should accept normalized clip metadata plus the requested `middle_count` and return an ordered `CapturePlan` with `Start`, optional `Mid1` through `Mid3`, and `End`.

Planner rules to lock in:

- support `middle_count` values `0`, `1`, `2`, and `3`
- prefer `frame_count` over `duration_seconds` whenever both exist
- when using frame counts, compute against the last valid frame index and use `floor(x + 0.5)` rounding, not Python banker’s rounding
- when using duration fallback, compute requested seconds and clamp within the clip duration bounds
- preserve duplicate-collapsed slots for short clips rather than deleting them
- keep requested ratio and requested position data even when multiple labels collapse to the same actual frame later

### Timecode helpers

- `src/frameproof/core/timecode.py`

This module should provide pure utilities that later adapters, report builders, and UI code can call without duplicating logic. The planned responsibilities are:

- parse and validate basic SMPTE-style timecode strings at foundation level
- format display labels while respecting `tc_drop_frame` when known
- calculate derived timecode from `start_timecode` plus frame offset when a stable frame rate is known
- expose elapsed-time fallback formatting when no trustworthy timecode exists
- preserve the distinction between `native_adapter`, `container_metadata`, `calculated`, and `elapsed_fallback` instead of collapsing them into one display path

Stage 3 should not overreach into full media-specific drop-frame math for unsupported cases. If the inputs are insufficient, the utility should return an honest degraded result or warning-ready outcome rather than fabricate certainty.

### Adapter base contracts

- `src/frameproof/adapters/__init__.py`
- `src/frameproof/adapters/base.py`

`src/frameproof/adapters/base.py` should implement the shared adapter surface described in `docs/api-contract.md`:

- `ProbeAdapter`
- `CaptureAdapter`

The file should import the domain models from `frameproof.core.models` and define only the base protocol and shared contract helpers needed by later adapters. It must not add FFmpeg, BRAW, R3D, or ARRIRAW behavior in Stage 3.

### Settings and config

- `src/frameproof/config/__init__.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/settings.py`

`src/frameproof/config/settings.py` should become the durable home for runtime configuration models and validation logic. The plan assumes:

- path fields for input roots, output destination, and optional staging directory
- report and capture options such as `middle_count`, PDF layout selection, still-export toggle, and privacy/path-display settings where those values are already implied by Stage 2 docs
- adapter-path or dependency-path settings as pure configuration data only, not live discovery
- validation that rejects impossible or contradictory settings while keeping Stage 3 free of side effects

Because the repository already ships `src/frameproof/settings.py`, Stage 3 implement should keep that module as a thin compatibility wrapper or re-export layer unless the CLI and tests are updated in the same change. That keeps the diff reversible and avoids breaking the Stage 1 bootstrap shell.

### Unit tests

- `tests/unit/core/test_models.py`
- `tests/unit/core/test_capture_planner.py`
- `tests/unit/core/test_timecode.py`
- `tests/unit/config/test_settings.py`
- `tests/unit/adapters/test_base.py`

The existing bootstrap tests in `tests/test_cli.py` and `tests/test_package.py` should remain green. Stage 3 implementation should expand the test tree under `tests/unit/` rather than replacing the earlier smoke coverage.

## Acceptance Criteria For Stage 3 Implement

- The repository contains importable Stage 3 foundation modules under `src/frameproof/core/`, `src/frameproof/config/`, and `src/frameproof/adapters/base.py`.
- Shared schemas and enums exist for the normalized clip, capture, probe, report, and status/error records defined in the Stage 2 docs.
- Schema validation enforces the documented invariants without depending on FFmpeg, RAW SDKs, scanners, renderers, or GUI code.
- The capture planner implements `middle_count` `0` to `3`, frame-count priority, duration fallback, `floor(x + 0.5)` rounding, and duplicate preservation for short clips.
- Timecode utilities can format native, calculated, container-metadata, and elapsed-fallback labels while preserving drop-frame flags and degraded cases honestly.
- Base adapter protocols are present and typed, but no concrete media adapter behavior is introduced yet.
- Settings/config models cover reusable Stage 3 foundation needs and keep the bootstrap CLI working.
- Unit tests cover the foundation rules and the full test suite remains green after Stage 3 implementation.

## Unit Test Plan For Stage 3 Implement

### `tests/unit/core/test_models.py`

- validate `ClipInfo` rejection when both `frame_count` and `duration_seconds` are missing
- validate `fps_num` and `fps_den` pair rules
- validate capture records require requested position data
- validate default empty collections for `metadata_raw`, `warnings`, and `errors`
- validate status vocabulary and timecode-source names match the Stage 2 contract

### `tests/unit/core/test_capture_planner.py`

- assert slot ordering for `middle_count` `0`, `1`, `2`, and `3`
- assert frame-count path wins when both `frame_count` and `duration_seconds` are present
- assert rounding uses `floor(x + 0.5)` on frame indexes
- assert duration fallback works when frame count is unavailable
- assert very short clips preserve duplicate slot records instead of silently dropping labels

### `tests/unit/core/test_timecode.py`

- assert non-drop and drop-frame display formatting stay distinct
- assert calculated timecode requires a stable frame rate and a usable start timecode
- assert elapsed fallback is used when native or calculated timecode cannot be produced honestly
- assert VFR or unknown-rate clips degrade cleanly instead of fabricating frame-accurate labels
- assert nullable drop-frame flags stay nullable when the source is unknown

### `tests/unit/config/test_settings.py`

- assert valid config objects accept expected paths and Stage 3 option values
- assert invalid `middle_count`, contradictory path settings, or malformed tool-path settings fail fast
- assert the new config module can coexist with the existing bootstrap import path

### `tests/unit/adapters/test_base.py`

- assert the base protocol surface matches the Stage 2 API contract naming and required method signatures
- assert probe and capture result models can represent `dependency_missing`, `metadata_incomplete`, `probe_failed`, and `decode_failed` without adapter-specific code
- assert Stage 3 contract code stays side-effect free and does not perform filesystem or tool probing on import

## Required Edge Cases To Carry Into Stage 3 Implement

- Short clips: clips with one or only a few frames must still keep all requested labels in the plan, with duplicate collapse represented explicitly instead of hidden.
- `frame_count` versus `duration_seconds`: when both are present, planner math must prefer frame count even if the implied duration does not align exactly with the duration field.
- Rounding: any frame-index calculation that converts a ratio to a target frame must use `floor(x + 0.5)` so the spec’s rounding rule is stable across platforms and Python versions.
- VFR: clips with missing or unreliable `fps_num` and `fps_den` must still support duration-based planning, but timecode derivation must not pretend there is a stable frame clock.
- Drop-frame flags: `tc_drop_frame` must support `true`, `false`, and `null`, with display helpers respecting known flags and preserving uncertainty when the source does not prove the value.
- `dependency_missing` statuses: the status and error model must represent missing tools or SDKs as normalized structured results, not exceptions that force concrete adapter code into the foundation layer.

## Risks

- The largest design risk is model overlap between `CaptureRequest`, `CapturePoint`, and `CaptureResult`. Stage 3 implement should keep their responsibilities distinct so later manifests and renderers do not need a second translation layer.
- Moving from the bootstrap `src/frameproof/settings.py` into the Stage 2 target path `src/frameproof/config/settings.py` can break the CLI if compatibility is not handled deliberately.
- Timecode helpers can easily become too ambitious. Stage 3 should implement only the deterministic shared logic and leave media-tool specifics to later adapters.
- If Stage 3 loosens status naming or nullability rules, later adapters and reports will drift from the Stage 2 contract and require avoidable rework.

## Validation Commands For This Plan Phase

- `cat docs/qa.md`
- `cat docs/stage.md`
- `find src docs tests -maxdepth 4 -type f | sort | sed -n '1,200p'`

## Exact Next Prompt

`[Stage 3-Implement]`

## Outcome

Stage 3 planning is complete. The next phase should implement only the reusable foundation layer described here, keep the bootstrap shell intact, and stop before any standard-video, RAW, PDF, manifest, or GUI feature work begins.
