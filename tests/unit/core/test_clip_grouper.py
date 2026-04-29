from __future__ import annotations

from pathlib import Path

from frameproof.core.clip_grouper import group_clip_candidates


def test_group_clip_candidates_keeps_single_r3d_file_as_one_candidate(tmp_path: Path) -> None:
    clip_path = tmp_path / "A001_C001_001.R3D"
    clip_path.write_bytes(b"r3d")

    candidates = group_clip_candidates((clip_path,))

    assert len(candidates) == 1
    assert candidates[0].source_path == str(clip_path)
    assert candidates[0].part_files == (str(clip_path),)
    assert candidates[0].format_hint == "r3d"


def test_group_clip_candidates_groups_numeric_r3d_parts_in_numeric_order(tmp_path: Path) -> None:
    part_10 = tmp_path / "A001_C001_010.R3D"
    part_2 = tmp_path / "A001_C001_002.R3D"
    part_1 = tmp_path / "A001_C001_001.R3D"
    for path in (part_10, part_2, part_1):
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates((part_10, part_2, part_1))

    assert len(candidates) == 1
    assert candidates[0].source_path == str(part_1)
    assert candidates[0].part_files == (str(part_1), str(part_2), str(part_10))


def test_group_clip_candidates_does_not_merge_r3d_files_across_directories(tmp_path: Path) -> None:
    day_a = tmp_path / "day-a"
    day_b = tmp_path / "day-b"
    day_a.mkdir()
    day_b.mkdir()

    first = day_a / "A001_C001_001.R3D"
    second = day_b / "A001_C001_002.R3D"
    first.write_bytes(b"one")
    second.write_bytes(b"two")

    candidates = group_clip_candidates((first, second))

    assert len(candidates) == 2
    assert candidates[0].part_files == (str(first),)
    assert candidates[1].part_files == (str(second),)
