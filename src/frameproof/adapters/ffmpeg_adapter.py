from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from frameproof.config.settings import AdapterSettings
from frameproof.core.dependency_inspector import AdapterAvailability, DependencyInspector
from frameproof.core.models import (
    AdapterDependencyState,
    AdapterError,
    AdapterErrorCode,
    CapturePlan,
    CaptureProfile,
    CaptureRequest,
    CaptureResult,
    CaptureStatus,
    ClipCandidate,
    ClipInfo,
    ClipStatus,
    FormatFamily,
    ProbeResult,
    TimecodeSource,
)

STANDARD_FAMILY: tuple[str, ...] = ("standard",)
COLOR_METADATA_REPAIR_FILTER = "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709"


@dataclass(frozen=True)
class CaptureContext:
    fps_num: int | None
    fps_den: int | None

    def seconds_for_frame(self, frame_index: int | None) -> float | None:
        if frame_index is None or self.fps_num is None or self.fps_den is None:
            return None
        return (frame_index * self.fps_den) / self.fps_num


class FFmpegAdapter:
    name = "ffmpeg"
    format_families = STANDARD_FAMILY
    required_tools: tuple[str, ...] = ("ffmpeg", "ffprobe")

    def __init__(self, settings: AdapterSettings) -> None:
        self._settings = settings
        self._inspector = DependencyInspector(settings)

    def is_available(self) -> AdapterDependencyState:
        return self._availability().state

    def dependency_details(self) -> Mapping[str, object]:
        return self._availability().error_detail()

    def probe(self, candidate: ClipCandidate) -> ProbeResult:
        ffprobe = self._inspector.ffprobe()
        if ffprobe.resolved_path is None:
            return _dependency_missing_probe(candidate, ffprobe.name, self._availability())

        try:
            ffprobe_payload = self._probe_payload(ffprobe.resolved_path, candidate)
        except subprocess.TimeoutExpired:
            return _probe_failure(candidate, "ffprobe timed out", AdapterErrorCode.TIMEOUT)
        except subprocess.CalledProcessError as exc:
            return _probe_failure(candidate, exc.stderr.strip() or "ffprobe failed", AdapterErrorCode.PROBE_FAILED)
        except json.JSONDecodeError:
            return _probe_failure(candidate, "ffprobe returned invalid JSON", AdapterErrorCode.INVALID_RESPONSE)

        mediainfo_payload: Mapping[str, object] | None = None
        if _needs_mediainfo_fallback(ffprobe_payload):
            mediainfo = self._inspector.mediainfo()
            if mediainfo.resolved_path is not None:
                try:
                    mediainfo_payload = self._run_json_command(
                        [mediainfo.resolved_path, "--Output=JSON", candidate.source_path],
                        timeout_seconds=30,
                    )
                except (subprocess.SubprocessError, json.JSONDecodeError):
                    mediainfo_payload = None

        try:
            clip, warnings, status = _build_clip_info(candidate, ffprobe_payload, mediainfo_payload)
        except ValueError as exc:
            return _probe_failure(candidate, str(exc), AdapterErrorCode.PROBE_FAILED, ffprobe_payload, mediainfo_payload)

        return ProbeResult(
            ok=True,
            adapter_name=self.name,
            format_family=FormatFamily.STANDARD,
            clip=clip,
            warnings=warnings,
            status=status,
            metadata_raw=_build_metadata_raw(candidate, ffprobe_payload, mediainfo_payload),
        )

    def capture(
        self,
        candidate: ClipCandidate,
        plan: CapturePlan,
        profile: CaptureProfile,
        staging_dir: Path,
    ) -> tuple[CaptureResult, ...]:
        del profile
        ffmpeg = self._inspector.ffmpeg()
        if ffmpeg.resolved_path is None:
            error = AdapterError(
                code=AdapterErrorCode.DEPENDENCY_MISSING,
                message="ffmpeg is not available",
                detail=self._availability().error_detail(),
            )
            return tuple(_decode_failed_result(request, error=error) for request in plan.requests)

        context = self._capture_context(candidate)
        results: list[CaptureResult] = []
        by_label: dict[str, CaptureResult] = {}

        for index, request in enumerate(plan.requests, start=1):
            if request.duplicate_of is not None:
                original = by_label[request.duplicate_of]
                duplicate_result = CaptureResult(
                    label=request.label,
                    requested_ratio=request.requested_ratio,
                    requested_frame_index=request.requested_frame_index,
                    requested_seconds=request.requested_seconds,
                    actual_frame_index=original.actual_frame_index,
                    actual_seconds=original.actual_seconds,
                    actual_timecode=original.actual_timecode,
                    actual_timecode_source=original.actual_timecode_source,
                    image_path_temp=original.image_path_temp,
                    duplicate_of=request.duplicate_of,
                    status=CaptureStatus.SKIPPED_DUPLICATE,
                    warnings=("short_clip_duplicate",),
                )
                results.append(duplicate_result)
                by_label[duplicate_result.label] = duplicate_result
                continue

            output_path = staging_dir / f"{index:02d}_{request.label.lower()}.png"
            command = _build_capture_command(ffmpeg.resolved_path, candidate.source_path, request, output_path)
            try:
                subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
            except subprocess.TimeoutExpired:
                failed = _decode_failed_result(
                    request,
                    error=AdapterError(code=AdapterErrorCode.TIMEOUT, message="ffmpeg capture timed out"),
                )
                results.append(failed)
                by_label[failed.label] = failed
                continue
            except subprocess.CalledProcessError as exc:
                if _is_swscale_color_metadata_failure(exc.stderr):
                    repaired_command = _build_capture_command(
                        ffmpeg.resolved_path,
                        candidate.source_path,
                        request,
                        output_path,
                        repair_color_metadata=True,
                    )
                    try:
                        subprocess.run(repaired_command, capture_output=True, text=True, check=True, timeout=60)
                    except subprocess.TimeoutExpired:
                        failed = _decode_failed_result(
                            request,
                            error=AdapterError(code=AdapterErrorCode.TIMEOUT, message="ffmpeg capture timed out"),
                        )
                        results.append(failed)
                        by_label[failed.label] = failed
                        continue
                    except subprocess.CalledProcessError as retry_exc:
                        failed = _decode_failed_result(
                            request,
                            error=AdapterError(
                                code=AdapterErrorCode.DECODE_FAILED,
                                message=retry_exc.stderr.strip() or exc.stderr.strip() or "ffmpeg capture failed",
                            ),
                        )
                        results.append(failed)
                        by_label[failed.label] = failed
                        continue
                else:
                    failed = _decode_failed_result(
                        request,
                        error=AdapterError(
                            code=AdapterErrorCode.DECODE_FAILED,
                            message=exc.stderr.strip() or "ffmpeg capture failed",
                        ),
                    )
                    results.append(failed)
                    by_label[failed.label] = failed
                    continue

            if not output_path.is_file():
                failed = _decode_failed_result(
                    request,
                    error=AdapterError(
                        code=AdapterErrorCode.DECODE_FAILED,
                        message="ffmpeg completed without writing an output image",
                    ),
                )
                results.append(failed)
                by_label[failed.label] = failed
                continue

            result = CaptureResult(
                label=request.label,
                requested_ratio=request.requested_ratio,
                requested_frame_index=request.requested_frame_index,
                requested_seconds=request.requested_seconds,
                actual_frame_index=request.requested_frame_index,
                actual_seconds=_actual_seconds(request, context),
                actual_timecode=None,
                actual_timecode_source=None,
                image_path_temp=str(output_path),
                status=CaptureStatus.SUCCESS,
            )
            results.append(result)
            by_label[result.label] = result

        return tuple(results)

    def _capture_context(self, candidate: ClipCandidate) -> CaptureContext:
        ffprobe = self._inspector.ffprobe()
        if ffprobe.resolved_path is None:
            return CaptureContext(fps_num=None, fps_den=None)
        try:
            payload = self._probe_payload(ffprobe.resolved_path, candidate)
        except (subprocess.SubprocessError, json.JSONDecodeError):
            return CaptureContext(fps_num=None, fps_den=None)

        streams = payload.get("streams")
        if not isinstance(streams, list):
            return CaptureContext(fps_num=None, fps_den=None)
        for stream in streams:
            if isinstance(stream, dict) and stream.get("codec_type") == "video":
                fps_num, fps_den = _parse_frame_rate(stream, None)
                return CaptureContext(fps_num=fps_num, fps_den=fps_den)
        return CaptureContext(fps_num=None, fps_den=None)

    def _probe_payload(self, ffprobe_path: str, candidate: ClipCandidate) -> Mapping[str, object]:
        return self._run_json_command(
            [
                ffprobe_path,
                "-v",
                "error",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                candidate.source_path,
            ]
        )

    def _run_json_command(
        self,
        command: list[str],
        *,
        timeout_seconds: int = 60,
    ) -> Mapping[str, object]:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout_seconds,
        )
        payload = json.loads(completed.stdout)
        if not isinstance(payload, dict):
            raise json.JSONDecodeError("Expected object payload", completed.stdout, 0)
        return payload

    def _availability(self) -> AdapterAvailability:
        return self._inspector.availability_for_adapter(self.name)


