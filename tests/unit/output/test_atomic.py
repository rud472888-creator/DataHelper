from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from frameproof.output.atomic import atomic_output_path


def test_atomic_output_replaces_destination_only_on_success(tmp_path: Path) -> None:
    destination = tmp_path / "nested" / "report.csv"

    with atomic_output_path(destination) as temp_path:
        assert temp_path.parent == destination.parent
        temp_path.write_text("new", encoding="utf-8")
        assert not destination.exists()

    assert destination.read_text(encoding="utf-8") == "new"
    assert sorted(p.name for p in destination.parent.iterdir()) == ["report.csv"]


def test_atomic_output_keeps_existing_file_when_writer_fails(tmp_path: Path) -> None:
    destination = tmp_path / "report.json"
    destination.write_text("old", encoding="utf-8")

    with pytest.raises(OSError), atomic_output_path(destination) as temp_path:
        temp_path.write_text("half", encoding="utf-8")
        raise OSError("disk full")

    assert destination.read_text(encoding="utf-8") == "old"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["report.json"]


def test_atomic_output_honours_umask_like_a_direct_write(tmp_path: Path) -> None:
    previous = os.umask(0o022)
    try:
        with atomic_output_path(tmp_path / "report.pdf") as temp_path:
            temp_path.write_bytes(b"pdf")
    finally:
        os.umask(previous)

    assert stat.S_IMODE((tmp_path / "report.pdf").stat().st_mode) == 0o644
