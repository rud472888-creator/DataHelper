from __future__ import annotations

import json
from pathlib import Path

from frameproof.adapters.arriraw_art_adapter_client import ARRIRAWArtAdapterClient
from frameproof.config.settings import AdapterSettings
from frameproof.core.models import (
    AdapterErrorCode,
    CapturePlan,
    CaptureProfile,
    CaptureRequest,
    CaptureStatus,
    ClipCandidate,
    ClipStatus,
)


def _write_executable(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def _candidate(
    tmp_path: Path,
    extension: str = "ari",
    *,
    include_source_part: bool = True,
) -> ClipCandidate:
    source_path = tmp_path / f"A001C001.{extension}"
    source_path.write_bytes(b"arriraw")
    return ClipCandidate(
        candidate_id="candidate-0001",
        source_path=str(source_path),
        part_files=(str(source_path),) if include_source_part else (),
        file_size_bytes=source_path.stat().st_size,
        modified_time=source_path.stat().st_mtime,
        format_hint=extension,
    )


def _plan() -> CapturePlan:
    return CapturePlan(
        clip_id="candidate-0001",
        requests=(
            CaptureRequest(label="Start", requested_ratio=0.0, requested_frame_index=0),
            CaptureRequest(label="End", requested_ratio=1.0, requested_frame_index=23),
        ),
        middle_count=0,
        used_frame_count=True,
    )


def _write_sequence_validating_art_cmd(path: Path) -> Path:
    return _write_executable(
        path,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import base64",
                "import json",
                "import os",
                "import pathlib",
                "import sys",
                "argv = sys.argv[1:]",
                "def validate_sequence_input():",
                "    input_path = pathlib.Path(argv[argv.index('--input') + 1])",
                "    if not input_path.is_dir():",
                "        raise SystemExit('legacy ARI input must be a directory')",
                "    entries = sorted(input_path.iterdir())",
                "    names = [entry.name for entry in entries]",
                "    expected = json.loads(os.environ['FRAMEPROOF_EXPECTED_SEQUENCE'])",
                "    if names != expected:",
                "        raise SystemExit(f'unexpected sequence files: {names!r}')",
                "    if not all(entry.is_symlink() for entry in entries):",
                "        raise SystemExit('sequence staging must not copy or mutate source frames')",
                "    record = {'command': argv[0], 'input': str(input_path), 'names': names, 'targets': [str(entry.resolve()) for entry in entries]}",
                "    with open(os.environ['FRAMEPROOF_SEQUENCE_LOG_PATH'], 'a', encoding='utf-8') as handle:",
                "        handle.write(json.dumps(record) + '\\n')",
                "if argv == ['--help']:",
                "    sys.stdout.write('help')",
                "elif argv[:1] == ['export']:",
                "    validate_sequence_input()",
                "    output_path = pathlib.Path(argv[argv.index('--output') + 1])",
                "    frame_count = len(json.loads(os.environ['FRAMEPROOF_EXPECTED_SEQUENCE']))",
                "    output_path.write_text(json.dumps({'clip': {'clip_name': 'A001C001', 'frame_count': frame_count, 'duration_seconds': frame_count / 24, 'fps_num': 24, 'fps_den': 1, 'container': 'ARI', 'codec': 'ARRIRAW'}, 'warnings': [], 'errors': [], 'status': 'success'}), encoding='utf-8')",
                "elif argv[:1] == ['process']:",
                "    validate_sequence_input()",
                "    output_path = pathlib.Path(argv[argv.index('--output') + 1])",
                "    output_path.parent.mkdir(parents=True, exist_ok=True)",
                "    output_path.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC'))",
                "else:",
                "    raise SystemExit(2)",
            ]
        )
        + "\n",
    )


def _assert_isolated_sequence_inputs(log_path: Path, part_paths: tuple[Path, ...], source_dir: Path) -> None:
    records = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert [record["command"] for record in records] == ["export", "process", "process"]
    expected_targets = [str(path.resolve()) for path in part_paths]
    for record in records:
        assert record["names"] == [path.name for path in part_paths]
        assert record["targets"] == expected_targets
        assert Path(record["input"]) != source_dir
        assert not Path(record["input"]).exists()


