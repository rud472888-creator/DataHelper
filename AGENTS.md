# AGENTS.md - Repo Delivery Orchestrator

This repository uses Hermes as the delivery orchestrator.

## Role Model

- Hermes is the controller, launcher, gate keeper, reporter, and recovery manager.
- Dev lane workers run Plan / Implement / Fix only.
- QA lane workers validate only and must return explicit PASS or FAIL.

## Hard Rules

- Every Plan / Implement / QA / Fix run must use a fresh Codex session.
- Dev and QA must never rely on prior hidden chat context.
- Repository markdown files are the only durable workflow memory.
- QA must not silently fix implementation.
- No stage may advance without explicit QA PASS.
- Missing reports block advancement.

## Core State Files

- `docs/stage.md`
- `docs/reports/status/current-status.md`
- `docs/reports/dev/stage-XX-handoff.md`
- `docs/reports/qa/stage-XX-qa-report.md`

## Allowed Flow

Plan -> Implement -> QA -> Fix if needed -> Re-QA -> next stage only after QA PASS
