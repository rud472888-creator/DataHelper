# Stage 05 QA

- lane: qa
- stage: stage-05
- verdict: PASS
- gate: passed
- next_recommended_prompt: `[Stage 6-Plan]`
- stage_6_status: unblocked-by-qa

## Summary

Independent QA re-ran Stage 5 in a fresh session against the Stage 5 plan, implementation notes, fix note, dev handoff, UI spec, current GUI and PDF source, current tests, and the generated Stage 5 visual artifacts. The current tree clears the Stage 5 gate: `python -m pytest` passed with `87 passed, 2 skipped`, `ruff check .` passed, `mypy src` passed, `python scripts/generate_visual_artifacts.py` regenerated the expected PDF and GUI artifacts, and direct offscreen geometry probing confirmed the fixed viewport targets with `minimumSizeHint=879x707`, `actual_1024=1024x720`, and `actual_1280=1280x860`.

The visual evidence is credible and spec-aligned. `sips` confirms the regenerated GUI screenshots are `1280x860` for the main window and `1180x520` for the dependency dialog, OCR confirms the expected Stage 5 sections and explicit status copy in the GUI artifacts, and raw PDF text inspection confirms `Layout B` and `Layout A` both include the required preview-only disclaimer while `Layout A` includes the required per-frame detail fields such as `Requested ratio`, `Requested frame`, `Requested time`, `Actual frame`, `Actual time`, and `Actual timecode`. No repo Playwright harness exists, but the Stage 5 plan explicitly allows the native PySide6 screenshot plus deterministic PDF path for this desktop surface, so validation completeness passes without browser automation.

## Evidence Checked

- `AGENTS.md`
- `docs/qa.md`
- `docs/stages/stage-05-plan.md`
- `docs/stages/stage-05-implement.md`
- `docs/stages/stage-05-fix.md`
- `docs/reports/dev/stage-05-handoff.md`
- `docs/ui-spec.md`
- `src/frameproof/gui/app.py`
- `src/frameproof/gui/main_window.py`
- `src/frameproof/gui/dependency_dialog.py`
- `src/frameproof/gui/status_text.py`
- `src/frameproof/render/pdf_renderer.py`
- `src/frameproof/gui/__main__.py`
- `scripts/generate_visual_artifacts.py`
- `tests/manual/gui_smoke_checklist.md`
- `tests/unit/gui/test_main_window.py`
- `tests/unit/render/test_pdf_renderer.py`
- `artifacts/stage-05/verification-summary.txt`
- `artifacts/stage-05/pdf/layout-b-stage5.pdf`
- `artifacts/stage-05/pdf/layout-a-stage5.pdf`
- `artifacts/stage-05/gui/gui-empty.png`
- `artifacts/stage-05/gui/gui-partial.png`
- `artifacts/stage-05/gui/gui-error.png`
- `artifacts/stage-05/gui/dependency-dialog.png`

## Validation Results

- `python -m pytest` -> PASS (`87 passed, 2 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS (`Success: no issues found in 41 source files`)
- `python scripts/generate_visual_artifacts.py` -> PASS
- `python -m frameproof.gui --help` -> PASS
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS
- `npx playwright --version` -> PASS (`Version 1.59.1`)
- `rg -n "playwright|browser" . --glob '!node_modules/**' --glob '!*.pyc'` -> no repo Playwright harness found
- `sips -g pixelWidth -g pixelHeight artifacts/stage-05/gui/gui-empty.png artifacts/stage-05/gui/gui-partial.png artifacts/stage-05/gui/gui-error.png artifacts/stage-05/gui/dependency-dialog.png` -> PASS
- Offscreen geometry probe -> PASS (`minimumSizeHint=879x707`, `actual_1024=1024x720`, `actual_1280=1280x860`, required controls visible)
- PDF artifact text inspection -> PASS
- GUI artifact OCR inspection -> PASS

## Evaluation

- Spec fidelity / product depth: PASS. The required Stage 4D control set remains intact, the dependency dialog preserves the exact required state vocabulary, and both PDF layouts stay aligned with the Stage 5 UI and reporting requirements.
- Functionality: PASS. The full regression suite, lint, and typecheck all pass, and the GUI entrypoint plus smoke-test launch cleanly in offscreen mode.
- Visual design / UX clarity: PASS. The GUI artifacts expose the expected Stage 5 hierarchy and explicit state messaging, and the PDFs preserve header hierarchy, failed or partial clip visibility, and disclaimer language.
- Code quality / maintainability: PASS. The GUI remains thin over the shared pipeline, the dependency wording remains centralized in `src/frameproof/gui/status_text.py`, and the PDF renderer has direct source ownership plus targeted tests.
- Accessibility / responsiveness: PASS. The fixed main window now honors both the `1024x720` and `1280x860` targets in offscreen QA, the stylesheet provides visible focus treatment, and `src/frameproof/gui/main_window.py` defines explicit tab order through the required controls.
- Validation completeness: PASS. Stage 5 includes deterministic GUI and PDF artifacts, explicit geometry proof, OCR-backed screenshot checks, renderer text checks, and the documented rationale for using the native desktop verification path instead of browser automation.

## Visual Findings

- `gui-empty.png` OCR confirms the Stage 5 section structure, explicit readiness copy, dependency summary, and empty-state banner text.
- `gui-partial.png` OCR confirms the partial-result banner, clip-progress summary text, and non-color-only partial status wording.
- `gui-error.png` OCR confirms the invalid-settings banner remains explicit rather than hiding failure behind a silent state.
- `dependency-dialog.png` OCR confirms the dialog keeps the `Tool`, `Configured Path`, `Applies To`, `Status`, and `Resolved` columns, and shows the required exact state labels that apply in the artifact.
- `layout-b-stage5.pdf` contains `Layout B / contact_sheet`, the preview-only language, counts, source summary, and the failed or partial clip section.
- `layout-a-stage5.pdf` contains `Layout A / detail`, `Source path`, the required per-frame requested and actual detail labels, warnings, and the preview-only disclaimer.

## Defects

No blocking or moderate QA defects were found in this session.

## Residual Risks

- Offscreen Qt runs still log a missing `IBM Plex Sans` warning on this host, so hosts without that font may see minor typography fallback differences.
- This fresh QA session used the accepted native artifact path rather than a human-operated desktop walkthrough, so physical-display contrast judgment remains partly dependent on the documented manual checklist.

## Gate Decision

PASS. Stage 05 satisfies the QA gate in this session.

Exact next recommended prompt: `[Stage 6-Plan]`

Stop after QA.
