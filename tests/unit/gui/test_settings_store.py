from __future__ import annotations

from pathlib import Path

from frameproof.gui.settings_store import GuiStoredSettings, SettingsStore


def test_settings_store_round_trips_gui_defaults(tmp_path: Path) -> None:
    store = SettingsStore(tmp_path / "gui.ini")
    stored = GuiStoredSettings(
        source_paths=("/Volumes/Footage/A", "/Volumes/Footage/B"),
        include_subfolders=False,
        output_pdf_path="/tmp/report.pdf",
        last_output_dir="/tmp",
        project_name="Stage 4D",
        middle_count=2,
        layout="detail",
        export_stills=True,
        write_csv=False,
        write_json=True,
        include_failed_section=False,
        path_display="full",
        ffmpeg_path="/usr/local/bin/ffmpeg",
        ffprobe_path="/usr/local/bin/ffprobe",
        mediainfo_path="/usr/local/bin/mediainfo",
        braw_adapter_path="/Applications/BRAW",
        r3d_adapter_path="/Applications/R3D",
        arri_art_cmd_path="/Applications/ARRI",
    )

    store.save(stored)
    loaded = store.load()

    assert loaded == stored
