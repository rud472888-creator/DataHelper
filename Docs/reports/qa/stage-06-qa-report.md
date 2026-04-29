# Stage 06 QA Report

- gate: passed
- verdict: PASS
- stage: stage-06
- lane: qa
- next_recommended_prompt: `[Stage 7-Plan]`
- stage_7_status: unblocked-by-qa

## Scope

Independent QA review of Stage 6 hardening against:

- `docs/stages/stage-06-plan.md`
- `docs/stages/stage-06-implement.md`
- `docs/reports/dev/stage-06-handoff.md`
- `docs/release-checklist.md`
- `src/frameproof/`
- `tests/`

This was a QA-only gate. No product code was modified. Only QA documents were updated.

## Checked Files

- `AGENTS.md`
- `docs/qa.md`
- `docs/stages/stage-06-plan.md`
- `docs/stages/stage-06-implement.md`
- `docs/reports/dev/stage-06-handoff.md`
- `docs/release-checklist.md`
- `docs/stages/stage-06-fix.md`
- `src/frameproof/cli.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/core/batch_runner.py`
- `src/frameproof/core/scanner.py`
- `src/frameproof/gui/__main__.py`
- `src/frameproof/gui/main_window.py`
- `src/frameproof/output/manifest_writer.py`
- `src/frameproof/output/still_exporter.py`
- `src/frameproof/render/pdf_renderer.py`
- `tests/test_cli.py`
- `tests/integration/test_cli_standard_pipeline.py`
- `tests/integration/test_dependency_missing.py`
- `tests/integration/test_raw_dependency_missing.py`
- `tests/unit/core/test_batch_runner.py`
- `tests/unit/core/test_scanner.py`
- `tests/unit/gui/conftest.py`
- `tests/unit/gui/test_batch_controller.py`
- `tests/unit/gui/test_main_window.py`
- `tests/unit/output/test_manifest_writer.py`
- `tests/unit/output/test_still_exporter.py`
- `tests/unit/render/test_pdf_renderer.py`
- `tests/unit/test_gui_status_text.py`
- `tests/manual/gui_smoke_checklist.md`

## Command Results

- `python -m pytest` -> PASS

```text
======================== 95 passed, 9 skipped in 4.44s =========================
```

- `ruff check .` -> PASS

```text
All checks passed!
```

- `mypy src` -> PASS

```text
Success: no issues found in 43 source files
```

- `python -m frameproof --help` -> PASS

```text
usage: frameproof [-h] [--version] [--input PATH] [--recursive]
                  [--no-recursive] [--middle-count {0,1,2,3}]
                  [--layout {contact_sheet,detail}] [--output PDF_PATH]
                  [--csv CSV_PATH] [--json JSON_PATH] [--export-stills]
                  [--stills-dir PATH] [--project-name NAME]
                  [--ffmpeg-path FFMPEG_PATH] [--ffprobe-path FFPROBE_PATH]
                  [--mediainfo-path MEDIAINFO_PATH] [--braw-adapter-path PATH]
                  [--r3d-adapter-path PATH] [--arri-art-cmd-path PATH]
```

- `python -m frameproof --input /tmp/frameproof-stage6-qa.LzTYiT/unsupported/unsupported.txt --output /tmp/frameproof-stage6-qa.LzTYiT/unsupported/unsupported.pdf` -> PASS

```text
status: failed
total_clips: 0
success_count: 0
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 0
fatal_reason: No supported input files were found.
fatal: batch could not produce a report
```

- `find /tmp/frameproof-stage6-qa.LzTYiT/unsupported -maxdepth 1 -type f | sort` -> PASS

```text
/tmp/frameproof-stage6-qa.LzTYiT/unsupported/unsupported.txt
```

- `python -m frameproof --input /tmp/frameproof-stage6-qa-raw.Fhm5Zg/raw-missing/clip.braw --output /tmp/frameproof-stage6-qa-raw.Fhm5Zg/raw-missing/raw.pdf` -> PASS

