# Stage 03 QA Report

- gate: PASS
- verdict: PASS
- stage: stage-03
- lane: qa
- next_recommended_prompt: `[Stage 4A-Plan]`
- stage_4a_status: unblocked-by-qa

## Scope

Independent QA review of the Stage 3 foundation implementation against:

- `docs/stages/stage-03-plan.md`
- `docs/stages/stage-03-implement.md`
- `docs/reports/dev/stage-03-handoff.md`
- `docs/stage.md`
- `docs/qa.md`
- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/data-inventory.md`
- `docs/frameproof_tech_spec_ko.md`
- `src/frameproof/core/`
- `src/frameproof/adapters/base.py`
- `tests/unit/`

This was a QA-only gate. No source files were modified. Only QA documents were updated.

## Checked Files

- `AGENTS.md`
- `docs/stage.md`
- `docs/qa.md`
- `docs/stages/stage-03-plan.md`
- `docs/stages/stage-03-implement.md`
- `docs/reports/dev/stage-03-handoff.md`
- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/data-inventory.md`
- `docs/frameproof_tech_spec_ko.md`
- `src/frameproof/core/__init__.py`
- `src/frameproof/core/models.py`
- `src/frameproof/core/capture_planner.py`
- `src/frameproof/core/timecode.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/settings.py`
- `src/frameproof/adapters/base.py`
- `tests/unit/adapters/test_base.py`
- `tests/unit/config/test_settings.py`
- `tests/unit/core/test_capture_planner.py`
- `tests/unit/core/test_models.py`
- `tests/unit/core/test_timecode.py`

## Command Results

- `python -m pytest tests/unit` -> PASS

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-8.3.2, pluggy-1.6.0
collected 32 items
...
============================== 32 passed in 0.03s ==============================
```

- `python -m pytest` -> PASS

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-8.3.2, pluggy-1.6.0
collected 38 items
...
============================== 38 passed in 0.21s ==============================
```

- `ruff check .` -> PASS

```text
All checks passed!
```

- `mypy src` -> PASS

```text
Success: no issues found in 13 source files
```

- `grep -R "floor" src/frameproof tests || true` -> PASS

```text
src/frameproof/core/capture_planner.py:from math import floor
src/frameproof/core/capture_planner.py:    return floor(value + 0.5)
tests/unit/core/test_capture_planner.py:def test_frame_count_rounding_uses_floor_plus_half() -> None:
```

- `grep -R "duplicate_of" src/frameproof tests` -> PASS

```text
src/frameproof/core/models.py:    duplicate_of: str | None = None
src/frameproof/core/capture_planner.py:        duplicate_of = seen.get(requested_frame_index)
src/frameproof/core/capture_planner.py:        duplicate_of = seen.get(duplicate_key)
tests/unit/core/test_capture_planner.py:    assert [request.duplicate_of for request in plan.requests] == [None, "Start", "Start", "Start", "Start"]
```

- `grep -R "dependency_missing" src/frameproof docs` -> PASS

```text
src/frameproof/core/models.py:    DEPENDENCY_MISSING = "dependency_missing"
docs/architecture.md:- Probe failures become `ReportItem` seeds with `probe_failed`, `dependency_missing`, `unsupported_format`, or `metadata_incomplete`.
docs/api-contract.md:  "status": "dependency_missing",
docs/data-inventory.md:| `dependency_missing` | clip | required tool or SDK missing |
```

## Evidence

### Shared schema fidelity

- `src/frameproof/core/models.py:36-40` constrains `CaptureStatus` to `success`, `decode_failed`, `metadata_incomplete`, and `skipped_duplicate`, matching the Stage 3 capture contract.
- `src/frameproof/core/models.py:283-294` and `src/frameproof/core/models.py:323-334` enforce requested-position requirements plus the documented actual-position or `duplicate_of` requirement for non-`decode_failed` captures.
- `src/frameproof/core/models.py:403-420` restores the documented `BatchSummary` counters: `success_count`, `partial_success_count`, `probe_failed_count`, `decode_failed_count`, and `skipped_count`.
- `tests/unit/core/test_models.py:78-85`, `tests/unit/core/test_models.py:151-177`, and `tests/unit/core/test_models.py:180-190` lock the capture-status vocabulary, reject clip-only statuses at capture scope, and verify the normalized batch counters.

### Capture planner rules

- `src/frameproof/core/capture_planner.py:10-18` and `src/frameproof/core/models.py:69-72` enforce `middle_count` within `0..3`.
- `src/frameproof/core/capture_planner.py:21-22` implements the required `floor(x + 0.5)` rounding rule.
- `src/frameproof/core/capture_planner.py:31-62` prefers `frame_count`, computes against the last valid frame index, and preserves duplicate-collapsed slots through `duplicate_of`.
- `src/frameproof/core/capture_planner.py:65-100` falls back to duration planning, clamps within clip bounds, and preserves duplicate-collapsed slots in the duration path as well.
- `tests/unit/core/test_capture_planner.py:24-70` covers `middle_count` shapes, frame-count priority, rounding, duration fallback, and short-clip duplicate preservation.

### Timecode fallback rules

- `src/frameproof/core/timecode.py:153-196` calculates derived timecode only when a usable start timecode and stable frame rate exist, preserving nullable drop-frame behavior and degraded warnings.
- `src/frameproof/core/timecode.py:199-242` applies the documented priority order: native actual timecode, calculated timecode, container metadata, then elapsed fallback, before returning `N/A`.
- `tests/unit/core/test_timecode.py:19-78` locks calculated output, unknown drop-frame warning behavior, container-metadata precedence, and elapsed fallback behavior.

### Adapter base contract

- `src/frameproof/adapters/base.py:16-37` defines the `ProbeAdapter` and `CaptureAdapter` protocol surface required by the API contract.
- `tests/unit/adapters/test_base.py:53-83` verifies runtime-checkable protocol conformance and side-effect-free import behavior.

## Evaluation

- Spec fidelity / product depth: PASS. The Stage 3 foundation now matches the documented schema, planner, adapter, and timecode rules.
- Functionality: PASS. The required commands passed, and the target rules called out in the QA prompt are implemented correctly.
- Visual design / UX clarity: PASS for Stage 3 scope. This phase is foundational and does not ship a new UI surface.
- Code quality / maintainability: PASS. The implementation is typed, deterministic, and reusable without introducing a second pipeline.
- Accessibility / responsiveness: PASS for Stage 3 scope. No interactive UX surface changed here.
- Validation completeness: PASS. Required commands passed, and the tests now guard the previously failing schema-contract surfaces.

## Defects

- Blocking defects: none
- Non-blocking observations:
  1. Stage 3 intentionally stops at contracts and pure helpers; real media-tool integration remains a Stage 4 concern.
  2. The grep commands also matched `__pycache__` artifacts during execution, but the relevant source and test hits were present in the same command output.

## Verdict

PASS. Stage 3 satisfies the QA gate in this session. Stage 4A is unblocked.

Exact next recommended prompt: `[Stage 4A-Plan]`
