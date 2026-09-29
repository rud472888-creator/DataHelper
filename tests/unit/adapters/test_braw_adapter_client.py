from __future__ import annotations

import json
from pathlib import Path

import pytest

from frameproof.adapters.braw_adapter_client import BRAWAdapterClient
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


def _candidate(tmp_path: Path) -> ClipCandidate:
    source_path = tmp_path / "A001_0001.braw"
    source_path.write_bytes(b"braw")
    return ClipCandidate(
        candidate_id="candidate-0001",
        source_path=str(source_path),
        part_files=(str(source_path),),
        file_size_bytes=source_path.stat().st_size,
        modified_time=source_path.stat().st_mtime,
        format_hint="braw",
    )


def _plan() -> CapturePlan:
    return CapturePlan(
        clip_id="candidate-0001",
        requests=(
            CaptureRequest(label="Start", requested_ratio=0.0, requested_frame_index=0),
            CaptureRequest(label="End", requested_ratio=1.0, requested_frame_index=47),
        ),
        middle_count=0,
        used_frame_count=True,
    )


def test_braw_adapter_probe_and_capture_follow_json_contract(tmp_path: Path, monkeypatch) -> None:
    log_path = tmp_path / "requests.jsonl"
    monkeypatch.setenv("FRAMEPROOF_LOG_PATH", str(log_path))
    adapter_path = _write_executable(
        tmp_path / "braw-adapter",
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
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'braw_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'metadata_raw': {}}",
                "elif command == 'probe':",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'braw_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'clip': {'clip_name': pathlib.Path(payload['input']['source_path']).name, 'format_family': 'braw', 'frame_count': 48, 'duration_seconds': 2.0, 'fps_num': 24, 'fps_den': 1, 'start_timecode': '01:00:00:00'}, 'metadata_raw': {}}",
                "elif command == 'capture':",
                "    captures = []",
                "    for index, point in enumerate(payload['capture_points'], start=1):",
                "        output_path = pathlib.Path(payload['options']['staging_dir']) / f\"{index:02d}_{point['label'].lower()}.png\"",
                "        output_path.parent.mkdir(parents=True, exist_ok=True)",
                "        output_path.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC'))",
                "        captures.append({'label': point['label'], 'requested_ratio': point['requested_ratio'], 'requested_frame_index': point['requested_frame_index'], 'requested_seconds': point['requested_seconds'], 'actual_frame_index': point['requested_frame_index'], 'actual_seconds': None if point['requested_frame_index'] is None else point['requested_frame_index'] / 24.0, 'actual_timecode': '01:00:00:00', 'actual_timecode_source': 'native_adapter', 'image_path_temp': str(output_path), 'duplicate_of': None, 'status': 'success', 'warnings': [], 'errors': []})",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'braw_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'captures': captures, 'metadata_raw': {}}",
                "else:",
                "    raise SystemExit(2)",
                "sys.stdout.write(json.dumps(response))",
            ]
        )
        + "\n",
    )
    candidate = _candidate(tmp_path)
    adapter = BRAWAdapterClient(AdapterSettings(braw_adapter_path=adapter_path))

    probe = adapter.probe(candidate)
    captures = adapter.capture(candidate, _plan(), CaptureProfile(name="preview_rec709_sdr"), tmp_path / "staging")

    assert probe.ok is True
    assert probe.status is ClipStatus.SUCCESS
    assert probe.clip is not None
    assert probe.clip.frame_count == 48
    assert probe.clip.start_timecode == "01:00:00:00"
    assert [capture.status for capture in captures] == [CaptureStatus.SUCCESS, CaptureStatus.SUCCESS]

    requests = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert [request["command"] for request in requests] == ["version", "probe", "capture"]
    assert requests[1]["input"]["part_files"] == []
    assert requests[2]["capture_points"][1]["requested_frame_index"] == 47


