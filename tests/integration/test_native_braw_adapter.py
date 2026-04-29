from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
BRAW_ADAPTER = REPO_ROOT / "tools" / "braw_adapter"
SAMPLE_BRAW = Path("/Applications/Blackmagic RAW/Blackmagic RAW Speed Test.app/Contents/Resources/profile.braw")
SDK_LIBRARIES = Path("/Applications/Blackmagic RAW/Blackmagic RAW SDK/Mac/Libraries")


def _run_adapter(payload: dict[str, object], *, env: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
    completed = subprocess.run(
        [str(BRAW_ADAPTER)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
        env={**os.environ, **(env or {})},
    )
    assert completed.stdout, completed.stderr
    return completed.returncode, json.loads(completed.stdout)


def test_native_braw_adapter_dependency_error_is_actionable(tmp_path: Path) -> None:
    rc, response = _run_adapter(
        {"request_id": "version-missing", "command": "version"},
        env={"FRAMEPROOF_BRAW_NATIVE_HELPER": str(tmp_path / "missing-helper")},
    )

    assert rc == 2
    assert response["ok"] is False
    assert response["status"] == "dependency_missing"
    message = response["errors"][0]["message"]
    assert "Blackmagic RAW SDK" in message
    assert "native helper not found" in message


@pytest.mark.skipif(
    not (BRAW_ADAPTER.exists() and SAMPLE_BRAW.exists() and SDK_LIBRARIES.exists()),
    reason="Blackmagic RAW SDK 5.1 sample media/runtime not installed on this host",
)
def test_native_braw_adapter_probe_and_capture_real_sample_no_proxy() -> None:
    rc, version = _run_adapter({"request_id": "version", "command": "version"})
    assert rc == 0
    assert version["ok"] is True
    assert version["metadata_raw"]["native_no_proxy"] is True

    rc, probe = _run_adapter(
        {
            "request_id": "probe",
            "command": "probe",
            "input": {"source_path": str(SAMPLE_BRAW)},
        }
    )
    assert rc == 0
    assert probe["ok"] is True
    clip = probe["clip"]
    assert clip["codec"] == "blackmagic_raw_native_sdk"
    assert clip["frame_count"] > 0
    assert clip["fps_num"] > 0
    assert clip["width"] > 0
    assert clip["height"] > 0
    assert probe["metadata_raw"]["native_no_proxy"] is True

    with tempfile.TemporaryDirectory() as tmp:
        rc, capture = _run_adapter(
            {
                "request_id": "capture",
                "command": "capture",
                "input": {"source_path": str(SAMPLE_BRAW)},
                "options": {"staging_dir": tmp},
                "capture_points": [
                    {"label": "Start", "requested_ratio": 0.0, "requested_frame_index": 0, "requested_seconds": 0},
                    {"label": "End", "requested_ratio": 1.0, "requested_frame_index": clip["frame_count"] - 1, "requested_seconds": None},
                ],
            }
        )
        assert rc == 0
        assert capture["ok"] is True
        assert capture["metadata_raw"]["native_no_proxy"] is True
        paths = [Path(item["image_path_temp"]) for item in capture["captures"]]
        assert all(path.exists() for path in paths)
        assert all(path.read_bytes().startswith(b"\x89PNG") for path in paths)
