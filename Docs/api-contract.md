# Adapter API Contract

This document fixes the shared adapter contract for Frame Proof. All later implementations must conform to these Python interfaces and JSON payloads so standard-video adapters, `BRAW`, R3D, and ARRIRAW all feed the same normalization and reporting pipeline.

## Contract Goals

- One Python-facing probe and capture API for every adapter.
- One subprocess JSON envelope for every RAW adapter client.
- Stable status and error semantics across CLI, GUI, PDF, and manifest outputs.
- No adapter may skip requested-versus-actual capture reporting.

## Python Interfaces

Recommended Stage 3 interface shape:

```python
from __future__ import annotations

from pathlib import Path
from typing import Protocol, Sequence

from frameproof.core.models import (
    AdapterDependencyState,
    CapturePlan,
    CaptureProfile,
    CaptureResult,
    ClipCandidate,
    ClipInfo,
    ProbeResult,
)


class ProbeAdapter(Protocol):
    name: str
    format_families: tuple[str, ...]

    def is_available(self) -> AdapterDependencyState: ...
    def probe(self, candidate: ClipCandidate) -> ProbeResult: ...


class CaptureAdapter(ProbeAdapter, Protocol):
    def capture(
        self,
        candidate: ClipCandidate,
        plan: CapturePlan,
        profile: CaptureProfile,
        staging_dir: Path,
    ) -> Sequence[CaptureResult]: ...
```

Interface rules:

- `is_available()` reports tool-path and dependency state without touching the source clip.
- `probe()` returns either normalized-enough probe data for the normalizer or a structured error.
- `capture()` only runs after a successful or partially successful probe.
- `capture()` must return one result per requested capture slot, even when multiple slots collapse to the same actual frame.
- Adapter implementations must not write final manifests or PDFs.

## Python Domain Types

Required types to expose from Stage 3:

- `ClipCandidate`
- `ClipInfo`
- `CapturePlan`
- `CaptureRequest`
- `CaptureResult`
- `ProbeResult`
- `ReportItem`
- `AdapterError`
- `BatchStatus`
- `ClipStatus`
- `CaptureStatus`
- `AdapterDependencyState`

## Probe Result Contract

`probe()` returns a structured result with these fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `ok` | `bool` | yes | `false` when probe cannot produce usable clip data |
| `adapter_name` | `str` | yes | stable machine-readable name |
| `format_family` | `str` | yes | `standard`, `braw`, `r3d`, `arriraw` |
| `clip` | `ClipInfo | None` | conditional | present on success or metadata-incomplete success |
| `warnings` | `list[str]` | yes | includes fallback notes |
| `errors` | `list[AdapterError]` | yes | empty on clean success |
| `status` | `str` | yes | normalized clip-level status |
| `metadata_raw` | `dict[str, object]` | yes | raw adapter payload preserved for debugging and appendices |

Probe rules:

- `ClipInfo.frame_count` or `ClipInfo.duration_seconds` must be present whenever `ok=true`.
- `start_timecode` is nullable.
- `BRAW`, R3D, and ARRIRAW probe responses may carry vendor-specific raw metadata inside `metadata_raw`, but normalized fields must still be filled where possible.

## Capture Result Contract

`capture()` returns an ordered sequence of slot results:

| Field | Type | Required | Notes |
|---|---|---|---|
| `label` | `str` | yes | `Start`, `Mid1`, `Mid2`, `Mid3`, `End` |
| `requested_ratio` | `float` | yes | exact planner ratio |
| `requested_frame_index` | `int | None` | conditional | preferred when frame-count path was used |
| `requested_seconds` | `float | None` | conditional | required when duration fallback was used |
| `actual_frame_index` | `int | None` | conditional | adapter-reported actual frame |
| `actual_seconds` | `float | None` | conditional | adapter-reported actual timestamp |
| `actual_timecode` | `str | None` | conditional | nullable before fallback labeling |
| `actual_timecode_source` | `str | None` | conditional | `native_adapter`, `calculated`, `container_metadata`, `elapsed_fallback` |
| `image_path_temp` | `str | None` | conditional | staging PNG path when decode succeeded |
| `warnings` | `list[str]` | yes | duplicate collapse, fallback, uncertain drop-frame flag |
| `errors` | `list[AdapterError]` | yes | decode failure details |
| `status` | `str` | yes | `success`, `decode_failed`, `skipped_duplicate`, `metadata_incomplete` |
| `duplicate_of` | `str | None` | conditional | slot label of the shared frame for very short clips |

Capture rules:

- A duplicate-collapsed slot is still returned as its own record.
- `image_path_temp` points to staging output only. Final exported PNG path is assigned later.
- Adapters may return both `actual_frame_index` and `actual_seconds`.
- If a decoder lands on a nearby decodable frame, the adapter returns the actual location instead of hiding the drift.

## RAW Subprocess JSON Envelope

RAW adapters must accept these commands:

- `probe`
- `capture`
- optionally `version`

Canonical request envelope:

