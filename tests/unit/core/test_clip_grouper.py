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


def test_group_clip_candidates_groups_flattened_canonical_red_parts_in_numeric_order(
    tmp_path: Path,
) -> None:
    part_10 = tmp_path / "A001_A001_05026M_010.R3D"
    part_2 = tmp_path / "A001_A001_05026M_002.R3D"
    part_1 = tmp_path / "A001_A001_05026M_001.R3D"
    for path in (part_10, part_2, part_1):
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates((part_10, part_2, part_1))

    assert len(candidates) == 1
    assert candidates[0].source_path == str(part_1)
    assert candidates[0].part_files == (str(part_1), str(part_2), str(part_10))


def test_group_clip_candidates_groups_r3d_parts_inside_rdc_directory(tmp_path: Path) -> None:
    clip_directory = tmp_path / "A001_C001_05026M.rDc"
    clip_directory.mkdir()
    part_2 = clip_directory / "A001_C001_002.R3D"
    part_1 = clip_directory / "A001_C001_001.R3D"
    for path in (part_2, part_1):
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates((part_2, part_1))

    assert len(candidates) == 1
    assert candidates[0].part_files == (str(part_1), str(part_2))


def test_group_clip_candidates_does_not_merge_three_digit_dsc_r3d_clips(tmp_path: Path) -> None:
    clip_paths = (tmp_path / "DSC_001.R3D", tmp_path / "DSC_002.R3D")
    for path in clip_paths:
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates(clip_paths)

    assert len(candidates) == 2
    assert tuple(candidate.part_files for candidate in candidates) == tuple((str(path),) for path in clip_paths)


def test_group_clip_candidates_does_not_merge_nikon_zr_numbered_r3d_clips(tmp_path: Path) -> None:
    clip_paths = tuple(tmp_path / f"DSC_{index:04d}.R3D" for index in range(156, 210))
    for path in clip_paths:
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates(clip_paths)

    assert len(candidates) == 54
    assert tuple(candidate.part_files for candidate in candidates) == tuple((str(path),) for path in clip_paths)


def test_group_clip_candidates_requires_first_r3d_part_before_grouping(tmp_path: Path) -> None:
    part_2 = tmp_path / "A001_C001_05026M_002.R3D"
    part_3 = tmp_path / "A001_C001_05026M_003.R3D"
    for path in (part_2, part_3):
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates((part_2, part_3))

    assert tuple(candidate.part_files for candidate in candidates) == ((str(part_2),), (str(part_3),))


def test_group_clip_candidates_allows_gaps_after_first_r3d_part(tmp_path: Path) -> None:
    part_3 = tmp_path / "A001_C001_05026M_003.R3D"
    part_1 = tmp_path / "A001_C001_05026M_001.R3D"
    for path in (part_3, part_1):
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates((part_3, part_1))

    assert len(candidates) == 1
    assert candidates[0].part_files == (str(part_1), str(part_3))


def test_group_clip_candidates_does_not_merge_r3d_files_across_directories(tmp_path: Path) -> None:
    day_a = tmp_path / "day-a"
    day_b = tmp_path / "day-b"
    day_a.mkdir()
    day_b.mkdir()

    first = day_a / "A001_C001_05026M_001.R3D"
    second = day_b / "A001_C001_05026M_002.R3D"
    first.write_bytes(b"one")
    second.write_bytes(b"two")

    candidates = group_clip_candidates((first, second))

    assert len(candidates) == 2
    assert candidates[0].part_files == (str(first),)
    assert candidates[1].part_files == (str(second),)


def test_group_clip_candidates_groups_arriraw_frames_by_shot_in_numeric_order(tmp_path: Path) -> None:
    frame_10 = tmp_path / "A004C010_180208_R18T.1886786.ari"
    frame_2 = tmp_path / "A004C010_180208_R18T.1886778.ari"
    frame_1 = tmp_path / "A004C010_180208_R18T.1886777.ari"
    for path in (frame_10, frame_2, frame_1):
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates((frame_10, frame_2, frame_1))

    assert len(candidates) == 1
    assert candidates[0].source_path == str(frame_1)
    assert candidates[0].part_files == (str(frame_1), str(frame_2), str(frame_10))
    assert candidates[0].format_hint == "ari"


def test_group_clip_candidates_does_not_merge_different_arriraw_shots(tmp_path: Path) -> None:
    first_shot = tmp_path / "A004C010_180208_R18T.1886777.ari"
    second_shot = tmp_path / "A004C011_180208_R18T.1886778.ari"
    for path in (first_shot, second_shot):
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates((first_shot, second_shot))

    assert tuple(candidate.part_files for candidate in candidates) == ((str(first_shot),), (str(second_shot),))


def test_group_clip_candidates_does_not_merge_arriraw_frames_across_directories(tmp_path: Path) -> None:
    day_a = tmp_path / "day-a"
    day_b = tmp_path / "day-b"
    day_a.mkdir()
    day_b.mkdir()
    first = day_a / "A004C010_180208_R18T.1886777.ari"
    second = day_b / "A004C010_180208_R18T.1886778.ari"
    first.write_bytes(b"one")
    second.write_bytes(b"two")

    candidates = group_clip_candidates((first, second))

    assert tuple(candidate.part_files for candidate in candidates) == ((str(first),), (str(second),))


def test_group_clip_candidates_does_not_group_numeric_braw_mov_or_arx_names(tmp_path: Path) -> None:
    paths = tuple(
        tmp_path / name
        for name in (
            "clip_001.braw",
            "clip_002.braw",
            "clip_001.mov",
            "clip_002.mov",
            "clip_001.mxf",
            "clip_002.mxf",
            "A004C010_180208_R18T.1886777.arx",
            "A004C010_180208_R18T.1886778.arx",
        )
    )
    for path in paths:
        path.write_bytes(path.name.encode("utf-8"))

    candidates = group_clip_candidates(paths)

    assert tuple(candidate.part_files for candidate in candidates) == tuple((str(path),) for path in paths)
