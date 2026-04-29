from __future__ import annotations

from pathlib import Path

import pytest

from frameproof.adapters.ffmpeg_adapter import FFmpegAdapter
from frameproof.config.settings import AdapterSettings
from frameproof.core.dependency_inspector import AdapterAvailability, DependencyRecord
from frameproof.core.models import (
    AdapterDependencyState,
    CapturePlan,
    CaptureProfile,
    CaptureRequest,
    CaptureStatus,
    ClipCandidate,
    ClipStatus,
)


def make_candidate(path: str = "/clips/A001_C001.mov") -> ClipCandidate:
    return ClipCandidate(candidate_id="candidate-0001", source_path=path, part_files=(path,), format_hint="mov")


def test_is_available_reports_missing_dependency_for_invalid_tool_paths() -> None:
    adapter = FFmpegAdapter(
        AdapterSettings(
            ffmpeg_path="/missing/ffmpeg",
            ffprobe_path="/missing/ffprobe",
            mediainfo_path="/missing/mediainfo",
        )
    )

    assert adapter.is_available() is AdapterDependencyState.CONFIGURED_MISSING


def test_probe_returns_dependency_missing_when_ffprobe_is_unavailable() -> None:
    adapter = FFmpegAdapter(
        AdapterSettings(
            ffmpeg_path="/missing/ffmpeg",
            ffprobe_path="/missing/ffprobe",
            mediainfo_path="/missing/mediainfo",
        )
    )

    result = adapter.probe(make_candidate())

    assert result.ok is False
    assert result.status is ClipStatus.DEPENDENCY_MISSING
    assert result.errors[0].message == "ffprobe is not available"


def test_capture_returns_decode_failures_when_ffmpeg_is_unavailable(tmp_path: Path) -> None:
    adapter = FFmpegAdapter(
        AdapterSettings(
            ffmpeg_path="/missing/ffmpeg",
            ffprobe_path="/missing/ffprobe",
            mediainfo_path="/missing/mediainfo",
        )
    )
    plan = CapturePlan(
        clip_id="candidate-0001",
        requests=(
            CaptureRequest(label="Start", requested_ratio=0.0, requested_frame_index=0),
            CaptureRequest(label="End", requested_ratio=1.0, requested_frame_index=23),
        ),
        middle_count=0,
        used_frame_count=True,
    )

    results = adapter.capture(make_candidate(), plan, profile=CaptureProfile(name="preview"), staging_dir=tmp_path)

    assert [result.status for result in results] == [CaptureStatus.DECODE_FAILED, CaptureStatus.DECODE_FAILED]


def test_probe_builds_clip_info_from_ffprobe_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = FFmpegAdapter(AdapterSettings())
    candidate = make_candidate()

    def fake_availability() -> AdapterAvailability:
        dependency = DependencyRecord(
            name="ffprobe",
            state=AdapterDependencyState.AVAILABLE,
            configured_path="ffprobe",
            resolved_path="/usr/bin/ffprobe",
        )
        return AdapterAvailability(
            adapter_name="ffmpeg",
            required_tools=("ffmpeg", "ffprobe"),
            state=AdapterDependencyState.AVAILABLE,
            dependencies=(dependency,),
        )

    def fake_probe_payload(_ffprobe_path: str, _candidate: ClipCandidate) -> dict[str, object]:
        return {
            "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": "2.0", "size": "2048"},
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "avg_frame_rate": "24/1",
                    "width": 1280,
                    "height": 720,
                    "nb_frames": "48",
                }
            ],
        }

    monkeypatch.setattr(adapter, "_availability", fake_availability)
    monkeypatch.setattr(adapter._inspector, "ffprobe", lambda: fake_availability().dependencies[0])
    monkeypatch.setattr(adapter, "_probe_payload", fake_probe_payload)

    result = adapter.probe(candidate)

    assert result.ok is True
    assert result.status is ClipStatus.SUCCESS
    assert result.clip is not None
    assert result.clip.codec == "h264"
    assert result.clip.frame_count == 48
    assert result.clip.width == 1280
