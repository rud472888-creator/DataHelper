# Stage 05 QA Report

- gate: passed
- verdict: PASS
- stage: stage-05
- lane: qa
- next_recommended_prompt: `[Stage 6-Plan]`
- stage_6_status: unblocked-by-qa

## Scope

Independent QA review of Stage 5 UI and PDF refinements against:

- `docs/stages/stage-05-plan.md`
- `docs/stages/stage-05-implement.md`
- `docs/stages/stage-05-fix.md`
- `docs/reports/dev/stage-05-handoff.md`
- `docs/ui-spec.md`
- `src/frameproof/`
- `tests/`
- `artifacts/stage-05/`

This was a QA-only gate. No product code was modified. Only QA documents were updated.

## Checked Files

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
- `src/frameproof/gui/__main__.py`
- `src/frameproof/render/pdf_renderer.py`
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

## Command Results

- `python -m pytest` -> PASS

```text
======================== 87 passed, 2 skipped in 3.23s =========================
```

- `ruff check .` -> PASS

```text
All checks passed!
```

- `mypy src` -> PASS

```text
Success: no issues found in 41 source files
```

- `python scripts/generate_visual_artifacts.py` -> PASS

```text
qt.qpa.fonts: Populating font family aliases took 78 ms. Replace uses of missing font family "IBM Plex Sans" with one that exists to avoid this cost.
This plugin does not support propagateSizeHints()
This plugin does not support propagateSizeHints()
/Users/server_jay/Desktop/DataHelper/artifacts/stage-05/verification-summary.txt
```

- `python -m frameproof.gui --help` -> PASS

```text
usage: python -m frameproof.gui [-h] [--settings-file PATH] [--smoke-test]

Launch the Frame Proof PySide6 GUI.

options:
  -h, --help            show this help message and exit
  --settings-file PATH  Override the GUI settings INI file location.
  --smoke-test          Create and show the GUI briefly, then exit without
                        starting a batch.
```

- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` -> PASS

```text
qt.qpa.fonts: Populating font family aliases took 79 ms. Replace uses of missing font family "IBM Plex Sans" with one that exists to avoid this cost.
This plugin does not support propagateSizeHints()
```

- `npx playwright --version` -> PASS

```text
Version 1.59.1
```

- `rg -n "playwright|browser" . --glob '!node_modules/**' --glob '!*.pyc'` -> no repo Playwright harness found

```text
./Docs/stages/stage-05-qa.md:45:- `npx playwright --version` -> PASS (`Version 1.59.1`)
./Docs/stages/stage-05-qa.md:46:- `rg --files | rg 'playwright|e2e|spec\\.|visual'` -> no repo Playwright harness found
./Docs/implement.md:42:- Used repository-native artifact generation instead of a browser harness because the product surface is a PySide6 desktop app and the repo does not ship an HTML UI to verify.
./Docs/stages/stage-05-implement.md:47:- `npx playwright --version` -> PASS (`Version 1.59.1`), but Playwright was not used for verification because the product surface remains a native PySide6 GUI rather than an HTML/browser UI
./Docs/stages/stage-05-implement.md:63:- No browser harness was added because it would have created verification-only architecture outside the Stage 5 scope boundary.
./Docs/reports/qa/stage-05-qa-report.md:92:- `npx playwright --version` -> PASS
./Docs/reports/qa/stage-05-qa-report.md:98:- `rg --files | rg 'playwright|e2e|spec\\.|visual'` -> no repo Playwright harness found
./Docs/stages/stage-05-plan.md:53:- The repository does not currently define Playwright or another browser-based visual harness, and dev dependencies remain limited to `mypy`, `pytest`, and `ruff` (`pyproject.toml:18`).
./Docs/ui-spec.md:280:- A browser harness is optional only if it exists without adding new product-facing architecture; Stage 5 does not require Playwright when the product surface remains the native PySide6 desktop app.
```

- `sips -g pixelWidth -g pixelHeight artifacts/stage-05/gui/gui-empty.png artifacts/stage-05/gui/gui-partial.png artifacts/stage-05/gui/gui-error.png artifacts/stage-05/gui/dependency-dialog.png` -> PASS

```text
/Users/server_jay/Desktop/DataHelper/artifacts/stage-05/gui/gui-empty.png
  pixelWidth: 1280
  pixelHeight: 860
/Users/server_jay/Desktop/DataHelper/artifacts/stage-05/gui/gui-partial.png
  pixelWidth: 1280
  pixelHeight: 860
/Users/server_jay/Desktop/DataHelper/artifacts/stage-05/gui/gui-error.png
  pixelWidth: 1280
  pixelHeight: 860
/Users/server_jay/Desktop/DataHelper/artifacts/stage-05/gui/dependency-dialog.png
  pixelWidth: 1180
  pixelHeight: 520
