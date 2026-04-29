# Stage 07 Plan

- lane: dev
- stage: stage-07
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_6_pass_verified: yes
- risk_level: high
- next_recommended_prompt: `[Stage 7-Implement]`

## Gate Verification

- `docs/qa.md:7` through `docs/qa.md:18` record `latest_stage: stage-06`, `latest_verdict: PASS`, `latest_gate: passed`, and `next_recommended_prompt: [Stage 7-Plan]`.
- `docs/stages/stage-06-qa.md:5` through `docs/stages/stage-06-qa.md:8` record `verdict: PASS`, `gate: passed`, and `stage_7_status: unblocked-by-qa`.
- `docs/stages/stage-06-qa.md:12` through `docs/stages/stage-06-qa.md:16` document the fresh Stage 6 QA rerun and confirm that the earlier fail report is stale relative to the current repository state.
- At session start, `docs/stage.md:3` through `docs/stage.md:15` recorded Stage 7 Dev planning with the QA gate passed, no blocker, and implementation still disallowed.
- The required planning inputs were read explicitly before drafting this file: `AGENTS.md`, `docs/stage.md`, `docs/qa.md`, `docs/release-checklist.md`, `docs/implement.md`, and `docs/stages/stage-06-qa.md`.
- The required validation commands for this phase were executed:
- `cat docs/qa.md`
- `cat docs/release-checklist.md`
- `find . -maxdepth 3 -type f | sort | sed -n '1,260p'`
- Stage 7 planning is therefore legal. This phase remains docs-only and stops before release-wrap implementation.

## Release Goal

- Make the repository usable by a fresh developer or operator without hidden session context: product overview, setup, dependency expectations, CLI and GUI entrypoints, smoke commands, outputs, known issues, and release handoff.
- Replace bootstrap-stage messaging with documentation that matches the implemented shared pipeline, GUI surface, manifests, still export, and dependency behavior (`README.md:3`, `src/frameproof/cli.py:27`, `src/frameproof/cli.py:47`, `src/frameproof/cli.py:75`, `src/frameproof/gui/__main__.py:9`).
- Keep the release docs faithful to the one-pipeline architecture and the RAW subprocess boundary instead of implying an alternate GUI path or bundled proprietary SDK support (`docs/architecture.md:3`, `docs/architecture.md:7`, `docs/architecture.md:9`, `docs/architecture.md:112`, `docs/architecture.md:116`).

## Non-Scope

- No new product features, adapters, packaging code, or installer implementation.
- No claims that FFmpeg, FFprobe, MediaInfo, `BRAW`, R3D, or ARRI tools are bundled unless the repository actually provides and legally supports that distribution path (`docs/release-checklist.md:7`, `docs/release-checklist.md:9`, `docs/release-checklist.md:10`, `docs/release-checklist.md:28`).
- No release-ready declaration unless the documented smoke path is accurate for the host where it is claimed and the remaining dependency or licensing blockers are stated plainly (`docs/release-checklist.md:46`, `docs/release-checklist.md:54`, `docs/release-checklist.md:87`, `docs/release-checklist.md:94`).
- No implementation work in this phase.

## Current Release-Doc Baseline

