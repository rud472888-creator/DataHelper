# Stage 06 Plan

- lane: dev
- stage: stage-06
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_5_pass_verified: yes
- risk_level: high
- next_recommended_prompt: `[Stage 6-Implement]`

## Gate Verification

- `docs/qa.md:7` records `latest_stage: stage-05`, `latest_verdict: PASS`, and `next_recommended_prompt: [Stage 6-Plan]`.
- `docs/qa.md:15` records Stage 05 `verdict: PASS`, and `docs/qa.md:18` points to `[Stage 6-Plan]`.
- `docs/stages/stage-05-qa.md:5` records `verdict: PASS`, `docs/stages/stage-05-qa.md:6` records `gate: passed`, and `docs/stages/stage-05-qa.md:8` records `stage_6_status: unblocked-by-qa`.
- At session start, `docs/stage.md:3`, `docs/stage.md:4`, `docs/stage.md:6`, `docs/stage.md:7`, and `docs/stage.md:10` recorded Stage 6 Dev planning with the QA gate passed and implementation still disallowed.
- The required planning inputs were read explicitly before drafting this file: `AGENTS.md`, `docs/stage.md`, `docs/qa.md`, `docs/architecture.md`, `docs/data-inventory.md`, `docs/release-checklist.md`, and `docs/stages/stage-05-qa.md`.
- The required validation commands for this phase were executed:
- `cat docs/qa.md`
- `cat docs/release-checklist.md`
- `find tests src docs -maxdepth 4 -type f | sort | sed -n '1,260p'`
- Stage 6 planning is therefore legal. This phase remains docs-only and stops before hardening implementation.

## Sprint Goal

- Harden the existing shared pipeline for reliability, failure visibility, file safety, and acceptance readiness without adding any new product features.
- Expand test coverage around the failure modes already required by the architecture and release checklist: damaged media, short clips, non-ASCII paths, long clips, dependency loss, output write failure, and batch continuation (`docs/architecture.md:140`, `docs/release-checklist.md:78`).
- Keep the one-pipeline architecture intact so CLI, GUI, PDF, still export, and manifests continue to report the same normalized facts (`docs/architecture.md:3`, `docs/architecture.md:7`, `docs/architecture.md:106`, `docs/data-inventory.md:75`, `docs/data-inventory.md:177`).

## Non-Scope

- No new capture modes, report layouts, GUI features, or packaging features.
- No alternate GUI-only execution path or second reporting pipeline.
- No dependency bundling decisions; Stage 7 still owns packaging and release distribution decisions (`docs/release-checklist.md:5`, `docs/release-checklist.md:107`).
- No implementation work in this phase.

## Current Hardening Baseline

