# Stage 02 Dev Handoff

- status: complete
- run_type: implement
- stage: stage-02
- lane: dev
- summary: Wrote the durable architecture and milestone-planning documents for Frame Proof without adding application code. Future fresh sessions can now implement the Stage 3 foundation layer from repository docs only.
- source_plan: `docs/stages/stage-02-plan.md`
- latest_artifact: `docs/stages/stage-02-implement.md`
- next_recommended_prompt: `[Stage 2-QA]`
- implementation_allowed_by_board: false
- qa_required: true

## Delivered Documents

- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/data-inventory.md`
- `docs/ui-spec.md`
- `docs/release-checklist.md`

## What These Docs Lock In

- one shared pipeline for CLI, GUI, PDF, manifest, and still export
- subprocess-only isolation for RAW adapters, including `BRAW`
- normalized schema ownership for `ClipInfo`, `CapturePoint`, and `ReportItem`
- requested-versus-actual capture reporting as a first-class invariant
- `Layout B` as the default report and `Layout A` as a renderer variant over the same data
- per-file failure continuation rules and the small set of fatal batch-stop conditions
- milestone mapping from Stage 3 foundation through Stage 7 release work

## Updated Files

- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/data-inventory.md`
- `docs/ui-spec.md`
- `docs/release-checklist.md`
- `docs/stages/stage-02-implement.md`
- `docs/implement.md`
- `docs/stage.md`
- `docs/reports/status/current-status.md`
- `docs/reports/dev/stage-02-handoff.md`

## Validation

- `test -f docs/architecture.md` -> PASS
- `test -f docs/api-contract.md` -> PASS
- `test -f docs/data-inventory.md` -> PASS
- `test -f docs/ui-spec.md` -> PASS
- `test -f docs/release-checklist.md` -> PASS
- `grep -R "BRAW" docs/architecture.md docs/api-contract.md` -> PASS
- `grep -R "CapturePoint" docs/data-inventory.md docs/api-contract.md` -> PASS
- `grep -R "Layout B" docs/ui-spec.md` -> PASS

## Known Issues

- Stage 2 QA has not run yet.
- No product code changed in this phase, so Stage 3 still starts from the Stage 1 bootstrap codebase.
- The durable source spec path in this repository is `docs/frameproof_tech_spec_ko.md`, not `docs/source/frameproof_tech_spec_ko.md`.

## Fresh Session Notes

- For Stage 2 QA, review the new docs against the source spec and confirm the board points to `[Stage 2-QA]`.
- For Stage 3 planning and implementation, treat `docs/architecture.md`, `docs/api-contract.md`, and `docs/data-inventory.md` as mandatory inputs.
- Do not create parallel GUI or RAW architectures later. Extend the shared pipeline defined in `docs/architecture.md`.
