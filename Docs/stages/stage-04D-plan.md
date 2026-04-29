# Stage 04D Plan

- lane: dev
- stage: stage-04D
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_4c_pass_verified: yes
- risk_level: moderate
- next_recommended_prompt: `[Stage 4D-Implement]`

## Gate Verification

- `docs/qa.md` records `latest_stage: stage-04C`, `latest_verdict: PASS`, `latest_gate: passed`, and `next_recommended_prompt: [Stage 4D-Plan]`.
- `docs/stages/stage-04C-qa.md` records `verdict: PASS`, `gate: passed`, and `stage_4d_status: unblocked-by-qa`.
- At session start, `docs/stage.md` recorded `current_stage: stage-04D`, `current_subphase: plan`, `last_result: stage-04C-qa-pass`, `qa_gate: pass`, and `implementation_allowed: false`.
- The required repo files for this session were read explicitly before planning: `AGENTS.md`, `docs/stage.md`, `docs/qa.md`, `docs/architecture.md`, `docs/ui-spec.md`, and `docs/stages/stage-04C-qa.md`.
- The required validation commands for this phase were executed:
- `cat docs/qa.md`
- `grep -R "PySide6" docs/ui-spec.md docs/architecture.md`
- `grep -R "Progress" docs/ui-spec.md`
- The `PySide6` grep returned direct Stage 4D UI-spec hits and no architecture-only `PySide6` implementation note, which reinforces the existing architecture rule that the GUI is a thin client over the shared pipeline rather than a separate subsystem.
- Stage 4D planning is therefore legal. This phase remains docs-only and must stop before implementation.

## Sprint Goal

- Add a real PySide6 desktop GUI that launches the existing batch pipeline without creating a GUI-only media-processing path.
- Reuse the current `AppSettings`, `DependencyInspector`, scanner, grouping, probe, capture, report, PDF, still-export, and manifest flow.
- Add truthful progress and dependency visibility for operators while preserving the same status vocabulary already used by CLI and report output.
- Add durable settings persistence for operator defaults and tool paths without redesigning the core pipeline or introducing a second config model.
- Add a start/cancel flow that is cooperative, safe, and explicit about what has already run versus what was skipped.

## Non-Scope

- No redesign of the scan/probe/capture/report pipeline.
- No replacement of the existing CLI entrypoint or CLI contract.
- No Stage 5 visual-polish work beyond the minimum functional PySide6 UI required by `docs/ui-spec.md`.
- No packaging, installer, or distribution work beyond the minimum GUI entrypoint needed for local launch.
- No fake progress events, placeholder rows, or demo-only data.
- No persistence format migration for CLI config files in this stage; Stage 4D should keep persistence focused on GUI operator defaults.

## Current Baseline

- `src/frameproof/cli.py` currently owns the real batch orchestration through `run_batch(settings)`.
- `src/frameproof/config/settings.py` already defines the validated runtime shape for inputs, capture options, report layout, output options, path privacy, and adapter paths.
- `src/frameproof/core/dependency_inspector.py` already exposes the dependency-state vocabulary required by the dependency screen:
- `available`
- `configured_missing`
- `not_configured`
- `runtime_error`
- `src/frameproof/core/models.py` already provides the clip, capture, and batch status vocabulary the GUI should display instead of inventing GUI-only states.
- No `src/frameproof/gui/` package exists yet, so Stage 4D must add the GUI surface cleanly without disturbing the current CLI-first package layout.

## Architectural Direction

- Keep one shared execution path. Stage 4D should extract the current orchestration in `src/frameproof/cli.py:run_batch()` into a shared batch-runner surface that both CLI and GUI call.
- Prefer a narrow extraction over a redesign:
- move the orchestration body into a new shared module such as `src/frameproof/core/batch_runner.py`
- keep CLI argument parsing and summary printing in `src/frameproof/cli.py`
- let the GUI call the same runner with the same validated `AppSettings`
- Add progress emission as an additive observer/callback layer on top of the existing runner. The pipeline order stays the same; the GUI only subscribes to truthful events.
- Keep batch-result truth anchored in existing domain types. The GUI may derive display rows from progress events and final `BatchReport`, but it must not compute alternate clip status semantics.

