from __future__ import annotations

import csv
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from .conftest import run_cli


@pytest.mark.parametrize(
    ("middle_count", "expected_labels"),
    (
        (0, ["Start", "End"]),
        (1, ["Start", "Mid1", "End"]),
        (2, ["Start", "Mid1", "Mid2", "End"]),
        (3, ["Start", "Mid1", "Mid2", "Mid3", "End"]),
    ),
)
def test_cli_standard_pipeline_writes_pdf_csv_and_json(
    synthetic_standard_video: Path,
    tmp_path: Path,
    middle_count: int,
    expected_labels: list[str],
) -> None:
    pdf_path = tmp_path / "report.pdf"
    csv_path = tmp_path / "report.csv"
    json_path = tmp_path / "report.json"

    result = run_cli(
        "--input",
        str(synthetic_standard_video),
        "--middle-count",
        str(middle_count),
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
    assert "status: success" in result.stdout
    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 0
    assert csv_path.is_file()
    assert json_path.is_file()
    assert not (tmp_path / "stills").exists()

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len(expected_labels)
    assert [row["capture_label"] for row in rows] == expected_labels
    assert all(row["image_path"] == "" for row in rows)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_clips"] == 1
    assert payload["summary"]["success_count"] == 1
    assert len(payload["rows"]) == len(expected_labels)
    assert all(row["image_path"] is None for row in payload["rows"])
    assert payload["clips"][0]["clip"]["clip_name"] == synthetic_standard_video.name


def test_cli_detail_pipeline_can_export_png_stills(
    synthetic_standard_video: Path,
    tmp_path: Path,
) -> None:
    pdf_path = tmp_path / "detail.pdf"
    csv_path = tmp_path / "detail.csv"
    json_path = tmp_path / "detail.json"
    stills_dir = tmp_path / "stills"

    result = run_cli(
        "--input",
        str(synthetic_standard_video),
        "--middle-count",
        "0",
        "--layout",
        "detail",
        "--export-stills",
        "--stills-dir",
        str(stills_dir),
        "--output",
        str(pdf_path),
        "--csv",
        str(csv_path),
        "--json",
        str(json_path),
    )

    assert result.returncode == 0, result.stderr
    assert pdf_path.is_file()
    assert csv_path.is_file()
    assert json_path.is_file()

    pngs = sorted(stills_dir.rglob("*.png"))
    assert len(pngs) == 2

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["capture_label"] for row in rows] == ["Start", "End"]
    assert all(row["image_path"] for row in rows)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["clips"][0]["status"] == "success"
    assert payload["clips"][0]["captures"][0]["image_path"].endswith(".png")


def test_cli_standard_pipeline_supports_non_ascii_input_and_output_paths(
    synthetic_standard_video: Path,
    tmp_path: Path,
) -> None:
    source_dir = tmp_path / "소스 폴더"
    source_dir.mkdir()
    unicode_clip = source_dir / "테스트 클립.mp4"
    shutil.copy2(synthetic_standard_video, unicode_clip)
    output_dir = tmp_path / "보고서 폴더"
    pdf_path = output_dir / "결과 보고서.pdf"
    csv_path = output_dir / "결과 보고서.csv"
    json_path = output_dir / "결과 보고서.json"

    result = run_cli(
        "--input",
        str(unicode_clip),
        "--middle-count",
        "2",
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
    assert pdf_path.is_file()
    assert csv_path.is_file()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["clips"][0]["clip"]["clip_name"] == "테스트 클립.mp4"
    assert len(payload["rows"]) == 4


def test_cli_short_clip_preserves_duplicate_capture_slots(tmp_path: Path) -> None:
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path is None:
        pytest.skip("ffmpeg is not available in this environment")

    short_clip = tmp_path / "one-frame.mp4"
    subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=160x90:r=24",
            "-frames:v",
            "1",
            str(short_clip),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    pdf_path = tmp_path / "report.pdf"
    csv_path = tmp_path / "report.csv"
    json_path = tmp_path / "report.json"

    result = run_cli(
        "--input",
        str(short_clip),
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
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    captures = payload["clips"][0]["captures"]
    assert [capture["label"] for capture in captures] == ["Start", "Mid1", "Mid2", "Mid3", "End"]
    assert captures[1]["duplicate_of"] == "Start"
    assert [capture["status"] for capture in captures] == [
        "success",
        "skipped_duplicate",
        "skipped_duplicate",
        "skipped_duplicate",
        "skipped_duplicate",
    ]


def test_cli_mixed_batch_continues_after_probe_failure(
    synthetic_standard_video: Path,
    tmp_path: Path,
) -> None:
    broken_clip = tmp_path / "broken.mp4"
    broken_clip.write_bytes(b"not-a-real-video")
    pdf_path = tmp_path / "report.pdf"
    csv_path = tmp_path / "report.csv"
    json_path = tmp_path / "report.json"

    result = run_cli(
        "--input",
        str(synthetic_standard_video),
        "--input",
        str(broken_clip),
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
    assert "probe_failed_count: 1" in result.stdout
    assert pdf_path.is_file()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_clips"] == 2
    assert {clip["status"] for clip in payload["clips"]} == {"success", "probe_failed"}


@pytest.mark.parametrize(
    ("container", "timecode", "expected_start", "expected_end"),
    (
        # 29.97 DF across a non-tenth minute boundary (frames ;00 and ;01 are dropped).
        ("mov", "00:59:58;00", "00:59:58;00 (calculated)", "01:00:00;29 (calculated)"),
        ("mp4", "10:00:00:00", "10:00:00:00 (calculated)", "10:00:02:29 (calculated)"),
    ),
)
def test_cli_reports_capture_timecodes_from_container_start_timecode(
    tmp_path: Path,
    container: str,
    timecode: str,
    expected_start: str,
    expected_end: str,
) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("ffmpeg/ffprobe are not available in this environment")
    rate = "30000/1001" if ";" in timecode else "30"
    clip_path = tmp_path / f"tc.{container}"
    subprocess.run(
        [shutil.which("ffmpeg") or "ffmpeg", "-y", "-f", "lavfi", "-i", f"testsrc=size=160x90:rate={rate}",
         "-frames:v", "90", "-timecode", timecode, str(clip_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    json_path = tmp_path / "report.json"

    result = run_cli("--input", str(clip_path), "--middle-count", "0", "--output", str(tmp_path / "report.pdf"),
                     "--json", str(json_path))

    assert result.returncode == 0, result.stderr
    clip = json.loads(json_path.read_text(encoding="utf-8"))["clips"][0]
    assert clip["clip"]["start_timecode"] == timecode
    assert clip["clip"]["end_timecode"] == expected_end
    assert [capture["actual_timecode"] for capture in clip["captures"]] == [expected_start, expected_end]
    assert "start_timecode_missing" not in clip["warnings"]
