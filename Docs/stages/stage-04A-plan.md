# Stage 04A Plan

- lane: dev
- stage: stage-04A
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_3_pass_verified: yes
- risk_level: high
- next_recommended_prompt: `[Stage 4A-Implement]`

## Gate Verification

- `docs/qa.md` records `latest_stage: stage-03`, `latest_verdict: PASS`, `latest_gate: passed`, and `next_recommended_prompt: [Stage 4A-Plan]`.
- `docs/stages/stage-03-qa.md` records `verdict: PASS`, `gate: passed`, and `stage_4a_status: unblocked-by-qa`.
- At session start, `docs/stage.md` recorded `current_stage: stage-04A`, `current_subphase: plan`, `last_result: stage-03-qa-pass`, `qa_gate: pass`, and `implementation_allowed: true`.
- The required repo files for this session were read explicitly before planning: `AGENTS.md`, `docs/stage.md`, `docs/qa.md`, `docs/architecture.md`, `docs/api-contract.md`, `docs/data-inventory.md`, `docs/ui-spec.md`, and `docs/stages/stage-03-qa.md`.
- Stage 4A planning is therefore legal. This phase remains docs-only and must stop before implementation.

## Sprint Goal

- Implement the first real end-to-end media pipeline for standard video formats only.
- Cover recursive scan, baseline grouping, adapter resolution, FFprobe metadata probe, FFmpeg frame capture, Layout B PDF output, CSV/JSON manifest output, and CLI orchestration.
- Keep the pipeline truthful: use real FFprobe/FFmpeg behavior when tools are available, and emit normalized `dependency_missing`, `probe_failed`, `decode_failed`, or `metadata_incomplete` states when they are not.
- Defer RAW native adapter execution, GUI work, Layout A, and PNG still export persistence to later stages.

## Non-Scope

- No BRAW, R3D, or ARRIRAW native adapter client implementation in this sprint.
- No GUI screens, PySide6 work, or dependency-check UI.
- No Layout A detailed PDF mode.
- No still-export feature or `--export-stills` CLI path.
- No mock-only pipeline that bypasses FFprobe or FFmpeg.
- No second report pipeline or format-specific manifest schema.

## Dependency And Path Decisions

- Use `src/frameproof/render/pdf_renderer.py` for Stage 4A because the Stage 4A implement prompt names that path explicitly. Do not create both `render/` and `rendering/`; the Stage 2 architecture entry for `rendering/` should be treated as conceptual only.
- Keep `src/frameproof/output/manifest_writer.py` as the single manifest surface so CSV and JSON remain derived from one `ReportItem` collection.
- Stage 4A may add only the runtime dependencies already named by the source tech spec for this milestone:
- `reportlab` for real PDF generation
- `Pillow` for image sizing and layout-safe thumbnail handling
- No other new runtime dependencies are planned.

## Stage 4A Module Scope

### Extend existing configuration and CLI surfaces

- `src/frameproof/cli.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/settings.py`

Planned changes:

- Replace the bootstrap-only CLI with a real batch command path while preserving `--version`.
- Add Stage 4A CLI arguments for `--input`, `--recursive` / `--no-recursive`, `--middle-count`, `--layout`, `--output`, `--csv`, and `--json`.
- Limit `--layout` to `contact_sheet` in this sprint. Do not expose `detail` yet because Layout A is a Stage 4C deliverable.
- Extend settings models to accept explicit CSV and JSON output paths or derive them from the PDF path when omitted.
- Keep adapter-path configuration in the shared settings model so the ffmpeg adapter can resolve `ffmpeg`, `ffprobe`, and optional `mediainfo` paths without inventing a second config surface.

### Add input discovery and standard-format routing

- `src/frameproof/core/scanner.py`
- `src/frameproof/core/clip_grouper.py`
- `src/frameproof/core/adapter_resolver.py`

Planned behavior:

- Scanner expands files and folders, supports recursion, preserves deterministic path ordering, and filters to configured extensions.
- Stage 4A grouping stays conservative: one standard-video file becomes one logical clip. Do not add RAW multipart grouping logic here.
- Adapter resolver maps standard extensions such as `mov`, `mp4`, `mxf`, and `avi` to the FFmpeg adapter.
- RAW-family extensions may still be discovered by the scanner if configured, but Stage 4A must report them honestly as deferred / unsupported for this sprint instead of silently dropping them.

### Implement the standard adapter and runtime services

- `src/frameproof/adapters/__init__.py`
- `src/frameproof/adapters/ffmpeg_adapter.py`
- `src/frameproof/core/probe_service.py`
- `src/frameproof/core/capture_service.py`
- `src/frameproof/core/report_builder.py`

Planned behavior:

