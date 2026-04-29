# UI Specification

This document defines the v1 user surfaces for Frame Proof. The UI must stay thin: CLI and GUI are both clients of the same shared scan, probe, capture, and reporting services.

## Product Surfaces

- CLI for scripted and batch use.
- PySide6 desktop GUI for operator-driven review and export.
- PDF output in two modes: `Layout B` by default and `Layout A` when the detailed-report option is selected.

## Interaction Principles

- Default to the smallest truthful surface that exposes the shared pipeline.
- Show dependency gaps without blocking unrelated formats.
- Preserve requested-versus-actual capture facts everywhere.
- Treat failure as visible state, not an exception path hidden from the user.
- Keep report output readable first, dense second. Density may adapt, but label fidelity cannot.

## CLI Specification

Core command shape:

```bash
frameproof \
  --input "/Volumes/Footage/Day01" \
  --recursive \
  --middle-count 3 \
  --layout contact_sheet \
  --output "/Exports/FrameProof_Project_20260424.pdf" \
  --csv "/Exports/FrameProof_Project_20260424.csv" \
  --json "/Exports/FrameProof_Project_20260424.json"
```

Detailed mode with still export:

```bash
frameproof \
  --input "/Volumes/Footage/Day01" \
  --recursive \
  --middle-count 2 \
  --layout detail \
  --export-stills \
  --stills-dir "/Exports/stills" \
  --output "/Exports/FrameProof_Project_20260424_detail.pdf"
```

CLI requirements:

- `--layout contact_sheet` maps to `Layout B`.
- `--layout detail` maps to `Layout A`.
- `--middle-count` accepts `0`, `1`, `2`, `3`.
- default output behavior writes PDF plus CSV and JSON manifests.
- default still-export behavior is off.
- stdout should summarize progress and final counts.
- non-zero exit is reserved for fatal batch-stop conditions, not ordinary per-file failures.

## GUI Screen Inventory

### Main Screen

Required controls:

- source files picker
- source folder picker
- include subfolders toggle, default on
- output folder or output PDF picker
- project name field
- middle frame count selector
- layout selector with `Contact Sheet (Layout B)` default and `Detailed File Report (Layout A)` secondary
- export still PNGs toggle, default off
- include CSV manifest toggle, default on
- include JSON manifest toggle, default on
- failed files section toggle, default on
- start button
- cancel button
- progress table

Stage 5 presentation notes:

- The main window may add non-destructive summary surfaces such as a session overview or run-readiness summary, but it must not replace or remove the required control set above.
- Source/output guidance should explicitly warn when the chosen PDF destination sits inside a selected source tree.
- Success, partial, cancel, and invalid-settings states must stay textually explicit in the banner/detail area.

### Dependency Check Screen

Purpose:

- show availability of FFmpeg, FFprobe, MediaInfo, `BRAW` adapter, R3D adapter, and ARRI Reference Tool CMD
- let the user set or correct tool paths
- warn that missing RAW dependencies disable only the affected format families

Required states:

- available
- configured path missing
- not configured
- runtime startup failure

Stage 5 presentation notes:

- Long configured or resolved paths must remain scannable without changing the required state wording.
- The dialog may add usage-scoping copy such as which format family a dependency affects, but it must not reinterpret dependency truth.

### Settings Surface

This can be a dedicated screen or a modal. It must expose:

- tool and adapter paths
- last used output folder
- report defaults
- privacy option for full-path display in PDFs

## Progress Table

Required columns:

| Column | Meaning |
|---|---|
| `Clip` | clip or logical clip name |
| `Format` | `standard`, `braw`, `r3d`, `arriraw` |
| `Probe` | waiting, running, success, fail |
| `Capture` | waiting, running, success, partial, fail |
| `PDF` | included, skipped, failed |
| `Warning` | short warning summary |

Behavior:

- rows appear as soon as candidates are grouped
- status updates stream without reordering rows
- the cancel action prevents new work from starting and allows in-flight clip work to terminate safely
- partial-success rows remain visually distinct from full success

## Shared Screen States

### Empty State

Shown before input is selected.

- explain accepted file and folder sources
- explain that `Layout B` is the default report mode
- show that PNG export is optional and off by default

### Loading State

Shown during scan, dependency checks, probe, capture, and render.

- stage-specific progress text
- clip counts processed and remaining
- cancel affordance

### Error State

Required classes:

- invalid settings or output path
- dependency missing for one or more formats
- per-file probe failure
- per-file decode failure
- fatal renderer failure

Rules:

- per-file errors stay attached to the clip row and the final failed section
- fatal errors stop the batch and preserve already collected diagnostics

### Success State

- show output file paths for PDF and manifests
- show counts for total clips, success, partial success, failed, skipped
- show a note when `actual_timecode` used fallback sources

## PDF Layout Specification

## `Layout B`

