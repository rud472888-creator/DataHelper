# Data Inventory

This document defines the durable data model for Frame Proof v1. Stage 3 should implement these schemas directly, and later stages must reuse them instead of inventing new per-feature records.

## Normalized Entities

- `ClipCandidate`: pre-probe logical input record.
- `ClipInfo`: normalized clip metadata after probe.
- `CapturePoint`: one requested capture slot with requested and actual positions.
- `ReportItem`: one clip plus captures, warnings, and errors for output layers.
- `ManifestRow`: flattened row model derived from `ReportItem`.
- `BatchSummary`: aggregate counters for CLI, GUI, and PDF headers.

## `ClipCandidate`

| Field | Type | Null | Notes |
|---|---|---|---|
| `candidate_id` | `str` | no | batch-local stable ID |
| `source_path` | `str` | no | canonical primary file path |
| `part_files` | `list[str]` | no | ordered logical-clip members, empty for single-file clips |
| `file_size_bytes` | `int` | yes | primary file size before probe |
| `modified_time` | `float` | yes | batch-local candidate key support |
| `format_hint` | `str` | yes | extension-derived hint before resolver |

Candidate keys:

- preferred synthetic key: `candidate_id`
- natural batch key: `source_path + file_size_bytes + modified_time`
- logical R3D batch key: first `source_path` + joined `part_files`

## `ClipInfo`

| Field | Type | Null | Notes |
|---|---|---|---|
| `clip_id` | `str` | no | primary durable application key |
| `clip_name` | `str` | no | display file or logical clip name |
| `logical_clip_name` | `str` | yes | grouped display name for multi-part clips |
| `source_path` | `str` | no | canonical primary source path |
| `part_files` | `list[str]` | no | ordered logical group members |
| `format_family` | `str` | no | `standard`, `braw`, `r3d`, `arriraw` |
| `container` | `str` | yes | `MOV`, `MXF`, `R3D`, `BRAW`, `ARI` |
| `codec` | `str` | yes | codec string or RAW family label |
| `file_size_bytes` | `int` | yes | size of primary file |
| `duration_seconds` | `float` | yes | required unless `frame_count` is present |
| `frame_count` | `int` | yes | preferred planner input |
| `fps_num` | `int` | yes | nullable for VFR or unknown-rate inputs |
| `fps_den` | `int` | yes | nullable for VFR or unknown-rate inputs |
| `width` | `int` | yes | display and PDF metadata |
| `height` | `int` | yes | display and PDF metadata |
| `camera_make` | `str` | yes | optional metadata |
| `camera_model` | `str` | yes | optional metadata |
| `reel` | `str` | yes | optional metadata |
| `camera_id` | `str` | yes | optional metadata |
| `start_timecode` | `str` | yes | nullable when missing |
| `end_timecode` | `str` | yes | nullable or calculated later |
| `timecode_source` | `str` | yes | `native_adapter`, `container_metadata`, `calculated`, `elapsed_fallback` |
| `tc_drop_frame` | `bool` | yes | null when unknown |
| `metadata_raw` | `dict[str, object]` | no | raw adapter payload preserved for debugging |

Candidate keys:

- primary key: `clip_id`
- natural candidate key for single-file clips: `source_path + file_size_bytes`
- logical candidate key for grouped clips: `logical_clip_name + first(source_path) + len(part_files)`

Nullability rules:

- `frame_count` and `duration_seconds` must not both be null.
- `fps_num` and `fps_den` are nullable together, not independently.
- `start_timecode` may be null without failing the clip.
- `metadata_raw` is never null, even if empty.

## `CapturePoint`

`CapturePoint` is the core requested-versus-actual record and must remain the same across PDF, manifest, and GUI progress reporting.

| Field | Type | Null | Notes |
|---|---|---|---|
| `label` | `str` | no | `Start`, `Mid1`, `Mid2`, `Mid3`, `End` |
| `requested_ratio` | `float` | no | 0.0 to 1.0 inclusive |
| `requested_frame_index` | `int` | yes | frame-count path |
| `requested_seconds` | `float` | yes | duration fallback path |
| `actual_frame_index` | `int` | yes | final decoder-selected frame |
| `actual_seconds` | `float` | yes | final decoder-selected timestamp |
| `actual_timecode` | `str` | yes | final display timecode or null before fallback |
| `actual_timecode_source` | `str` | yes | `native_adapter`, `calculated`, `container_metadata`, `elapsed_fallback` |
| `image_path_temp` | `str` | yes | staging PNG path |
| `image_path_exported` | `str` | yes | final exported PNG path when enabled |
| `duplicate_of` | `str` | yes | another slot label for short-clip collapse |
| `status` | `str` | no | capture status |
| `warnings` | `list[str]` | no | never null |
| `errors` | `list[str]` or `list[object]` | no | never null |

Candidate keys:

- composite application key: `clip_id + label`
- flattened manifest key: `clip_name + label + requested_ratio`

Nullability rules:

- At least one of `requested_frame_index` or `requested_seconds` must be present.
- At least one of `actual_frame_index`, `actual_seconds`, or `duplicate_of` must be present unless `status=decode_failed`.
- `image_path_temp` is nullable until capture succeeds.
- `image_path_exported` is null when `export_stills=false`.

## `ReportItem`

| Field | Type | Null | Notes |
|---|---|---|---|
| `clip` | `ClipInfo` | no | normalized clip |
| `captures` | `list[CapturePoint]` | no | ordered Start-to-End list |
| `status` | `str` | no | clip-level summary |
| `warnings` | `list[str]` | no | aggregated warnings |
| `errors` | `list[object]` | no | aggregated errors |

Candidate keys:

- primary: `clip.clip_id`

Rules:

- `status=success` only when probe and every capture slot succeeded without clip-level downgrade.
- `status=partial_success` when at least one capture slot failed but the clip still produced output.
- `warnings` and `errors` aggregate clip-level and capture-level information without deleting the per-slot detail.

## `ManifestRow`

CSV and JSON manifest records are flattened from `ReportItem`. Every capture slot becomes one row.

| Column | Source | Null | Notes |
|---|---|---|---|
| `clip_id` | `ClipInfo.clip_id` | no | recommended to add beyond the source spec for durable joins |
| `clip_name` | `ClipInfo.clip_name` | no | required |
| `logical_clip_name` | `ClipInfo.logical_clip_name` | yes | useful for grouped R3D clips |
| `source_path` | `ClipInfo.source_path` | no | may be hidden in shared PDF mode, not in manifest by default |
| `format_family` | `ClipInfo.format_family` | no | required |
| `adapter_name` | adapter response | no | required |
| `capture_label` | `CapturePoint.label` | no | required |
| `requested_ratio` | `CapturePoint.requested_ratio` | no | required |
| `requested_frame_index` | `CapturePoint.requested_frame_index` | yes | required for frame-count path |
| `requested_seconds` | `CapturePoint.requested_seconds` | yes | required for duration fallback path |
| `actual_frame_index` | `CapturePoint.actual_frame_index` | yes | required when known |
| `actual_seconds` | `CapturePoint.actual_seconds` | yes | required when known |
| `actual_timecode` | `CapturePoint.actual_timecode` | yes | `N/A` may be rendered later while raw value stays null |
| `actual_timecode_source` | `CapturePoint.actual_timecode_source` | yes | useful for fallback visibility |
| `image_path` | exported or temp path policy | yes | exported path only when still export is on |
| `status` | `CapturePoint.status` or clip summary | no | required |
| `warnings` | joined warning text | yes | CSV-friendly serialization |
| `errors` | joined error text | yes | CSV-friendly serialization |

## Status Inventory

Clip-level and capture-level statuses share the same vocabulary where possible:

| Status | Scope | Meaning |
|---|---|---|
| `success` | clip, capture | completed as requested |
| `partial_success` | clip | some capture slots failed or degraded |
| `probe_failed` | clip | metadata probe failed |
| `decode_failed` | clip, capture | frame decode failed |
| `unsupported_format` | clip | no supported adapter |
| `dependency_missing` | clip | required tool or SDK missing |
| `metadata_incomplete` | clip, capture | output can proceed with missing metadata |
| `skipped_duplicate` | capture | slot preserved but shares another slot’s actual frame |

## Timecode Source Inventory

| Value | Meaning |
|---|---|
| `native_adapter` | direct per-frame or clip metadata from the adapter |
| `calculated` | derived from start timecode plus frame offset |
| `container_metadata` | fallback from container or stream metadata |
| `elapsed_fallback` | elapsed duration display when timecode is unavailable |

## Schema Invariants

- `CapturePoint` ordering must always be `Start`, `Mid1`, `Mid2`, `Mid3`, `End`, omitting mids above the selected `middle_count`.
- Requested slots remain in output even when multiple labels map to the same actual frame.
- PDF, CSV, and JSON must all reflect the same `CapturePoint` facts.
- A batch must never silently drop a failed candidate; every scanned candidate ends as a `ReportItem` or a documented skip record.

## Adapter-To-Normalized Mapping

| Source field family | Normalized field |
|---|---|
| vendor or ffprobe clip identifier | `clip_id` or input to deterministic ID generation |
| file basename or logical clip title | `clip_name`, `logical_clip_name` |
| primary media path | `source_path` |
| grouped file list | `part_files` |
| duration metadata | `duration_seconds` |
| total frames | `frame_count` |
| frame rate numerator and denominator | `fps_num`, `fps_den` |
| raster width and height | `width`, `height` |
| clip start TC or per-frame TC | `start_timecode`, `actual_timecode` |
| raw metadata dump | `metadata_raw` |

## Validation Targets For Stage 3

- schema constructors reject records where both `frame_count` and `duration_seconds` are null
- `CapturePoint` requires requested position data
- duplicate-collapsed short clips keep five rows at `middle_count=3`
- manifest rows preserve `CapturePoint` values without recomputing them
- `CapturePoint` and `CaptureStatus` names match the adapter API contract exactly
