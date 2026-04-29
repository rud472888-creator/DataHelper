# HOTDRIVE 뜸들이다 260111 A캠 QA Report

- Date: 2026-04-29
- Request: HOTDRIVE `뜸들이다` footage folder, `260111-a캠`
- Input: `/Volumes/HOTDRIVE/뜸들이다/001_촬영본/260111/001_a캠`
- Artifact directory: `/Users/server_jay/Desktop/DataHelper/artifacts/qa/hotdrive-tteumdeulida-260111-a-cam-2026-04-29`
- Verdict: PASS for requested media pipeline QA

## Scope

This was an ad hoc real-media QA run against the requested A-cam RED footage. It did not advance or alter the Hermes stage gate, and source code was not modified.

The input folder contains 108 `.R3D` part files, grouped by Frame Proof into 90 logical clips. The QA run used `middle-count 0`, so each logical clip produced Start and End captures only.

## Commands

```bash
.venv/bin/python -m frameproof --input '/Volumes/HOTDRIVE/뜸들이다/001_촬영본/260111/001_a캠' --output artifacts/qa/hotdrive-tteumdeulida-260111-a-cam-2026-04-29/260111-a-cam-contact-sheet.pdf --layout contact_sheet --middle-count 0 --project-name '뜸들이다 260111 A캠 QA' --r3d-adapter-path tools/r3d_adapter
```

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
.venv/bin/mypy src
```

## Results

- Frame Proof run: `status: success`
- Total logical clips: 90
- Successful clips: 90
- Failed probes: 0
- Failed decodes: 0
- Skipped clips: 0
- Manifest rows: 180, with 90 Start and 90 End capture rows
- Format family: `r3d`
- Resolution reported: 4096x2160
- Clip range: `A001_A001_01109A_001.R3D` through `A001_A065_0111DK_001.R3D`
- PDF page count: 45
- Warnings/errors in generated JSON: 0 warnings, 0 errors

## Artifacts

- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/hotdrive-tteumdeulida-260111-a-cam-2026-04-29/260111-a-cam-contact-sheet.pdf`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/hotdrive-tteumdeulida-260111-a-cam-2026-04-29/260111-a-cam-contact-sheet.csv`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/hotdrive-tteumdeulida-260111-a-cam-2026-04-29/260111-a-cam-contact-sheet.json`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/hotdrive-tteumdeulida-260111-a-cam-2026-04-29/260111-a-cam-contact-sheet-preview.png`
- `/Users/server_jay/Desktop/DataHelper/artifacts/qa/hotdrive-tteumdeulida-260111-a-cam-2026-04-29/frameproof-run.log`

## Repository Checks

- `pytest`: PASS, 116 passed
- `ruff check .`: PASS
- `mypy src`: FAIL, existing static type issue at `src/frameproof/render/pdf_renderer.py:814` (`Returning Any from function declared to return "float"`)

## Notes

The generated PDF preview rendered real R3D frame thumbnails and valid clip metadata. The PNG preview showed some Korean header text as square glyphs, which appears to be a PDF/font rendering limitation in the preview conversion path rather than a media-processing failure.

The requested media pipeline QA passes. The repo-wide `mypy` failure remains a separate code-quality risk and was not fixed as part of this QA-only request.
