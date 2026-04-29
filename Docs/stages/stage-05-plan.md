# Stage 05 Plan

- lane: dev
- stage: stage-05
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_4d_pass_verified: yes
- risk_level: moderate
- next_recommended_prompt: `[Stage 5-Implement]`

## Gate Verification

- `docs/qa.md:7` records `latest_stage: stage-04D`, `latest_verdict: PASS`, and `next_recommended_prompt: [Stage 5-Plan]`.
- `docs/stages/stage-04D-qa.md:5` records `verdict: PASS`, `gate: passed`, and `stage_5_status: unblocked-by-qa`.
- At session start, `docs/stage.md` recorded `current_stage: stage-05`, `current_subphase: plan`, `current_lane: dev`, `last_result: stage-04D-qa-pass`, `qa_gate: pass`, and `implementation_allowed: false`.
- The required repository files were read explicitly before planning:
- `AGENTS.md`
- `docs/stage.md`
- `docs/qa.md`
- `docs/ui-spec.md`
- `docs/stages/stage-04D-qa.md`
- The required validation commands for this phase were executed:
- `cat docs/qa.md`
- `cat docs/ui-spec.md`
- `find docs src tests -maxdepth 4 -type f | sort | sed -n '1,240p'`
- Stage 5 planning is therefore legal. This phase remains docs-only and stops before implementation.

## Sprint Goal

- Refine the existing PySide6 GUI and PDF presentation for clarity, density, and operator confidence without adding new product features or altering the shared batch-processing behavior.
- Turn the Stage 5 token draft and UI-state requirements into a concrete implementation lane for visual polish, accessibility, responsiveness, and verification artifacts.
- Keep CLI, GUI, and PDF outputs aligned to the same `AppSettings`, `ReportItem`, `CapturePoint`, and `BatchSummary` truth already validated in Stage 4D.

## Non-Scope

- No new scan, probe, capture, export, or report features.
- No GUI-only execution path, alternate status vocabulary, or changes to core batch semantics.
- No changes to capture-position math, manifest schema, or adapter behavior beyond presentational clarity.
- No new repository dependency should be required for Stage 5 verification by default.
- No implementation work occurs in this phase.

## Current Baseline

- The UI spec already reserves Stage 5 for token cleanup, visual polish, and accessibility after the Stage 4A through 4D surfaces ship (`docs/ui-spec.md:57`, `docs/ui-spec.md:102`, `docs/ui-spec.md:122`, `docs/ui-spec.md:163`, `docs/ui-spec.md:204`, `docs/ui-spec.md:232`, `docs/ui-spec.md:282`).
- The current main window is a single top-to-bottom stack with dependency summary, source controls, one report/settings form, action buttons, a banner, and a 6-column progress table (`src/frameproof/gui/main_window.py:68`, `src/frameproof/gui/main_window.py:99`, `src/frameproof/gui/main_window.py:135`, `src/frameproof/gui/main_window.py:150`).
- The current GUI behavior already preserves truthful status updates and completion summaries, but readability is still driven by simple banner text and per-cell tinting (`src/frameproof/gui/main_window.py:334`, `src/frameproof/gui/main_window.py:371`, `src/frameproof/gui/main_window.py:426`, `src/frameproof/gui/main_window.py:439`).
- The app stylesheet already uses the Stage 5 draft color palette and IBM Plex Sans, but only as a short global stylesheet with limited hierarchy and no deeper sizing or layout rules (`src/frameproof/gui/app.py:15`, `src/frameproof/gui/app.py:23`, `src/frameproof/gui/app.py:24`).
- The dependency dialog already exposes the required tools and exact operator-facing state labels, so Stage 5 should refine readability and layout rather than change dependency semantics (`src/frameproof/gui/dependency_dialog.py:25`, `src/frameproof/gui/dependency_dialog.py:51`, `src/frameproof/gui/dependency_dialog.py:124`, `src/frameproof/gui/status_text.py:6`).
- `Layout B` already uses fixed page geometry and clips-per-page heuristics, while `Layout A` already renders metadata, capture cards, and note boxes. Stage 5 is a density and hierarchy pass over those existing structures, not a new reporting mode (`src/frameproof/render/pdf_renderer.py:16`, `src/frameproof/render/pdf_renderer.py:47`, `src/frameproof/render/pdf_renderer.py:121`, `src/frameproof/render/pdf_renderer.py:187`, `src/frameproof/render/pdf_renderer.py:238`, `src/frameproof/render/pdf_renderer.py:259`).
- Existing automated coverage proves state restore, progress-row updates, completion banners, and PDF content presence, but it does not yet prove polished visual hierarchy, resize behavior, or screenshot artifacts (`tests/unit/gui/test_main_window.py:34`, `tests/unit/render/test_pdf_renderer.py:71`).
- The current manual GUI checklist covers launch, dependencies, persistence, shared pipeline, and cancel, but not Stage 5 concerns such as window resizing, keyboard navigation, screenshot capture, or contrast review (`tests/manual/gui_smoke_checklist.md:5`).
- The repository does not currently define Playwright or another browser-based visual harness, and dev dependencies remain limited to `mypy`, `pytest`, and `ruff` (`pyproject.toml:18`).

