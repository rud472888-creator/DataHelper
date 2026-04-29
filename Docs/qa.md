# QA Overview

Use this file as the top-level QA source of truth across isolated sessions.

## Current QA State

- latest_stage: stage-07
- latest_verdict: PASS
- latest_gate: passed
- latest_report: `docs/reports/qa/stage-07-qa-report.md`
- next_recommended_prompt: none

## Stage 07

- verdict: PASS
- summary: Independent QA re-verified the Stage 7 release-wrap documentation and final readiness gate in a fresh session against the required docs, Stage 7 plan and handoff artifacts, current packaging metadata, and the current test tree. `python -m frameproof --help`, `python -m frameproof config`, `python -m frameproof config --format json`, `python -m pytest`, `ruff check .`, `mypy src`, `python -m frameproof.gui --help`, and `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` all passed; README-linked docs all exist; the documented dependency-missing smoke remained explicit and artifact-clean; and the final report is honest about known issues, backlog, and the host-specific absence of `ffmpeg`, `ffprobe`, and proprietary RAW tools. README commands that could not be executed meaningfully in this sandbox, such as fresh-install console-script verification and interactive GUI launch, were inspected instead, with the host limitation recorded explicitly. The final Stage 7 gate therefore passes and the project is release-ready.
- blocker: none
- next_recommended_prompt: none

## Stage 06

- verdict: PASS
- summary: Independent QA re-verified Stage 6 in a fresh session against the Stage 6 plan, implementation notes, dev handoff, release checklist, current hardening code, and current tests. The current tree clears the gate: `python -m pytest` passed with `95 passed, 9 skipped`, `ruff check .` passed, `mypy src` passed, the documented Stage 6 CLI smokes returned the expected structured fatal and dependency-missing output without leaving behind PDF/CSV/JSON artifacts, `python -m frameproof.gui --help` passed, `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` passed, and the direct GUI pytest lane executed with `6 passed`. Source inspection and targeted test review confirm early output-target validation, partial-output cleanup, source-byte preservation, traversal-safe still export, manifest failure-row parity, path-privacy messaging, and the required `middle_count`/short-clip/export/dependency-missing acceptance cases are covered in the current repo. The earlier Stage 6 QA FAIL report is stale relative to the current repository state, so Stage 7 is now unblocked.
- blocker: none
- next_recommended_prompt: `[Stage 7-Plan]`

## Stage 05

- verdict: PASS
- summary: Independent QA re-verified Stage 5 in a fresh session against the Stage 5 plan, implementation notes, fix note, dev handoff, UI spec, current GUI and PDF source, current tests, and the regenerated Stage 5 artifacts. The current tree clears the gate: `python -m pytest` passed with `87 passed, 2 skipped`, `ruff check .` passed, `mypy src` passed, `python scripts/generate_visual_artifacts.py` regenerated the Stage 5 evidence, direct offscreen probing confirmed `minimumSizeHint=879x707`, `actual_1024=1024x720`, and `actual_1280=1280x860`, and the generated `Layout B` and `Layout A` PDFs include the required preview-only disclaimer plus the required Layout A detail fields. GUI screenshots and OCR confirm the intended Stage 5 hierarchy and explicit status copy, so Stage 6 is unblocked.
- blocker: none
- next_recommended_prompt: `[Stage 6-Plan]`

## Stage 04D

- verdict: PASS
- summary: Independent QA re-verified the Stage 4D GUI implementation in a fresh session against the Stage 4D plan, implementation notes, dev handoff, UI spec, current GUI/core code, current tests, and current command outputs. The current tree now clears the full Stage 4D gate: `python -m pytest` passes with `82 passed, 2 skipped`, `ruff check .` passes, `mypy src` passes, `python -m frameproof.gui --help` passes, `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test` succeeds on this host, the GUI pytest lane executes directly with `3 passed`, and targeted offscreen widget inspection confirms the required controls, dependency wording, settings persistence, and progress table. The GUI remains thin over the shared `run_batch()` pipeline and does not implement a parallel media-processing path, so Stage 5 is unblocked.
- blocker: none
- next_recommended_prompt: `[Stage 5-Plan]`

