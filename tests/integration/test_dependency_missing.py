from __future__ import annotations

import json
from pathlib import Path

from .conftest import run_cli


def test_cli_reports_dependency_missing_for_standard_video_when_ffmpeg_tools_are_invalid(tmp_path: Path) -> None:
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"not-a-real-video")
    pdf_path = tmp_path / "report.pdf"
    csv_path = tmp_path / "report.csv"
    json_path = tmp_path / "report.json"

    result = run_cli(
        "--input",
        str(clip_path),
        "--middle-count",
        "3",
        "--layout",
        "contact_sheet",
        "--output",
        str(pdf_path),
        "--csv",
        str(csv_path),
        "--json",
        str(json_path),
        "--ffmpeg-path",
        "/missing/ffmpeg",
        "--ffprobe-path",
        "/missing/ffprobe",
        "--mediainfo-path",
        "/missing/mediainfo",
    )

    assert result.returncode == 2
    assert "status: partial_success" in result.stdout
    assert "skipped_count: 1" in result.stdout
    assert "dependency_missing:" in result.stdout
    assert "status=dependency_missing" in result.stdout
    assert "adapter=ffmpeg" in result.stdout
    assert "required_tools=ffmpeg,ffprobe" in result.stdout
    assert "dependency_state=configured_missing" in result.stdout
    assert "fatal: batch could not produce a report" in result.stdout
    assert not pdf_path.exists()
    assert not csv_path.exists()
    assert not json_path.exists()


def test_cli_continues_when_standard_video_is_processable_but_raw_dependency_is_missing(
    synthetic_standard_video: Path,
    tmp_path: Path,
) -> None:
    raw_clip = tmp_path / "clip.braw"
    raw_clip.write_bytes(b"braw")
    pdf_path = tmp_path / "report.pdf"
    csv_path = tmp_path / "report.csv"
    json_path = tmp_path / "report.json"

    result = run_cli(
        "--input",
        str(synthetic_standard_video),
        "--input",
        str(raw_clip),
        "--middle-count",
        "3",
        "--layout",
        "contact_sheet",
        "--output",
        str(pdf_path),
        "--csv",
        str(csv_path),
        "--json",
        str(json_path),
    )

    assert result.returncode == 0, result.stderr
    assert "status: partial_success" in result.stdout
    assert "success_count: 1" in result.stdout
    assert "skipped_count: 1" in result.stdout
    assert pdf_path.is_file()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_clips"] == 2
    assert {clip["status"] for clip in payload["clips"]} == {"success", "dependency_missing"}