def _build_capture_command(
    ffmpeg_path: str,
    source_path: str,
    request: CaptureRequest,
    output_path: Path,
    *,
    repair_color_metadata: bool = False,
) -> list[str]:
    command = [ffmpeg_path, "-y", "-v", "error"]
    if request.requested_seconds is not None:
        command.extend(
            [
                "-ss",
                f"{request.requested_seconds:.6f}",
                "-i",
                source_path,
                "-frames:v",
                "1",
                "-vf",
                _build_scale_filter(repair_color_metadata=repair_color_metadata),
                str(output_path),
            ]
        )
        return command

    assert request.requested_frame_index is not None
    command.extend(
        [
            "-i",
            source_path,
            "-vf",
            _build_frame_filter(request.requested_frame_index, repair_color_metadata=repair_color_metadata),
            "-frames:v",
            "1",
            "-fps_mode",
            "vfr",
            str(output_path),
        ]
    )
    return command


def _build_frame_filter(frame_index: int, *, repair_color_metadata: bool) -> str:
    return ",".join((f"select=eq(n\\,{frame_index})", _build_scale_filter(repair_color_metadata=repair_color_metadata)))


def _build_scale_filter(*, repair_color_metadata: bool) -> str:
    filters = ["scale=min(960\\,iw):-2"]
    if repair_color_metadata:
        filters.insert(0, COLOR_METADATA_REPAIR_FILTER)
        filters.append("format=rgb24")
    return ",".join(filters)