## Stage 04C

- verdict: PASS
- summary: Independent QA re-verified Stage 4C against the plan, fix handoff, UI spec, data inventory, current implementation, current tests, direct detail-PDF and manifest artifacts, still-export artifacts, and an invalid-input CLI dependency-path check. The required automated suite passes, `Layout A` now includes the required `requested_ratio` field, still export remains off by default, sanitized still-export filenames and collision suffixes behave correctly when enabled, and failed or partial clips remain visible in both PDF and manifest outputs. FFmpeg-backed live standard-video smoke remains environment-blocked because `ffmpeg` and `ffprobe` are absent here, but that path is conditional in the prompt and the inspected artifacts satisfy the Stage 4C gate.
- blocker: none
- next_recommended_prompt: `[Stage 4D-Plan]`

## Stage 04B

- verdict: PASS
- summary: Independent QA re-verified Stage 4B RAW adapter routing, dependency inspection, subprocess isolation, malformed-response handling, and RAW-only fatal batch behavior in a fresh session. `ffmpeg`, `ffprobe`, `mediainfo`, `braw_adapter`, `r3d_adapter`, `art-cmd`, and `arri_art_cmd` are all absent in this environment, so real vendor-binary smoke is blocked here; within that constraint, the required automated suite passed, a real CLI RAW-only batch surfaced truthful `dependency_missing` diagnostics for all RAW families, malformed JSON handling is covered by unit tests, and a direct subprocess-crash smoke confirmed structured failure normalization instead of fake success.
- blocker: none
- next_recommended_prompt: `[Stage 4C-Plan]`

## Stage 04A

- verdict: PASS
- summary: Independent QA re-verified the Stage 4A CLI surface, required test/static-analysis commands, fatal dependency-missing behavior, and non-fatal deferred-format batch behavior in a fresh session. `ffmpeg` and `ffprobe` are unavailable on this machine, so full happy-path standard-video artifact generation remains environment-blocked here; within that constraint, the CLI now reports `dependency_missing` explicitly, suppresses outputs on the fatal all-standard dependency-missing path, continues non-fatal deferred-format batches, derives default manifest paths correctly, and leaves PNG export off by default.
- blocker: none
- next_recommended_prompt: `[Stage 4B-Plan]`

## Stage 03

- verdict: PASS
- summary: Independent QA verified the Stage 3 foundation implementation directly against the source spec, architecture, API contract, data inventory, current code, tests, and required command output. Capture planner rounding, short-clip duplicate preservation, `middle_count` validation, shared schema fidelity, adapter base contracts, and timecode fallback rules are all correct in the current tree, so Stage 4A is unblocked.
- blocker: none
- next_recommended_prompt: `[Stage 4A-Plan]`

## Stage 02

- verdict: PASS
- summary: Independent QA verified the Stage 2 architecture, API, data, UI, and release documents directly against the repository tech spec and planning docs. The Stage 2 doc set is complete, materially faithful to the source spec, concrete on adapter and RAW subprocess contracts, and clear enough to unblock Stage 3 planning without hidden context.
- blocker: none
- next_recommended_prompt: `[Stage 3-Plan]`

## Stage 01

- verdict: PASS
- summary: Independent QA verified the actual Stage 1 repository state in a fresh session. The exact required commands now pass, the package is importable, the CLI remains honest about missing scan/capture/PDF functionality, and the Dev handoff docs contain the expected durable structure.
- blocker: none
- next_recommended_prompt: `[Stage 2-Plan]`

## Stage 00

- verdict: PASS
- summary: Stage 0 durable memory and orchestration docs are complete, docs-only, and materially faithful to `docs/frameproof_tech_spec_ko.md`. The stage artifacts, ledgers, and Dev handoff support fresh-session continuation without hidden context.
- blocker: none
- next_recommended_prompt: `[Stage 1-Plan]`