## GUI Scope

### Main window

- Source file picker and source folder picker.
- Include subfolders toggle, default on.
- Output PDF picker or output folder-assisted PDF target selection.
- Project name field.
- Middle frame count selector for `0` to `3`.
- Layout selector with `Contact Sheet (Layout B)` default and `Detailed File Report (Layout A)` secondary.
- Export still PNGs toggle, default off.
- Include CSV manifest toggle, default on.
- Include JSON manifest toggle, default on.
- Failed files section toggle, default on.
- Start and cancel buttons.
- Progress table with the required columns from `docs/ui-spec.md`.
- Status banner or footer for empty, loading, error, cancelled, and success summaries.

### Dependency check surface

- Show FFmpeg, FFprobe, MediaInfo, BRAW adapter, R3D adapter, and ARRI ART CMD state using `DependencyInspector`.
- Allow path editing and re-check.
- Explain that missing RAW tools disable only their format families.
- Surface the four required dependency states exactly as the UI spec names them.

### Shared screen states

- Empty:
- shown before any input selection
- explains accepted file/folder sources
- reminds the user that `Layout B` is default and PNG export is optional
- Loading:
- shown during scan, dependency refresh, probe, capture, render, and manifest write
- shows stage text plus processed/remaining counts
- keeps cancel available while work is active
- Error:
- invalid settings or output path
- dependency missing for some or all formats
- per-file probe failure
- per-file decode failure
- fatal render or write failure
- Success:
- shows generated PDF and manifest paths
- shows total, success, partial, failed, and skipped counts
- notes timecode fallback when applicable
- Cancelled:
- shows that no new work was started after cancel
- preserves already collected per-row diagnostics
- clearly distinguishes cancel from fatal failure

## Module And File Plan

- `src/frameproof/core/batch_runner.py` (new)
- shared batch orchestration extracted from the current CLI
- owns event emission, cancellation checks, and final `BatchRunOutcome`
- `src/frameproof/core/progress_events.py` (new)
- immutable progress/event dataclasses for scan, dependency, clip, render, manifest, cancel, and complete notifications
- `src/frameproof/cli.py`
- changed to call the shared batch runner and keep CLI summary behavior unchanged
- `src/frameproof/gui/__init__.py` (new)
- package marker plus minimal public exports
- `src/frameproof/gui/__main__.py` (new)
- GUI launch entrypoint so Stage 4D can validate `python -m frameproof.gui --help` or launch behavior without disturbing `python -m frameproof`
- `src/frameproof/gui/app.py` (new)
- top-level GUI bootstrap and application creation
- `src/frameproof/gui/main_window.py` (new)
- main window widgets, layout, and signal wiring
- `src/frameproof/gui/dependency_dialog.py` (new)
- dependency-check modal or dedicated panel
- `src/frameproof/gui/settings_store.py` (new)
- QSettings-backed persistence for GUI defaults and tool-path values
- `src/frameproof/gui/view_state.py` (new)
- GUI-facing immutable or narrowly mutable state objects for form values, row snapshots, and summary banners
- `src/frameproof/gui/batch_controller.py` (new)
- bridges GUI signals to the shared batch runner on a worker thread and maps runner events into Qt signals
- `tests/unit/core/test_batch_runner.py` (new)
- shared runner event and cancellation coverage
- `tests/unit/gui/test_settings_store.py` (new)
- persistence round-trip coverage without needing a full visible GUI
- `tests/unit/gui/test_batch_controller.py` (new)
- start/cancel signal flow and event mapping coverage
- `tests/unit/gui/test_main_window.py` (new if headless Qt is viable)
- basic widget-state, validation, and progress-table updates
- `docs/stages/stage-04D-implement.md`
- `docs/reports/dev/stage-04D-handoff.md`
- `docs/implement.md`