def _is_swscale_color_metadata_failure(stderr: str | None) -> bool:
    if stderr is None:
        return False
    return "Unsupported input (Operation not supported)" in stderr and "swscaler" in stderr


def _decode_failed_result(request: CaptureRequest, *, error: AdapterError) -> CaptureResult:
    return CaptureResult(
        label=request.label,
        requested_ratio=request.requested_ratio,
        requested_frame_index=request.requested_frame_index,
        requested_seconds=request.requested_seconds,
        duplicate_of=request.duplicate_of,
        status=CaptureStatus.DECODE_FAILED,
        errors=(error,),
    )


def _actual_seconds(request: CaptureRequest, context: CaptureContext) -> float | None:
    if request.requested_seconds is not None:
        return request.requested_seconds
    return context.seconds_for_frame(request.requested_frame_index)


def _build_metadata_raw(
    candidate: ClipCandidate,
    ffprobe_payload: Mapping[str, object] | None = None,
    mediainfo_payload: Mapping[str, object] | None = None,
) -> dict[str, object]:
    metadata_raw: dict[str, object] = {
        "candidate_id": candidate.candidate_id,
        "source_path": candidate.source_path,
        "clip_name": Path(candidate.source_path).name,
    }
    if ffprobe_payload is not None:
        metadata_raw["ffprobe"] = ffprobe_payload
    if mediainfo_payload is not None:
        metadata_raw["mediainfo"] = mediainfo_payload
    return metadata_raw


def _dependency_missing_probe(
    candidate: ClipCandidate,
    dependency_name: str,
    availability: AdapterAvailability,
) -> ProbeResult:
    return ProbeResult(
        ok=False,
        adapter_name="ffmpeg",
        format_family=FormatFamily.STANDARD,
        status=ClipStatus.DEPENDENCY_MISSING,
        errors=(
            AdapterError(
                code=AdapterErrorCode.DEPENDENCY_MISSING,
                message=f"{dependency_name} is not available",
                detail=availability.error_detail(),
            ),
        ),
        metadata_raw=_build_metadata_raw(candidate),
    )


