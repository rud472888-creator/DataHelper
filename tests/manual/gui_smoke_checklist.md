# GUI Smoke Checklist

Use this checklist on a machine where the local Qt runtime can actually launch `PySide6`.

## Launch

- Run `python -m frameproof.gui --smoke-test` and confirm the app opens and closes without starting a batch.
- Run `python -m frameproof.gui --help` and confirm the GUI entrypoint help renders.
- Run `python -m frameproof.gui` or `frameproof-gui`.
- Confirm the main window opens with the `Session Overview`, `Sources`, `Output And Report`, `Run`, `Batch Status`, and `Clip Progress` sections visible at once.
- Confirm the main window opens at its default size without clipping the action row, status card, or progress header.
- Resize the window down to approximately `1024x720` and confirm the primary action row, dependency button, and progress table remain usable without hidden controls.

## Dependency Screen

- Open `Dependencies`.
- Confirm FFmpeg, FFprobe, MediaInfo, BRAW adapter, R3D adapter, and ARRI ART CMD each show a status row.
- Confirm each row shows `Configured Path`, `Applies To`, `Status`, and `Resolved` information without overlapping when paths are long.
- Confirm the exact required state labels remain visible: `available`, `configured path missing`, `not configured`, and `runtime startup failure`.
- Edit at least one adapter/tool path, save, reopen the dialog, and confirm the value persisted.
- Re-check dependencies and confirm the status labels update without crashing the app.

## Settings Persistence

- Add at least one source path and set an output PDF path.
- Change layout, middle count, still-export, CSV/JSON, failed-files section, and path-privacy settings.
- Close the GUI and relaunch it.
- Confirm the prior values are restored.

## Shared Pipeline Run

- Run one supported standard-video batch.
- Run one mixed batch containing at least one processable clip and one damaged or dependency-missing clip.
- Confirm the progress table adds rows as grouped clips are discovered.
- Confirm row order does not change while statuses update.
- Confirm probe/capture/PDF cells move through truthful states rather than placeholder data, and that partial rows remain distinguishable from clean success rows without relying on color alone.
- Confirm warning text remains readable when long fallback or error summaries are present.
- Confirm long dependency-missing or probe-failure text stays readable without clipping critical words.
- Confirm the empty-state, running-state, success-state, and partial/failure-state banner copy stays explicit about what happened.
- Confirm the PDF path reported by the success banner exists.
- If CSV/JSON toggles are enabled, confirm the manifest files exist beside the PDF.
- If the path privacy mode is `Basename Only` or `Hidden`, confirm the status copy explains that choice without hiding clip identity entirely.
- Confirm degraded clips remain visible after a mixed batch completes and that valid clips still report success in the same run.

## Cancel

- Start a batch large enough to leave time to click `Cancel`.
- Click `Cancel` while the batch is active.
- Confirm no new clip starts after the current in-flight work completes.
- Confirm the banner reports cancellation instead of fatal failure.
- Confirm already collected row diagnostics remain visible.

## Keyboard And Focus

- Tab from `Add Files` through the source controls, output controls, dependency button, `Start`, `Cancel`, and into the progress table.
- Confirm focus indication is visible on interactive controls.
- Confirm the default button remains `Start` when the form is valid and that keyboard navigation does not skip required controls.

## Visual Artifacts

- Run `python scripts/generate_visual_artifacts.py`.
- Review the generated PDFs under `artifacts/stage-05/pdf/`.
- If the local Qt runtime supports offscreen rendering, review the generated screenshots under `artifacts/stage-05/gui/`.
- If GUI screenshots are skipped, confirm `artifacts/stage-05/verification-summary.txt` records the environment limitation instead of silently omitting GUI evidence.

## Notes

- On the current Stage 5 implementation machine, the installed Qt runtime aborts before launch with `Incompatible processor ... neon`, so live GUI launch and offscreen screenshot generation are blocked there.
- On hosts missing `IBM Plex Sans`, Qt may log a fallback-font warning during `--smoke-test`; the warning is acceptable if the app still opens and closes cleanly.