## State Ownership

| Concern | Owning layer |
|---|---|
| validated runtime settings | `frameproof.config.settings.AppSettings` |
| persisted GUI defaults | `frameproof.gui.settings_store` |
| dependency truth | `frameproof.core.dependency_inspector.DependencyInspector` |
| batch orchestration | shared `frameproof.core.batch_runner` |
| cancel intent | shared batch runner cancellation token / controller |
| live row snapshots | `frameproof.gui.batch_controller` plus GUI view state |
| final clip/report truth | `ReportItem`, `BatchReport`, `BatchSummary` |
| widget enable/disable state | `frameproof.gui.main_window` |

Rules:

- The GUI owns presentation state only.
- The shared batch runner owns work sequencing and progress-event emission.
- `AppSettings` remains the only runtime settings object passed into the core pipeline.
- QSettings stores operator defaults, not mutable batch execution truth.
- The final success or failure summary must come from the batch result and emitted events, not from inferred widget state.

## Threading And Process Strategy

- Keep the Qt UI thread read/write limited to widgets, view state, and user interaction.
- Run the shared batch runner on a background `QThread` via a `QObject` controller worker.
- Do not call scan, probe, capture, PDF render, still export, or manifest write on the UI thread.
- Reuse the existing subprocess behavior inside adapters exactly as it exists today; Stage 4D should not wrap RAW tools in a second process model.
- Progress updates should be emitted after real milestones:
- scan start and scan complete
- dependency refresh start and complete
- row discovered
- probe start and probe result
- capture start and capture result
- PDF render start and complete
- manifest write start and complete
- batch success, batch failure, or batch cancelled
- Row ordering must be based on grouped candidate order and must not reorder as statuses update.

## Start And Cancel Flow

### Start

- Validate form inputs locally before launching background work.
- Persist the latest form values to QSettings before starting the batch.
- Build one `AppSettings` mapping from current form state.
- Clear prior progress summary and table state.
- Refresh dependency status before batch start so obvious path mistakes are visible immediately.
- Launch the shared batch runner on the worker thread and disable inputs that should not change mid-run.

### Cancel

- Cancel is cooperative, not a fake immediate reset.
- The controller sets a cancellation token checked by the shared runner:
- before scan starts
- between grouped clips
- before render/export/write stages
- after any in-flight clip finishes
- Required Stage 4D cancel behavior:
- no new clip work starts after cancel is requested
- the current in-flight clip may finish or fail naturally
- already collected row diagnostics remain visible
- the batch exits as `cancelled`, not `failed`, unless a real fatal error happened first
- If later implementation can safely interrupt adapter subprocesses without destabilizing the pipeline, that can be additive, but Stage 4D should not depend on invasive adapter redesign.

## Settings Persistence Plan

- Use Qt `QSettings` for Stage 4D GUI persistence because it is OS-native, lightweight, and avoids introducing a second handwritten config parser in this stage.
- Persist the following values:
- last selected source paths
- include-subfolders toggle
- last output PDF path or output folder helper value
- project name
- middle count
- layout
- export-stills toggle
- include CSV / JSON toggles
- include failed files toggle
- path privacy mode
- ffmpeg path
- ffprobe path
- mediainfo path
- braw adapter path
- r3d adapter path
- arri art cmd path
- QSettings values should be translated into the existing `AppSettings.from_mapping()` input shape at run start.
- Validation still belongs to `AppSettings`; QSettings is only persistence, not truth.
- Missing or invalid persisted paths should not block app startup. They should surface through the dependency screen and form validation instead.
- Stage 4D should avoid persisting ephemeral run data such as per-row progress or temporary staging paths.

## Progress Table Strategy

