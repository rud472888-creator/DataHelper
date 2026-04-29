# Stage 04C Plan

- lane: dev
- stage: stage-04C
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_4b_pass_verified: yes
- risk_level: moderate
- next_recommended_prompt: `[Stage 4C-Implement]`

## Gate Verification

- `docs/qa.md` records `latest_stage: stage-04B`, `latest_verdict: PASS`, `latest_gate: passed`, and `next_recommended_prompt: [Stage 4C-Plan]`.
- `docs/stages/stage-04B-qa.md` records `verdict: PASS`, `gate: passed`, and `stage_4c_status: unblocked-by-qa`.
- At session start, `docs/stage.md` recorded `current_stage: stage-04C`, `current_subphase: plan`, `last_result: stage-04B-qa-pass`, `qa_gate: pass`, and `implementation_allowed: false`.
- The required repository files for this session were read explicitly before planning:
- `AGENTS.md`
- `docs/stage.md`
- `docs/qa.md`
- `docs/architecture.md`
- `docs/data-inventory.md`
- `docs/ui-spec.md`
- `docs/stages/stage-04B-qa.md`
- The required validation commands for this phase were executed:
- `cat docs/qa.md`
- `grep -R "Layout A" docs/ui-spec.md`
- `grep -R "Export still" docs/ui-spec.md docs/data-inventory.md`
- The `Layout A` grep returned the expected UI-spec hits. The exact `Export still` grep returned no literal matches in those two docs, so still-export acceptance details were grounded using the already-declared `export_stills` / `stills_dir` settings surface plus the source spec sections for PNG export and sanitize rules.
- Stage 4C planning is therefore legal. This phase remains docs-only and must stop before implementation.

## Sprint Goal

- Add the detailed `Layout A` PDF renderer as a variant over the same `ReportItem` and `CapturePoint` data already used by `Layout B`.
- Add optional PNG still export that remains OFF by default, writes only when explicitly enabled, and records exported paths back into the shared report model.
- Tighten filename safety and determinism for exported stills with sanitize, collision handling, and long-name protection.
- Improve failed and partial clip reporting so PDF and manifests tell the same truthful story for success, degraded, and failed items.
- Preserve the Stage 4A and 4B shared pipeline shape. Stage 4C extends renderer and output behavior; it does not introduce a second reporting architecture.

## Non-Scope

- No GUI work.
- No new adapter capabilities, no RAW SDK scope changes, and no capture-planner rule changes.
- No recomputation of capture points inside the renderer or manifests.
- No change to the default report mode: `Layout B` remains the default.
- No change to the default still behavior: `export_stills` remains `false` unless explicitly requested.
- No new runtime dependencies are planned for this sprint.

## Current Baseline

- `src/frameproof/config/settings.py` already defines `ReportLayout.CLIP_DETAIL`, `output.export_stills`, and `output.stills_dir`.
- `src/frameproof/cli.py` currently exposes only `--layout contact_sheet`; it does not yet wire `--layout detail`, `--export-stills`, or `--stills-dir`.
- `src/frameproof/render/pdf_renderer.py` currently renders only `Layout B` plus a basic trailing failed/partial section.
- `src/frameproof/output/manifest_writer.py` already serializes requested and actual capture fields plus `image_path`, but no Stage 4A code populates exported PNG paths yet.
- `src/frameproof/core/report_builder.py` builds `CapturePoint.image_path_exported`, but only through the optional value passed into `CapturePoint.from_capture_result`; Stage 4C must supply that value from a real still-export step.

## Path And Module Decisions

- Keep the real repository package layout that Stage 4A established:
- PDF rendering stays in `src/frameproof/render/pdf_renderer.py`.
- Manifest writing stays in `src/frameproof/output/manifest_writer.py`.
- Stage 4C should add the still exporter under `src/frameproof/output/still_exporter.py` rather than introducing a new `rendering/` package.
- The data-flow rule for Stage 4C is:
- capture temp PNGs are produced exactly as they are today
- optional still export copies or promotes those PNGs into `stills_dir`
- exported PNG paths are written back into the shared `CapturePoint`
- PDF and manifest outputs consume that same `CapturePoint` data without recomputing positions
- If Stage 4C needs a narrow report-builder extension, prefer adding an explicit exported-path input to `build_report_item()` or a small helper around it instead of mutating adapters.

## Stage 4C Module Scope

### 1. CLI and settings wiring

- `src/frameproof/cli.py`
- `src/frameproof/config/settings.py`
- `tests/test_cli.py`
- `tests/unit/config/test_settings.py`

Planned behavior:

- Extend the CLI to accept:
- `--layout detail`
- `--export-stills`
- `--stills-dir PATH`
- Keep `contact_sheet` as the default layout and `detail` as the explicit Layout A selection.
- Keep PNG export OFF by default. A run that does not pass `--export-stills` must not create a stills directory or exported PNG files.
- Keep `stills_dir` explicit when still export is enabled. The current `OutputSettings` requirement stays in force rather than inventing a silent default folder.
- Ensure CLI help and settings validation describe the new flags truthfully and do not imply GUI support.