```json
{
  "request_id": "uuid-string",
  "command": "probe",
  "input": {
    "source_path": "/Volumes/Footage/A001_C001.R3D",
    "part_files": [
      "/Volumes/Footage/A001_C001_001.R3D",
      "/Volumes/Footage/A001_C001_002.R3D"
    ]
  },
  "options": {
    "profile": "preview_rec709_sdr",
    "staging_dir": "/tmp/frameproof/session-123",
    "timeout_seconds": 120
  }
}
```

Capture request envelope:

```json
{
  "request_id": "uuid-string",
  "command": "capture",
  "input": {
    "source_path": "/Volumes/Footage/A001_0001.BRAW",
    "part_files": []
  },
  "capture_points": [
    {
      "label": "Start",
      "requested_ratio": 0.0,
      "requested_frame_index": 0,
      "requested_seconds": null
    },
    {
      "label": "Mid1",
      "requested_ratio": 0.5,
      "requested_frame_index": 508,
      "requested_seconds": null
    },
    {
      "label": "End",
      "requested_ratio": 1.0,
      "requested_frame_index": 1016,
      "requested_seconds": null
    }
  ],
  "options": {
    "profile": "preview_rec709_sdr",
    "staging_dir": "/tmp/frameproof/session-123"
  }
}
```

Canonical success response envelope:

```json
{
  "request_id": "uuid-string",
  "ok": true,
  "adapter_name": "braw_adapter",
  "adapter_version": "1.0.0",
  "status": "success",
  "warnings": [],
  "errors": [],
  "clip": {
    "clip_name": "A001_0001.BRAW",
    "format_family": "braw",
    "frame_count": 1017,
    "duration_seconds": 42.375,
    "fps_num": 24000,
    "fps_den": 1001,
    "start_timecode": "01:00:00:00"
  },
  "captures": [
    {
      "label": "Start",
      "requested_ratio": 0.0,
      "requested_frame_index": 0,
      "requested_seconds": null,
      "actual_frame_index": 0,
      "actual_seconds": 0.0,
      "actual_timecode": "01:00:00:00",
      "actual_timecode_source": "native_adapter",
      "image_path_temp": "/tmp/frameproof/session-123/start.png",
      "duplicate_of": null,
      "status": "success",
      "warnings": [],
      "errors": []
    }
  ],
  "metadata_raw": {}
}
```

Canonical error response envelope:

```json
{
  "request_id": "uuid-string",
  "ok": false,
  "adapter_name": "r3d_adapter",
  "status": "dependency_missing",
  "warnings": [],
  "errors": [
    {
      "code": "dependency_missing",
      "message": "RED SDK runtime not found",
      "detail": {
        "required_path": "/Applications/FrameProof/native/r3d_adapter"
      }
    }
  ]
}
```

Envelope rules:

- `request_id` must round-trip.
- `stdout` must contain valid JSON on both success and structured failure.
- `stderr` may carry diagnostic logs but must not be the only error carrier.
- Unknown fields are allowed only under `metadata_raw` or `detail`.

## Status And Error Semantics

Clip-level statuses:

| Status | Meaning | Recoverable |
|---|---|---|
| `success` | probe and all requested captures succeeded | yes |
| `partial_success` | probe succeeded, at least one capture failed or fell back materially | yes |
| `probe_failed` | clip metadata could not be produced | yes |
| `decode_failed` | one or more requested frames could not be decoded | yes |
| `unsupported_format` | no adapter supports the candidate | yes |
| `dependency_missing` | required tool or SDK path is unavailable | yes |
| `metadata_incomplete` | required output can proceed with warnings but metadata is incomplete | yes |
| `skipped_duplicate` | logical clip or capture slot was intentionally preserved but did not perform a unique decode | yes |

Batch-level fatal conditions:

- output path not writable
- renderer fatal error
- explicit user cancel
- zero processable files because all relevant dependencies are missing

Canonical error codes:

- `dependency_missing`
- `probe_failed`
- `decode_failed`
- `invalid_response`
- `timeout`
- `unsupported_format`
- `metadata_incomplete`
- `output_write_failed`
- `renderer_failed`

## Adapter Resolution Rules

- Standard video extensions default to the FFmpeg adapter.
- `.braw` resolves to the `BRAW` adapter.
- `.r3d` resolves to the R3D adapter, with logical grouping handled before probe.
- `.ari` and ARRIRAW `.mxf` resolve to the ARRIRAW adapter.
- Unsupported candidates must still produce a deterministic `unsupported_format` record rather than disappearing from the batch.

## Dependency Contract

`is_available()` and dependency inspection must distinguish:

| State | Meaning |
|---|---|
| `available` | required tool path is callable |
| `configured_missing` | configured path is absent or not executable |
| `not_configured` | adapter requires a path the user has not configured |
| `runtime_error` | tool exists but version or startup check failed |

GUI and CLI surfaces use this contract to disable only the affected formats rather than stopping the whole app.

## Test Expectations

Stage 3 tests should lock these API properties:

- `CapturePoint` slot ordering remains stable for `middle_count` 0 to 3.
- planner preserves duplicate-collapsed slots on very short clips.
- raw JSON envelopes serialize and validate required fields.
- adapter error mapping produces normalized codes and statuses.
- timecode source labels survive round-trip into `CapturePoint`.
- `BRAW` and other RAW adapters are represented only as contracts and dependency states in Stage 3, not as fake implementations.