- The architecture already defines the shared pipeline, fatal-stop conditions, subprocess isolation rules, and concurrency defaults that Stage 6 must preserve rather than redesign (`docs/architecture.md:15`, `docs/architecture.md:112`, `docs/architecture.md:138`, `docs/architecture.md:158`).
- The data model already requires requested-versus-actual capture parity across PDF, CSV, and JSON, duplicate preservation for short clips, and deterministic visibility for failed candidates (`docs/data-inventory.md:75`, `docs/data-inventory.md:101`, `docs/data-inventory.md:128`, `docs/data-inventory.md:177`).
- Current automated coverage already locks some core reliability behaviors:
- capture planning covers `middle_count=0`, `middle_count=3`, frame-count priority, duration fallback, rounding, and duplicate preservation for very short clips (`tests/unit/core/test_capture_planner.py:24`, `tests/unit/core/test_capture_planner.py:32`, `tests/unit/core/test_capture_planner.py:39`, `tests/unit/core/test_capture_planner.py:52`, `tests/unit/core/test_capture_planner.py:65`)
- scanner tests cover deterministic sort order and non-recursive behavior, but not non-ASCII path cases (`tests/unit/core/test_scanner.py:8`, `tests/unit/core/test_scanner.py:24`)
- batch runner tests cover happy-path progress and cancel-between-clips behavior, but not fatal output-write failure or mixed-batch continuation assertions (`tests/unit/core/test_batch_runner.py:68`, `tests/unit/core/test_batch_runner.py:130`)
- standard CLI integration covers successful PDF/CSV/JSON generation and still export on/off, but only on ASCII temp paths (`tests/integration/test_cli_standard_pipeline.py:10`, `tests/integration/test_cli_standard_pipeline.py:55`)
- dependency-missing integration exists for standard and RAW-only fatal batches (`tests/integration/test_dependency_missing.py:8`, `tests/integration/test_raw_dependency_missing.py:8`)
- still-export tests cover sanitize, long-name truncation, drop-frame token handling, and collision suffixes, but not non-ASCII retention policy or traversal across full nested outputs (`tests/unit/output/test_still_exporter.py:50`, `tests/unit/output/test_still_exporter.py:65`)
- manifest tests cover exported-image parity and failure rows, but not mixed damaged-media continuation or hidden-path expectations (`tests/unit/output/test_manifest_writer.py:52`, `tests/unit/output/test_manifest_writer.py:104`, `tests/unit/output/test_manifest_writer.py:149`)
- GUI coverage and the manual smoke checklist already cover resize, cancel, progress streaming, and keyboard focus, so Stage 6 only needs reliability-oriented additions there, not another visual redesign (`tests/unit/gui/test_main_window.py:98`, `tests/unit/gui/test_main_window.py:129`, `tests/unit/gui/test_main_window.py:152`, `tests/manual/gui_smoke_checklist.md:31`, `tests/manual/gui_smoke_checklist.md:43`, `tests/manual/gui_smoke_checklist.md:49`)

## Hardening Scope

### 1. Edge-case test expansion

- Add explicit tests for `middle_count` values `0`, `1`, `2`, and `3` at the CLI and batch-runner layers so configuration, planner output, manifests, and GUI/report summaries all stay aligned instead of relying on planner-only proof (`tests/unit/core/test_capture_planner.py:24`, `src/frameproof/cli.py:48`, `src/frameproof/core/batch_runner.py:132`).
- Add damaged-media cases that prove corrupt or empty clips surface `probe_failed` or `decode_failed` truthfully and remain visible in summaries, manifests, and reports (`docs/architecture.md:147`, `docs/release-checklist.md:85`, `src/frameproof/output/manifest_writer.py:46`).
- Add long-clip cases that stress larger frame counts and duration fallback without turning the Stage 6 suite into a performance benchmark; the goal is smoke-level correctness, not exhaustive soak testing (`docs/architecture.md:92`, `docs/architecture.md:163`).
- Add mixed-batch continuation cases that combine at least one processable file with one damaged file and one dependency-missing file, and assert the batch still completes with truthful partial results (`docs/architecture.md:140`, `docs/architecture.md:147`, `tests/integration/test_dependency_missing.py:36`).

### 2. File safety and path hardening

- Validate non-ASCII and space-containing paths at scan, output, still-export, manifest, and CLI argument boundaries because the release checklist explicitly requires those paths to work end to end (`docs/release-checklist.md:84`, `src/frameproof/core/scanner.py:11`, `src/frameproof/output/manifest_writer.py:71`, `src/frameproof/output/still_exporter.py:15`).
- Tighten output-path validation so fatal write failures happen before expensive batch work whenever possible, matching the architecture’s fatal-stop model (`docs/architecture.md:142`, `src/frameproof/core/batch_runner.py:172`, `src/frameproof/config/settings.py:153`).
- Re-check still-export sanitation against traversal attempts, reserved relative components, and directory collisions. The current sanitizer blocks many unsafe components already, but Stage 6 should lock those behaviors with clearer tests and path-boundary assertions (`docs/release-checklist.md:37`, `src/frameproof/output/still_exporter.py:44`, `src/frameproof/output/still_exporter.py:95`).
- Verify staging stays outside source media directories by default, and document any current limitation when users explicitly override `staging_dir` (`docs/release-checklist.md:38`, `docs/architecture.md:121`, `src/frameproof/core/batch_runner.py:102`, `src/frameproof/config/settings.py:151`).

