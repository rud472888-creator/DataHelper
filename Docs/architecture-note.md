# Architecture Note

This note is the release-facing summary of the implementation architecture. For the full design record, see [Docs/architecture.md](Docs/architecture.md).

## One Pipeline

Frame Proof has one shared processing pipeline for both CLI and GUI runs:

`scan -> group clips -> resolve adapter -> inspect dependencies -> probe -> plan captures -> capture -> build report -> render PDF -> write manifests`

The GUI is not a second media-processing engine. It is a thin desktop surface over the same batch services the CLI uses.

## Format Routing

- Standard video routes through the FFmpeg adapter flow.
- BRAW, R3D, and ARRIRAW route through subprocess adapter clients.
- RAW subprocess isolation is intentional: vendor-tool crashes or malformed responses are supposed to fail the affected clip, not take down the whole Python host.

## Output Contract

The application builds one normalized report model, then uses it for:

- PDF output
- CSV manifest output
- JSON manifest output
- GUI progress/status reporting

This matters because requested-versus-actual capture facts should stay aligned across all visible outputs.

## Capture Rules

- Start and End capture slots are always requested.
- `middle_count` controls whether `Mid1`, `Mid2`, and `Mid3` are added.
- Short clips keep the requested labels even when some slots collapse onto the same frame.
- PNG still export changes persistence only; it does not change capture selection.

## Failure Model

Frame Proof is designed to continue past per-clip failures where possible. The main batch stops only for documented fatal conditions such as:

- unwritable output targets
- fatal PDF/render output failure
- user cancellation
- no processable files left because all relevant dependencies are missing

Everything else should remain attached to clip-level or capture-level diagnostics rather than disappearing silently.

## Operator Implications

- Source media is intended to remain read-only.
- Default staging stays app-owned and outside the source media tree unless the operator overrides it.
- Missing RAW tooling should affect only the relevant RAW family.
- The generated PDF is a review artifact and explicitly not a color-critical grading reference.

## Config And Settings

- CLI runs are configured by explicit flags.
- GUI runs are configured by persisted GUI settings.
- `python -m frameproof config` reports runtime config-path diagnostics only.

The example TOML in [Docs/examples/frameproof.example.toml](Docs/examples/frameproof.example.toml) is a shape/reference document, not proof of a fully config-driven pipeline run.
