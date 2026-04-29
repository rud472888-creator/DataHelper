from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    active_env = os.environ.copy()
    if env is not None:
        active_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "frameproof", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=active_env,
    )


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


@pytest.fixture
def synthetic_standard_video(tmp_path: Path) -> Path:
    if not ffmpeg_available():
        pytest.skip("ffmpeg/ffprobe are not available in this environment")

    clip_path = tmp_path / "synthetic.mp4"
    subprocess.run(
        [
            shutil.which("ffmpeg") or "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=320x180:rate=24",
            "-t",
            "2",
            str(clip_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return clip_path