- `ffmpeg_adapter.py` owns real tool-path availability checks, FFprobe metadata extraction, optional MediaInfo fallback when configured and callable, and FFmpeg frame capture for standard video.
- `probe_service.py` runs adapter probe, maps tool and subprocess failures into normalized status/error records, and preserves raw metadata for later reporting.
- `capture_service.py` executes requested capture slots in order, writes staging thumbnails, and records requested-versus-actual capture facts without recomputing planner intent.
- `report_builder.py` converts clip metadata plus capture results into `ReportItem` objects and a `BatchSummary` that both the CLI summary and output writers can reuse.
- The existing Stage 3 `metadata_raw`, status vocabulary, timecode helpers, and capture planner remain the source of truth; Stage 4A must extend them, not bypass them.

### Implement output writers

- `src/frameproof/render/__init__.py`
- `src/frameproof/render/pdf_renderer.py`
- `src/frameproof/output/__init__.py`
- `src/frameproof/output/manifest_writer.py`

Planned behavior:

- `pdf_renderer.py` writes the real Layout B contact-sheet PDF only.
- The PDF renderer must include the required header summary, clip blocks, thumbnail strip, compact metadata line, warning summary, page footer, and preview-only disclaimer.
- `manifest_writer.py` writes CSV and JSON from the same `ReportItem` list used by the PDF renderer so QA can compare one normalized output model across all export types.
- Stage 4A should include partial and failed clip reporting in the main outputs when enough probe data exists to identify the clip.

### Add real integration coverage

- `tests/integration/conftest.py`
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/integration/test_dependency_missing.py`
- `tests/unit/core/test_scanner.py`
- `tests/unit/core/test_report_builder.py`
- `tests/unit/adapters/test_ffmpeg_adapter.py`
- update existing CLI tests in `tests/test_cli.py`

Planned behavior:

- Keep the Stage 1 and Stage 3 tests green.
- Add real CLI integration coverage for the standard pipeline when FFmpeg is available.
- Add explicit dependency-missing coverage when FFmpeg or FFprobe is absent or intentionally configured to invalid paths.
- Keep MediaInfo fallback mostly component-tested unless the tool is actually present in the environment.

## Planned Implementation Touched Files

- `src/frameproof/cli.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/settings.py`
- `src/frameproof/core/__init__.py`
- `src/frameproof/core/scanner.py`
- `src/frameproof/core/clip_grouper.py`
- `src/frameproof/core/adapter_resolver.py`
- `src/frameproof/core/probe_service.py`
- `src/frameproof/core/capture_service.py`
- `src/frameproof/core/report_builder.py`
- `src/frameproof/adapters/__init__.py`
- `src/frameproof/adapters/ffmpeg_adapter.py`
- `src/frameproof/render/__init__.py`
- `src/frameproof/render/pdf_renderer.py`
- `src/frameproof/output/__init__.py`
- `src/frameproof/output/manifest_writer.py`
- `tests/test_cli.py`
- `tests/integration/conftest.py`
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/integration/test_dependency_missing.py`
- `tests/unit/core/test_scanner.py`
- `tests/unit/core/test_report_builder.py`
- `tests/unit/adapters/test_ffmpeg_adapter.py`
- `docs/stages/stage-04A-implement.md`
- `docs/reports/dev/stage-04A-handoff.md`
- `docs/implement.md`

## Acceptance Criteria For Stage 4A Implement

- A standard-video input path can be processed through one CLI run that performs scan, grouping, probe, capture planning, capture, report build, PDF export, CSV export, and JSON export.
- The CLI accepts `--input`, `--recursive` / `--no-recursive`, `--middle-count`, `--layout contact_sheet`, `--output`, `--csv`, and `--json`, and rejects Stage 4C-only options honestly.
- Scanner output is deterministic and limited to configured extensions.
- Grouping stays one-file-per-clip for standard formats and does not introduce fake RAW grouping behavior.
- Standard extensions resolve to the FFmpeg adapter without creating a second adapter path for the same files.
- The FFmpeg adapter uses real `ffprobe` for metadata, real `ffmpeg` for capture, and MediaInfo only as an optional fallback when configured and available.
- The Stage 3 capture planner remains authoritative for slot selection and duplicate preservation.
- Capture results preserve requested and actual facts for every slot, including duplicate-collapsed short clips.
- Layout B PDF output contains the required header, clip blocks, thumbnails, compact metadata, warning visibility, page numbering, and preview-only disclaimer.
- CSV and JSON manifests are generated from the same `ReportItem` collection used by the PDF renderer.
- Per-file failures continue the batch unless a documented fatal stop condition is hit.
- Non-zero CLI exit codes are reserved for fatal batch-stop conditions or zero processable files because required standard-video dependencies are missing.
- Integration tests exercise real FFmpeg/FFprobe behavior when available, and dependency-missing behavior when not.