## Refinement Scope

### 1. GUI hierarchy and control clarity

- Preserve the exact Stage 4D control set from `docs/ui-spec.md` while improving information hierarchy, section spacing, copy, and visual grouping (`docs/ui-spec.md:61`, `src/frameproof/gui/main_window.py:78`, `src/frameproof/gui/main_window.py:99`).
- Keep `Start`, `Cancel`, and `Dependencies` semantics unchanged, but make primary versus secondary actions more obvious and make disabled states easier to read at a glance (`src/frameproof/gui/main_window.py:135`, `src/frameproof/gui/main_window.py:401`).
- Replace flat banner/detail presentation with clearer state-specific summaries for empty, loading, cancelled, error, and success states while preserving the existing truthful vocabulary (`docs/ui-spec.md:124`, `docs/ui-spec.md:132`, `docs/ui-spec.md:140`, `docs/ui-spec.md:155`, `src/frameproof/gui/main_window.py:65`, `src/frameproof/gui/main_window.py:260`, `src/frameproof/gui/main_window.py:377`, `src/frameproof/gui/main_window.py:396`).
- Add inline UX clarification where the spec already calls for safety messaging, especially path privacy and output-inside-source cautioning, without changing batch behavior (`docs/ui-spec.md:275`).

### 2. Progress and feedback readability

- Keep the existing row-order, status-streaming, and cancel behavior intact, but refine table density, header legibility, status emphasis, and partial-success distinction so operators can scan long runs faster (`docs/ui-spec.md:104`, `docs/ui-spec.md:115`, `src/frameproof/gui/main_window.py:150`, `src/frameproof/gui/main_window.py:355`, `src/frameproof/gui/main_window.py:439`).
- Keep status meaning explicit in text, not just color, because the table and banner already rely on text-state values that QA validated in Stage 4D (`docs/stages/stage-04D-qa.md:14`, `src/frameproof/gui/main_window.py:361`).
- Improve artifact-path, count, and fallback-note presentation in the success banner so the final state is dense but easy to parse (`docs/ui-spec.md:157`, `src/frameproof/gui/main_window.py:384`).

### 3. Dependency and settings polish

- Retain the exact dependency-state labels `available`, `configured path missing`, `not configured`, and `runtime startup failure`, but improve dialog readability, path-field balance, and saved-state clarity (`docs/ui-spec.md:86`, `src/frameproof/gui/dependency_dialog.py:59`, `src/frameproof/gui/dependency_dialog.py:124`, `src/frameproof/gui/status_text.py:6`).
- Preserve the QSettings-backed persistence model while improving how restored values and helper text are surfaced in the main window and dependency screen (`docs/stages/stage-04D-qa.md:14`, `tests/unit/gui/test_main_window.py:49`).

### 4. PDF layout polish and density control

- Keep both report modes on the same `ReportItem` and `CapturePoint` data, but apply the Stage 5 design tokens and density rules more intentionally across header hierarchy, metadata spacing, thumbnail framing, and warning/error placement (`docs/ui-spec.md:167`, `docs/ui-spec.md:189`, `docs/ui-spec.md:208`, `docs/ui-spec.md:225`, `src/frameproof/render/pdf_renderer.py:25`, `src/frameproof/render/pdf_renderer.py:121`, `src/frameproof/render/pdf_renderer.py:160`, `src/frameproof/render/pdf_renderer.py:187`).
- For `Layout B`, tune clips-per-page, clip-card padding, and warning placement so the report stays readable before it becomes dense, matching the existing density policy instead of shrinking text into illegibility (`docs/ui-spec.md:191`, `src/frameproof/render/pdf_renderer.py:47`, `src/frameproof/render/pdf_renderer.py:168`).
- For `Layout A`, rebalance metadata table weight, capture-card spacing, and note-box hierarchy so path text, metadata, captures, and warnings do not visually compete (`docs/ui-spec.md:208`, `src/frameproof/render/pdf_renderer.py:227`, `src/frameproof/render/pdf_renderer.py:245`, `src/frameproof/render/pdf_renderer.py:294`).
- Preserve privacy behavior and clip identity when full paths are hidden (`docs/ui-spec.md:221`, `docs/ui-spec.md:277`, `src/frameproof/render/pdf_renderer.py:218`).

### 5. Verification artifacts and QA readiness