def test_mxf_probe_and_capture_keep_direct_art_cmd_input(
    tmp_path: Path,
    monkeypatch,
) -> None:
    log_path = tmp_path / "commands.jsonl"
    monkeypatch.setenv("FRAMEPROOF_LOG_PATH", str(log_path))
    adapter_path = _write_executable(
        tmp_path / "art-cmd",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import os",
                "import pathlib",
                "import sys",
                "argv = sys.argv[1:]",
                "with open(os.environ['FRAMEPROOF_LOG_PATH'], 'a', encoding='utf-8') as handle:",
                "    handle.write(json.dumps(argv) + '\\n')",
                "if argv == ['--help']:",
                "    sys.stdout.write('help')",
                "elif argv[:1] == ['export']:",
                "    output_path = pathlib.Path(argv[argv.index('--output') + 1])",
                "    input_path = pathlib.Path(argv[argv.index('--input') + 1])",
                "    output_path.write_text(json.dumps({'clip': {'clip_name': input_path.name, 'frame_count': 24, 'duration_seconds': 1.0, 'fps_num': 24, 'fps_den': 1, 'container': 'ARI', 'codec': 'ARRIRAW'}, 'warnings': [], 'errors': [], 'status': 'success'}), encoding='utf-8')",
                "elif argv[:1] == ['process']:",
                "    import base64",
                "    output_path = pathlib.Path(argv[argv.index('--output') + 1])",
                "    output_path.parent.mkdir(parents=True, exist_ok=True)",
                "    output_path.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC'))",
                "else:",
                "    raise SystemExit(2)",
            ]
        )
        + "\n",
    )
    candidate = _candidate(tmp_path, "mxf")
    adapter = ARRIRAWArtAdapterClient(AdapterSettings(arri_art_cmd_path=adapter_path))

    probe = adapter.probe(candidate)
    captures = adapter.capture(candidate, _plan(), CaptureProfile(name="arri_preview_rec709"), tmp_path / "staging")

    assert probe.ok is True
    assert probe.status is ClipStatus.SUCCESS
    assert probe.clip is not None
    assert probe.clip.codec == "ARRIRAW"
    assert [capture.status for capture in captures] == [CaptureStatus.SUCCESS, CaptureStatus.SUCCESS]

    commands = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert commands[0] == ["--help"]
    assert all(command[command.index("--input") + 1] == candidate.source_path for command in commands[1:])
    assert commands[1][0] == "export"
    assert "--skip-audio" in commands[1]
    assert "--skip-look" in commands[1]
    assert commands[2][0] == "process"
    assert "--target-colorspace" in commands[2]


def test_single_arriraw_frame_with_empty_parts_uses_isolated_directory_for_probe_and_capture(
    tmp_path: Path,
    monkeypatch,
) -> None:
    candidate = _candidate(tmp_path, include_source_part=False)
    source_path = Path(candidate.source_path)
    (tmp_path / "A001C002.ari").write_bytes(b"other-clip")

    log_path = tmp_path / "single-inputs.jsonl"
    monkeypatch.setenv("FRAMEPROOF_SEQUENCE_LOG_PATH", str(log_path))
    monkeypatch.setenv("FRAMEPROOF_EXPECTED_SEQUENCE", json.dumps([source_path.name]))
    adapter_path = _write_sequence_validating_art_cmd(tmp_path / "art-cmd")
    adapter = ARRIRAWArtAdapterClient(AdapterSettings(arri_art_cmd_path=adapter_path))

    probe = adapter.probe(candidate)
    captures = adapter.capture(candidate, _plan(), CaptureProfile(name="arri_preview_rec709"), tmp_path / "staging")

    assert probe.ok is True
    assert [capture.status for capture in captures] == [CaptureStatus.SUCCESS, CaptureStatus.SUCCESS]
    _assert_isolated_sequence_inputs(log_path, (source_path,), tmp_path)


def test_grouped_arriraw_sequence_uses_isolated_directory_for_probe_and_capture(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    part_paths = (
        source_dir / "A001C001.000001.ari",
        source_dir / "A001C001.000002.ari",
    )
    for part_path in part_paths:
        part_path.write_bytes(b"arriraw")
    (source_dir / "A001C002.000001.ari").write_bytes(b"other-clip")

    log_path = tmp_path / "sequence-inputs.jsonl"
    monkeypatch.setenv("FRAMEPROOF_SEQUENCE_LOG_PATH", str(log_path))
    monkeypatch.setenv("FRAMEPROOF_EXPECTED_SEQUENCE", json.dumps([path.name for path in part_paths]))
    adapter_path = _write_sequence_validating_art_cmd(tmp_path / "art-cmd")
    candidate = ClipCandidate(
        candidate_id="candidate-0001",
        source_path=str(part_paths[0]),
        part_files=tuple(str(path) for path in part_paths),
        file_size_bytes=sum(path.stat().st_size for path in part_paths),
        modified_time=part_paths[0].stat().st_mtime,
        format_hint="ari",
    )
    adapter = ARRIRAWArtAdapterClient(AdapterSettings(arri_art_cmd_path=adapter_path))

    probe = adapter.probe(candidate)
    captures = adapter.capture(candidate, _plan(), CaptureProfile(name="arri_preview_rec709"), tmp_path / "staging")

    assert probe.ok is True
    assert [capture.status for capture in captures] == [CaptureStatus.SUCCESS, CaptureStatus.SUCCESS]
    _assert_isolated_sequence_inputs(log_path, part_paths, source_dir)


def test_arriraw_art_adapter_rejects_malformed_metadata_export_json(tmp_path: Path) -> None:
    adapter_path = _write_executable(
        tmp_path / "art-cmd",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import pathlib",
                "import sys",
                "argv = sys.argv[1:]",
                "if argv == ['--help']:",
                "    sys.stdout.write('help')",
                "elif argv[:1] == ['export']:",
                "    output_path = pathlib.Path(argv[argv.index('--output') + 1])",
                "    output_path.write_text('{', encoding='utf-8')",
                "else:",
                "    raise SystemExit(2)",
            ]
        )
        + "\n",
    )

    result = ARRIRAWArtAdapterClient(AdapterSettings(arri_art_cmd_path=adapter_path)).probe(_candidate(tmp_path))

    assert result.ok is False
    assert result.status is ClipStatus.PROBE_FAILED
    assert result.errors[0].code is AdapterErrorCode.INVALID_RESPONSE
