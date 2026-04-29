from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Mapping, Sequence

from PIL import Image

from frameproof.adapters.base import CaptureAdapter
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

_PROBE_TIMEOUT_SECONDS = 60
_CAPTURE_TIMEOUT_SECONDS = 120
_TARGET_COLORSPACE = "Rec.709/D65/BT.1886"


class ARRIRAWArtAdapterClient(CaptureAdapter):
    name = "arriraw_art_adapter"
    format_families = (FormatFamily.ARRIRAW.value,)
    required_tools = ("arri_art_cmd",)

    def __init__(self, settings: AdapterSettings) -> None:
        self._settings = settings
        self._inspector = DependencyInspector(settings)

    def is_available(self) -> AdapterDependencyState:
        return self._availability().state

    def dependency_details(self) -> Mapping[str, object]:
        return self._availability().error_detail()

    def probe(self, candidate: ClipCandidate) -> ProbeResult:
        availability = self._availability()
        dependency = availability.dependencies[0]
        if dependency.resolved_path is None:
            return _dependency_missing_probe(candidate, availability)

        with tempfile.TemporaryDirectory(prefix="frameproof-arri-probe-") as temporary_root:
            metadata_path = Path(temporary_root) / "metadata.json"
            command = _metadata_export_command(dependency.resolved_path, candidate.source_path, metadata_path)
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=_PROBE_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                return _probe_failure(candidate, "ARRI ART CMD probe timed out", AdapterErrorCode.TIMEOUT)
            except subprocess.CalledProcessError as exc:
                return _probe_failure(
                    candidate,
                    exc.stderr.strip() or "ARRI ART CMD metadata export failed",
                    AdapterErrorCode.PROBE_FAILED,
                )
            except OSError as exc:
                return ProbeResult(
                    ok=False,
                    adapter_name=self.name,
                    format_family=FormatFamily.ARRIRAW,
                    status=ClipStatus.DEPENDENCY_MISSING,
                    errors=(
                        AdapterError(
                            code=AdapterErrorCode.DEPENDENCY_MISSING,
                            message="ARRI ART CMD is not available",
                            detail={"exception": str(exc), **availability.error_detail()},
                        ),
                    ),
                    metadata_raw=_metadata_raw(candidate),
                )

            if not metadata_path.is_file():
                return _probe_failure(
                    candidate,
                    "ARRI ART CMD metadata export did not write a JSON file",
                    AdapterErrorCode.INVALID_RESPONSE,
                )

            try:
                metadata_payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return _probe_failure(candidate, "ARRI ART CMD metadata JSON was malformed", AdapterErrorCode.INVALID_RESPONSE)
            if not isinstance(metadata_payload, dict):
                return _probe_failure(
                    candidate,
                    "ARRI ART CMD metadata JSON must contain an object payload",
                    AdapterErrorCode.INVALID_RESPONSE,
                )

            clip_payload = metadata_payload.get("clip")
            if isinstance(clip_payload, dict):
                normalized_clip_payload = clip_payload
                warnings = _string_list(metadata_payload.get("warnings"))
                errors = _adapter_errors(metadata_payload.get("errors"))
                status_text = metadata_payload.get("status", ClipStatus.SUCCESS.value)
            else:
                normalized_clip_payload = _clip_payload_from_art_metadata(candidate, metadata_payload)
                warnings = ()
                errors = ()
                status_text = ClipStatus.SUCCESS.value

            try:
                status = ClipStatus(str(status_text))
                if status not in {ClipStatus.SUCCESS, ClipStatus.METADATA_INCOMPLETE}:
                    raise ValueError("probe status must be success or metadata_incomplete")
                clip = _build_clip_info(candidate, normalized_clip_payload)
            except (ValueError, TypeError) as exc:
                return _probe_failure(candidate, str(exc), AdapterErrorCode.INVALID_RESPONSE)

            metadata_raw = _metadata_raw(candidate)
            metadata_raw["response"] = metadata_payload
            if completed.stderr.strip():
                metadata_raw["stderr"] = completed.stderr.strip()
            return ProbeResult(
                ok=True,
                adapter_name=self.name,
                format_family=FormatFamily.ARRIRAW,
                clip=clip,
                warnings=warnings,
                errors=errors,
                status=status,
                metadata_raw=metadata_raw,
            )

    def capture(
        self,
        candidate: ClipCandidate,
        plan: CapturePlan,
        profile: CaptureProfile,
        staging_dir: Path,
    ) -> Sequence[CaptureResult]:
        del profile
        availability = self._availability()
        dependency = availability.dependencies[0]
        if dependency.resolved_path is None:
            return _failed_capture_results(
                plan,
                error=AdapterError(
                    code=AdapterErrorCode.DEPENDENCY_MISSING,
                    message="ARRI ART CMD is not available",
                    detail=availability.error_detail(),
                ),
            )

        results: list[CaptureResult] = []
        by_label: dict[str, CaptureResult] = {}
        for index, request in enumerate(plan.requests, start=1):
            if request.duplicate_of is not None:
                source = by_label[request.duplicate_of]
                duplicate = CaptureResult(
                    label=request.label,
                    requested_ratio=request.requested_ratio,
                    requested_frame_index=request.requested_frame_index,
                    requested_seconds=request.requested_seconds,
                    actual_frame_index=source.actual_frame_index,
                    actual_seconds=source.actual_seconds,
                    actual_timecode=source.actual_timecode,
                    actual_timecode_source=source.actual_timecode_source,
                    image_path_temp=source.image_path_temp,
                    duplicate_of=request.duplicate_of,
                    status=CaptureStatus.SKIPPED_DUPLICATE,
                    warnings=("short_clip_duplicate",),
                )
                results.append(duplicate)
                by_label[duplicate.label] = duplicate
                continue

            output_path = staging_dir / f"{index:02d}_{request.label.lower()}.png"
            art_output_path = staging_dir / f"{index:02d}_{request.label.lower()}_art.tif"
            command = _process_frame_command(
                dependency.resolved_path,
                candidate.source_path,
                art_output_path,
                request,
            )

            try:
                subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=_CAPTURE_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                failed = _decode_failed_result(
                    request=request,
                    error=AdapterError(code=AdapterErrorCode.TIMEOUT, message="ARRI ART CMD capture timed out"),
                )
                results.append(failed)
                by_label[failed.label] = failed
                continue
            except subprocess.CalledProcessError as exc:
                failed = _decode_failed_result(
                    request=request,
                    error=AdapterError(
                        code=AdapterErrorCode.DECODE_FAILED,
                        message=exc.stderr.strip() or "ARRI ART CMD process command failed",
                    ),
                )
                results.append(failed)
                by_label[failed.label] = failed
                continue
            except OSError as exc:
                failed = _decode_failed_result(
                    request=request,
                    error=AdapterError(
                        code=AdapterErrorCode.DEPENDENCY_MISSING,
                        message="ARRI ART CMD is not available",
                        detail={"exception": str(exc), **availability.error_detail()},
                    ),
                )
                results.append(failed)
                by_label[failed.label] = failed
                continue

            if not art_output_path.is_file():
                failed = _decode_failed_result(
                    request=request,
                    error=AdapterError(
                        code=AdapterErrorCode.DECODE_FAILED,
                        message="ARRI ART CMD completed without writing a still output",
                    ),
                )
                results.append(failed)
                by_label[failed.label] = failed
                continue
            try:
                _convert_art_still_to_png(art_output_path, output_path)
            except OSError as exc:
                failed = _decode_failed_result(
                    request=request,
                    error=AdapterError(
                        code=AdapterErrorCode.DECODE_FAILED,
                        message="ARRI ART CMD still output could not be converted to PNG",
                        detail={"exception": str(exc), "art_output_path": str(art_output_path)},
                    ),
                )
                results.append(failed)
                by_label[failed.label] = failed
                continue

            success = CaptureResult(
                label=request.label,
                requested_ratio=request.requested_ratio,
                requested_frame_index=request.requested_frame_index,
                requested_seconds=request.requested_seconds,
                actual_frame_index=request.requested_frame_index,
                actual_seconds=request.requested_seconds,
                actual_timecode=None,
                actual_timecode_source=None,
                image_path_temp=str(output_path),
                status=CaptureStatus.SUCCESS,
            )
            results.append(success)
            by_label[success.label] = success

        return tuple(results)

    def _availability(self) -> AdapterAvailability:
        return self._inspector.availability_for_adapter(self.name)


