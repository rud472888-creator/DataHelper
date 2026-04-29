from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def test_help_reports_stage_4c_cli_surface() -> None:
    result = run_cli("--help")

    assert result.returncode == 0
    assert "Frame Proof standard video CLI pipeline." in result.stdout
    assert "--input PATH" in result.stdout
    assert "--middle-count {0,1,2,3}" in result.stdout
    assert "--layout {contact_sheet,detail}" in result.stdout
    assert "--output PDF_PATH" in result.stdout
    assert "--export-stills" in result.stdout
    assert "--stills-dir PATH" in result.stdout
    assert "--braw-adapter-path PATH" in result.stdout
    assert "--r3d-adapter-path PATH" in result.stdout
    assert "--arri-art-cmd-path PATH" in result.stdout


def test_version_flag_matches_package_version() -> None:
    from frameproof import __version__

    result = run_cli("--version")

    assert result.returncode == 0
    assert result.stdout.strip() == __version__


def test_config_command_uses_default_path_when_env_is_absent(tmp_path: Path) -> None:
    result = run_cli("config", "--format", "json", env={"HOME": str(tmp_path), "FRAMEPROOF_CONFIG": ""})

    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["config_source"] == "default"
    assert payload["config_exists"] is False
    assert str(payload["config_path"]).endswith(".config/frameproof/config.toml")


def test_config_command_respects_env_override(tmp_path: Path) -> None:
    config_path = tmp_path / "frameproof.toml"
    config_path.write_text("log_level = 'info'\n", encoding="utf-8")

    result = run_cli("config", "--format", "json", env={"FRAMEPROOF_CONFIG": str(config_path)})

    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["config_source"] == "env"
    assert payload["config_exists"] is True
    assert payload["config_path"] == str(config_path.resolve())


def test_pipeline_requires_output_path_when_inputs_are_provided(tmp_path: Path) -> None:
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"not-a-real-video")

    result = run_cli("--input", str(clip_path))

    assert result.returncode == 2
    assert "--output is required for pipeline runs" in result.stderr


def test_pipeline_requires_stills_dir_when_exporting_stills(tmp_path: Path) -> None:
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"not-a-real-video")

    result = run_cli("--input", str(clip_path), "--output", str(tmp_path / "report.pdf"), "--export-stills")

    assert result.returncode == 2
    assert "--stills-dir is required when --export-stills is enabled" in result.stderr


def test_pipeline_reports_no_supported_inputs_when_only_unsupported_files_are_provided(tmp_path: Path) -> None:
    unsupported_path = tmp_path / "clip.txt"
    unsupported_path.write_text("not media", encoding="utf-8")

    result = run_cli("--input", str(unsupported_path), "--output", str(tmp_path / "report.pdf"))

    assert result.returncode == 2
    assert "status: failed" in result.stdout
    assert "fatal_reason: No supported input files were found." in result.stdout
