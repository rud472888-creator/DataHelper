from __future__ import annotations

from pathlib import Path

import pytest

from frameproof.config.settings import AppSettings
from frameproof.settings import collect_runtime_snapshot


def test_app_settings_accepts_stage_three_shapes() -> None:
    settings = AppSettings.from_mapping(
        {
            "input": {
                "paths": ["/Volumes/Footage/Day01"],
                "recursive": True,
                "extensions": ["mov", "r3d"],
            },
            "capture": {
                "middle_count": 3,
                "profile": "preview_rec709_sdr",
                "prefer_frame_index": True,
            },
            "report": {
                "layout": "detail",
                "project_name": "Project Name",
                "include_failed_section": True,
                "include_summary_page": True,
                "path_display": "basename",
            },
            "output": {
                "pdf_path": "/Exports/frameproof.pdf",
                "export_stills": True,
                "stills_dir": "/Exports/stills",
                "write_csv": True,
                "write_json": True,
                "staging_dir": "/tmp/frameproof",
            },
            "adapters": {
                "ffmpeg_path": "ffmpeg",
                "ffprobe_path": "ffprobe",
                "mediainfo_path": "mediainfo",
                "braw_adapter_path": "/Applications/FrameProof/native/braw_adapter",
            },
        }
    )

    assert settings.capture.middle_count == 3
    assert settings.report.layout.value == "detail"
    assert settings.output.export_stills is True
    assert settings.output.stills_dir == Path("/Exports/stills")
    assert settings.adapters.braw_adapter_path == Path("/Applications/FrameProof/native/braw_adapter")


def test_app_settings_reject_invalid_middle_count() -> None:
    with pytest.raises(ValueError, match="middle_count"):
        AppSettings.from_mapping(
            {
                "input": {"paths": ["/Volumes/Footage/Day01"]},
                "capture": {"middle_count": 4},
                "output": {"pdf_path": "/Exports/frameproof.pdf"},
            }
        )


def test_app_settings_rejects_contradictory_output_configuration() -> None:
    with pytest.raises(ValueError, match="stills_dir"):
        AppSettings.from_mapping(
            {
                "input": {"paths": ["/Volumes/Footage/Day01"]},
                "output": {"pdf_path": "/Exports/frameproof.pdf", "export_stills": True},
            }
        )


def test_app_settings_rejects_blank_tool_paths() -> None:
    with pytest.raises(ValueError, match="ffmpeg_path"):
        AppSettings.from_mapping(
            {
                "input": {"paths": ["/Volumes/Footage/Day01"]},
                "output": {"pdf_path": "/Exports/frameproof.pdf"},
                "adapters": {"ffmpeg_path": "   "},
            }
        )


def test_bootstrap_settings_wrapper_still_exposes_runtime_snapshot() -> None:
    snapshot = collect_runtime_snapshot(env={}, home=Path("/tmp")).to_dict()

    assert snapshot["config_source"] == "default"
    assert str(snapshot["config_path"]).endswith("frameproof/config.toml")
