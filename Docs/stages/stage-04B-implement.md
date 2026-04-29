# Stage 04B Implement

- lane: dev
- stage: stage-04B
- subphase: implement
- status: complete
- scope_boundary: raw-adapter-clients-and-dependency-detection
- next_recommended_prompt: `[Stage 4B-QA]`

## Delivered Scope

- Implemented real RAW adapter resolution for `.braw`, `.r3d`, and `.ari`.
- Added subprocess-backed `BRAW` and R3D clients using the documented JSON envelope.
- Added the ARRIRAW ART CMD client using metadata export for probe and process commands for capture.
- Added shared dependency inspection and per-adapter dependency diagnostics for both standard and RAW tools.
- Added conservative multi-part R3D grouping and Stage 4B RAW contract test coverage.

## Changed Files And Reasons

- `src/frameproof/cli.py` exposes RAW path flags and routes all-dependency-missing batches to the existing fatal-report path.
- `src/frameproof/core/adapter_resolver.py` replaces RAW deferrals with real adapter client selection.
- `src/frameproof/core/clip_grouper.py` groups same-directory numeric R3D parts into one logical candidate.
- `src/frameproof/core/dependency_inspector.py` centralizes tool checks for `ffmpeg`, `ffprobe`, `mediainfo`, `braw_adapter`, `r3d_adapter`, and `arri_art_cmd`.
- `src/frameproof/core/probe_service.py` preserves dependency detail in normalized RAW probe failures.
- `src/frameproof/adapters/_json_subprocess_adapter.py` implements the shared BRAW/R3D JSON subprocess transport and validation layer.
- `src/frameproof/adapters/braw_adapter_client.py`, `src/frameproof/adapters/r3d_adapter_client.py`, and `src/frameproof/adapters/arriraw_art_adapter_client.py` implement the Stage 4B RAW clients.
- `src/frameproof/adapters/ffmpeg_adapter.py` removes stale dependency-resolution code that conflicted with the shared inspector.
- `tests/unit/adapters/`, `tests/unit/core/`, and `tests/integration/` gained the Stage 4B regression coverage.

## Implementation Decisions

- Kept the RAW clients on the existing probe/capture/report path instead of creating a second RAW pipeline.
- Reused one JSON subprocess transport for `BRAW` and R3D because their contracts are structurally the same.
- Kept ARRIRAW separate because ART CMD is argv-driven rather than stdin/stdout JSON-driven.
- Kept ARRIRAW `.mxf` routing conservative and did not steal generic MXF files from the FFmpeg adapter.
- Treated absent or broken vendor binaries as truthful `dependency_missing` states, never as fake probe or capture success.

## Validation Results

- `python -m pytest tests/unit tests/integration` -> PASS (`56 passed, 1 skipped`)
- `python -m pytest` -> PASS (`63 passed, 1 skipped`)
- `ruff check .` -> PASS
- `mypy src` -> PASS
- `env | rg 'FRAMEPROOF|BRAW|R3D|ARRI'` -> no output, exit code `1`

## Generated Artifacts

- No persistent runtime artifacts were checked into the repository during this run.
- No proprietary RAW smoke artifacts were generated because no real RAW tool path was configured in the environment.

## Blockers And Known Gaps

- Real vendor-binary smoke verification remains environment-blocked on this machine.
- The standard FFmpeg happy-path integration test remains skipped until `ffmpeg` and `ffprobe` are available locally.
- Stage 4B requires fresh QA before Stage 4C begins.

## Fresh Session Notes

- Run `[Stage 4B-QA]` next.
- QA should validate missing-dependency handling, malformed JSON handling, and the new R3D grouping rules directly from the repository files and required command outputs.