- `README.md` still describes the repository as a bootstrap-stage shell where scan, capture, PDF rendering, and manifest generation are not implemented, which is now materially false for the current tree (`README.md:3`, `README.md:7`).
- The real CLI surface already supports pipeline execution inputs, recursive scan control, `middle_count`, both report layouts, optional manifests, optional still export, project naming, and adapter-path overrides (`src/frameproof/cli.py:27`, `src/frameproof/cli.py:47`, `src/frameproof/cli.py:55`, `src/frameproof/cli.py:65`, `src/frameproof/cli.py:75`, `src/frameproof/cli.py:85`, `src/frameproof/cli.py:90`, `src/frameproof/cli.py:105`).
- The CLI also exposes `frameproof config` diagnostics, but the current runtime uses that command to report config-path metadata rather than loading a general config file for batch runs (`src/frameproof/cli.py:123`, `src/frameproof/cli.py:152`, `src/frameproof/config/settings.py:68`, `src/frameproof/config/settings.py:80`).
- The settings model defines the durable config-path environment contract and the shape of input, capture, report, output, and adapter settings, so Stage 7 docs should use those names for examples without overclaiming automatic TOML ingestion (`src/frameproof/config/settings.py:8`, `src/frameproof/config/settings.py:99`, `src/frameproof/config/settings.py:115`, `src/frameproof/config/settings.py:127`, `src/frameproof/config/settings.py:142`, `src/frameproof/config/settings.py:173`, `src/frameproof/config/settings.py:191`).
- The GUI entrypoint already supports `--help`, `--settings-file`, and `--smoke-test`, so Stage 7 docs should include both quick verification and interactive launch guidance (`src/frameproof/gui/__main__.py:9`, `src/frameproof/gui/__main__.py:11`, `src/frameproof/gui/__main__.py:13`, `src/frameproof/gui/__main__.py:23`).
- The release checklist already defines the dependency matrix, smoke expectations, file-safety checks, and known external risks that the final docs must summarize rather than reinvent (`docs/release-checklist.md:14`, `docs/release-checklist.md:42`, `docs/release-checklist.md:76`, `docs/release-checklist.md:87`, `docs/release-checklist.md:109`).

## Release Docs Scope

### 1. Top-level README refresh

- Rewrite `README.md` from bootstrap status to current-product orientation.
- Cover product overview, supported media families, current CLI and GUI entrypoints, generated outputs (PDF, CSV, JSON, optional PNG stills), quick install, quick start, dependency summary, and doc map.
- Include at least one truthful CLI example for `contact_sheet` output and one GUI launch example tied to the real commands already exposed by the repo (`src/frameproof/cli.py:55`, `src/frameproof/cli.py:61`, `src/frameproof/gui/__main__.py:9`).
- Link only to docs that actually exist after Stage 7 implement.

### 2. Setup guide

- Add `docs/setup-guide.md` for fresh-user and fresh-developer setup.
- Cover Python version, virtualenv creation, `pip install -e .` plus optional `.[dev]`, repository-local fallback for `ruff` and `mypy` when `.venv/bin` is not on `PATH`, and first-run verification commands derived from the current repo workflow (`pyproject.toml:7`, `pyproject.toml:12`, `pyproject.toml:18`).
- Include both CLI and GUI startup steps and explain when GUI validation should use `--smoke-test` versus full launch.

### 3. Dependency guide

- Add `docs/dependency-guide.md` for FFmpeg, FFprobe, MediaInfo, `BRAW`, R3D, and ARRI ART CMD.
- Separate standard dependencies from proprietary RAW tooling and document that RAW operators may need user-supplied executables, runtime libraries, and licenses (`docs/release-checklist.md:18`, `docs/release-checklist.md:28`, `docs/release-checklist.md:31`).
- Map the guide to the actual CLI path-override flags and GUI dependency-screen expectations (`src/frameproof/cli.py:90`, `src/frameproof/cli.py:95`, `src/frameproof/cli.py:100`, `src/frameproof/cli.py:105`, `src/frameproof/cli.py:110`, `src/frameproof/cli.py:115`).
- State plainly that redistribution rights for proprietary SDK assets remain an external constraint until verified (`docs/release-checklist.md:10`, `docs/release-checklist.md:111`).

### 4. Config example and config behavior note