def _probe_failure(
    candidate: ClipCandidate,
    message: str,
    code: AdapterErrorCode,
    ffprobe_payload: Mapping[str, object] | None = None,
    mediainfo_payload: Mapping[str, object] | None = None,
) -> ProbeResult:
    return ProbeResult(
        ok=False,
        adapter_name="ffmpeg",
        format_family=FormatFamily.STANDARD,
        status=ClipStatus.PROBE_FAILED if code is not AdapterErrorCode.DEPENDENCY_MISSING else ClipStatus.DEPENDENCY_MISSING,
        errors=(AdapterError(code=code, message=message),),
        metadata_raw=_build_metadata_raw(candidate, ffprobe_payload, mediainfo_payload),
    )


def _build_clip_info(
    candidate: ClipCandidate,
    ffprobe_payload: Mapping[str, object],
    mediainfo_payload: Mapping[str, object] | None,
) -> tuple[ClipInfo, tuple[str, ...], ClipStatus]:
    streams = ffprobe_payload.get("streams")
    if not isinstance(streams, list):
        raise ValueError("ffprobe output did not include stream metadata")

    video_stream = next(
        (stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "video"),
        None,
    )
    if video_stream is None:
        raise ValueError("No video stream found")

    format_section = ffprobe_payload.get("format")
    if not isinstance(format_section, dict):
        raise ValueError("ffprobe output did not include format metadata")

    mediainfo_track = _extract_mediainfo_video_track(mediainfo_payload)
    fps_num, fps_den = _parse_frame_rate(video_stream, mediainfo_track)
    duration_seconds = _first_float(
        video_stream.get("duration"),
        format_section.get("duration"),
        mediainfo_track.get("Duration") if mediainfo_track is not None else None,
    )
    frame_count = _first_int(
        video_stream.get("nb_frames"),
        _nested_get(video_stream, "tags", "NUMBER_OF_FRAMES"),
        mediainfo_track.get("FrameCount") if mediainfo_track is not None else None,
    )
    if frame_count is None and duration_seconds is not None and fps_num is not None and fps_den is not None:
        frame_count = max(round(duration_seconds * fps_num / fps_den), 1)

    start_timecode = _first_text(
        _nested_get(video_stream, "tags", "timecode"),
        _nested_get(format_section, "tags", "timecode"),
        mediainfo_track.get("TimeCode_FirstFrame") if mediainfo_track is not None else None,
        mediainfo_track.get("TimeCode_Start") if mediainfo_track is not None else None,
    )
    width = _first_int(video_stream.get("width"), mediainfo_track.get("Width") if mediainfo_track is not None else None)
    height = _first_int(video_stream.get("height"), mediainfo_track.get("Height") if mediainfo_track is not None else None)

    if frame_count is None and duration_seconds is None:
        raise ValueError("No duration or frame count metadata was available")

    warnings: list[str] = []
    if mediainfo_payload is not None:
        warnings.append("mediainfo_fallback_consulted")
    if start_timecode is None:
        warnings.append("start_timecode_missing")

    status = ClipStatus.SUCCESS
    if frame_count is None or fps_num is None or fps_den is None or width is None or height is None:
        status = ClipStatus.METADATA_INCOMPLETE

    metadata_raw = _build_metadata_raw(candidate, ffprobe_payload, mediainfo_payload)
    clip = ClipInfo(
        clip_id=candidate.candidate_id,
        clip_name=Path(candidate.source_path).name,
        logical_clip_name=None,
        source_path=candidate.source_path,
        part_files=candidate.part_files,
        format_family=FormatFamily.STANDARD,
        container=_normalize_container(format_section.get("format_name"), candidate),
        codec=_first_text(
            video_stream.get("codec_name"),
            mediainfo_track.get("CodecID/Hint") if mediainfo_track is not None else None,
        ),
        file_size_bytes=_first_int(candidate.file_size_bytes, format_section.get("size")),
        duration_seconds=duration_seconds,
        frame_count=frame_count,
        fps_num=fps_num,
        fps_den=fps_den,
        width=width,
        height=height,
        camera_make=_first_text(
            _nested_get(format_section, "tags", "com.apple.proapps.manufacturer"),
            mediainfo_track.get("Encoded_Application") if mediainfo_track is not None else None,
        ),
        camera_model=_first_text(_nested_get(format_section, "tags", "model")),
        reel=_first_text(_nested_get(format_section, "tags", "reel_name")),
        camera_id=_first_text(_nested_get(format_section, "tags", "camera_id")),
        start_timecode=start_timecode,
        timecode_source=TimecodeSource.CONTAINER_METADATA if start_timecode is not None else None,
        tc_drop_frame=";" in start_timecode if start_timecode is not None else None,
        metadata_raw=metadata_raw,
    )
    return clip, tuple(warnings), status


