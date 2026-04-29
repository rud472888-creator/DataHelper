# Stage 02 Implement

- lane: dev
- subphase: implement
- status: complete
- scope_boundary: architecture-and-planning-docs-only
- next_recommended_prompt: `[Stage 2-QA]`

## Delivered Scope

- Wrote the durable architecture document for the shared Frame Proof pipeline.
- Defined the adapter API contract for Python interfaces and RAW subprocess JSON envelopes.
- Defined the normalized data inventory for `ClipInfo`, `CapturePoint`, `ReportItem`, and manifest rows.
- Defined the CLI, GUI, `Layout B`, and `Layout A` UI specification with states and design-token draft.
- Defined the release checklist covering dependencies, smoke validation, packaging, licensing, and file safety.
- Updated the stage ledger and Dev handoff so a fresh Stage 3 session can continue from repository docs only.

## Changed Files And Reasons

- `docs/architecture.md` fixes module boundaries, data flow, subprocess isolation rules, concurrency defaults, and the v1 requirement map.
- `docs/api-contract.md` fixes the shared adapter interface, `BRAW` and other RAW subprocess request and response envelopes, and normalized status semantics.
- `docs/data-inventory.md` defines canonical data entities, `CapturePoint` field rules, nullability, candidate keys, and manifest parity.
- `docs/ui-spec.md` defines CLI and GUI surfaces, `Layout B` and `Layout A`, state handling, density rules, and draft design tokens.
- `docs/release-checklist.md` defines dependency checks, smoke-test scope, packaging constraints, and release gates.
- `docs/implement.md` now records Stage 2 implementation decisions, changed files, validation evidence, and next prompt.
- `docs/stage.md` advances the board to fresh Stage 2 QA.
- `docs/reports/status/current-status.md` mirrors the updated board state for fresh sessions.
- `docs/stages/stage-02-implement.md` records this implementation phase.
- `docs/reports/dev/stage-02-handoff.md` provides the durable Dev handoff.

## Implementation Decisions

- Kept Stage 2 documentation-only as required. No application code, fake adapters, or placeholder implementation was added.
- Chose one shared pipeline for CLI and GUI so later stages cannot drift into separate orchestration paths.
- Locked RAW handling behind subprocess-only clients to preserve the source spec's isolation and crash-containment model.
- Treated requested-versus-actual capture facts as first-class data so renderer, manifests, and progress UI all consume the same `CapturePoint` records.
- Mapped every major v1 requirement to a module or later delivery stage to keep Stage 3 through Stage 7 aligned with the source spec.

## Data/API/State Ownership Changes

- Stage 3 is now expected to implement the durable schema and contract layer described in `docs/architecture.md`, `docs/api-contract.md`, and `docs/data-inventory.md`.
- The report surfaces are now contractually tied to the same `ReportItem` and `CapturePoint` data model.
- Durable workflow state is updated in `docs/stage.md`, `docs/implement.md`, and `docs/reports/`.

## Validation Results

- `test -f docs/architecture.md` -> PASS
- `test -f docs/api-contract.md` -> PASS
- `test -f docs/data-inventory.md` -> PASS
- `test -f docs/ui-spec.md` -> PASS
- `test -f docs/release-checklist.md` -> PASS
- `grep -R "BRAW" docs/architecture.md docs/api-contract.md` -> PASS
- `grep -R "CapturePoint" docs/data-inventory.md docs/api-contract.md` -> PASS
- `grep -R "Layout B" docs/ui-spec.md` -> PASS

## Blockers And Known Gaps

- Stage 2 still requires a fresh QA pass before Stage 3 planning or implementation may begin.
- No application code changed in this phase by design, so the repo still has only the Stage 1 bootstrap implementation.
- The prompt-listed spec path `docs/source/frameproof_tech_spec_ko.md` does not exist in this repository. This stage used the repository-local authoritative copy at `docs/frameproof_tech_spec_ko.md`.

## Fresh Session Notes

- Use `docs/frameproof_tech_spec_ko.md` as the repository-local source spec until the docs tree changes explicitly.
- Stage 3 should read `docs/architecture.md`, `docs/api-contract.md`, and `docs/data-inventory.md` before implementing foundation code.
- Do not implement FFmpeg capture, RAW adapters, PDF rendering, or GUI work in Stage 3 beyond the base contracts and reusable foundation models allowed by that stage prompt.
