# Stage 00 Plan

- lane: dev
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- next_recommended_prompt: `[Stage 0-Implement]`

## Scope

- Freeze Stage 0 as a docs-only orchestration phase.
- Identify the repository source-of-truth spec path and preserve it in durable docs.
- Define the durable memory roles for `docs/stage.md`, `docs/plan.md`, `docs/implement.md`, `docs/qa.md`, and the report directories under `docs/reports/`.
- Define the staged delivery contract from Stage 0 through Stage 7 and Stage R without implementing product functionality.

## Planned Touched Files

- `AGENTS.md`
- `docs/stage.md`
- `docs/plan.md`
- `docs/implement.md`
- `docs/qa.md`
- `docs/documentation.md`
- `docs/prompt.md`
- `docs/stages/stage-00-implement.md`
- `docs/reports/dev/stage-00-handoff.md`

## Risks

- Placeholder stage artifacts break the repository's isolated-session workflow because fresh workers cannot reconstruct the plan from durable files alone.
- Path or casing drift between documented prompt/report locations can send later workers to the wrong artifact.
- Any product-code work during Stage 0 would violate the approved gate and force QA failure.

## Assumptions

- `docs/frameproof_tech_spec_ko.md` is the repository-local source-of-truth specification for Stage 0 planning.
- The repository is greenfield for product code even though orchestration docs and scripts already exist.
- Stage 0 is limited to freezing requirements, workflow rules, and durable memory surfaces.
- Future sessions must rely on repository files only, not hidden chat context.

## Acceptance Criteria

- `docs/stages/stage-00-plan.md` records the source spec path, scope, touched files, risks, assumptions, acceptance criteria, validation plan, and exact next prompt.
- `docs/stage.md` records that Stage 0 planning is complete and routes the next worker to Stage 0 implementation.
- No product functionality is implemented in this phase.

## Validation Plan

- `pwd`
- `ls`
- `find . -maxdepth 3 -type f | sort | sed -n '1,120p'`
- Verify that the Stage 0 source spec exists at `docs/frameproof_tech_spec_ko.md` before implementation planning proceeds.

## Outcome

Stage 0 planning froze the docs-only boundary, the durable documentation surfaces, the stage-gate sequence, and the next legal prompt for implementation. No product code was introduced.

## Maintenance Note

This artifact was expanded during Stage 0-Fix to replace the original placeholder with the actual planning outcome already reflected elsewhere in the repository. The rewrite preserves the original Stage 0 scope and does not add new work.
