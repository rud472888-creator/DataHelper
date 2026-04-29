Metadata
Stage ID: 0
Sub-phase: Plan
Lane: Dev
Required input files: frameproof_tech_spec_ko.md or docs/source/frameproof_tech_spec_ko.md
Required output files: docs/stages/stage-00-plan.md, docs/stage.md
Gate condition: Stage 0 planning complete; no implementation started.
Next recommended prompt: [Stage 0-Implement]
Stop condition: Stop after writing the Stage 0 plan and next prompt reference.

Execution contract
This prompt is intended to run as a fresh `codex exec` session. Do not use `codex exec resume`. Do not rely on previous chat context, terminal context, hidden memory, local Codex transcripts, or prior session state. Read the required repository files explicitly before acting. Use only durable repository files as cross-session memory. Stop after completing this phase. Do not proceed to the next phase until the user provides the next prompt.

Goal
Freeze the product target, source-of-truth documents, working rules, and durable memory plan for Frame Proof PDF Generator. Do not implement product functionality.

Context
The source specification describes a local CLI/desktop tool that scans video/RAW files, probes metadata, captures Start/Mid/End frames, renders PDF reports, and writes CSV/JSON manifests. BRAW/R3D/ARRIRAW require adapter-based subprocess handling.

Constraints
- Do not implement application code in this phase.
- Treat OpenClaw as orchestrator/controller/reporter, not implementer.
- Use repository files only as durable memory.
- If the source spec is not present, create a blocking note in docs/stage.md and docs/stages/stage-00-plan.md instead of inventing requirements.
- Existing repo context is unknown; assume Greenfield unless repository files clearly prove otherwise.
- Do not depend on previous Codex sessions, transcripts, or hidden memory.

Deliverables
- Identify the source-of-truth spec path.
- Create or plan creation of AGENTS.md and docs skeleton.
- Define stage gates from Stage 0 through Stage 7 and Stage R.
- Define durable memory roles for docs/stage.md, docs/implement.md, docs/qa.md, docs/reports/dev, docs/reports/qa, docs/reports/final.
- Record assumptions, risks, acceptance criteria, validation plan, and exact next prompt.

Done when
- docs/stages/stage-00-plan.md exists and contains scope, touched files, risks, assumptions, acceptance criteria, validation plan, and next prompt.
- docs/stage.md exists or is planned with current_stage=0, current_subphase=Plan, gate_status=PLAN_COMPLETE.
- No product implementation has been performed.

Validation
Run:
- pwd
- ls
- find . -maxdepth 3 -type f | sort | sed -n '1,120p'
- test -f frameproof_tech_spec_ko.md || test -f docs/source/frameproof_tech_spec_ko.md

Reporting
Write a concise Stage 0 planning report in docs/stages/stage-00-plan.md. Include any missing source files as blockers.

Update files
Update only planning/status documentation needed for Stage 0 planning.

Stop rule
Stop immediately after documenting the plan and next recommended prompt. Do not proceed to Stage 0 implementation.