def _build_clip_info(candidate: ClipCandidate, payload: Mapping[str, object]) -> ClipInfo:
    start_timecode = _optional_text(payload.get("start_timecode"))
    return ClipInfo(
        clip_id=_optional_text(payload.get("clip_id")) or candidate.candidate_id,
        clip_name=_require_text(payload.get("clip_name"), "clip.clip_name"),
        source_path=candidate.source_path,
        part_files=candidate.part_files,
        format_family=FormatFamily.ARRIRAW,
        container=_optional_text(payload.get("container")) or candidate.source_path.rsplit(".", 1)[-1].upper(),
        codec=_optional_text(payload.get("codec")) or "ARRIRAW",
        file_size_bytes=candidate.file_size_bytes,
        duration_seconds=_optional_float(payload.get("duration_seconds")),
        frame_count=_optional_int(payload.get("frame_count")),
        fps_num=_optional_int(payload.get("fps_num")),
        fps_den=_optional_int(payload.get("fps_den")),
        width=_optional_int(payload.get("width")),
        height=_optional_int(payload.get("height")),
        camera_make=_optional_text(payload.get("camera_make")),
        camera_model=_optional_text(payload.get("camera_model")),
        reel=_optional_text(payload.get("reel")),
        camera_id=_optional_text(payload.get("camera_id")),
        start_timecode=start_timecode,
        end_timecode=_optional_text(payload.get("end_timecode")),
        timecode_source=TimecodeSource.NATIVE_ADAPTER if start_timecode is not None else None,
        tc_drop_frame=(";" in start_timecode) if start_timecode is not None else _optional_bool(payload.get("tc_drop_frame")),
        metadata_raw={"candidate_id": candidate.candidate_id, "source_path": candidate.source_path},
    )


