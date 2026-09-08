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


def _fake_runtime(tmp_path: Path, helper_body: str) -> dict[str, str]:
    helper = tmp_path / "fake-braw-helper"
    helper.write_text(f"#!/bin/sh\n{helper_body}\n", encoding="utf-8")
    helper.chmod(0o755)
    libraries = tmp_path / "Libraries"
    (libraries / "BlackmagicRawAPI.framework").mkdir(parents=True)
    return {
        "FRAMEPROOF_BRAW_NATIVE_HELPER": str(helper),
        "BLACKMAGIC_RAW_SDK_LIBRARIES": str(libraries),
    }


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


def test_native_braw_adapter_version_executes_helper_runtime_check(tmp_path: Path) -> None:
    env = _fake_runtime(
        tmp_path,
        "test \"$1\" = version && test -d \"$2/BlackmagicRawAPI.framework\" || exit 9\n"
        "printf '%s' '{\"ok\":true,\"sdk_initialized\":true}'",
    )

    rc, response = _run_adapter({"request_id": "version-ok", "command": "version"}, env=env)

    assert rc == 0
    assert response["request_id"] == "version-ok"
    assert response["ok"] is True
    assert response["status"] == "success"


def test_native_braw_adapter_version_maps_helper_exit_127_to_dependency_missing(tmp_path: Path) -> None:
    env = _fake_runtime(tmp_path, "exit 127")

    rc, response = _run_adapter({"request_id": "version-exec-failed", "command": "version"}, env=env)

    assert rc == 2
    assert response["ok"] is False
    assert response["status"] == "dependency_missing"
    assert response["errors"][0]["code"] == "dependency_missing"
    assert "status 127" in response["errors"][0]["message"]


def test_native_braw_adapter_version_maps_invalid_helper_output_to_runtime_error(tmp_path: Path) -> None:
    env = _fake_runtime(tmp_path, "printf '%s' 'not-json'")

    rc, response = _run_adapter({"request_id": "version-invalid", "command": "version"}, env=env)

    assert rc == 2
    assert response["ok"] is False
    assert response["status"] == "runtime_error"
    assert response["errors"][0]["code"] == "runtime_error"
    assert "invalid JSON" in response["errors"][0]["message"]


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