`Layout B` is the default contact-sheet report and must ship before `Layout A`.

Header content:

- project name
- source root or selected input summary
- generated timestamp
- total clips, success count, partial count, failed count
- `middle_count`

Clip block content:

- clip name
- compact timecode range line
- compact format line: format, resolution, fps, duration
- thumbnail strip for Start and End plus `Mid1` to `Mid3` as selected
- warning text or icon summary

Footer content:

- page number
- report filename
- preview-only disclaimer: not color-critical

Density policy:

| Frames per clip | Target density |
|---:|---|
| 2 | 6 clips per page |
| 3 | 4 clips per page |
| 4 | 3 clips per page |
| 5 | 2 to 3 clips per page |

Rules:

- automatic density is allowed, but thumbnail legibility must not drop below the minimum preview size target
- over-dense pages must spill to a new page instead of shrinking labels into unreadability
- failed or partial clips may appear in the main report if probe succeeded enough to identify the clip
- the footer disclaimer must remain visible on every rendered page

## `Layout A`

`Layout A` is the detailed per-clip report variant.

Page content:

- clip title
- source path, with privacy setting respected
- metadata table
- 2 to 5 capture frames
- per-frame detail beneath or beside each thumbnail:
  `label`, `requested_ratio`, `requested frame/time`, `actual frame/time`, `actual timecode`
- warnings and errors section
- compact raw metadata appendix or summary

Rules:

- `Layout A` uses the same `ReportItem` and `CapturePoint` data as `Layout B`
- `Layout A` must not invent or recompute capture positions
- if path privacy is enabled, the user still needs enough file identity to distinguish clips
- warnings, errors, and timecode fallback notes must remain visible without forcing the reader to inspect thumbnails alone

## Visual Density And Imagery

- `Layout B` thumbnail sources: approximately 360 to 480 px
- `Layout A` thumbnail sources: approximately 720 to 1080 px
- PDF preview frames remain PNG-based
- full-resolution RAW frames must not be embedded directly in PDF

## Design Tokens Draft

These are draft tokens for Stage 5 refinement, but Stage 4 implementations should use them as the first stable naming set.

### Color

| Token | Value | Use |
|---|---|---|
| `color.bg.canvas` | `#F3F1EA` | app window and report margin tone |
| `color.bg.panel` | `#FBFAF7` | cards, settings sections |
| `color.text.primary` | `#1F2328` | main text |
| `color.text.muted` | `#5D6470` | secondary text |
| `color.border.default` | `#C9C2B8` | table and panel borders |
| `color.state.success` | `#1E7A46` | success indicators |
| `color.state.warning` | `#A35A00` | warnings and fallback labels |
| `color.state.error` | `#B42318` | failures |
| `color.state.info` | `#1D5F8C` | running and informational state |

### Typography

| Token | Value | Use |
|---|---|---|
| `font.family.ui` | `"IBM Plex Sans", "Noto Sans KR", sans-serif` | GUI |
| `font.family.report` | `"Source Serif 4", "Noto Serif KR", serif` | PDF titles and metadata emphasis |
| `font.size.body` | `10pt` | report body |
| `font.size.small` | `8.5pt` | secondary metadata |
| `font.size.title` | `16pt` | report title |
| `font.weight.medium` | `500` | labels |
| `font.weight.bold` | `700` | titles and totals |

## Visual Verification Artifacts

- Stage 5 verification uses repository-native artifacts under `artifacts/stage-05/`.
- `python scripts/generate_visual_artifacts.py` must generate deterministic `Layout B` and `Layout A` sample PDFs.
- When the local Qt runtime can render offscreen, the same command should also generate representative GUI screenshots for empty, partial, error, and dependency-dialog states.
- A browser harness is optional only if it exists without adding new product-facing architecture; Stage 5 does not require Playwright when the product surface remains the native PySide6 desktop app.

### Spacing And Sizing

| Token | Value |
|---|---|
| `space.1` | `4px` |
| `space.2` | `8px` |
| `space.3` | `12px` |
| `space.4` | `16px` |
| `space.5` | `24px` |
| `radius.card` | `8px` |
| `thumb.layout_b.min_width` | `96px` |
| `thumb.layout_a.min_width` | `180px` |

## Privacy And Safety UX

- the GUI must expose a hide-full-paths option for shareable PDFs
- the app must never imply that source files are modified
- still-export paths must be sanitized before write
- output inside the source tree is allowed but should show a caution note

## Stage Mapping

| UI requirement | Delivery stage |
|---|---|
| CLI argument shape and batch summary | Stage 4A |
| `Layout B` PDF | Stage 4A |
| failure section and PNG export UX | Stage 4C |
| `Layout A` PDF | Stage 4C |
| PySide6 GUI screens and progress table | Stage 4D |
| token cleanup, visual polish, accessibility pass | Stage 5 |