```text
status: partial_success
total_clips: 1
success_count: 0
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 1
dependency_missing: clip=clip.braw status=dependency_missing adapter=braw_adapter required_tools=braw_adapter dependency_state=not_configured
fatal: batch could not produce a report
```

- `find /tmp/frameproof-stage6-qa-raw.Fhm5Zg/raw-missing -maxdepth 1 -type f | sort` -> PASS

```text
/tmp/frameproof-stage6-qa-raw.Fhm5Zg/raw-missing/clip.braw
```

- `python -m frameproof --input /tmp/frameproof-stage6-qa-std.zA7zJR/std-missing/broken.mp4 --output /tmp/frameproof-stage6-qa-std.zA7zJR/std-missing/standard.pdf --ffmpeg-path /missing/ffmpeg --ffprobe-path /missing/ffprobe --mediainfo-path /missing/mediainfo` -> PASS

```text
status: partial_success
total_clips: 1
success_count: 0
partial_success_count: 0
probe_failed_count: 0
decode_failed_count: 0
skipped_count: 1
dependency_missing: clip=broken.mp4 status=dependency_missing adapter=ffmpeg required_tools=ffmpeg,ffprobe dependency_state=configured_missing
fatal: batch could not produce a report
```

- `find /tmp/frameproof-stage6-qa-std.zA7zJR/std-missing -maxdepth 1 -type f | sort` -> PASS

```text
/tmp/frameproof-stage6-qa-std.zA7zJR/std-missing/broken.mp4
```

- `python -m frameproof.gui --help` -> PASS

```text
usage: python -m frameproof.gui [-h] [--settings-file PATH] [--smoke-test]

Launch the Frame Proof PySide6 GUI.
```

- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS

```text
[no output]
```

- `python -m pytest tests/unit/gui -q` -> PASS

```text
......                                                                   [100%]
6 passed in 0.02s
```

- offscreen GUI inspection -> PASS

```text
actual_size=1280x860
controls_visible=True,True,True,True
hidden_note=Preview-only PDF output is shareable. The app does not modify source media. Caution: this output is inside a selected source tree. Keep exports separate to avoid rescans. Path Privacy is Hidden. PDFs hide full source paths but keep clip identity. Layout B keeps the denser contact-sheet view with readable timecode labels and warnings.
basename_note=Preview-only PDF output is shareable. The app does not modify source media. Caution: this output is inside a selected source tree. Keep exports separate to avoid rescans. Path Privacy is Basename Only. PDFs keep filenames but omit parent folders. Layout B keeps the denser contact-sheet view with readable timecode labels and warnings.
```

## Coverage Observations

- The repo contains the required Stage 6 test shapes, and the current tree includes explicit coverage for the required acceptance cases.
- `tests/integration/test_cli_standard_pipeline.py` covers:
  - `middle_count` values `0`, `1`, `2`, and `3`
  - still export off and on
  - non-ASCII input and output paths
  - short-clip duplicate-slot preservation
  - mixed valid-plus-broken batch continuation
  Those eight tests were skipped in this session because the standard-video happy path depends on `ffmpeg` and `ffprobe`.
- `tests/integration/test_dependency_missing.py` covers:
  - fatal standard dependency-missing behavior
  - mixed processable standard clip plus RAW dependency-missing continuation
- `tests/integration/test_raw_dependency_missing.py` covers RAW-only dependency-missing behavior and executed successfully here.
- `tests/unit/core/test_batch_runner.py` covers:
  - early output-target rejection before scan work
  - cleanup of partial PDF/manifest artifacts on output-stage failure
  - cancellation between clips
  - default staging outside the source tree
  - source-byte preservation
- `tests/unit/output/test_still_exporter.py` covers:
  - drop-frame and long-name sanitization
  - sanitized fallbacks
  - non-ASCII name retention
  - collision suffixes
  - traversal-style name confinement inside the stills root
- `tests/unit/output/test_manifest_writer.py` covers:
  - failure-row visibility
  - partial capture parity with still export off
  - duplicate-slot parity
  - exported-image path parity between row and clip views
