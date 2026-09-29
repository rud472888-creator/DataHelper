from __future__ import annotations

import json
from pathlib import Path

from frameproof.adapters.r3d_adapter_client import R3DAdapterClient
from frameproof.config.settings import AdapterSettings
from frameproof.core.models import (
    AdapterErrorCode,
    CapturePlan,
    CaptureProfile,
    CaptureRequest,
    CaptureStatus,
    ClipCandidate,
)


def _write_executable(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def _candidate(tmp_path: Path) -> ClipCandidate:
    first = tmp_path / "A001_C001_001.R3D"
    second = tmp_path / "A001_C001_002.R3D"
    first.write_bytes(b"one")
    second.write_bytes(b"two")
    return ClipCandidate(
        candidate_id="candidate-0001",
        source_path=str(first),
        part_files=(str(first), str(second)),
        file_size_bytes=first.stat().st_size,
        modified_time=first.stat().st_mtime,
        format_hint="r3d",
    )


def _plan() -> CapturePlan:
    return CapturePlan(
        clip_id="candidate-0001",
        requests=(
            CaptureRequest(label="Start", requested_ratio=0.0, requested_frame_index=0),
            CaptureRequest(label="Mid1", requested_ratio=0.5, requested_frame_index=12),
            CaptureRequest(label="End", requested_ratio=1.0, requested_frame_index=24),
        ),
        middle_count=1,
        used_frame_count=True,
    )


def test_r3d_adapter_includes_part_files_and_logical_clip_name(tmp_path: Path, monkeypatch) -> None:
    log_path = tmp_path / "requests.jsonl"
    monkeypatch.setenv("FRAMEPROOF_LOG_PATH", str(log_path))
    adapter_path = _write_executable(
        tmp_path / "r3d-adapter",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import base64",
                "import json",
                "import os",
                "import pathlib",
                "import sys",
                "payload = json.loads(sys.stdin.read() or '{}')",
                "with open(os.environ['FRAMEPROOF_LOG_PATH'], 'a', encoding='utf-8') as handle:",
                "    handle.write(json.dumps(payload) + '\\n')",
                "request_id = payload['request_id']",
                "command = payload['command']",
                "if command == 'version':",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'r3d_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'metadata_raw': {}}",
                "elif command == 'probe':",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'r3d_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'clip': {'clip_name': pathlib.Path(payload['input']['source_path']).name, 'logical_clip_name': 'A001_C001', 'format_family': 'r3d', 'frame_count': 25, 'duration_seconds': 1.0, 'fps_num': 25, 'fps_den': 1}, 'metadata_raw': {}}",
                "elif command == 'capture':",
                "    captures = []",
                "    for index, point in enumerate(payload['capture_points'], start=1):",
                "        output_path = pathlib.Path(payload['options']['staging_dir']) / f\"{index:02d}_{point['label'].lower()}.png\"",
                "        output_path.parent.mkdir(parents=True, exist_ok=True)",
                "        output_path.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC'))",
                "        captures.append({'label': point['label'], 'requested_ratio': point['requested_ratio'], 'requested_frame_index': point['requested_frame_index'], 'requested_seconds': point['requested_seconds'], 'actual_frame_index': point['requested_frame_index'], 'actual_seconds': None if point['requested_frame_index'] is None else point['requested_frame_index'] / 25.0, 'actual_timecode': None, 'actual_timecode_source': None, 'image_path_temp': str(output_path), 'duplicate_of': None, 'status': 'success', 'warnings': [], 'errors': []})",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'r3d_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'captures': captures, 'metadata_raw': {}}",
                "else:",
                "    raise SystemExit(2)",
                "sys.stdout.write(json.dumps(response))",
            ]
        )
        + "\n",
    )
    candidate = _candidate(tmp_path)
    adapter = R3DAdapterClient(AdapterSettings(r3d_adapter_path=adapter_path))

    probe = adapter.probe(candidate)
    captures = adapter.capture(candidate, _plan(), CaptureProfile(name="preview_rec709_sdr"), tmp_path / "staging")

    assert probe.ok is True
    assert probe.clip is not None
    assert probe.clip.logical_clip_name == "A001_C001"
    assert [capture.status for capture in captures] == [
        CaptureStatus.SUCCESS,
        CaptureStatus.SUCCESS,
        CaptureStatus.SUCCESS,
    ]

    requests = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert requests[1]["input"]["part_files"] == list(candidate.part_files)


def test_r3d_adapter_maps_adapter_declared_dependency_missing_to_capture_failures(tmp_path: Path) -> None:
    adapter_path = _write_executable(
        tmp_path / "r3d-adapter",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import sys",
                "payload = json.loads(sys.stdin.read() or '{}')",
                "request_id = payload['request_id']",
                "if payload['command'] == 'version':",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'r3d_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'metadata_raw': {}}",
                "elif payload['command'] == 'capture':",
                "    response = {'request_id': request_id, 'ok': False, 'adapter_name': 'r3d_adapter', 'status': 'dependency_missing', 'warnings': [], 'errors': [{'code': 'dependency_missing', 'message': 'RED runtime missing', 'detail': {'required_path': '/Applications/RED/r3d_adapter'}}]}",
                "else:",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'r3d_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'clip': {'clip_name': 'A001_C001_001.R3D', 'format_family': 'r3d', 'frame_count': 25, 'duration_seconds': 1.0, 'fps_num': 25, 'fps_den': 1}, 'metadata_raw': {}}",
                "sys.stdout.write(json.dumps(response))",
            ]
        )
        + "\n",
    )

    captures = R3DAdapterClient(AdapterSettings(r3d_adapter_path=adapter_path)).capture(
        _candidate(tmp_path),
        _plan(),
        CaptureProfile(name="preview_rec709_sdr"),
        tmp_path / "staging",
    )

    assert [capture.status for capture in captures] == [
        CaptureStatus.DECODE_FAILED,
        CaptureStatus.DECODE_FAILED,
        CaptureStatus.DECODE_FAILED,
    ]
    assert captures[0].errors[0].code is AdapterErrorCode.DEPENDENCY_MISSING