## Failure Handling Rules

### Fatal batch-stop conditions

- output PDF path or manifest path is not writable
- PDF renderer fails fatally and no valid document can be produced
- the user interrupts the batch from CLI execution
- zero processable files remain because the only relevant adapter dependency for this sprint (`ffprobe` and/or `ffmpeg`) is missing or unusable

Fatal behavior rules:

- return a non-zero exit code
- print a truthful batch-level failure summary
- preserve diagnostics gathered before the stop
- do not claim success just because scanning found files

### Non-fatal per-clip failures

- corrupt or unreadable container causing `probe_failed`
- missing or partial metadata that still allows degraded processing (`metadata_incomplete`)
- capture decode failure for one or more slots (`decode_failed`)
- RAW-family files discovered during this sprint but not implemented yet (`unsupported_format`)
- duplicate-preserved short-clip slots (`skipped_duplicate`)

Non-fatal behavior rules:

- continue processing remaining clips
- keep the clip visible in summary/manifests with normalized status
- downgrade clip status to `partial_success` when some captures fail but the clip still produces reportable output
- reserve exit code `0` for batches that completed without a fatal stop, even if some clips failed

## Test Fixture Strategy

- Do not commit large binary sample media to the repository for this sprint.
- Generate synthetic standard-video fixtures inside pytest temp directories with real FFmpeg commands when FFmpeg is callable.
- Keep generated fixtures short, deterministic, and cheap to decode so the suite stays fast.

Required synthetic fixture cases:

- a normal 2-second standard clip with stable fps for the happy-path CLI E2E test
- a very short clip that forces duplicate capture preservation at `middle_count=3`
- a clip with no trusted timecode so elapsed or calculated fallback behavior is visible
- a corrupt or empty `.mp4` file to assert `probe_failed`

Suggested generation approach:

- use FFmpeg `lavfi` sources such as `testsrc` or `color` to synthesize MP4 or MOV clips
- embed stable frame rate and, where practical, a start timecode for one fixture
- write outputs to pytest temp directories only

Fallback test strategy when tools are absent:

- dependency-missing integration tests must configure invalid `ffprobe` / `ffmpeg` paths and assert normalized `dependency_missing` handling
- the suite must not silently skip all Stage 4A integration coverage just because FFmpeg is missing
- optional MediaInfo integration may run only when `mediainfo` is callable; otherwise cover fallback decision logic in unit or component tests

## Validation Commands For Stage 4A Implement

- `python -m frameproof --help`
- `python -m pytest tests/unit tests/integration`
- `python -m pytest`
- `ruff check .`
- `mypy src`

If FFmpeg is installed, also run a real smoke flow similar to:

```bash
ffmpeg -y -f lavfi -i testsrc=size=320x180:rate=24 -t 2 /tmp/frameproof-stage4a-smoke.mp4
python -m frameproof \
  --input /tmp/frameproof-stage4a-smoke.mp4 \
  --middle-count 3 \
  --layout contact_sheet \
  --output /tmp/frameproof-stage4a-smoke.pdf \
  --csv /tmp/frameproof-stage4a-smoke.csv \
  --json /tmp/frameproof-stage4a-smoke.json
```

## Risks And Watchpoints

- The largest technical risk is external-tool truthfulness: FFprobe and FFmpeg do not always expose exact per-frame timecode or actual decode frame identity, so the adapter must preserve what is known and fall back honestly instead of fabricating precision.
- Stage 4A introduces the first runtime dependency-backed E2E flow. Missing tools must become normalized statuses, not unhandled subprocess exceptions.
- The repo currently has no runtime dependencies in `pyproject.toml`, but the source tech spec names `reportlab` and `Pillow` as required for PDF and image handling. Stage 4A implement should add only those two runtime dependencies if they are still absent.
- The CLI must not advertise Stage 4C features such as Layout A or still export before those paths exist.
- The plan must not let RAW placeholders leak into the standard adapter path. RAW implementation remains a later stage even if scanner/resolver see those extensions.

## Validation Commands Run For This Plan Phase

- `cat docs/qa.md`
- `cat docs/stage.md`
- `find src tests docs -maxdepth 4 -type f | sort | sed -n '1,220p'`

## Touched Files In This Plan Phase

- `docs/stages/stage-04A-plan.md`
- `docs/stage.md`

## Exact Next Prompt

`[Stage 4A-Implement]`

## Outcome

Stage 4A planning is complete. The next fresh Dev session should implement only the standard-video CLI pipeline defined here, write the Stage 4A implementation and handoff artifacts, and stop before QA or Stage 4B work.
