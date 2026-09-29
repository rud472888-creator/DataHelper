from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from frameproof.adapters.ffmpeg_adapter import CaptureContext, FFmpegAdapter
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


def test_capture_retries_with_color_metadata_repair_for_mov_swscale_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = FFmpegAdapter(AdapterSettings())
    dependency = DependencyRecord(
        name="ffmpeg",
        state=AdapterDependencyState.AVAILABLE,
        configured_path="ffmpeg",
        resolved_path="/usr/bin/ffmpeg",
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
    commands: list[list[str]] = []

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        del capture_output, text, check, timeout
        commands.append(command)
        if len(commands) == 1:
            raise subprocess.CalledProcessError(
                returncode=211,
                cmd=command,
                stderr="[swscaler] Unsupported input (Operation not supported): fmt:yuv422p10le",
            )
        Path(command[-1]).write_bytes(b"png")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(adapter._inspector, "ffmpeg", lambda: dependency)
    monkeypatch.setattr(adapter, "_capture_context", lambda _candidate: CaptureContext(fps_num=24, fps_den=1))
    monkeypatch.setattr(subprocess, "run", fake_run)

    results = adapter.capture(make_candidate(), plan, profile=CaptureProfile(name="preview"), staging_dir=tmp_path)

    assert [result.status for result in results] == [CaptureStatus.SUCCESS, CaptureStatus.SUCCESS]
    assert len(commands) == 3
    assert any(
        "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709" in arg
        for arg in commands[1]
    )


def test_capture_uses_fast_seek_seconds_for_frame_index_requests(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = FFmpegAdapter(AdapterSettings())
    dependency = DependencyRecord(
        name="ffmpeg",
        state=AdapterDependencyState.AVAILABLE,
        configured_path="ffmpeg",
        resolved_path="/usr/bin/ffmpeg",
    )
    plan = CapturePlan(
        clip_id="candidate-0001",
        requests=(
            CaptureRequest(label="Start", requested_ratio=0.0, requested_frame_index=0),
            CaptureRequest(label="Mid1", requested_ratio=0.5, requested_frame_index=48),
            CaptureRequest(label="End", requested_ratio=1.0, requested_frame_index=96),
        ),
        middle_count=1,
        used_frame_count=True,
    )
    commands: list[list[str]] = []

    def fake_run(
        command: list[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]:
        del capture_output, text, check, timeout
        commands.append(command)
        Path(command[-1]).write_bytes(b"png")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(adapter._inspector, "ffmpeg", lambda: dependency)
    monkeypatch.setattr(adapter, "_capture_context", lambda _candidate: CaptureContext(fps_num=24, fps_den=1))
    monkeypatch.setattr(subprocess, "run", fake_run)

    results = adapter.capture(make_candidate(), plan, profile=CaptureProfile(name="preview"), staging_dir=tmp_path)

    assert results[0].status is CaptureStatus.SUCCESS
    assert commands[1] == [
        "/usr/bin/ffmpeg",
        "-y",
        "-v",
        "error",
        "-ss",
        "2.000000",
        "-i",
        "/clips/A001_C001.mov",
        "-frames:v",
        "1",
        "-vf",
        "scale=min(960\\,iw):-2",
        str(tmp_path / "02_mid1.png"),
    ]


def _available(name: str) -> DependencyRecord:
    return DependencyRecord(
        name=name,
        state=AdapterDependencyState.AVAILABLE,
        configured_path=name,
        resolved_path=f"/usr/bin/{name}",
    )


def _build(ffprobe_payload: dict[str, object], mediainfo_payload: dict[str, object] | None = None):  # type: ignore[no-untyped-def]
    from frameproof.adapters.ffmpeg_adapter import _build_clip_info

    return _build_clip_info(make_candidate(), ffprobe_payload, mediainfo_payload)


def test_build_clip_info_reads_uppercase_matroska_timecode_tag() -> None:
    clip, warnings, _status = _build(
        {
            "format": {"format_name": "matroska,webm", "duration": "4.0", "tags": {"TIMECODE": "10:00:00:00"}},
            "streams": [{"codec_type": "video", "avg_frame_rate": "25/1", "width": 1920, "height": 1080}],
        }
    )

    assert clip.start_timecode == "10:00:00:00"
    assert "start_timecode_missing" not in warnings


def test_build_clip_info_reads_timecode_from_quicktime_tmcd_stream_and_mediainfo_other_track() -> None:
    clip, _warnings, _status = _build(
        {
            "format": {"format_name": "mov", "duration": "2.0"},
            "streams": [
                {"codec_type": "video", "avg_frame_rate": "24/1", "width": 1920, "height": 1080, "nb_frames": "48"},
                {"codec_type": "data", "codec_tag_string": "tmcd", "tags": {"timecode": "01:02:03:04"}},
            ],
        }
    )
    assert clip.start_timecode == "01:02:03:04"

    clip, _warnings, _status = _build(
        {
            "format": {"format_name": "mxf", "duration": "2.0"},
            "streams": [{"codec_type": "video", "avg_frame_rate": "24/1", "width": 1920, "height": 1080}],
        },
        {"media": {"track": [{"@type": "Video"}, {"@type": "Other", "TimeCode_FirstFrame": "05:00:00:00"}]}},
    )
    assert clip.start_timecode == "05:00:00:00"


def test_build_clip_info_treats_zero_frame_count_and_rate_as_unknown() -> None:
    clip, _warnings, status = _build(
        {
            "format": {"format_name": "mxf", "duration": "2.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "avg_frame_rate": "0/0",
                    "r_frame_rate": "25/1",
                    "width": 1920,
                    "height": 1080,
                    "nb_frames": "0",
                }
            ],
        }
    )

    assert (clip.fps_num, clip.fps_den) == (25, 1)
    assert clip.frame_count == 50
    assert status is ClipStatus.SUCCESS


def test_build_clip_info_snaps_mediainfo_float_rate_to_ntsc_rational() -> None:
    clip, _warnings, _status = _build(
        {
            "format": {"format_name": "mxf", "duration": "1.001"},
            "streams": [{"codec_type": "video", "avg_frame_rate": "0/0", "width": 1920, "height": 1080}],
        },
        {"media": {"track": [{"@type": "Video", "FrameRate": "29.970"}]}},
    )

    assert (clip.fps_num, clip.fps_den) == (30000, 1001)


def test_capture_reuses_probe_payload_instead_of_running_ffprobe_again(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = FFmpegAdapter(AdapterSettings())
    probe_calls: list[str] = []

    def fake_probe_payload(_ffprobe_path: str, candidate: ClipCandidate) -> dict[str, object]:
        probe_calls.append(candidate.source_path)
        return {
            "format": {"format_name": "mov", "duration": "2.0"},
            "streams": [
                {"codec_type": "video", "avg_frame_rate": "24/1", "width": 1280, "height": 720, "nb_frames": "48"}
            ],
        }

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        Path(command[-1]).write_bytes(b"png")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(adapter._inspector, "ffprobe", lambda: _available("ffprobe"))
    monkeypatch.setattr(adapter._inspector, "ffmpeg", lambda: _available("ffmpeg"))
    monkeypatch.setattr(adapter, "_probe_payload", fake_probe_payload)
    monkeypatch.setattr(subprocess, "run", fake_run)
    plan = CapturePlan(
        clip_id="candidate-0001",
        requests=(
            CaptureRequest(label="Start", requested_ratio=0.0, requested_frame_index=0),
            CaptureRequest(label="End", requested_ratio=1.0, requested_frame_index=47),
        ),
        middle_count=0,
        used_frame_count=True,
    )

    assert adapter.probe(make_candidate()).ok is True
    results = adapter.capture(make_candidate(), plan, profile=CaptureProfile(name="preview"), staging_dir=tmp_path)

    assert probe_calls == ["/clips/A001_C001.mov"]
    assert results[1].actual_seconds == pytest.approx(47 / 24)