### 3. Structured error handling and acceptance fidelity

- Keep every scanned candidate visible as a `ReportItem` or deterministic skip record, including damaged clips and mixed-format batches (`docs/data-inventory.md:180`, `src/frameproof/core/batch_runner.py:88`, `src/frameproof/output/manifest_writer.py:13`).
- Audit batch-level fatal paths so exit codes, summary status, manifest/PDF suppression, and user-facing diagnostics stay consistent across dependency loss, render/write failure, and cancellation (`docs/architecture.md:140`, `src/frameproof/core/batch_runner.py:168`, `src/frameproof/core/batch_runner.py:202`, `src/frameproof/cli.py:205`).
- Preserve the Stage 4B subprocess contract: malformed RAW subprocess responses or runtime failures must remain structured per-clip errors, not uncaught exceptions or fake successes (`docs/architecture.md:116`, `docs/architecture.md:118`, `docs/release-checklist.md:57`).

### 4. Performance and responsiveness smoke coverage

- Add smoke-level validation that long or mixed batches still stream progress without row reordering or GUI lockup, using the existing progress event model rather than new concurrency features (`docs/architecture.md:31`, `docs/architecture.md:160`, `src/frameproof/core/batch_runner.py:95`, `src/frameproof/gui/main_window.py:650`).
- Verify current concurrency defaults remain documented and effectively preserved: standard probe `4`, standard capture `2`, RAW capture `1`, PDF render `1` (`docs/architecture.md:160`).
- Measure only practical Stage 6 smoke evidence: no crashes, no unbounded memory growth signals in small stress fixtures, and acceptable completion for representative long clips on the current host. Full profiling remains a later release concern.

### 5. Reliability cleanup

- Simplify only where hardening exposes duplicated failure-mapping, path-validation, or output-write logic. Prefer deletion or boundary repair over new abstraction layers, matching repo guidance.
- Keep cleanup narrowly targeted to modules already owning the behavior: `config/settings.py`, `core/batch_runner.py`, `core/scanner.py`, `output/still_exporter.py`, `output/manifest_writer.py`, selective adapter clients, and the corresponding tests.

## Test Matrix Expansion

| Area | Existing proof | Stage 6 additions |
|---|---|---|
| Planner invariants | Unit coverage for `middle_count=0` and `3`, duration fallback, short clips (`tests/unit/core/test_capture_planner.py:24`) | Add `middle_count=1` and `2` assertions at higher layers; prove manifest/report parity for every supported value |
| Scanner paths | Deterministic sorting and non-recursive scan (`tests/unit/core/test_scanner.py:8`) | Add non-ASCII names, spaces, mixed case extensions, and long path components |
| Standard CLI happy path | PDF/CSV/JSON success and still-export toggle (`tests/integration/test_cli_standard_pipeline.py:10`) | Add non-ASCII output/input paths, long clip smoke, and mixed damaged-plus-valid batch |
| Dependency loss | Fatal standard and RAW-only dependency-missing coverage (`tests/integration/test_dependency_missing.py:8`, `tests/integration/test_raw_dependency_missing.py:8`) | Add mixed batch continuation where at least one clip remains processable; add GUI/manual confirmation that dependency gaps stay visible without hiding valid clips |
| Damaged media | Partial indirect coverage through existing failure paths | Add explicit corrupt container and decode-failure fixtures with assertions on `probe_failed`, `decode_failed`, CLI exit code, PDF/manifest visibility, and batch continuation |
| Output write failure | Architecture and release checklist require fatal behavior (`docs/architecture.md:142`, `docs/release-checklist.md:83`) | Add unit/integration tests that force unwritable or invalid output targets and assert early fatal stop plus absent output artifacts |
| Still-export safety | Sanitization and collision tests exist (`tests/unit/output/test_still_exporter.py:50`, `tests/unit/output/test_still_exporter.py:65`) | Add traversal-attempt cases, non-ASCII clip names, nested output dir safety, and no-write-when-temp-image-missing proof |
| Manifest parity | Exported image path and failure rows are tested (`tests/unit/output/test_manifest_writer.py:52`, `tests/unit/output/test_manifest_writer.py:149`) | Add damaged-media parity, duplicate-slot parity, hidden/basename path mode expectations, and mixed-batch summary consistency |
| Batch cancellation | Unit coverage for cancel between clips (`tests/unit/core/test_batch_runner.py:130`) | Add cancel-near-output-stage assertions and GUI/manual proof that cancellation preserves existing diagnostics after long-running batches |
| GUI responsiveness/accessibility | Resize, caution banner, partial-result copy, manual keyboard and cancel checklist (`tests/unit/gui/test_main_window.py:98`, `tests/manual/gui_smoke_checklist.md:49`) | Add reliability-oriented checks for long warning text, long clip lists, dependency warning states during mixed batches, and documented constraints if host font/runtime differences remain |

