# Stage 06 QA

- lane: qa
- stage: stage-06
- verdict: PASS
- gate: passed
- next_recommended_prompt: `[Stage 7-Plan]`
- stage_7_status: unblocked-by-qa

## Summary

Independent QA re-ran Stage 6 in a fresh session against `docs/stages/stage-06-plan.md`, `docs/stages/stage-06-implement.md`, `docs/reports/dev/stage-06-handoff.md`, `docs/release-checklist.md`, the current `src/frameproof/` tree, and the current `tests/` tree. The current repository state clears the Stage 6 gate: `python -m pytest` returned `95 passed, 9 skipped`, `ruff check .` passed, `mypy src` passed, the documented Stage 6 CLI smokes returned the expected structured fatal and dependency-missing output without leaving behind stray PDF/CSV/JSON artifacts, `python -m frameproof.gui --help` passed, `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` passed, and the direct GUI unit lane executed with `6 passed`.

Source inspection and targeted test review confirm that the hardening acceptance behaviors are materially covered in the current tree. `src/frameproof/core/batch_runner.py` validates output targets before scan/probe work, keeps default staging app-owned, and removes partial output artifacts after terminal output-stage failures. `src/frameproof/output/still_exporter.py` sanitizes still-export names and rejects resolved paths that escape the configured stills root. `src/frameproof/output/manifest_writer.py` preserves failure rows and duplicate-slot parity across CSV/JSON. `tests/integration/test_cli_standard_pipeline.py`, `tests/integration/test_dependency_missing.py`, `tests/integration/test_raw_dependency_missing.py`, `tests/unit/core/test_batch_runner.py`, `tests/unit/output/test_manifest_writer.py`, `tests/unit/output/test_still_exporter.py`, `tests/unit/gui/test_main_window.py`, `tests/unit/gui/test_batch_controller.py`, `tests/unit/test_gui_status_text.py`, and `tests/unit/render/test_pdf_renderer.py` collectively cover `middle_count` values, short clips, dependency-missing behavior, still export on/off, failed-file visibility, manifest parity, path privacy messaging, geometry/readability expectations, and file-safety boundaries.

The prior Stage 6 QA FAIL report is stale relative to the current repository state. The earlier blocking GUI findings do not reproduce now: offscreen GUI smoke succeeds on this host, and the GUI pytest lane is collected and executed normally rather than being suppressed. Stage 6 is therefore acceptance-ready for hardening and unblocks Stage 7 planning.

## Evidence Checked

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

## Validation Results

- `python -m pytest` -> PASS (`95 passed, 9 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS (`Success: no issues found in 43 source files`)
- `python -m frameproof --help` -> PASS
- `python -m frameproof --input /tmp/frameproof-stage6-qa.LzTYiT/unsupported/unsupported.txt --output /tmp/frameproof-stage6-qa.LzTYiT/unsupported/unsupported.pdf` -> PASS (`EXIT:2`, structured `status: failed`, `fatal_reason: No supported input files were found.`, no report artifacts written)
- `python -m frameproof --input /tmp/frameproof-stage6-qa-raw.Fhm5Zg/raw-missing/clip.braw --output /tmp/frameproof-stage6-qa-raw.Fhm5Zg/raw-missing/raw.pdf` -> PASS (`EXIT:2`, structured RAW `dependency_missing`, no report artifacts written)
- `python -m frameproof --input /tmp/frameproof-stage6-qa-std.zA7zJR/std-missing/broken.mp4 --output /tmp/frameproof-stage6-qa-std.zA7zJR/std-missing/standard.pdf --ffmpeg-path /missing/ffmpeg --ffprobe-path /missing/ffprobe --mediainfo-path /missing/mediainfo` -> PASS (`EXIT:2`, structured standard-video `dependency_missing`, no report artifacts written)
- `python -m frameproof.gui --help` -> PASS
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS
- supplemental: `python -m pytest tests/unit/gui -q` -> PASS (`6 passed`)
- supplemental offscreen GUI inspection confirmed `1280x860` window layout and the expected Hidden/Basename path-privacy guidance text

## Coverage Observations

- The prompt metadata listed `source/tests` as a required input path, but the repository test tree is `tests/`; there is no `source/tests` path in the current repo.
- `tests/integration/test_cli_standard_pipeline.py` covers `middle_count` values `0/1/2/3`, still export off and on, non-ASCII input/output paths, short-clip duplicate-slot preservation, and mixed valid-plus-broken batch continuation. Those eight tests remain skipped on this host because the happy-path standard-video fixture depends on `ffmpeg` and `ffprobe`.
- `tests/integration/test_dependency_missing.py` and `tests/integration/test_raw_dependency_missing.py` cover standard and RAW dependency-missing behavior, including the fatal all-missing path and the mixed processable-standard-plus-RAW-dependency-missing continuation path.
- `tests/unit/core/test_batch_runner.py` covers early output-target failure, partial-output cleanup, cancellation behavior, default staging outside the source tree, and source-byte preservation.
- `tests/unit/output/test_still_exporter.py` covers filename sanitization, Unicode retention, collision suffixing, and traversal-style name confinement inside the stills root.
- `tests/unit/output/test_manifest_writer.py` covers failure-row visibility, duplicate-slot parity, partial-capture parity with still export off, and exported-image path parity.
- `tests/unit/gui/test_main_window.py`, `tests/unit/gui/test_batch_controller.py`, `tests/unit/test_gui_status_text.py`, and `tests/unit/render/test_pdf_renderer.py` cover saved GUI state, geometry/responsiveness targets, warning/status copy, partial-result visibility, operator-facing dependency labels, path-privacy messaging, and failed/partial PDF rendering text.

## Evaluation

- Spec fidelity / product depth: PASS. The delivered hardening matches the Stage 6 plan and release-checklist expectations without adding a second pipeline or weakening the status vocabulary.
- Functionality: PASS. Required CLI fatal/dependency-missing smokes behave correctly, GUI smoke launches successfully, and the direct GUI unit lane executes.
- Visual design / UX clarity: PASS. The current GUI surface exposes the expected sections, path-privacy guidance, caution copy, partial-result messaging, and readable warning/status text through the current tests and offscreen inspection.
- Code quality / maintainability: PASS. The hardening remains localized to the existing batch runner, CLI, output, and GUI ownership boundaries and is backed by focused regression tests.
- Accessibility / responsiveness: PASS. Geometry/readability checks, explicit text labels, keyboard-tab wiring in `src/frameproof/gui/main_window.py`, and GUI test coverage are adequate for the Stage 6 gate.
- Validation completeness: PASS. All required commands and documented CLI smokes were run in this session, and the remaining skipped happy-path standard-video integrations are explained by missing external tools rather than missing Stage 6 coverage.

## Defects

No blocking Stage 6 defects were reproduced in the current repository state.

## Residual Risks

- ffmpeg-backed happy-path standard-video integration tests remain skipped on this host because `ffmpeg` and `ffprobe` are unavailable locally.
- Live manual GUI validation still depends on a host where an operator can interact with the full desktop app, but the required offscreen smoke and GUI regression lane both pass here.

## Gate Decision

PASS. Stage 06 satisfies the QA gate in the current repository state, and Stage 7 is unblocked.

Exact next recommended prompt: `[Stage 7-Plan]`

Stop after QA.