def _needs_mediainfo_fallback(payload: Mapping[str, object]) -> bool:
    streams = payload.get("streams")
    if not isinstance(streams, list):
        return True

    video_stream = next(
        (stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "video"),
        None,
    )
    if video_stream is None:
        return True

    if video_stream.get("nb_frames") in (None, "N/A"):
        return True
    if _first_int(video_stream.get("width")) is None or _first_int(video_stream.get("height")) is None:
        return True
    fps_num, fps_den = _parse_frame_rate(video_stream, None)
    return fps_num is None or fps_den is None


def _extract_mediainfo_video_track(payload: Mapping[str, object] | None) -> Mapping[str, Any] | None:
    if payload is None:
        return None
    media = payload.get("media")
    if not isinstance(media, dict):
        return None
    track_list = media.get("track")
    if not isinstance(track_list, list):
        return None
    for track in track_list:
        if isinstance(track, dict) and str(track.get("@type", "")).lower() == "video":
            return track
    return None


def _parse_frame_rate(
    video_stream: Mapping[str, object],
    mediainfo_track: Mapping[str, Any] | None,
) -> tuple[int | None, int | None]:
    for key in ("avg_frame_rate", "r_frame_rate"):
        parsed = _parse_fraction(video_stream.get(key))
        if parsed is not None:
            return parsed

    if mediainfo_track is not None:
        parsed = _parse_fraction(mediainfo_track.get("FrameRate_Num"), mediainfo_track.get("FrameRate_Den"))
        if parsed is not None:
            return parsed
        parsed_float = _first_float(mediainfo_track.get("FrameRate"))
        if parsed_float is not None and parsed_float > 0:
            thousand = 1000
            return round(parsed_float * thousand), thousand

    return None, None


def _parse_fraction(value: object, denominator: object | None = None) -> tuple[int, int] | None:
    if isinstance(value, str) and "/" in value:
        left, right = value.split("/", 1)
        left_int = _first_int(left)
        right_int = _first_int(right)
        if left_int is not None and right_int not in (None, 0):
            assert right_int is not None
            return left_int, right_int
    if denominator is not None:
        left_int = _first_int(value)
        right_int = _first_int(denominator)
        if left_int is not None and right_int not in (None, 0):
            assert right_int is not None
            return left_int, right_int
    return None


def _normalize_container(value: object, candidate: ClipCandidate) -> str:
    text = _first_text(value)
    if text is None:
        return Path(candidate.source_path).suffix.lstrip(".").upper() or "UNKNOWN"
    return text.split(",", 1)[0].upper()


def _first_text(*values: object) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text and text.upper() != "N/A":
            return text
    return None


def _first_int(*values: object) -> int | None:
    for value in values:
        if value is None or isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        text = str(value).strip()
        if not text or text.upper() == "N/A":
            continue
        try:
            return int(float(text))
        except ValueError:
            continue
    return None


def _first_float(*values: object) -> float | None:
    for value in values:
        if value is None or isinstance(value, bool):
            continue
        if isinstance(value, float):
            return value
        if isinstance(value, int):
            return float(value)
        text = str(value).strip()
        if not text or text.upper() == "N/A":
            continue
        try:
            return float(text)
        except ValueError:
            continue
    return None


def _nested_get(value: object, *keys: str) -> object | None:
    current = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current