```

- Offscreen geometry probe -> PASS

```text
minimumSizeHint= 879 707
actual_1024= 1024 720
actual_1280= 1280 860
controls_visible= True True True True
```

- PDF artifact text inspection -> PASS

```text
layout-b-stage5.pdf
  present: Preview-only disclaimer: not color-critical
  present: Failed / Partial Clips
  present: Warning: clip warning
  present: Mid1 warning: fallback tc
layout-a-stage5.pdf
  present: Preview-only disclaimer: not color-critical
  present: Failed / Partial Clips
  present: Source path:
  present: Requested ratio:
  present: Actual timecode:
  present: Warning: clip warning
  present: Mid1 warning: fallback tc
```

- GUI artifact OCR inspection -> PASS

```text
1:Sources Output And Report Run
4:Start refreshes dependency status before launch.
5:Mla eWemar ate SAC A CT Output PDF Cancel stops after the current in-flight step.
8:Carnes 2|| Races ——— Readiness: inputs and output are set. Start
10:Dependency status: 0/6 tools resolved. Core blockers: Stage 5 Artifact Run Standard video is blocked until these core
12:CMD. Additional gaps: Medialnfo. Open Dependencies for Middle Frames 2 +
13:per-tool status labels and paths. Dependencies [start | orrnn
16:PES Gy Path Privacy Batch Status
20:¥) Export still PNGs Select source files or folders to begin.
28:M7] Include subfolders Privacy is Basename Only. PDFs keep filenames but omit parent
29:Clip Progress
```

## Artifact Review

### PDF artifacts

- `Layout B` passes the required content check. The generated artifact includes the layout label, source summary, generated timestamp, counts, preview-only language, and the failed or partial clip section. This matches the Stage 5 PDF requirements and the renderer behavior in `src/frameproof/render/pdf_renderer.py`.
- `Layout A` passes the required content check. The generated artifact includes the layout label, source path, per-frame requested and actual detail labels, warnings, and the footer disclaimer. This matches the Stage 5 detail-PDF requirements and the renderer behavior in `src/frameproof/render/pdf_renderer.py`.
- `tests/unit/render/test_pdf_renderer.py` covers the major Stage 5 PDF text contracts and passed in this session.

### GUI artifacts

- The generated GUI screenshots are credible Stage 5 evidence. `sips` confirms the fixed viewport dimensions for the main window and dependency dialog, and OCR on `gui-empty.png`, `gui-partial.png`, `gui-error.png`, and `dependency-dialog.png` surfaced the expected Stage 5 structure and explicit messaging.
- The dependency dialog fits its intended size and preserves the exact required dependency-state wording through `src/frameproof/gui/status_text.py`, while the artifact itself shows the expected scan-friendly column structure and present-state labels.
- The main window now satisfies the Stage 5 responsiveness target. The repo artifact summary records `requested=1024x720 actual=1024x720 minimumSizeHint=880x720`, and QA's direct offscreen probe measured `minimumSizeHint=879x707`, `actual_1024=1024x720`, and `actual_1280=1280x860`.

### Playwright applicability

- Playwright is installed locally, but the repository does not ship a Playwright harness or browser UI surface to validate. That is acceptable for Stage 5 because the plan explicitly allows the alternative path of offscreen PySide6 screenshots plus deterministic PDFs plus the manual checklist when the product surface is the native desktop GUI.
- QA therefore used the accepted native verification path rather than treating Playwright absence as a defect.

## Evaluation

- Spec fidelity / product depth: PASS. The current tree preserves the required control set, dependency wording, and both PDF layouts while adding the intended Stage 5 visual summaries and disclaimers.
- Functionality: PASS. The repo passes the required regression suite, static analysis, GUI smoke launch, artifact generation, and the Stage 5 PDF content checks.
- Visual design / UX clarity: PASS. The GUI artifacts expose the intended hierarchy and explicit state messaging, and the PDFs preserve warning visibility, dense-but-readable summaries, and footer disclaimers.
- Code quality / maintainability: PASS. The GUI remains thin over the shared pipeline, the dependency-state wording is centralized, and the PDF renderer plus artifact generator are directly covered by targeted tests.
- Accessibility / responsiveness: PASS. The fixed main window honors the required desktop viewport, focus styling exists in `src/frameproof/gui/app.py`, and the tab order is explicitly configured in `src/frameproof/gui/main_window.py`.
- Validation completeness: PASS. The Stage 5 QA lane includes command verification, GUI launch smoke, deterministic artifact regeneration, geometry proof, OCR-backed screenshot checks, PDF text inspection, and a documented rationale for not using Playwright.

## Defects

No blocking or moderate QA defects were found in this session.

## Residual Risks

- Offscreen Qt runs still log a missing `IBM Plex Sans` warning on this host, so typography may shift slightly on hosts without that font.
- This fresh QA session validated the documented manual checklist and native artifacts rather than re-running a fully manual desktop walkthrough on a physical display.

## Verdict

PASS. Stage 5 satisfies the QA gate in this session, and Stage 6 is unblocked.

Exact next recommended prompt: `[Stage 6-Plan]`

Stop after QA.