### 2. Still exporter and filename safety

- `src/frameproof/output/still_exporter.py` (new)
- `src/frameproof/output/__init__.py`
- `src/frameproof/cli.py`
- `src/frameproof/core/report_builder.py`
- `tests/unit/output/test_still_exporter.py` (new)

Planned behavior:

- The still exporter consumes existing clip identity plus capture temp PNG paths and writes exported PNGs only when `output.export_stills` is `true`.
- Export layout should follow the source spec’s per-clip directory pattern under the configured `stills_dir`, for example:
- `<stills_dir>/<sanitized_clip_dir>/<sanitized_clip_name>__<label_token>__<position_token>.png`
- `label_token` should be deterministic and lowercase, for example `start`, `mid1`, `mid2`, `mid3`, `end`.
- `position_token` should prefer actual timecode when present and otherwise fall back to stable actual-position tokens such as frame index or seconds, so duplicate labels do not collapse into ambiguous names.
- Sanitize rules must cover both directory names and filenames:
- remove path separators
- replace colon `:` with `_`
- replace drop-frame semicolon `;` with `_df_` or another deterministic safe token
- collapse other unsafe filename characters to `_`
- prevent path traversal
- Collision handling must follow the source spec shape:
- first name wins with no suffix
- later collisions append `_001`, `_002`, and so on before `.png`
- Overlong clip-derived names must receive a stable hash suffix before the extension so exports stay portable on common filesystems.
- Decode-failed captures and captures with no temp image must not create fake PNGs. Their exported path remains null.
- The still exporter must return exported paths in a structure that can be written back into `CapturePoint.image_path_exported` without touching adapter code.

### 3. Layout A renderer

- `src/frameproof/render/pdf_renderer.py`
- `src/frameproof/render/__init__.py`
- `tests/unit/render/test_pdf_renderer.py` (new)

Planned behavior:

- Add a renderer entrypoint that dispatches on `settings.report.layout` instead of hardcoding `Layout B`.
- `Layout A` must render one page per clip when probe data exists, and each page must include:
- clip title
- source path with `path_display` respected
- metadata table
- 2 to 5 capture frames
- per-frame detail values taken directly from `CapturePoint`
- warnings and errors
- compact raw metadata summary or appendix
- `Layout A` must not invent or recompute capture positions. It should display the same requested and actual values already stored in `CapturePoint`.
- Layout A should tolerate partial clips by rendering the captures that exist and showing decode failures inline rather than dropping the clip.
- Probe-only failures that have no usable captures should remain visible through the trailing failed/partial section rather than forcing a fake detailed page.
- Layout B remains intact and remains the default. Stage 4C may refactor shared PDF helpers only where that simplifies parity between the two layouts.

### 4. Failed and partial sections

- `src/frameproof/render/pdf_renderer.py`
- `src/frameproof/core/report_builder.py`
- `tests/unit/render/test_pdf_renderer.py`

Planned behavior:

- Preserve a dedicated trailing `Failed / Partial Clips` PDF section for both layouts.
- Upgrade the section from the current brief note list into a truthful summary that can cover:
- clip status
- adapter name
- first failing capture labels when relevant
- warning or error messages that explain degraded output
- Clips with `partial_success`, `probe_failed`, `decode_failed`, `dependency_missing`, and `metadata_incomplete` should all be eligible for this section when they are not fully clean successes.
- The failed section must not duplicate fabricated data. It summarizes the existing `ReportItem` state only.

### 5. Manifest and PDF parity improvements

- `src/frameproof/output/manifest_writer.py`
- `src/frameproof/core/report_builder.py`
- `tests/unit/output/test_manifest_writer.py` (new)
- `tests/integration/test_cli_standard_pipeline.py`

Planned behavior:

- Keep CSV and JSON manifests derived from the same final `ReportItem` collection used by the PDF renderer.
- Ensure manifest rows and JSON clip payloads preserve the exact Stage 4C capture facts needed for parity:
- `requested_ratio`
- `requested_frame_index`
- `requested_seconds`
- `actual_frame_index`
- `actual_seconds`
- `actual_timecode`
- `actual_timecode_source`
- `image_path`
- `status`
- `warnings`
- `errors`
- When still export is OFF, manifest `image_path` must stay null.
- When still export is ON, manifest `image_path` must point at the exported PNG path, not the temporary staging path.
- Clip-level failures with no captures must remain represented in the manifests rather than disappearing because they lack frame rows.
- Stage 4C should avoid adding manifest-only semantics. If a new field is truly required, it must be justified by PDF parity and surfaced consistently in both CSV and JSON.

## Planned Implementation Touched Files