- Required columns remain:
- `Clip`
- `Format`
- `Probe`
- `Capture`
- `PDF`
- `Warning`
- A row is created when grouped candidates are known, not after the clip is done.
- `Format` comes from adapter resolution or normalized clip metadata.
- `Probe` and `Capture` show `waiting`, `running`, `success`, `partial`, or `fail` based on real event transitions and final report state.
- `PDF` is a clip-level inclusion signal:
- `waiting` before render
- `included` when the clip is in the final report
- `skipped` for unsupported or dependency-missing cases
- `failed` when a final fatal output error prevents inclusion truthfully
- `Warning` shows the first concise warning or error summary, with fuller text available in a detail pane, tooltip, or status area if implemented.

## Dependency-Missing UX

- Dependency gaps must be visible before the run and during the run.
- Mixed-format batches must not be blocked by missing unrelated tools.
- If every discovered clip is unprocessable because required dependencies are missing, the GUI should show a fatal error summary consistent with the CLI fatal-batch rule.
- If only some clips are blocked, the GUI should continue and show those rows as `dependency_missing` or skipped in a visibly distinct way.
- Dependency screen wording must stay truthful:
- `available`
- `configured path missing`
- `not configured`
- `runtime startup failure`

## Acceptance Criteria For Stage 4D Implement

- The repository gains a launchable PySide6 GUI entrypoint without breaking the existing CLI entrypoint.
- The GUI uses the shared batch runner and does not duplicate scan/probe/capture/report logic in GUI-only code.
- The main window exposes the required source, output, middle-count, layout, still-export, start, cancel, and progress-table controls.
- The dependency check surface shows all required tools and supports the four required dependency states.
- GUI settings persist across launches for the required operator defaults and tool paths.
- Start runs the existing pipeline with validated `AppSettings`.
- Cancel prevents new work from starting, preserves completed diagnostics, and ends in a visible cancelled state.
- Empty, loading, error, success, and dependency-missing states are implemented explicitly.
- Progress rows are created in grouped clip order and update without reordering.
- The GUI shows final PDF and manifest paths on success and surfaces fatal output failures truthfully.
- Automated tests cover the shared batch runner, settings persistence, and GUI controller behavior where practical.
- If full GUI automation is limited headlessly, the repo includes an executable manual verification checklist and smoke launch instructions instead of pretending those checks ran.

## Validation Plan

### Automated

- `python -m pytest`
- `ruff check .`
- `mypy src`
- `python -m frameproof --help`
- `python -m frameproof.gui --help` or the exact documented GUI launch command

Unit and component focus:

- shared batch-runner event ordering and final-result parity with the existing CLI behavior
- cancellation token behavior between clips and before output stages
- settings-store round trips for persisted values
- dependency-dialog or dependency-state mapping
- main-window validation for required fields and button enablement
- progress-table row updates from emitted events

### Manual

- launch GUI
- select files or folder, output path, layout, and middle count
- verify settings persist after closing and reopening
- open dependency screen and confirm missing-tool states render truthfully in this environment
- run a dependency-missing batch and verify row/status messaging
- if processable media and tools are available, run a happy-path batch and verify PDF/manifests are produced and shown in the success state
- start a larger run and cancel mid-batch; verify no new rows begin after cancel and the summary reads cancelled

## Risks And Watchpoints

- The main technical risk is extracting a shared batch-runner seam from `src/frameproof/cli.py` without accidentally changing CLI behavior.
- GUI cancel must remain truthful. A fake instant reset would violate the UI spec and make row state unreliable.
- Dependency refresh may be slow because runtime checks can invoke real executables; that work must stay off the UI thread.
- A full widget-level headless GUI test may be environment-sensitive. Stage 4D should bias toward well-tested controller/state layers plus a documented manual smoke path if needed.
- Stage 4D must not drift into a second settings model. Persisted GUI values should translate directly into the existing validated mapping shape.

## Next Prompt

- `[Stage 4D-Implement]`

## Validation Commands Run For This Plan Phase

- `cat docs/qa.md`
- `grep -R "PySide6" docs/ui-spec.md docs/architecture.md`
- `grep -R "Progress" docs/ui-spec.md`

## Touched Files In This Plan Phase

- `docs/stages/stage-04D-plan.md`
- `docs/stage.md`