- Expand the existing manual GUI checklist into a Stage 5 checklist that covers resizing, keyboard flow, contrast, screenshot capture, dependency dialog readability, progress-table scanability, success/error/cancel states, and path-privacy review (`tests/manual/gui_smoke_checklist.md:5`).
- Extend targeted GUI and PDF tests so Stage 5 locks presentation-sensitive regressions into the current `pytest` lane without requiring a new framework by default (`tests/unit/gui/test_main_window.py:34`, `tests/unit/render/test_pdf_renderer.py:71`, `pyproject.toml:18`).
- Add deterministic visual artifacts for QA, using offscreen PySide6 screenshots and generated sample PDFs as the baseline evidence path.

## Planned Implementation Touched Files

- `src/frameproof/gui/app.py`
- `src/frameproof/gui/main_window.py`
- `src/frameproof/gui/dependency_dialog.py`
- `src/frameproof/gui/view_state.py`
- `src/frameproof/gui/status_text.py`
- `src/frameproof/render/pdf_renderer.py`
- `tests/unit/gui/test_main_window.py`
- `tests/unit/render/test_pdf_renderer.py`
- `tests/manual/gui_smoke_checklist.md`
- `docs/stages/stage-05-implement.md`
- `docs/reports/dev/stage-05-handoff.md`

## Visual Acceptance Criteria

- The GUI keeps every Stage 4D-required control and shared-pipeline behavior, but the screen reads as clearly separated source, output/report, action, status, and results areas.
- Empty, loading, success, error, and cancelled states remain textually explicit and visually distinct without inventing any new state vocabulary.
- The progress table continues to stream updates without row reordering, and `partial` rows remain visually distinct from clean success rows.
- Dependency status wording remains exactly spec-compliant while the dialog becomes easier to scan with long paths and missing-tool states.
- `Layout B` respects the defined density policy and minimum legibility target; long warnings or metadata must wrap or spill instead of collapsing the page into unreadable text.
- `Layout A` keeps the same underlying capture facts but presents metadata, path, capture details, and warnings in a clearer typographic hierarchy with no overlap or clipped text in representative fixtures.
- Privacy modes remain truthful: when full paths are hidden, clips are still distinguishable in both the GUI and the PDF.

## Accessibility And Responsiveness Checklist

- The GUI remains usable at the current default size and at a reduced desktop window size such as `1024x720` without hiding required controls or clipping the primary action row.
- Keyboard tab order reaches source controls, report controls, dependency actions, start/cancel actions, and the progress table in a sensible sequence.
- Focus indication is visible for actionable widgets.
- Status meaning is never color-only; the existing status words remain visible.
- Long source paths, output paths, and dependency paths wrap or elide safely while preserving enough identity for operator decisions.
- Font fallback remains readable on hosts where `IBM Plex Sans` is unavailable, matching the Stage 4D QA observation that fallback may occur (`docs/stages/stage-04D-qa.md:65`).
- PDF typography does not regress below the token targets of `10pt` body text and `8.5pt` secondary metadata (`docs/ui-spec.md:256`).

## Verification Plan

### Required automated validation after implementation

- `python -m pytest`
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/unit/gui -vv`
- `python -m pytest tests/unit/render/test_pdf_renderer.py -vv`
- `ruff check .`
- `mypy src`

### GUI visual verification

- Extend `tests/manual/gui_smoke_checklist.md` with Stage 5-specific checks for resize behavior, keyboard flow, contrast, path privacy, and screenshot capture.
- Add an offscreen screenshot path for the main window and dependency dialog so QA can compare real GUI states without relying on ad hoc manual descriptions.
- Capture representative states at minimum for empty, running, success, cancelled, dependency-warning, and validation-error views.

### PDF visual verification

- Generate deterministic sample PDFs for both `Layout B` and `Layout A` using existing renderer fixtures.
- Keep or extend text assertions in `tests/unit/render/test_pdf_renderer.py`, then add artifact review steps that inspect header hierarchy, clipping, warning placement, and density on the generated PDFs.
- Prefer artifact-driven verification over semantic-only assertions for density-sensitive changes.

### Playwright feasibility decision

- Stage 5 should not assume Playwright is available because the repository does not currently define it (`pyproject.toml:18`).
- If an already-available external Playwright runtime can be used without adding a new repository dependency, Stage 5 implement may add a small static HTML/PDF visual harness and run screenshot checks against it.
- If that is not feasible, the accepted alternative is offscreen PySide6 screenshots plus deterministic PDF artifacts plus the expanded manual checklist. The implementation and QA docs must state explicitly why Playwright was not used.

## Risks And Mitigations

- Risk: visual cleanup could accidentally change approved status wording or shared-pipeline behavior.
- Mitigation: keep status-text assertions and current GUI unit coverage in place, then extend them only around presentation.
- Risk: PDF density tuning could introduce clipping or unreadable blocks for long metadata and warnings.
- Mitigation: add representative renderer fixtures with long names, long paths, and warning-heavy clips before tuning spacing rules.
- Risk: screenshot-based verification can be host-sensitive.
- Mitigation: use deterministic window sizes, offscreen rendering where possible, and keep the manual checklist as the fallback evidence path.

## Next Prompt

`[Stage 5-Implement]`