def test_braw_adapter_reports_invalid_json_probe_output(tmp_path: Path) -> None:
    adapter_path = _write_executable(
        tmp_path / "braw-adapter",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import sys",
                "payload = json.loads(sys.stdin.read() or '{}')",
                "if payload['command'] == 'version':",
                "    sys.stdout.write(json.dumps({'request_id': payload['request_id'], 'ok': True, 'adapter_name': 'braw_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'metadata_raw': {}}))",
                "else:",
                "    sys.stdout.write('{')",
            ]
        )
        + "\n",
    )

    result = BRAWAdapterClient(AdapterSettings(braw_adapter_path=adapter_path)).probe(_candidate(tmp_path))

    assert result.ok is False
    assert result.status is ClipStatus.PROBE_FAILED
    assert result.errors[0].code is AdapterErrorCode.INVALID_RESPONSE


@pytest.mark.parametrize("mode", ["missing_field", "missing_file", "empty_file", "non_png"])
def test_braw_adapter_rejects_success_capture_with_invalid_image_path_temp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    monkeypatch.setenv("FRAMEPROOF_BAD_IMAGE_MODE", mode)
    adapter_path = _write_executable(
        tmp_path / "braw-adapter",
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import os",
                "import pathlib",
                "import sys",
                "payload = json.loads(sys.stdin.read() or '{}')",
                "request_id = payload['request_id']",
                "command = payload['command']",
                "if command == 'version':",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'braw_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'metadata_raw': {}}",
                "elif command == 'probe':",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'braw_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'clip': {'clip_name': pathlib.Path(payload['input']['source_path']).name, 'format_family': 'braw', 'frame_count': 48, 'duration_seconds': 2.0, 'fps_num': 24, 'fps_den': 1}, 'metadata_raw': {}}",
                "elif command == 'capture':",
                "    mode = os.environ['FRAMEPROOF_BAD_IMAGE_MODE']",
                "    captures = []",
                "    for index, point in enumerate(payload['capture_points'], start=1):",
                "        output_path = pathlib.Path(payload['options']['staging_dir']) / f\"{index:02d}_{point['label'].lower()}.png\"",
                "        output_path.parent.mkdir(parents=True, exist_ok=True)",
                "        if mode == 'empty_file':",
                "            output_path.write_bytes(b'')",
                "        elif mode == 'non_png':",
                "            output_path.write_bytes(b'not a png')",
                "        capture = {'label': point['label'], 'requested_ratio': point['requested_ratio'], 'requested_frame_index': point['requested_frame_index'], 'requested_seconds': point['requested_seconds'], 'actual_frame_index': point['requested_frame_index'], 'actual_seconds': None if point['requested_frame_index'] is None else point['requested_frame_index'] / 24.0, 'actual_timecode': None, 'actual_timecode_source': None, 'duplicate_of': None, 'status': 'success', 'warnings': [], 'errors': []}",
                "        if mode != 'missing_field':",
                "            capture['image_path_temp'] = str(output_path)",
                "        captures.append(capture)",
                "    response = {'request_id': request_id, 'ok': True, 'adapter_name': 'braw_adapter', 'adapter_version': '1.0.0', 'status': 'success', 'warnings': [], 'errors': [], 'captures': captures, 'metadata_raw': {}}",
                "else:",
                "    raise SystemExit(2)",
                "sys.stdout.write(json.dumps(response))",
            ]
        )
        + "\n",
    )

    captures = BRAWAdapterClient(AdapterSettings(braw_adapter_path=adapter_path)).capture(
        _candidate(tmp_path),
        _plan(),
        CaptureProfile(name="preview_rec709_sdr"),
        tmp_path / "staging",
    )

    assert [capture.status for capture in captures] == [
        CaptureStatus.DECODE_FAILED,
        CaptureStatus.DECODE_FAILED,
    ]
    assert captures[0].errors[0].code is AdapterErrorCode.DECODE_FAILED
