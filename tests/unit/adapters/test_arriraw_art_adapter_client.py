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


def _candidate(tmp_path: Path) -> ClipCandidate:
    source_path = tmp_path / "A001C001.ari"
    source_path.write_bytes(b"arriraw")
    return ClipCandidate(
        candidate_id="candidate-0001",
        source_path=str(source_path),
        part_files=(str(source_path),),
        file_size_bytes=source_path.stat().st_size,
        modified_time=source_path.stat().st_mtime,
        format_hint="ari",
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


def test_arriraw_art_adapter_probe_and_capture_use_art_cmd_contract(tmp_path: Path, monkeypatch) -> None:
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
    candidate = _candidate(tmp_path)
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
    assert commands[1][0] == "export"
    assert "--skip-audio" in commands[1]
    assert "--skip-look" in commands[1]
    assert commands[2][0] == "process"
    assert "--target-colorspace" in commands[2]


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