## Security And File Safety Checklist

- Verify source media remains read-only from CLI and GUI flows, including damaged-media and mixed-batch cases (`docs/release-checklist.md:35`, `src/frameproof/gui/main_window.py:82`, `src/frameproof/gui/main_window.py:482`).
- Verify sidecar files such as `RMD` are never modified or written beside source clips (`docs/release-checklist.md:36`).
- Verify still-export and manifest filenames remain sanitized and collision-safe across ASCII, non-ASCII, long names, and traversal-style inputs (`docs/release-checklist.md:37`, `src/frameproof/output/still_exporter.py:44`, `src/frameproof/output/still_exporter.py:95`).
- Verify staging defaults remain app-owned and outside source trees unless the operator explicitly overrides them, and reject unsafe output collisions where feasible (`docs/release-checklist.md:38`, `docs/architecture.md:121`, `src/frameproof/core/batch_runner.py:102`).
- Verify hidden and basename privacy modes still hide full source paths in PDFs without destroying clip identity or manifest correctness (`docs/release-checklist.md:39`, `src/frameproof/gui/main_window.py:497`, `docs/architecture.md:176`).
- Verify no network behavior is introduced while hardening Stage 6 (`docs/release-checklist.md:40`).

## Performance Smoke Plan

- Fixture shape:
- one short standard clip for baseline success
- one very short clip for duplicate preservation
- one long synthetic standard clip to exercise progress updates and output generation under larger frame counts
- one mixed batch containing a valid clip, a damaged clip, and one dependency-missing RAW clip
- Smoke expectations:
- row order remains fixed while progress streams (`tests/manual/gui_smoke_checklist.md:33`, `src/frameproof/gui/main_window.py:656`)
- cancel still prevents new work from starting after the current step (`tests/manual/gui_smoke_checklist.md:45`, `src/frameproof/core/batch_runner.py:104`)
- manifest and PDF generation remain single-pass terminal stages with no parallel output races (`docs/architecture.md:168`, `src/frameproof/core/batch_runner.py:191`, `src/frameproof/core/batch_runner.py:199`)
- standard probe/capture and RAW capture defaults remain aligned with the architecture table, even if the current implementation does not expose those knobs directly (`docs/architecture.md:162`)
- Required evidence after implementation:
- `python -m pytest`
- `ruff check .`
- `mypy src`
- one documented CLI smoke per fixture class above
- GUI/manual smoke where the local Qt runtime permits launch

## Cleanup Plan