- `tests/unit/gui/test_main_window.py`, `tests/unit/gui/test_batch_controller.py`, `tests/unit/test_gui_status_text.py`, and `tests/unit/render/test_pdf_renderer.py` cover:
  - saved GUI state and batch progress updates
  - geometry/responsiveness expectations
  - output caution and partial-result messaging
  - operator-facing dependency labels
  - path privacy and failed/partial PDF text
- The prompt metadata listed `source/tests` as a required input path, but the repository uses `tests/` and there is no `source/tests` path in the tree.

## Source Inspection Notes

### Output validation and fatal behavior

- `src/frameproof/core/batch_runner.py` calls `_validate_output_targets(settings.output)` before scan/probe work begins.
- `_validate_output_targets()` rejects duplicate targets, directories where files are expected, non-directory output roots, and unwritable paths by doing real temporary write checks.
- On render or manifest failure, `_cleanup_output_artifacts()` removes any partially written PDF/CSV/JSON files before the fatal outcome is returned.
- `tests/unit/core/test_batch_runner.py` includes direct proof for pre-scan output validation and partial-artifact cleanup.

### File safety and source preservation

- `src/frameproof/core/scanner.py` only discovers supported files and resolves paths; it does not write into source locations.
- `src/frameproof/core/batch_runner.py` uses `_staging_root()` to allocate a temporary app-owned staging directory unless the operator explicitly overrides `staging_dir`.
- `tests/unit/core/test_batch_runner.py` asserts that the source file bytes remain unchanged after a batch and that the generated staging path is outside the source directory tree.
- Still export writes use `shutil.copy2()` from temporary capture images to the configured stills root; no inspected Stage 6 hardening path writes beside the source media.

### Path sanitization and traversal resistance

- `src/frameproof/output/still_exporter.py` sanitizes clip names, labels, and timecode-derived tokens via `sanitize_path_component()`.
- `_safe_child_path()` resolves the candidate export path and raises if it would escape the configured stills directory.
- `tests/unit/output/test_still_exporter.py` proves Unicode names are preserved, traversal-style inputs stay inside the stills root, and collisions are suffixed rather than overwritten unsafely.

### Manifest and failed-file parity

- `src/frameproof/output/manifest_writer.py` emits a row for every capture when captures exist, and emits a synthetic failure row when a clip has no captures.
- Duplicate-slot and failure visibility are preserved in both row and clip JSON shapes.
- `tests/unit/output/test_manifest_writer.py` verifies failure rows, duplicate parity, and exported-image path parity.

## Evaluation

- Spec fidelity / product depth: PASS. Stage 6 matches the hardening plan and release-checklist intent without introducing new product features or alternate pipeline branches.
- Functionality: PASS. CLI hardening behavior, structured fatal output, GUI smoke launch, and the direct GUI regression lane all work in the current tree.
- Visual design / UX clarity: PASS. The GUI exposes the required sections, caution copy, path-privacy guidance, and readable warning/status messaging, and the rendered PDF tests preserve path-privacy and failure visibility expectations.
- Code quality / maintainability: PASS. The hardening stays localized to existing ownership boundaries and is backed by focused regression tests rather than broad rewrites.
- Accessibility / responsiveness: PASS. Geometry/readability checks, explicit text labels, row text authority over color, and keyboard-tab wiring in `src/frameproof/gui/main_window.py` are adequate for the Stage 6 gate.
- Validation completeness: PASS. All required commands and documented CLI smokes were run in this session. The remaining skipped happy-path standard-video tests are environment-limited, not missing from the repository.

## Defects

No blocking Stage 6 defects were reproduced in the current repository state.

## Residual Risks

- ffmpeg-backed happy-path standard-video integration tests remain skipped on this host because `ffmpeg` and `ffprobe` are unavailable locally.
- Full live desktop/manual GUI validation still depends on an operator-capable host, but the required offscreen smoke and GUI regression suite both pass here.

## Gate Decision

PASS. Stage 06 satisfies the QA gate in the current repository state, and Stage 7 is unblocked.

Exact next recommended prompt: `[Stage 7-Plan]`
