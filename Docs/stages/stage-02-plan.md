# Stage 02 Plan

- lane: dev
- stage: stage-02
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_1_pass_verified: yes
- next_recommended_prompt: `[Stage 2-Implement]`

## Gate Verification

- `docs/qa.md` records `latest_verdict: PASS`, `latest_gate: passed`, and `next_recommended_prompt: [Stage 2-Plan]`.
- `docs/reports/qa/stage-01-qa-report.md` records `gate: PASS`, `verdict: PASS`, and `stage_2_status: unblocked-by-qa`.
- `docs/stage.md` was stale when this session started and still reflected the earlier rerun-needed state. This plan corrects the board to match the durable QA PASS evidence.

## Scope

- Freeze the documentation-only architecture planning needed before Stage 3 foundation code begins.
- Define the durable document set that Stage 2 implement must write: architecture, adapter/API contract, data inventory and schemas, UI spec, and release checklist.
- Preserve the source spec's decisions for adapter-based processing, normalized schemas, capture planning, timecode priority, PDF layouts, GUI plus CLI surfaces, manifest outputs, per-file failure handling, and RAW subprocess isolation.
- Map Stage 3 through Stage 7 into concrete milestone slices that future fresh sessions can follow without hidden context.
- Document the validation and acceptance shape for later implementation without writing application code or the full architecture docs in this phase.

## Non-Scope

- No Python application code changes.
- No architecture-doc implementation yet beyond this planning artifact.
- No new product scope beyond `docs/frameproof_tech_spec_ko.md` and the already established repo prompts.
- No fake adapter behavior, mock feature claims, or speculative packaging commitments that the spec does not support.

## Planning Basis

- `docs/frameproof_tech_spec_ko.md` defines the core product contract: adapter-based media processing, normalized metadata, start/middle/end capture planning, timecode precedence, Layout B as default PDF output, Layout A as an option, CLI and GUI support, CSV/JSON manifests, failure handling, performance defaults, and file-safety constraints.
- `docs/plan.md` already sequences delivery as CLI-first with normalized contracts before GUI and packaging.
- `docs/prompts/stage3_plan.md` through `docs/prompts/stage7_plan.md` define the downstream stage boundaries, so this Stage 2 plan must align with those prompts instead of inventing a competing milestone map.
- The repository currently contains only Stage 1 bootstrap code, so Stage 2 must produce durable design documents that unblock implementation without introducing parallel architecture.

## Planned Touched Docs In Stage 2 Implement

- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/data-inventory.md`
- `docs/ui-spec.md`
- `docs/release-checklist.md`
- `docs/stages/stage-02-implement.md`
- `docs/reports/dev/stage-02-handoff.md`
- `docs/implement.md`
- `docs/stage.md`

## Planned Deliverable Content

### `docs/architecture.md`

- Module boundaries for scanner, clip grouping, adapter resolver, probe service, capture planner, capture service, metadata normalizer, timecode utilities, renderers, manifest writer, still exporter, settings, CLI, and GUI orchestration.
- End-to-end data flow from input selection through PDF/manifests and failure reporting.
- RAW subprocess isolation boundaries for BRAW, R3D, and ARRIRAW adapters.
- Concurrency defaults and ownership rules so Stage 3 through Stage 6 reuse one pipeline rather than split into separate code paths.

### `docs/api-contract.md`

- Shared Python adapter interface for `probe()` and `capture()`.
- JSON request/response contracts for RAW subprocess clients.
- Error/status payload rules, including `dependency_missing`, `probe_failed`, `decode_failed`, `partial_success`, and related status semantics.
- R3D logical clip grouping expectations and dependency detection responsibilities.

### `docs/data-inventory.md`

- Canonical field inventories for `ClipInfo`, `CapturePoint`, `ReportItem`, config/settings objects, and manifest rows.
- Candidate keys, nullability rules, source-of-truth ownership, and adapter-to-normalized-schema mappings.
- Capture planning data requirements for `middle_count`, requested versus actual positions, duplicate-collapse tracking, and timecode labels.
- Manifest column requirements and PDF/manifest parity rules.

### `docs/ui-spec.md`

- CLI option shape and GUI screen inventory.
- Layout B default contact-sheet rules and Layout A detailed-report rules.
- Empty/loading/error/success states, dependency-missing UX, progress table behavior, and cancellation expectations.
- Design tokens draft covering color, typography, spacing, iconography, density, and preview-only labeling.

### `docs/release-checklist.md`

- Dependency path verification for FFmpeg, FFprobe, MediaInfo, BRAW, R3D, and ARRI tooling.
- Smoke-test commands for CLI, renderer outputs, manifests, and GUI startup once those surfaces exist.
- Packaging, licensing, file-safety, known-issues disclosure, and release-readiness checks.
- Cross-stage completion checklist tied to the spec acceptance criteria.

## Test Strategy Plan

There will not be a standalone `docs/test-strategy.md` in Stage 2 because the downstream prompts already depend on `docs/architecture.md`, `docs/api-contract.md`, `docs/data-inventory.md`, and `docs/release-checklist.md`. Stage 2 implement should distribute test strategy content across those durable docs:

- `docs/api-contract.md`: adapter contract tests, subprocess JSON validation, dependency-missing cases.
- `docs/data-inventory.md`: schema validation, capture planner edge cases, timecode and nullability rules, manifest parity checks.
- `docs/architecture.md`: integration boundaries, ownership of end-to-end validation, and concurrency/failure assumptions.
- `docs/release-checklist.md`: smoke tests, regression gates, manual QA, and release verification.

Required test themes to preserve from the spec:

- short clips and duplicate capture collapse
- frame-count priority with duration fallback
- `floor(x + 0.5)` rounding consistency
- VFR handling and elapsed fallback
- drop-frame versus non-drop display rules
- dependency-missing degradation without fake success
- per-file failure continuation unless a fatal batch-stop condition is hit
- PDF and manifest parity for actual capture data
- non-ASCII paths, long clips, damaged clips, and unwritable output paths

## Stage Breakdown For Later Delivery

### Stage 3

- Foundation build only: schemas, settings, capture planner, timecode helpers, adapter base interfaces, status model, and unit tests.
- No FFmpeg capture, RAW execution, PDF rendering, or GUI yet.

### Stage 4A

- Standard-video CLI pipeline: scanner, standard adapter using FFprobe plus FFmpeg with MediaInfo fallback, probe/capture services, Layout B renderer, manifest writing, and end-to-end CLI flow.

### Stage 4B

- RAW adapter integration: BRAW, R3D, and ARRIRAW subprocess clients, dependency detection, contract fixtures, and R3D multi-part grouping behavior.

### Stage 4C

- Reporting expansion: Layout A, PNG still export, filename sanitization, collision suffixing, failed/partial clip sections, and stronger PDF/manifest parity.

### Stage 4D

- PySide6 GUI: settings persistence, dependency screen, progress table, start/cancel flow, and GUI reuse of the existing pipeline.

### Stage 5

- UI and report refinement only: visual clarity, accessibility, responsiveness, feedback quality, and visual verification artifacts.

### Stage 6

- Hardening: edge-case coverage, damaged media, security and file-safety checks, performance smoke passes, error handling, and cleanup.

### Stage 7

- Release wrap-up: setup and dependency docs, smoke validation, known-issues disclosure, backlog capture, final report, and fresh-developer handoff materials.

## Risks

- If Stage 2 implement drifts from the prompt-defined document set, later stages will lose their required inputs and fresh-session continuity will break.
- If the docs under-specify requested versus actual capture data, Stage 3 and Stage 4 work will diverge between capture logic, manifests, and PDFs.
- If RAW subprocess isolation is treated as optional, later stages risk crashes or dependency coupling that contradict the source spec.
- If the UI spec redesigns the pipeline instead of consuming shared core contracts, Stage 4D will create parallel architecture and rework.
- If the release checklist hides proprietary SDK constraints, Stage 7 may falsely present the product as self-contained.

## Assumptions

- `docs/frameproof_tech_spec_ko.md` remains the authoritative source spec for product behavior.
- The lowercase `docs/` tree remains the active durable-memory surface for this workflow.
- Stage 2 implement will remain docs-only and will not add application code.
- Later stage prompts already represent the approved milestone structure, so this plan aligns to them rather than redefining them.
- A distributed test-strategy plan is acceptable because no downstream prompt requires a dedicated `docs/test-strategy.md` file.

## Acceptance Criteria

- `docs/stages/stage-02-plan.md` records Stage 1 PASS verification, scope, non-scope, planning basis, touched docs, risks, assumptions, acceptance criteria, validation plan, and the exact next prompt.
- The plan explicitly covers architecture, API/adapter contract, data inventory and schemas, UI spec and design tokens, release checklist content, test strategy, and the Stage 3 through Stage 7 milestone map.
- The plan preserves the source spec's adapter model, RAW subprocess isolation, capture/timecode rules, layout rules, manifest requirements, and failure-handling rules without adding unsupported scope.
- `docs/stage.md` is updated so the next legal prompt is `[Stage 2-Implement]`.
- No architecture docs or application code are written in this phase.

## Validation Plan

- `cat docs/stage.md`
- `cat docs/qa.md`
- `find docs -maxdepth 3 -type f | sort`
- confirm `docs/reports/qa/stage-01-qa-report.md` still records PASS before Stage 2 implementation begins

## Exact Next Prompt

`[Stage 2-Implement]`

## Outcome

Stage 2 planning is complete. The next phase should write the durable architecture and contract documents that Stage 3 through Stage 7 will consume, while keeping this stage documentation-only and preserving the source spec decisions.
