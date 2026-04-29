from __future__ import annotations

import json
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

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


@dataclass(frozen=True)
class _JsonTransportResult:
    payload: Mapping[str, object] | None
    stderr: str
    error_code: AdapterErrorCode | None = None
    error_message: str | None = None
    detail: Mapping[str, object] | None = None


class JsonSubprocessAdapterClient(CaptureAdapter):
    name = "raw_json_adapter"
    format_families: tuple[str, ...] = ()
    required_tools: tuple[str, ...] = ()
    format_family = FormatFamily.STANDARD

    def __init__(self, settings: AdapterSettings) -> None:
        self._settings = settings
        self._inspector = DependencyInspector(settings)

    def is_available(self) -> AdapterDependencyState:
        return self._availability().state

    def dependency_details(self) -> Mapping[str, object]:
        return self._availability().error_detail()

    def probe(self, candidate: ClipCandidate) -> ProbeResult:
        request = _build_probe_request(candidate)
        transport = self._run_request(request, timeout_seconds=_PROBE_TIMEOUT_SECONDS)
        metadata_raw = _build_metadata_raw(candidate, request, transport.payload, transport.stderr)
        if transport.error_code is not None:
            return ProbeResult(
                ok=False,
                adapter_name=self.name,
                format_family=self.format_family,
                status=ClipStatus.DEPENDENCY_MISSING
                if transport.error_code is AdapterErrorCode.DEPENDENCY_MISSING
                else ClipStatus.PROBE_FAILED,
                errors=(
                    AdapterError(
                        code=transport.error_code,
                        message=transport.error_message or "adapter probe failed",
                        detail=transport.detail or {},
                    ),
                ),
                metadata_raw=metadata_raw,
            )
        assert transport.payload is not None
        return _map_probe_response(
            adapter_name=self.name,
            format_family=self.format_family,
            candidate=candidate,
            request=request,
            response=transport.payload,
            stderr=transport.stderr,
            logical_clip_name=self._logical_clip_name(candidate, transport.payload),
        )

    def capture(
        self,
        candidate: ClipCandidate,
        plan: CapturePlan,
        profile: CaptureProfile,
        staging_dir: Path,
    ) -> Sequence[CaptureResult]:
        request = _build_capture_request(candidate, plan, profile, staging_dir)
        transport = self._run_request(request, timeout_seconds=_CAPTURE_TIMEOUT_SECONDS)
        if transport.error_code is not None:
            return _failed_capture_results(
                plan,
                code=transport.error_code,
                message=transport.error_message or "adapter capture failed",
                detail=transport.detail or {},
            )

        assert transport.payload is not None
        return _map_capture_response(
            adapter_name=self.name,
            plan=plan,
            request=request,
            response=transport.payload,
            stderr=transport.stderr,
        )

    def _availability(self) -> AdapterAvailability:
        return self._inspector.availability_for_adapter(self.name)

    def _logical_clip_name(
        self,
        candidate: ClipCandidate,
        response: Mapping[str, object],
    ) -> str | None:
        del response
        del candidate
        return None

    def _run_request(
        self,
        request: Mapping[str, object],
        *,
        timeout_seconds: int,
    ) -> _JsonTransportResult:
        availability = self._availability()
        dependency = availability.dependencies[0]
        if dependency.resolved_path is None:
            return _JsonTransportResult(
                payload=None,
                stderr="",
                error_code=AdapterErrorCode.DEPENDENCY_MISSING,
                error_message=f"{dependency.name} is not available",
                detail=availability.error_detail(),
            )

        try:
            completed = subprocess.run(
                [dependency.resolved_path],
                input=json.dumps(request),
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return _JsonTransportResult(
                payload=None,
                stderr="",
                error_code=AdapterErrorCode.TIMEOUT,
                error_message=f"{self.name} timed out",
                detail={"timeout_seconds": timeout_seconds},
            )
        except OSError as exc:
            return _JsonTransportResult(
                payload=None,
                stderr="",
                error_code=AdapterErrorCode.DEPENDENCY_MISSING,
                error_message=f"{dependency.name} could not be executed",
                detail={"exception": str(exc), **availability.error_detail()},
            )

        stdout = completed.stdout.strip()
        if not stdout:
            if completed.returncode == 0:
                return _JsonTransportResult(
                    payload=None,
                    stderr=completed.stderr.strip(),
                    error_code=AdapterErrorCode.INVALID_RESPONSE,
                    error_message=f"{self.name} did not return JSON output",
                    detail={"returncode": completed.returncode},
                )
            return _JsonTransportResult(
                payload=None,
                stderr=completed.stderr.strip(),
                error_code=AdapterErrorCode.PROBE_FAILED,
                error_message=f"{self.name} exited without structured JSON",
                detail={"returncode": completed.returncode},
            )

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            return _JsonTransportResult(
                payload=None,
                stderr=completed.stderr.strip(),
                error_code=AdapterErrorCode.INVALID_RESPONSE,
                error_message=f"{self.name} returned invalid JSON",
                detail={"returncode": completed.returncode},
            )
        if not isinstance(payload, dict):
            return _JsonTransportResult(
                payload=None,
                stderr=completed.stderr.strip(),
                error_code=AdapterErrorCode.INVALID_RESPONSE,
                error_message=f"{self.name} returned a non-object JSON payload",
                detail={"returncode": completed.returncode},
            )
        return _JsonTransportResult(payload=payload, stderr=completed.stderr.strip())


def _build_probe_request(candidate: ClipCandidate) -> dict[str, object]:
    return {
        "request_id": str(uuid.uuid4()),
        "command": "probe",
        "input": {
            "source_path": candidate.source_path,
            "part_files": _request_part_files(candidate),
        },
        "options": {
            "timeout_seconds": _PROBE_TIMEOUT_SECONDS,
        },
    }


def _build_capture_request(
    candidate: ClipCandidate,
    plan: CapturePlan,
    profile: CaptureProfile,
    staging_dir: Path,
) -> dict[str, object]:
    return {
        "request_id": str(uuid.uuid4()),
        "command": "capture",
        "input": {
            "source_path": candidate.source_path,
            "part_files": _request_part_files(candidate),
        },
        "capture_points": [
            {
                "label": request.label,
                "requested_ratio": request.requested_ratio,
                "requested_frame_index": request.requested_frame_index,
                "requested_seconds": request.requested_seconds,
            }
            for request in plan.requests
        ],
        "options": {
            "profile": profile.name,
            "staging_dir": str(staging_dir),
            "timeout_seconds": _CAPTURE_TIMEOUT_SECONDS,
        },
    }


def _request_part_files(candidate: ClipCandidate) -> list[str]:
    if candidate.part_files == (candidate.source_path,):
        return []
    return list(candidate.part_files)


def _build_metadata_raw(
    candidate: ClipCandidate,
    request: Mapping[str, object],
    response: Mapping[str, object] | None,
    stderr: str,
) -> dict[str, object]:
    metadata_raw: dict[str, object] = {
        "candidate_id": candidate.candidate_id,
        "source_path": candidate.source_path,
        "part_files": list(candidate.part_files),
        "request": dict(request),
    }
    if response is not None:
        metadata_raw["response"] = dict(response)
    if stderr:
        metadata_raw["stderr"] = stderr
    return metadata_raw


def _map_probe_response(
    *,
    adapter_name: str,
    format_family: FormatFamily,
    candidate: ClipCandidate,
    request: Mapping[str, object],
    response: Mapping[str, object],
    stderr: str,
    logical_clip_name: str | None,
) -> ProbeResult:
    metadata_raw = _build_metadata_raw(candidate, request, response, stderr)
    try:
        _validate_common_response(response, request_id=str(request["request_id"]), adapter_name=adapter_name)
    except ValueError as exc:
        return _invalid_probe_response(adapter_name, format_family, metadata_raw, str(exc))

    ok = response.get("ok")
    if not isinstance(ok, bool):
        return _invalid_probe_response(adapter_name, format_family, metadata_raw, "response.ok must be a boolean")

    errors = _parse_adapter_errors(response.get("errors"))
    warnings = _parse_string_list(response.get("warnings"))
    status_value = response.get("status")
    if not isinstance(status_value, str):
        return _invalid_probe_response(adapter_name, format_family, metadata_raw, "response.status must be a string")

    if not ok:
        try:
            status = ClipStatus(status_value)
        except ValueError:
            return _invalid_probe_response(adapter_name, format_family, metadata_raw, "response.status is not a valid clip status")
        if not errors:
            errors = (
                AdapterError(
                    code=AdapterErrorCode.DEPENDENCY_MISSING
                    if status is ClipStatus.DEPENDENCY_MISSING
                    else AdapterErrorCode.PROBE_FAILED,
                    message=f"{adapter_name} reported {status.value}",
                ),
            )
        return ProbeResult(
            ok=False,
            adapter_name=adapter_name,
            format_family=format_family,
            status=status,
            warnings=warnings,
            errors=errors,
            metadata_raw=metadata_raw,
        )

    clip_payload = response.get("clip")
    if not isinstance(clip_payload, dict):
        return _invalid_probe_response(adapter_name, format_family, metadata_raw, "response.clip must be an object when ok=true")

    try:
        status = ClipStatus(status_value)
        if status not in {ClipStatus.SUCCESS, ClipStatus.METADATA_INCOMPLETE}:
            raise ValueError("response.status must be success or metadata_incomplete when ok=true")
        clip = _build_clip_info(
            candidate=candidate,
            clip_payload=clip_payload,
            format_family=format_family,
            logical_clip_name=logical_clip_name,
            metadata_raw=metadata_raw,
        )
    except ValueError as exc:
        return _invalid_probe_response(adapter_name, format_family, metadata_raw, str(exc))

    return ProbeResult(
        ok=True,
        adapter_name=adapter_name,
        format_family=format_family,
        clip=clip,
        warnings=warnings,
        errors=errors,
        status=status,
        metadata_raw=metadata_raw,
    )


def _map_capture_response(
    *,
    adapter_name: str,
    plan: CapturePlan,
    request: Mapping[str, object],
    response: Mapping[str, object],
    stderr: str,
) -> tuple[CaptureResult, ...]:
    try:
        _validate_common_response(response, request_id=str(request["request_id"]), adapter_name=adapter_name)
    except ValueError as exc:
        return _failed_capture_results(plan, code=AdapterErrorCode.INVALID_RESPONSE, message=str(exc))

    ok = response.get("ok")
    if not isinstance(ok, bool):
        return _failed_capture_results(
            plan,
            code=AdapterErrorCode.INVALID_RESPONSE,
            message="response.ok must be a boolean",
        )

    status_value = response.get("status")
    if not isinstance(status_value, str):
        return _failed_capture_results(
            plan,
            code=AdapterErrorCode.INVALID_RESPONSE,
            message="response.status must be a string",
        )
    errors = _parse_adapter_errors(response.get("errors"))

    if not ok:
        code = AdapterErrorCode.DEPENDENCY_MISSING if status_value == ClipStatus.DEPENDENCY_MISSING.value else AdapterErrorCode.DECODE_FAILED
        message = errors[0].message if errors else f"{adapter_name} reported {status_value}"
        return _failed_capture_results(
            plan,
            code=code,
            message=message,
            detail={"stderr": stderr} if stderr else {},
        )

    captures_payload = response.get("captures")
    if not isinstance(captures_payload, list):
        return _failed_capture_results(
            plan,
            code=AdapterErrorCode.INVALID_RESPONSE,
            message="response.captures must be a list when ok=true",
        )
    if len(captures_payload) != len(plan.requests):
        return _failed_capture_results(
            plan,
            code=AdapterErrorCode.INVALID_RESPONSE,
            message="response.captures length does not match the capture plan",
        )

    results: list[CaptureResult] = []
    for payload, expected in zip(captures_payload, plan.requests, strict=True):
        if not isinstance(payload, dict):
            return _failed_capture_results(
                plan,
                code=AdapterErrorCode.INVALID_RESPONSE,
                message="each capture response must be an object",
            )
        try:
            results.append(_build_capture_result(payload, expected))
        except ValueError as exc:
            return _failed_capture_results(plan, code=AdapterErrorCode.INVALID_RESPONSE, message=str(exc))

    return tuple(results)


def _build_clip_info(
    *,
    candidate: ClipCandidate,
    clip_payload: Mapping[str, object],
    format_family: FormatFamily,
    logical_clip_name: str | None,
    metadata_raw: Mapping[str, object],
) -> ClipInfo:
    clip_name = _require_text(clip_payload.get("clip_name"), "clip.clip_name")
    payload_format_family = clip_payload.get("format_family")
    if payload_format_family is not None and payload_format_family != format_family.value:
        raise ValueError("clip.format_family does not match the adapter format family")
    start_timecode = _optional_text(clip_payload.get("start_timecode"))
    tc_drop_frame = _optional_bool(clip_payload.get("tc_drop_frame"))
    if tc_drop_frame is None and start_timecode is not None:
        tc_drop_frame = ";" in start_timecode
    return ClipInfo(
        clip_id=_optional_text(clip_payload.get("clip_id")) or candidate.candidate_id,
        clip_name=clip_name,
        logical_clip_name=logical_clip_name,
        source_path=candidate.source_path,
        part_files=candidate.part_files,
        format_family=format_family,
        container=_optional_text(clip_payload.get("container")) or format_family.value.upper(),
        codec=_optional_text(clip_payload.get("codec")) or format_family.value.upper(),
        file_size_bytes=candidate.file_size_bytes,
        duration_seconds=_optional_float(clip_payload.get("duration_seconds")),
        frame_count=_optional_int(clip_payload.get("frame_count")),
        fps_num=_optional_int(clip_payload.get("fps_num")),
        fps_den=_optional_int(clip_payload.get("fps_den")),
        width=_optional_int(clip_payload.get("width")),
        height=_optional_int(clip_payload.get("height")),
        camera_make=_optional_text(clip_payload.get("camera_make")),
        camera_model=_optional_text(clip_payload.get("camera_model")),
        reel=_optional_text(clip_payload.get("reel")),
        camera_id=_optional_text(clip_payload.get("camera_id")),
        start_timecode=start_timecode,
        end_timecode=_optional_text(clip_payload.get("end_timecode")),
        timecode_source=TimecodeSource.NATIVE_ADAPTER if start_timecode is not None else None,
        tc_drop_frame=tc_drop_frame,
        metadata_raw=metadata_raw,
    )


def _build_capture_result(payload: Mapping[str, object], expected: CaptureRequest) -> CaptureResult:
    label = _require_text(payload.get("label"), "capture.label")
    if label != expected.label:
        raise ValueError("capture labels must match the requested capture plan order")
    requested_ratio = _require_float(payload.get("requested_ratio"), "capture.requested_ratio")
    if requested_ratio != expected.requested_ratio:
        raise ValueError("capture.requested_ratio must round-trip exactly")
    requested_frame_index = _optional_int(payload.get("requested_frame_index"))
    requested_seconds = _optional_float(payload.get("requested_seconds"))
    if requested_frame_index != expected.requested_frame_index:
        raise ValueError("capture.requested_frame_index must round-trip exactly")
    if requested_seconds != expected.requested_seconds:
        raise ValueError("capture.requested_seconds must round-trip exactly")
    status = CaptureStatus(_require_text(payload.get("status"), "capture.status"))
    actual_timecode_source = _optional_text(payload.get("actual_timecode_source"))
    return CaptureResult(
        label=label,
        requested_ratio=requested_ratio,
        requested_frame_index=requested_frame_index,
        requested_seconds=requested_seconds,
        actual_frame_index=_optional_int(payload.get("actual_frame_index")),
        actual_seconds=_optional_float(payload.get("actual_seconds")),
        actual_timecode=_optional_text(payload.get("actual_timecode")),
        actual_timecode_source=TimecodeSource(actual_timecode_source) if actual_timecode_source is not None else None,
        image_path_temp=_optional_text(payload.get("image_path_temp")),
        duplicate_of=_optional_text(payload.get("duplicate_of")),
        status=status,
        warnings=_parse_string_list(payload.get("warnings")),
        errors=_parse_adapter_errors(payload.get("errors")),
    )


def _failed_capture_results(
    plan: CapturePlan,
    *,
    code: AdapterErrorCode,
    message: str,
    detail: Mapping[str, object] | None = None,
) -> tuple[CaptureResult, ...]:
    error = AdapterError(code=code, message=message, detail=detail or {})
    return tuple(
        CaptureResult(
            label=request.label,
            requested_ratio=request.requested_ratio,
            requested_frame_index=request.requested_frame_index,
            requested_seconds=request.requested_seconds,
            duplicate_of=request.duplicate_of,
            status=CaptureStatus.DECODE_FAILED,
            errors=(error,),
        )
        for request in plan.requests
    )


def _invalid_probe_response(
    adapter_name: str,
    format_family: FormatFamily,
    metadata_raw: Mapping[str, object],
    message: str,
) -> ProbeResult:
    return ProbeResult(
        ok=False,
        adapter_name=adapter_name,
        format_family=format_family,
        status=ClipStatus.PROBE_FAILED,
        errors=(AdapterError(code=AdapterErrorCode.INVALID_RESPONSE, message=message),),
        metadata_raw=metadata_raw,
    )


def _validate_common_response(response: Mapping[str, object], *, request_id: str, adapter_name: str) -> None:
    if response.get("request_id") != request_id:
        raise ValueError("response.request_id did not round-trip")
    if response.get("adapter_name") != adapter_name:
        raise ValueError("response.adapter_name did not match the invoked adapter")


def _parse_adapter_errors(raw_errors: object) -> tuple[AdapterError, ...]:
    if raw_errors is None:
        return ()
    if not isinstance(raw_errors, list):
        raise ValueError("response.errors must be a list")
    parsed: list[AdapterError] = []
    for raw_error in raw_errors:
        if not isinstance(raw_error, dict):
            raise ValueError("each response error must be an object")
        code = _require_text(raw_error.get("code"), "error.code")
        message = _require_text(raw_error.get("message"), "error.message")
        detail = raw_error.get("detail")
        if detail is not None and not isinstance(detail, dict):
            raise ValueError("error.detail must be an object when present")
        parsed.append(
            AdapterError(
                code=AdapterErrorCode(code),
                message=message,
                detail=detail or {},
            )
        )
    return tuple(parsed)


def _parse_string_list(raw_values: object) -> tuple[str, ...]:
    if raw_values is None:
        return ()
    if not isinstance(raw_values, list):
        raise ValueError("expected a list of strings")
    values: list[str] = []
    for raw_value in raw_values:
        if not isinstance(raw_value, str):
            raise ValueError("expected a list of strings")
        values.append(raw_value)
    return tuple(values)


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    return _require_text(value, "text")


def _require_float(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    return float(value)


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    return _require_float(value, "float")


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("expected an integer")
    return value


def _optional_bool(value: object) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError("expected a boolean")
    return value