- Add a sample config artifact at `docs/examples/frameproof.example.toml`.
- Keep it aligned to the current `AppSettings` field names so users can see the intended shape of input, capture, report, output, and adapter values (`src/frameproof/config/settings.py:99`, `src/frameproof/config/settings.py:115`, `src/frameproof/config/settings.py:127`, `src/frameproof/config/settings.py:142`, `src/frameproof/config/settings.py:173`).
- Document the current limitation explicitly: the sample is a reference/example for settings shape and `FRAMEPROOF_CONFIG` path conventions, not proof that arbitrary batch runs already auto-load that TOML today (`src/frameproof/cli.py:154`, `src/frameproof/cli.py:170`, `src/frameproof/config/settings.py:68`, `src/frameproof/config/settings.py:80`).

### 5. Architecture note

- Add `docs/architecture-note.md` as a release-facing companion to the Stage 2 architecture.
- Summarize the single shared pipeline, requested-versus-actual capture parity, manifest/PDF alignment, RAW subprocess isolation, and failure model in reader-facing language (`docs/architecture.md:3`, `docs/architecture.md:10`, `docs/architecture.md:16`, `docs/architecture.md:37`, `docs/architecture.md:106`, `docs/architecture.md:138`, `docs/architecture.md:172`).
- Avoid duplicating the full architecture document; the note should translate core invariants into operator-facing guidance and link back to the full design doc where appropriate.

### 6. Finalized release checklist

- Update `docs/release-checklist.md` from a stage-planning checklist into a Stage 7 release-wrap checklist with current evidence, open blockers, and exact smoke command references.
- Preserve the existing dependency, file-safety, regression, and external-risk sections, but convert the checklist into something a fresh QA or release reviewer can execute directly (`docs/release-checklist.md:14`, `docs/release-checklist.md:33`, `docs/release-checklist.md:42`, `docs/release-checklist.md:76`, `docs/release-checklist.md:109`).

### 7. Final report and handoff

- Add `docs/reports/final/final-report.md` for implemented scope, validation summary, smoke evidence, known issues, backlog, and release-readiness status.
- Update `docs/stages/stage-07-implement.md`, `docs/reports/dev/stage-07-handoff.md`, and `docs/implement.md` so a fresh Stage 7 QA session can validate the release docs without hidden context.
- Keep the release-readiness statement conditional on actual evidence collected during implementation, not on planning assumptions.

## Setup And Smoke Validation Plan

- Required baseline validation in Stage 7 implement:
- `python -m frameproof --help`
- `python -m pytest`
- `ruff check .`
- `mypy src`
- `python -m frameproof.gui --help`
- `QT_QPA_PLATFORM=offscreen python -m frameproof.gui --smoke-test`
- Required configuration diagnostics coverage:
- `python -m frameproof config`
- `python -m frameproof config --format json`
- Standard-video success-path smoke plan:
- If `ffmpeg` and `ffprobe` are available, run one documented CLI smoke that generates a real PDF plus CSV/JSON manifests with the current CLI surface, then cite the exact command in README and the final report.
- Use `contact_sheet` as the default smoke because that matches the default layout contract, and optionally add a second `detail` example only if it is also run or clearly labeled as an alternate command (`src/frameproof/cli.py:55`, `docs/architecture.md:172`, `docs/release-checklist.md:46`, `docs/release-checklist.md:62`).
- RAW smoke plan:
- Document example commands and path overrides for `BRAW`, R3D, and ARRI, but classify them as conditional on operator-supplied proprietary tools and licenses.
- If no vendor tool is available in the implementation session, record that as an environment blocker and do not present RAW happy-path smoke as completed evidence (`docs/release-checklist.md:54`, `docs/release-checklist.md:57`, `docs/release-checklist.md:111`).
- Fallback honesty rule:
- Dependency-missing or unsupported-input smokes may stay in the docs as troubleshooting examples, but they do not count as release-readiness proof for happy-path packaging or operator setup.
- README and setup-guide verification:
- Every doc linked from `README.md` must exist in the tree at the end of Stage 7 implement.
- The final report must note which commands were run on this host, which were skipped or blocked, and why.

## Known Issues And Backlog Plan

