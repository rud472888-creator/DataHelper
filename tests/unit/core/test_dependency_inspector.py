from __future__ import annotations

from pathlib import Path

from frameproof.config.settings import AdapterSettings
from frameproof.core.dependency_inspector import DependencyInspector
from frameproof.core.models import AdapterDependencyState


def _write_executable(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def test_dependency_inspector_reports_raw_paths_as_not_configured_when_absent() -> None:
    inspector = DependencyInspector(AdapterSettings())

    assert inspector.braw_adapter().state is AdapterDependencyState.NOT_CONFIGURED
    assert inspector.r3d_adapter().state is AdapterDependencyState.NOT_CONFIGURED
    assert inspector.arri_art_cmd().state is AdapterDependencyState.NOT_CONFIGURED


def test_dependency_inspector_reports_configured_missing_for_bad_raw_path(tmp_path: Path) -> None:
    inspector = DependencyInspector(
        AdapterSettings(
            braw_adapter_path=tmp_path / "missing-braw",
            r3d_adapter_path=tmp_path / "missing-r3d",
            arri_art_cmd_path=tmp_path / "missing-art",
        )
    )

    assert inspector.braw_adapter().state is AdapterDependencyState.CONFIGURED_MISSING
    assert inspector.r3d_adapter().state is AdapterDependencyState.CONFIGURED_MISSING
    assert inspector.arri_art_cmd().state is AdapterDependencyState.CONFIGURED_MISSING


def test_dependency_inspector_reports_runtime_error_for_bad_json_version_response(tmp_path: Path) -> None:
    adapter_path = _write_executable(
        tmp_path / "braw-adapter",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import sys",
                "sys.stdin.read()",
                "sys.stdout.write('not-json')",
            ]
        )
        + "\n",
    )

    inspector = DependencyInspector(AdapterSettings(braw_adapter_path=adapter_path))
    record = inspector.braw_adapter()

    assert record.state is AdapterDependencyState.RUNTIME_ERROR
    assert record.detail["runtime_check"] == "json_version"


def test_dependency_inspector_reports_all_ffmpeg_tools_in_adapter_availability() -> None:
    inspector = DependencyInspector(
        AdapterSettings(
            ffmpeg_path="/missing/ffmpeg",
            ffprobe_path="/missing/ffprobe",
            mediainfo_path="/missing/mediainfo",
        )
    )

    availability = inspector.availability_for_adapter("ffmpeg")

    assert availability.required_tools == ("ffmpeg", "ffprobe")
    assert availability.state is AdapterDependencyState.CONFIGURED_MISSING
    assert availability.error_detail()["required_tools"] == ["ffmpeg", "ffprobe"]
