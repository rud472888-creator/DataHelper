# Stage 05 Implement

- lane: dev
- stage: stage-05
- subphase: implement
- status: complete
- scope_boundary: gui-and-pdf-ux-refinement-only
- source_plan: `docs/stages/stage-05-plan.md`
- next_recommended_prompt: `[Stage 5-QA]`

## Delivered Scope

- Refined the GUI hierarchy so operators now get a `Session Overview`, clearer source/output summaries, explicit run readiness messaging, and denser status/result copy without changing batch semantics.
- Refined the dependency dialog for long-path readability and quick scanning while preserving the exact required dependency-state wording.
- Implemented the repository `pdf_renderer.py` source for both `Layout B` and `Layout A`, with clearer headers, footers, disclaimer placement, warning treatment, failed/partial visibility, and timecode display.
- Added deterministic visual verification artifacts for both PDFs and representative GUI states.
- Expanded automated and manual verification coverage around the new Stage 5 presentation behavior.

## Changed Files And Reasons

- `src/frameproof/gui/app.py` tightened the Stage 5 visual styling for cards, summaries, focus states, and table readability.
- `src/frameproof/gui/main_window.py` added overview/readiness summaries, improved source/output guidance, and made progress states denser and easier to scan.
- `src/frameproof/gui/dependency_dialog.py` improved dependency status readability with an `Applies To` column and better long-path behavior.
- `src/frameproof/render/pdf_renderer.py` now provides the real repository renderer for both report layouts and the failed/partial section.
- `scripts/generate_visual_artifacts.py` now produces deterministic Stage 5 artifacts under `artifacts/stage-05/`.
- `tests/unit/gui/test_main_window.py` now covers readiness, output-tree cautioning, and partial-result summary behavior.
- `tests/unit/render/test_pdf_renderer.py` now covers footer disclaimer, privacy display, and density policy helpers.
- `tests/manual/gui_smoke_checklist.md` now covers Stage 5 resize, focus, artifact, and readability checks.
- `docs/ui-spec.md` now records the implemented Stage 5 presentation notes and visual verification path.

## Simplifications Made

- Kept the GUI control set and the shared runner untouched instead of adding a separate Stage 5 execution path.
- Reused the existing `ReportItem` and `CapturePoint` truth for PDF refinement instead of adding report-only data structures.
- Used one repo-native artifact generator for both PDFs and GUI screenshots instead of introducing a new verification framework.

## Validation Results

- `python -m pytest` -> PASS (`86 passed, 2 skipped`)
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/unit/gui -vv` -> PASS (`5 passed`)
- `python -m pytest tests/unit/render/test_pdf_renderer.py -vv` -> PASS (`5 passed`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `python scripts/generate_visual_artifacts.py` -> PASS
- `python -m frameproof.gui --help` -> PASS
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS
- `npx playwright --version` -> PASS (`Version 1.59.1`), but Playwright was not used for verification because the product surface remains a native PySide6 GUI rather than an HTML/browser UI

## Generated Artifacts

- `artifacts/stage-05/pdf/layout-b-stage5.pdf`
- `artifacts/stage-05/pdf/layout-a-stage5.pdf`
- `artifacts/stage-05/gui/gui-empty.png`
- `artifacts/stage-05/gui/gui-partial.png`
- `artifacts/stage-05/gui/gui-error.png`
- `artifacts/stage-05/gui/dependency-dialog.png`
- `artifacts/stage-05/verification-summary.txt`

## Remaining Risks

- Fresh QA should inspect the rendered PDFs and GUI screenshots directly; automated tests cover text/layout-sensitive regressions but not aesthetic judgment alone.
- Hosts missing `IBM Plex Sans` will log a fallback-font warning during offscreen Qt runs.
- No browser harness was added because it would have created verification-only architecture outside the Stage 5 scope boundary.

## Fresh Session Notes

- Run `[Stage 5-QA]` next.
- Review the generated artifacts in `artifacts/stage-05/` before QA signoff.
- Do not begin Stage 6 from this handoff.
