from __future__ import annotations

from pathlib import Path

from .conftest import run_cli


def test_cli_reports_dependency_missing_for_raw_only_batch_when_braw_adapter_is_unconfigured(tmp_path: Path) -> None:
    clip_path = tmp_path / "clip.braw"
    clip_path.write_bytes(b"braw")
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
    )

    assert result.returncode == 2
    assert "dependency_missing:" in result.stdout
    assert "adapter=braw_adapter" in result.stdout
    assert "required_tools=braw_adapter" in result.stdout
    assert "dependency_state=not_configured" in result.stdout
    assert "fatal: batch could not produce a report" in result.stdout
    assert not pdf_path.exists()
    assert not csv_path.exists()
    assert not json_path.exists()