- `src/frameproof/cli.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/core/report_builder.py`
- `src/frameproof/output/__init__.py`
- `src/frameproof/output/manifest_writer.py`
- `src/frameproof/output/still_exporter.py`
- `src/frameproof/render/__init__.py`
- `src/frameproof/render/pdf_renderer.py`
- `tests/test_cli.py`
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/unit/config/test_settings.py`
- `tests/unit/output/test_manifest_writer.py`
- `tests/unit/output/test_still_exporter.py`
- `tests/unit/render/test_pdf_renderer.py`
- `docs/stages/stage-04C-implement.md`
- `docs/reports/dev/stage-04C-handoff.md`
- `docs/implement.md`

## Acceptance Criteria For Stage 4C Implement

- The CLI accepts `--layout detail`, `--export-stills`, and `--stills-dir`, while `contact_sheet` remains the default layout.
- `Layout A` generates a detailed per-clip PDF page that shows clip metadata, 2 to 5 capture frames, per-frame requested and actual facts, and clip warnings or errors using the existing `ReportItem` data.
- `Layout A` does not recompute capture points or create a second report pipeline.
- `export_stills` remains OFF by default. A default run writes PDF and manifests only and does not create an export-stills directory.
- When `export_stills` is enabled, `stills_dir` is required and exported PNGs are written beneath it using sanitized, deterministic paths.
- Sanitization removes unsafe path characters, handles drop-frame semicolons safely, prevents path traversal, and preserves enough identity to distinguish clips.
- Filename collisions are resolved with `_001`, `_002`, and so on without overwriting an earlier still.
- Overlong sanitized names receive a stable hash suffix so still export remains portable.
- Failed and partial clips are listed in a dedicated PDF section for both layouts with truthful status and reason summaries.
- CSV and JSON manifests preserve the same requested and actual capture facts shown in Layout A, including exported `image_path` when still export is enabled.
- Clip-level failures with no captures remain visible in manifests and in the PDF failed section.
- RAW adapters remain untouched except for consuming their existing normalized capture output through the shared report and export flow.

## Test And Validation Plan

### Unit coverage

- `tests/test_cli.py`
- CLI help exposes `--layout {contact_sheet,detail}`, `--export-stills`, and `--stills-dir`.
- CLI rejects contradictory still-export configuration truthfully.
- `tests/unit/config/test_settings.py`
- default `export_stills` stays false
- `stills_dir` remains required when export is enabled
- `detail` layout parses cleanly
- `tests/unit/output/test_still_exporter.py`
- sanitize path separators, colons, and drop-frame semicolons
- collision suffix behavior uses `_001` / `_002`
- long-name hash suffix behavior is deterministic
- no export occurs for decode-failed or image-missing captures
- `tests/unit/render/test_pdf_renderer.py`
- `Layout A` renders a non-empty PDF
- failed/partial section is present when expected
- Layout dispatch stays on `Layout B` by default
- `tests/unit/output/test_manifest_writer.py`
- exported image paths remain null when still export is off
- exported image paths appear when still export is on
- JSON and CSV serialization preserve the same capture-point fields used by the PDF detail view

### Integration coverage

- Extend `tests/integration/test_cli_standard_pipeline.py` to cover:
- `--layout contact_sheet`
- `--layout detail`
- `--export-stills` off
- `--export-stills --stills-dir <tmp>`
- `middle_count 0` and `middle_count 3`
- Assert generated manifest rows, JSON clip payloads, and exported still paths stay internally consistent.
- If FFmpeg is available, smoke-test:
- `--layout contact_sheet`
- `--layout detail`
- `--export-stills`
- The still-export smoke should verify that the stills directory exists only when explicitly enabled.

### Required validation commands for implement phase

- `python -m frameproof --help`
- `python -m pytest`
- `ruff check .`
- `mypy src`

## Risks And Watchpoints

- The main product risk is parity drift: Layout A, Layout B, CSV, and JSON must all reflect the same `CapturePoint` facts after still export is applied.
- Filename safety can easily become platform-specific. The sanitize logic should stay deterministic and test-driven instead of depending on the local filesystem to reject bad names.
- Still-export path policy must not leak temporary staging paths into final manifests when export is disabled.
- Partial and failed clips are easy to under-report. Stage 4C must keep them visible even when probe succeeded only partially or capture failed after probe.
- The implementation should resist turning Layout A into a separate pipeline. Shared helpers are acceptable; duplicate model transformations are not.

## Validation Commands Run For This Plan Phase

- `cat docs/qa.md`
- `grep -R "Layout A" docs/ui-spec.md`
- `grep -R "Export still" docs/ui-spec.md docs/data-inventory.md`
- `rg -n "Layout A|detail|PNG|still|sanitize|failed|partial|collision|manifest" docs/frameproof_tech_spec_ko.md`

## Touched Files In This Plan Phase

- `docs/stages/stage-04C-plan.md`
- `docs/stage.md`

## Exact Next Prompt

`[Stage 4C-Implement]`

## Outcome

Stage 4C planning is complete. The next fresh Dev session should implement Layout A, optional still export, sanitize and collision handling, failed and partial reporting, and manifest/PDF parity as defined here, write the implementation and handoff artifacts, and stop before QA or Stage 4D work.