- Keep a dedicated known-issues section in both `README.md` and `docs/reports/final/final-report.md`, then keep the fuller backlog in the final report only.
- Required known issues to disclose unless implementation evidence proves otherwise:
- Proprietary RAW redistribution and packaging rights remain unresolved and may require user-supplied tool installation (`docs/release-checklist.md:10`, `docs/release-checklist.md:111`).
- Preview color remains a review/proxy output and may differ from grading-reference color (`docs/release-checklist.md:94`, `docs/release-checklist.md:112`).
- GUI live validation remains host-dependent even when `--smoke-test` passes, because full operator interaction still needs a working desktop runtime (`docs/stages/stage-06-qa.md:60`, `docs/stages/stage-06-qa.md:90`).
- Standard-video happy-path smoke may remain blocked on hosts without `ffmpeg` and `ffprobe`; if so, the final report must say release readiness was not fully proven on that machine (`docs/stages/stage-06-qa.md:68`, `docs/stages/stage-06-qa.md:90`).
- The repository exposes config-path diagnostics and settings shape, but the docs must not imply that a generic TOML config file already drives pipeline runs automatically (`src/frameproof/cli.py:154`, `src/frameproof/cli.py:170`).
- Backlog categories to capture in the final report:
- packaging and installer strategy by OS
- dependency auto-discovery and onboarding improvements
- validated dependency-enabled smoke harnesses on tool-equipped hosts
- any remaining doc gaps discovered during Stage 7 implement

## Final Report Plan

- `docs/reports/final/final-report.md` must include:
- implemented documentation scope
- exact files changed
- validation commands and results
- smoke commands run versus blocked
- known issues
- backlog
- release-readiness statement with explicit rationale
- The release-readiness section must use one of these honest outcomes:
- ready on collected evidence
- not ready because a blocking issue remains
- not fully verified on this host because required external tooling or licensing evidence is missing
- The report must not collapse environment blockers into PASS language. It should separate repository correctness from host-specific readiness evidence.

## Acceptance Criteria

- Stage 7 implement replaces the bootstrap README with current-product documentation that matches the repo’s actual CLI, GUI, output, and dependency surfaces.
- `README.md`, `docs/setup-guide.md`, `docs/dependency-guide.md`, `docs/architecture-note.md`, `docs/release-checklist.md`, and `docs/reports/final/final-report.md` form a coherent doc set for a fresh user or developer.
- A config example exists and is labeled accurately as either supported runtime input or reference-only schema material; no ambiguity is left for QA.
- Every README-linked document exists and the final docs do not promise features or packaging behavior that the repo does not implement.
- Known issues and backlog are explicit about proprietary RAW constraints, external-tool requirements, color limitations, host-specific smoke coverage, and any config-loading limitation still present.
- Final Stage 7 implementation docs record whether release readiness was actually proven, not merely intended.

## Planned Implementation Touched Files

- `README.md`
- `docs/setup-guide.md`
- `docs/dependency-guide.md`
- `docs/architecture-note.md`
- `docs/release-checklist.md`
- `docs/examples/frameproof.example.toml`
- `docs/reports/final/final-report.md`
- `docs/stages/stage-07-implement.md`
- `docs/reports/dev/stage-07-handoff.md`
- `docs/implement.md`

## Validation Commands Run For This Plan Phase

- `cat docs/qa.md`
- `cat docs/release-checklist.md`
- `find . -maxdepth 3 -type f | sort | sed -n '1,260p'`

## Touched Files In This Plan Phase

- `docs/stages/stage-07-plan.md`
- `docs/stage.md`

## Exact Next Prompt

`[Stage 7-Implement]`

## Outcome

Stage 7 planning is complete. The next fresh Dev session should deliver the release-wrap documentation set, run and record the highest-fidelity smoke evidence available on that host, disclose all unresolved external-tool and proprietary-SDK limits, update the final report and Dev handoff, and stop before QA.