- Write tests first for every hardening gap that reflects existing required behavior rather than new behavior.
- Consolidate duplicated output-path and fatal-write handling if the implementation reveals repeated parent-directory creation or inconsistent exception-to-status translation (`src/frameproof/core/batch_runner.py:172`, `src/frameproof/output/manifest_writer.py:80`).
- Tighten path-normalization boundaries in `config/settings.py`, `scanner.py`, and `still_exporter.py` instead of adding wrapper layers (`src/frameproof/config/settings.py:31`, `src/frameproof/core/scanner.py:20`, `src/frameproof/output/still_exporter.py:64`).
- Keep error/status vocabulary centralized and unchanged. Cleanup may simplify mapping code, but it must not invent new public status names (`docs/data-inventory.md:151`, `docs/architecture.md:147`).
- Preserve the thin-GUI-over-shared-pipeline rule; if any GUI hardening is needed, it should remain presentation or validation glue around `run_batch()` rather than new processing logic (`docs/architecture.md:3`, `docs/qa.md:22`, `src/frameproof/gui/main_window.py:557`).

## Acceptance Criteria

- Stage 6 adds automated coverage for `middle_count 0/1/2/3`, short clips, damaged media, dependency missing, output write failure, non-ASCII paths, filename sanitization, manifest parity, and batch continuation.
- Fatal output write failures stop before successful completion is reported, return a non-zero exit, and do not leave behind misleading PDF/CSV/JSON claims (`docs/architecture.md:142`, `docs/release-checklist.md:83`).
- Mixed batches continue when at least one clip is still processable, and damaged or dependency-missing clips remain visible with truthful normalized statuses in summaries and manifests (`docs/architecture.md:140`, `docs/data-inventory.md:180`).
- Requested-versus-actual capture facts remain aligned across PDF, CSV, JSON, and GUI progress for both clean and degraded runs (`docs/architecture.md:11`, `docs/data-inventory.md:75`, `docs/data-inventory.md:179`).
- Source media and sidecar files remain read-only, still-export outputs stay sanitized, and staging/output paths do not regress into unsafe defaults (`docs/release-checklist.md:35`, `docs/release-checklist.md:36`, `docs/release-checklist.md:37`, `docs/release-checklist.md:38`).
- GUI reliability checks continue to pass for resize, keyboard flow, cancel semantics, and long warning/status text within the existing Stage 5 desktop surface (`tests/manual/gui_smoke_checklist.md:11`, `tests/manual/gui_smoke_checklist.md:34`, `tests/manual/gui_smoke_checklist.md:45`, `tests/manual/gui_smoke_checklist.md:51`).
- The hardening implementation does not add product features, new pipeline branches, or relaxed tests.

## Planned Implementation Touched Files

- `src/frameproof/config/settings.py`
- `src/frameproof/core/batch_runner.py`
- `src/frameproof/core/scanner.py`
- `src/frameproof/core/capture_service.py`
- `src/frameproof/output/still_exporter.py`
- `src/frameproof/output/manifest_writer.py`
- selective adapter clients or adapter tests only where failure mapping needs hardening
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/integration/test_dependency_missing.py`
- `tests/integration/test_raw_dependency_missing.py`
- `tests/unit/core/test_batch_runner.py`
- `tests/unit/core/test_capture_planner.py`
- `tests/unit/core/test_scanner.py`
- `tests/unit/output/test_still_exporter.py`
- `tests/unit/output/test_manifest_writer.py`
- `tests/unit/gui/test_main_window.py`
- `tests/manual/gui_smoke_checklist.md`
- `docs/stages/stage-06-implement.md`
- `docs/reports/dev/stage-06-handoff.md`
- `docs/implement.md`

## Validation Commands Run For This Plan Phase

- `cat docs/qa.md`
- `cat docs/release-checklist.md`
- `find tests src docs -maxdepth 4 -type f | sort | sed -n '1,260p'`

## Touched Files In This Plan Phase

- `docs/stages/stage-06-plan.md`
- `docs/stage.md`

## Exact Next Prompt

`[Stage 6-Implement]`

## Outcome

Stage 6 planning is complete. The next fresh Dev session should implement the hardening scope above, expand the test matrix first, record validation evidence, update the Stage 6 implementation and handoff artifacts, and stop before QA or Stage 7 work.