def _metadata_export_command(
    executable_path: str,
    source_path: str,
    metadata_path: Path,
) -> list[str]:
    return [
        executable_path,
        "export",
        "--input",
        source_path,
        "--output",
        str(metadata_path),
        "--skip-audio",
        "--skip-look",
    ]


def _process_frame_command(
    executable_path: str,
    source_path: str,
    output_path: Path,
    request: CaptureRequest,
) -> list[str]:
    command = [
        executable_path,
        "process",
        "--input",
        source_path,
        "--output",
        str(output_path),
        "--duration",
        "1",
        "--target-colorspace",
        _TARGET_COLORSPACE,
    ]
    if request.requested_frame_index is not None:
        command.extend(["--start", str(request.requested_frame_index)])
    elif request.requested_seconds is not None:
        command.extend(["--start", "0"])
    return command


def _convert_art_still_to_png(source_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as image:
        image.convert("RGB").save(output_path, format="PNG")


def _clip_payload_from_art_metadata(candidate: ClipCandidate, payload: Mapping[str, object]) -> dict[str, object]:
    frame_count = _first_int(payload, ("frame_count", "frameCount", "frames", "durationFrames"))
    duration_seconds = _first_float(payload, ("duration_seconds", "durationSeconds", "duration"))
    fps_num = _first_int(payload, ("fps_num", "fpsNum", "frameRateNumerator"))
    fps_den = _first_int(payload, ("fps_den", "fpsDen", "frameRateDenominator"))
    fps = _first_float(payload, ("fps", "frameRate"))
    if fps is not None and fps_num is None and fps_den is None:
        fps_num = round(fps * 1000)
        fps_den = 1000
    return {
        "clip_name": Path(candidate.source_path).name,
        "clip_id": candidate.candidate_id,
        "frame_count": frame_count,
        "duration_seconds": duration_seconds if duration_seconds is not None else 0.0,
        "fps_num": fps_num,
        "fps_den": fps_den,
        "container": Path(candidate.source_path).suffix.lstrip(".").upper() or "ARRIRAW",
        "codec": "ARRIRAW",
        "width": _first_int(payload, ("width", "imageWidth", "storedWidth")),
        "height": _first_int(payload, ("height", "imageHeight", "storedHeight")),
        "camera_make": "ARRI",
        "camera_model": _first_text(payload, ("camera_model", "cameraModel", "cameraType")),
        "reel": _first_text(payload, ("reel", "reelName")),
        "camera_id": _first_text(payload, ("camera_id", "cameraId", "cameraID")),
        "start_timecode": _first_text(payload, ("start_timecode", "startTimecode", "startTc")),
    }


def _first_text(payload: Mapping[str, object], names: tuple[str, ...]) -> str | None:
    for value in _walk_named_values(payload, names):
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _first_int(payload: Mapping[str, object], names: tuple[str, ...]) -> int | None:
    for value in _walk_named_values(payload, names):
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
    return None


def _first_float(payload: Mapping[str, object], names: tuple[str, ...]) -> float | None:
    for value in _walk_named_values(payload, names):
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                continue
    return None


def _walk_named_values(payload: object, names: tuple[str, ...]) -> tuple[object, ...]:
    found: list[object] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key in names:
                found.append(value)
            found.extend(_walk_named_values(value, names))
    elif isinstance(payload, list):
        for value in payload:
            found.extend(_walk_named_values(value, names))
    return tuple(found)


def _dependency_missing_probe(candidate: ClipCandidate, availability: AdapterAvailability) -> ProbeResult:
    return ProbeResult(
        ok=False,
        adapter_name="arriraw_art_adapter",
        format_family=FormatFamily.ARRIRAW,
        status=ClipStatus.DEPENDENCY_MISSING,
        errors=(
            AdapterError(
                code=AdapterErrorCode.DEPENDENCY_MISSING,
                message="ARRI ART CMD is not available",
                detail=availability.error_detail(),
            ),
        ),
        metadata_raw=_metadata_raw(candidate),
    )


def _probe_failure(candidate: ClipCandidate, message: str, code: AdapterErrorCode) -> ProbeResult:
    return ProbeResult(
        ok=False,
        adapter_name="arriraw_art_adapter",
        format_family=FormatFamily.ARRIRAW,
        status=ClipStatus.PROBE_FAILED,
        errors=(AdapterError(code=code, message=message),),
        metadata_raw=_metadata_raw(candidate),
    )


def _failed_capture_results(plan: CapturePlan, *, error: AdapterError) -> tuple[CaptureResult, ...]:
    return tuple(_decode_failed_result(request=request, error=error) for request in plan.requests)


def _decode_failed_result(*, request: CaptureRequest, error: AdapterError) -> CaptureResult:
    return CaptureResult(
        label=request.label,
        requested_ratio=request.requested_ratio,
        requested_frame_index=request.requested_frame_index,
        requested_seconds=request.requested_seconds,
        duplicate_of=request.duplicate_of,
        status=CaptureStatus.DECODE_FAILED,
        errors=(error,),
    )


def _metadata_raw(candidate: ClipCandidate) -> dict[str, object]:
    return {
        "candidate_id": candidate.candidate_id,
        "source_path": candidate.source_path,
        "part_files": list(candidate.part_files),
    }


def _adapter_errors(raw_errors: object) -> tuple[AdapterError, ...]:
    if raw_errors is None:
        return ()
    if not isinstance(raw_errors, list):
        raise ValueError("errors must be a list")
    parsed: list[AdapterError] = []
    for raw_error in raw_errors:
        if not isinstance(raw_error, dict):
            raise ValueError("error entries must be objects")
        detail = raw_error.get("detail")
        if detail is not None and not isinstance(detail, dict):
            raise ValueError("error.detail must be an object")
        parsed.append(
            AdapterError(
                code=AdapterErrorCode(_require_text(raw_error.get("code"), "error.code")),
                message=_require_text(raw_error.get("message"), "error.message"),
                detail=detail or {},
            )
        )
    return tuple(parsed)


def _string_list(raw_values: object) -> tuple[str, ...]:
    if raw_values is None:
        return ()
    if not isinstance(raw_values, list):
        raise ValueError("warnings must be a list")
    values: list[str] = []
    for raw_value in raw_values:
        values.append(_require_text(raw_value, "warning"))
    return tuple(values)


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    return _require_text(value, "text")


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("expected an integer")
    return value


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("expected a numeric value")
    return float(value)


def _optional_bool(value: object) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError("expected a boolean value")
    return value
