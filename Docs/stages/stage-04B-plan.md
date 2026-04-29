# Stage 04B Plan

- lane: dev
- stage: stage-04B
- subphase: plan
- status: complete
- source_of_truth_spec: `docs/frameproof_tech_spec_ko.md`
- stage_4a_pass_verified: yes
- risk_level: high
- next_recommended_prompt: `[Stage 4B-Implement]`

## Gate Verification

- `docs/qa.md` records `latest_stage: stage-04A`, `latest_verdict: PASS`, `latest_gate: passed`, and `next_recommended_prompt: [Stage 4B-Plan]`.
- `docs/stages/stage-04A-qa.md` records `verdict: PASS`, `gate: passed`, and `stage_4b_status: unblocked-by-qa`.
- At session start, `docs/stage.md` recorded `current_stage: stage-04B`, `current_subphase: plan`, `last_result: stage-04A-qa-pass`, `qa_gate: pass`, and `implementation_allowed: false`.
- The required repo files for this session were read explicitly before planning: `AGENTS.md`, `docs/stage.md`, `docs/qa.md`, `docs/architecture.md`, `docs/api-contract.md`, `docs/data-inventory.md`, and `docs/stages/stage-04A-qa.md`.
- The required validation commands for this phase were executed:
- `cat docs/qa.md`
- `grep -R "BRAW" docs/architecture.md docs/api-contract.md`
- `grep -R "R3D" docs/architecture.md docs/api-contract.md`
- `grep -R "ARRIRAW" docs/architecture.md docs/api-contract.md`
- Stage 4B planning is therefore legal. This phase remains docs-only and must stop before implementation.

## Sprint Goal

- Add real subprocess-backed RAW adapter support planning for BRAW, R3D, and ARRIRAW.
- Replace the Stage 4A RAW deferral path with truthful dependency-aware adapter routing.
- Extend clip grouping for multi-part R3D logical clips without regressing deterministic scan order.
- Keep the pipeline honest: when adapter binaries or vendor tools are absent, report `dependency_missing` per format or per file instead of faking probe or capture success.
- Lock the subprocess JSON contract with tests so later implementation cannot drift from the documented envelope.

## Non-Scope

- No RAW client implementation in this phase.
- No bundling of Blackmagic, RED, or ARRI proprietary SDK binaries.
- No fake success path, canned metadata, or simulated capture in production code.
- No GUI dependency screen work in this phase.
- No Layout A, PNG export, or Stage 4C report-surface work.
- No change to the standard-video happy path beyond the wiring needed to introduce shared dependency inspection in Stage 4B.

## Dependency And Path Decisions

- Keep RAW execution subprocess-isolated behind Python adapter clients:
- `src/frameproof/adapters/braw_adapter_client.py`
- `src/frameproof/adapters/r3d_adapter_client.py`
- `src/frameproof/adapters/arriraw_art_adapter_client.py`
- Add a shared dependency inspection surface in `src/frameproof/core/dependency_inspector.py` rather than duplicating path checks inside each caller.
- Extend `src/frameproof/config/settings.py` and `src/frameproof/cli.py` to expose explicit adapter paths for:
- `--braw-adapter-path`
- `--r3d-adapter-path`
- `--arri-art-cmd-path`
- Keep `ffmpeg`, `ffprobe`, and `mediainfo` dependency detection in the same shared inspector so Stage 4A and Stage 4B use one availability vocabulary.
- Do not auto-download, auto-install, or vendor native binaries. Availability comes only from configured paths or already-callable tools.

## Stage 4B Module Scope

### 1. Shared dependency inspection

- `src/frameproof/core/dependency_inspector.py` (new)
- `src/frameproof/config/settings.py`
- `src/frameproof/cli.py`
- `tests/unit/config/test_settings.py`

Planned behavior:

- Centralize dependency-state checks for standard and RAW tools behind one inspector API.
- Preserve the existing `AdapterDependencyState` values exactly:
- `available`
- `configured_missing`
- `not_configured`
- `runtime_error`
- Treat BRAW and R3D wrapper paths as explicit configured executables. If absent, return `not_configured`; if set but missing or not executable, return `configured_missing`.
- Treat ARRI ART CMD the same way: explicit configured path, no bundling, no fallback download.
- Allow the inspector to run a lightweight startup check where safe:
- raw wrapper executables may support a JSON `version` command
- ART CMD may use a benign help or version invocation if available
- startup failure after the binary is found maps to `runtime_error`
- Reuse this inspector from the CLI summary path so batch diagnostics name the missing dependency and dependency state consistently across standard and RAW files.

### 2. Adapter resolution and honest RAW routing

- `src/frameproof/core/adapter_resolver.py`
- `src/frameproof/core/probe_service.py`
- `src/frameproof/cli.py`

Planned behavior:

- Replace the current Stage 4A `*_deferred` adapter selection for `.braw`, `.r3d`, and ARRIRAW inputs with real adapter client selection.
- `.braw` resolves to the BRAW adapter client.
- `.r3d` resolves to the R3D adapter client after grouping.
- `.ari` resolves to the ARRIRAW adapter client.
- `.mxf` remains on the FFmpeg path by default unless Stage 4B adds a conservative positive ARRIRAW hint; do not steal normal MXF files into the ARRI lane without evidence.
- `run_probe()` must continue to map non-available adapters to `ClipStatus.DEPENDENCY_MISSING`, but it should preserve the specific dependency name and `AdapterDependencyState` in `AdapterError.detail`.
- Mixed batches must stay file-isolated:
- RAW dependency failures remain per-file when standard-video files are still processable
- the batch becomes fatal only when zero processable files remain

### 3. R3D multi-part grouping strategy

- `src/frameproof/core/clip_grouper.py`
- `tests/unit/core/test_clip_grouper.py`

Planned behavior:

- Extend grouping beyond `group_standard_clips()` so `.r3d` candidates can collapse into one logical clip before adapter resolution.
- Group only files in the same directory whose stem matches a conservative `base + "_" + digits` part pattern, such as:
- `A001_C001_001.R3D`
- `A001_C001_002.R3D`
- Derive the logical key by stripping the final numeric part suffix from the stem.
- Sort grouped parts by parsed numeric suffix, not lexicographically.
- Use the first ordered part as `source_path` and store the full ordered list in `part_files`.
- Keep grouping deterministic and local:
- never merge across directories
- never merge files whose stems do not match the conservative part pattern
- a lone `.r3d` file remains a valid single-file logical clip
- Do not block probe or capture solely because part numbers are non-contiguous; preserve discovered order and let the adapter surface any decode/probe warnings.

### 4. RAW subprocess client scope

- `src/frameproof/adapters/braw_adapter_client.py`
- `src/frameproof/adapters/r3d_adapter_client.py`
- `src/frameproof/adapters/arriraw_art_adapter_client.py`
- `src/frameproof/adapters/__init__.py`
- `tests/unit/adapters/test_braw_adapter_client.py`
- `tests/unit/adapters/test_r3d_adapter_client.py`
- `tests/unit/adapters/test_arriraw_art_adapter_client.py`

Planned behavior:

- Each client owns JSON request serialization, subprocess execution, stdout parsing, stderr capture, timeout handling, and response-to-domain mapping.
- BRAW and R3D clients should use the canonical JSON envelope from `docs/api-contract.md` for:
- `probe`
- `capture`
- optionally `version`
- ARRIRAW client should adapt ART CMD to the shared Python contract:
- metadata export or probe command maps into `ProbeResult`
- capture or thumbnail extraction command maps into `CaptureResult`
- any ART-specific intermediate files stay in the app staging directory
- Clients must treat these conditions as real adapter failures, not success:
- executable missing
- subprocess timeout
- non-zero exit with no valid JSON
- malformed stdout JSON
- response missing required envelope fields
- stderr-only failure with no structured stdout
- A successful RAW capture still returns one `CaptureResult` per requested slot, including duplicate-collapsed slots.
- No client may fabricate timecode, frame count, or image paths when the underlying tool did not provide them.

### 5. Error and status handling plan

- `src/frameproof/core/probe_service.py`
- `src/frameproof/core/capture_service.py`
- `src/frameproof/core/report_builder.py`
- `src/frameproof/core/models.py` only if a narrow extension is required by the implementation

Planned behavior:

- Keep the existing status vocabulary and error codes from Stage 3 and Stage 4A; Stage 4B should reuse them rather than inventing RAW-only variants.
- Probe-time rules:
- missing or unusable configured RAW dependency -> clip `dependency_missing`
- subprocess timeout during probe -> clip `probe_failed` with `timeout`
- invalid or incomplete stdout JSON during probe -> clip `probe_failed` with `invalid_response`
- adapter-declared `metadata_incomplete` -> clip remains processable if `ClipInfo` is still usable
- Capture-time rules:
- one or more slot failures -> slot `decode_failed`, clip `partial_success`
- all slot failures after a valid probe -> clip `decode_failed`
- adapter-declared `dependency_missing` during capture -> slot errors recorded, clip downgraded truthfully, no fake images emitted
- Duplicate preservation rules stay unchanged:
- duplicate-collapsed slots remain in order
- `duplicate_of` still points at the source slot
- RAW dependency loss must not masquerade as `unsupported_format`. If the format is supported by code but unavailable in the environment, the status is `dependency_missing`.

### 6. Contract and integration test strategy

- `tests/unit/adapters/test_braw_adapter_client.py`
- `tests/unit/adapters/test_r3d_adapter_client.py`
- `tests/unit/adapters/test_arriraw_art_adapter_client.py`
- `tests/unit/core/test_clip_grouper.py`
- `tests/unit/core/test_dependency_inspector.py`
- `tests/integration/test_dependency_missing.py`
- `tests/integration/test_raw_dependency_missing.py`
- `tests/integration/conftest.py`
- optional fixtures under `tests/fixtures/raw_contract/`

Required test lanes:

- JSON contract fixture tests:
- request envelopes for `probe`, `capture`, and optional `version`
- success response mapping
- `dependency_missing` response mapping
- malformed JSON and missing-field failures
- R3D grouping tests:
- grouped multi-part clip produces one `ClipCandidate`
- single-file `.r3d` remains ungrouped
- part ordering is numeric and deterministic
- Dependency tests:
- invalid configured paths return `configured_missing`
- absent raw paths return `not_configured`
- startup/version failures return `runtime_error`
- CLI and batch-behavior tests:
- RAW-only batch with missing dependency returns the fatal no-processable-files behavior
- mixed standard + RAW batch continues and reports RAW clips as `dependency_missing`
- malformed raw adapter stdout becomes normalized failure output, not an unhandled traceback
- Optional real-sample tests:
- enable only via explicit environment variables pointing to local binaries and sample media
- skip by default
- document exact env vars and skip reason
- do not commit proprietary media or require proprietary SDKs in CI

## Planned Implementation Touched Files

- `src/frameproof/cli.py`
- `src/frameproof/config/settings.py`
- `src/frameproof/core/clip_grouper.py`
- `src/frameproof/core/adapter_resolver.py`
- `src/frameproof/core/dependency_inspector.py`
- `src/frameproof/core/probe_service.py`
- `src/frameproof/core/capture_service.py`
- `src/frameproof/core/report_builder.py`
- `src/frameproof/adapters/__init__.py`
- `src/frameproof/adapters/braw_adapter_client.py`
- `src/frameproof/adapters/r3d_adapter_client.py`
- `src/frameproof/adapters/arriraw_art_adapter_client.py`
- `tests/test_cli.py`
- `tests/integration/conftest.py`
- `tests/integration/test_dependency_missing.py`
- `tests/integration/test_raw_dependency_missing.py`
- `tests/unit/config/test_settings.py`
- `tests/unit/core/test_clip_grouper.py`
- `tests/unit/core/test_dependency_inspector.py`
- `tests/unit/adapters/test_braw_adapter_client.py`
- `tests/unit/adapters/test_r3d_adapter_client.py`
- `tests/unit/adapters/test_arriraw_art_adapter_client.py`
- `docs/stages/stage-04B-implement.md`
- `docs/reports/dev/stage-04B-handoff.md`
- `docs/implement.md`

## Acceptance Criteria For Stage 4B Implement

- `.braw`, `.r3d`, and `.ari` inputs resolve to real subprocess-backed adapter clients instead of Stage 4A deferred placeholders.
- The app exposes configured adapter paths for BRAW, R3D, and ARRI ART CMD without bundling proprietary binaries.
- Dependency detection uses one shared inspector and distinguishes `available`, `configured_missing`, `not_configured`, and `runtime_error`.
- Missing RAW dependencies produce truthful `dependency_missing` results and never fabricate probe or capture success.
- R3D multi-part inputs are grouped into one logical clip with ordered `part_files`, and single-file R3D clips still work.
- RAW subprocess clients serialize the documented JSON contract and validate required response fields before trusting output.
- Invalid JSON, timeout, missing fields, and stderr-only subprocess failures are normalized into adapter errors instead of uncaught exceptions.
- Mixed batches continue when at least one clip remains processable; all-missing-dependency batches stop fatally with truthful diagnostics.
- Contract tests cover dependency-missing, malformed-response, and success-shape behavior using temporary executable doubles.
- Optional real-sample tests stay opt-in and do not make the repository depend on proprietary media or SDKs.

## Risks And Watchpoints

- The highest product risk is false-positive support. Stage 4B must not present BRAW, R3D, or ARRIRAW as usable unless the configured binaries really exist and start cleanly.
- ARRIRAW-on-MXF routing is the largest resolver ambiguity. The implementation should stay conservative and avoid reclassifying ordinary MXF files as ARRIRAW without a positive hint.
- R3D grouping must be deterministic and conservative. Over-grouping unrelated files would corrupt batch identity and manifest joins.
- Vendor tools may emit noisy stderr even on success. The clients should preserve diagnostics without treating every stderr line as fatal when structured stdout is valid.
- Proprietary tools may be unavailable in local and CI environments. The main verification path therefore has to rely on temporary executable doubles plus opt-in smoke coverage.

## Validation Commands Run For This Plan Phase

- `cat docs/qa.md`
- `grep -R "BRAW" docs/architecture.md docs/api-contract.md`
- `grep -R "R3D" docs/architecture.md docs/api-contract.md`
- `grep -R "ARRIRAW" docs/architecture.md docs/api-contract.md`

## Touched Files In This Plan Phase

- `docs/stages/stage-04B-plan.md`
- `docs/stage.md`

## Exact Next Prompt

`[Stage 4B-Implement]`

## Outcome

Stage 4B planning is complete. The next fresh Dev session should implement RAW adapter clients, shared dependency detection, R3D grouping, and contract tests as defined here, write the Stage 4B implementation and handoff artifacts, and stop before QA or Stage 4C work.
