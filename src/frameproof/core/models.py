from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from math import isfinite
from typing import Iterable, Mapping

CAPTURE_LABEL_SEQUENCE: tuple[str, ...] = ("Start", "Mid1", "Mid2", "Mid3", "End")


class FormatFamily(StrEnum):
    STANDARD = "standard"
    BRAW = "braw"
    R3D = "r3d"
    ARRIRAW = "arriraw"


class BatchStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ClipStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    PROBE_FAILED = "probe_failed"
    DECODE_FAILED = "decode_failed"
    UNSUPPORTED_FORMAT = "unsupported_format"
    DEPENDENCY_MISSING = "dependency_missing"
    METADATA_INCOMPLETE = "metadata_incomplete"
    SKIPPED_DUPLICATE = "skipped_duplicate"


class CaptureStatus(StrEnum):
    SUCCESS = "success"
    DECODE_FAILED = "decode_failed"
    METADATA_INCOMPLETE = "metadata_incomplete"
    SKIPPED_DUPLICATE = "skipped_duplicate"


class AdapterDependencyState(StrEnum):
    AVAILABLE = "available"
    CONFIGURED_MISSING = "configured_missing"
    NOT_CONFIGURED = "not_configured"
    RUNTIME_ERROR = "runtime_error"


class TimecodeSource(StrEnum):
    NATIVE_ADAPTER = "native_adapter"
    CALCULATED = "calculated"
    CONTAINER_METADATA = "container_metadata"
    ELAPSED_FALLBACK = "elapsed_fallback"


class AdapterErrorCode(StrEnum):
    DEPENDENCY_MISSING = "dependency_missing"
    PROBE_FAILED = "probe_failed"
    DECODE_FAILED = "decode_failed"
    INVALID_RESPONSE = "invalid_response"
    TIMEOUT = "timeout"
    UNSUPPORTED_FORMAT = "unsupported_format"
    METADATA_INCOMPLETE = "metadata_incomplete"
    OUTPUT_WRITE_FAILED = "output_write_failed"
    RENDERER_FAILED = "renderer_failed"


def capture_labels_for_middle_count(middle_count: int) -> tuple[str, ...]:
    if middle_count < 0 or middle_count > 3:
        raise ValueError("middle_count must be between 0 and 3 inclusive")
    return CAPTURE_LABEL_SEQUENCE[:1] + CAPTURE_LABEL_SEQUENCE[1 : middle_count + 1] + CAPTURE_LABEL_SEQUENCE[-1:]


def _require_text(value: str, field_name: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{field_name} must not be empty")
    return text


def _require_non_negative_int(value: int | None, field_name: str) -> int | None:
    if value is None:
        return None
    if value < 0:
        raise ValueError(f"{field_name} must be >= 0")
    return value


def _require_positive_int(value: int | None, field_name: str) -> int | None:
    if value is None:
        return None
    if value <= 0:
        raise ValueError(f"{field_name} must be > 0")
    return value


def _require_non_negative_float(value: float | None, field_name: str) -> float | None:
    if value is None:
        return None
    if not isfinite(value) or value < 0:
        raise ValueError(f"{field_name} must be a finite value >= 0")
    return value


def _coerce_strings(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(str(value) for value in values)


def _coerce_mapping(values: Mapping[str, object] | None) -> dict[str, object]:
    return dict(values) if values is not None else {}


@dataclass(frozen=True)
class AdapterError:
    code: AdapterErrorCode
    message: str
    detail: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", AdapterErrorCode(self.code))
        object.__setattr__(self, "message", _require_text(self.message, "message"))
        object.__setattr__(self, "detail", _coerce_mapping(self.detail))


@dataclass(frozen=True)
class ClipCandidate:
    candidate_id: str
    source_path: str
    part_files: tuple[str, ...] = ()
    file_size_bytes: int | None = None
    modified_time: float | None = None
    format_hint: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", _require_text(self.candidate_id, "candidate_id"))
        object.__setattr__(self, "source_path", _require_text(self.source_path, "source_path"))
        object.__setattr__(self, "part_files", _coerce_strings(self.part_files))
        object.__setattr__(self, "file_size_bytes", _require_non_negative_int(self.file_size_bytes, "file_size_bytes"))
        object.__setattr__(self, "modified_time", _require_non_negative_float(self.modified_time, "modified_time"))
        if self.format_hint is not None:
            object.__setattr__(self, "format_hint", _require_text(self.format_hint, "format_hint"))


@dataclass(frozen=True)
class CaptureProfile:
    name: str
    description: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _require_text(self.name, "name"))
        if self.description is not None:
            object.__setattr__(self, "description", _require_text(self.description, "description"))


@dataclass(frozen=True)
class ClipInfo:
    clip_id: str
    clip_name: str
    logical_clip_name: str | None = None
    source_path: str = ""
    part_files: tuple[str, ...] = ()
    format_family: FormatFamily = FormatFamily.STANDARD
    container: str | None = None
    codec: str | None = None
    file_size_bytes: int | None = None
    duration_seconds: float | None = None
    frame_count: int | None = None
    fps_num: int | None = None
    fps_den: int | None = None
    width: int | None = None
    height: int | None = None
    camera_make: str | None = None
    camera_model: str | None = None
    reel: str | None = None
    camera_id: str | None = None
    start_timecode: str | None = None
    end_timecode: str | None = None
    timecode_source: TimecodeSource | None = None
    tc_drop_frame: bool | None = None
    metadata_raw: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "clip_id", _require_text(self.clip_id, "clip_id"))
        object.__setattr__(self, "clip_name", _require_text(self.clip_name, "clip_name"))
        object.__setattr__(self, "source_path", _require_text(self.source_path, "source_path"))
        object.__setattr__(self, "part_files", _coerce_strings(self.part_files))
        object.__setattr__(self, "format_family", FormatFamily(self.format_family))
        object.__setattr__(self, "file_size_bytes", _require_non_negative_int(self.file_size_bytes, "file_size_bytes"))
        object.__setattr__(self, "duration_seconds", _require_non_negative_float(self.duration_seconds, "duration_seconds"))
        object.__setattr__(self, "frame_count", _require_positive_int(self.frame_count, "frame_count"))
        object.__setattr__(self, "fps_num", _require_positive_int(self.fps_num, "fps_num"))
        object.__setattr__(self, "fps_den", _require_positive_int(self.fps_den, "fps_den"))
        object.__setattr__(self, "width", _require_positive_int(self.width, "width"))
        object.__setattr__(self, "height", _require_positive_int(self.height, "height"))
        object.__setattr__(self, "metadata_raw", _coerce_mapping(self.metadata_raw))
        if self.frame_count is None and self.duration_seconds is None:
            raise ValueError("frame_count and duration_seconds must not both be null")
        if (self.fps_num is None) != (self.fps_den is None):
            raise ValueError("fps_num and fps_den must be provided together or omitted together")
        if self.logical_clip_name is not None:
            object.__setattr__(self, "logical_clip_name", _require_text(self.logical_clip_name, "logical_clip_name"))
        for field_name in ("container", "codec", "camera_make", "camera_model", "reel", "camera_id"):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(self, field_name, _require_text(value, field_name))
        for field_name in ("start_timecode", "end_timecode"):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(self, field_name, _require_text(value, field_name))
        if self.timecode_source is not None:
            object.__setattr__(self, "timecode_source", TimecodeSource(self.timecode_source))


@dataclass(frozen=True)
class CaptureRequest:
    label: str
    requested_ratio: float
    requested_frame_index: int | None = None
    requested_seconds: float | None = None
    duplicate_of: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", _require_text(self.label, "label"))
        if self.label not in CAPTURE_LABEL_SEQUENCE:
            raise ValueError(f"unsupported capture label: {self.label}")
        if not isfinite(self.requested_ratio) or self.requested_ratio < 0 or self.requested_ratio > 1:
            raise ValueError("requested_ratio must be a finite value between 0 and 1 inclusive")
        object.__setattr__(
            self,
            "requested_frame_index",
            _require_non_negative_int(self.requested_frame_index, "requested_frame_index"),
        )
        object.__setattr__(self, "requested_seconds", _require_non_negative_float(self.requested_seconds, "requested_seconds"))
        if self.requested_frame_index is None and self.requested_seconds is None:
            raise ValueError("requested_frame_index or requested_seconds must be present")
        if self.duplicate_of is not None:
            object.__setattr__(self, "duplicate_of", _require_text(self.duplicate_of, "duplicate_of"))


@dataclass(frozen=True)
class CapturePlan:
    clip_id: str
    requests: tuple[CaptureRequest, ...]
    middle_count: int
    used_frame_count: bool
    collapse_warning: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "clip_id", _require_text(self.clip_id, "clip_id"))
        object.__setattr__(self, "requests", tuple(self.requests))
        expected_labels = capture_labels_for_middle_count(self.middle_count)
        actual_labels = tuple(request.label for request in self.requests)
        if actual_labels != expected_labels:
            raise ValueError("capture plan labels must match the expected Start/Mid*/End order")


@dataclass(frozen=True)
class CaptureResult:
    label: str
    requested_ratio: float
    requested_frame_index: int | None = None
    requested_seconds: float | None = None
    actual_frame_index: int | None = None
    actual_seconds: float | None = None
    actual_timecode: str | None = None
    actual_timecode_source: TimecodeSource | None = None
    image_path_temp: str | None = None
    duplicate_of: str | None = None
    status: CaptureStatus = CaptureStatus.SUCCESS
    warnings: tuple[str, ...] = ()
    errors: tuple[AdapterError, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", _require_text(self.label, "label"))
        object.__setattr__(self, "requested_frame_index", _require_non_negative_int(self.requested_frame_index, "requested_frame_index"))
        object.__setattr__(self, "requested_seconds", _require_non_negative_float(self.requested_seconds, "requested_seconds"))
        object.__setattr__(self, "actual_frame_index", _require_non_negative_int(self.actual_frame_index, "actual_frame_index"))
        object.__setattr__(self, "actual_seconds", _require_non_negative_float(self.actual_seconds, "actual_seconds"))
        object.__setattr__(self, "status", CaptureStatus(self.status))
        object.__setattr__(self, "warnings", _coerce_strings(self.warnings))
        object.__setattr__(self, "errors", tuple(self.errors))
        if self.requested_frame_index is None and self.requested_seconds is None:
            raise ValueError("capture result requires requested position data")
        if self.actual_timecode_source is not None:
            object.__setattr__(self, "actual_timecode_source", TimecodeSource(self.actual_timecode_source))
        if self.image_path_temp is not None:
            object.__setattr__(self, "image_path_temp", _require_text(self.image_path_temp, "image_path_temp"))
        if self.duplicate_of is not None:
            object.__setattr__(self, "duplicate_of", _require_text(self.duplicate_of, "duplicate_of"))
        if self.status != CaptureStatus.DECODE_FAILED and (
            self.actual_frame_index is None and self.actual_seconds is None and self.duplicate_of is None
        ):
            raise ValueError("successful or degraded capture results require actual position data or duplicate_of")


@dataclass(frozen=True)
class CapturePoint:
    label: str
    requested_ratio: float
    requested_frame_index: int | None = None
    requested_seconds: float | None = None
    actual_frame_index: int | None = None
    actual_seconds: float | None = None
    actual_timecode: str | None = None
    actual_timecode_source: TimecodeSource | None = None
    image_path_temp: str | None = None
    image_path_exported: str | None = None
    duplicate_of: str | None = None
    status: CaptureStatus = CaptureStatus.SUCCESS
    warnings: tuple[str, ...] = ()
    errors: tuple[AdapterError, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", _require_text(self.label, "label"))
        object.__setattr__(self, "requested_frame_index", _require_non_negative_int(self.requested_frame_index, "requested_frame_index"))
        object.__setattr__(self, "requested_seconds", _require_non_negative_float(self.requested_seconds, "requested_seconds"))
        object.__setattr__(self, "actual_frame_index", _require_non_negative_int(self.actual_frame_index, "actual_frame_index"))
        object.__setattr__(self, "actual_seconds", _require_non_negative_float(self.actual_seconds, "actual_seconds"))
        object.__setattr__(self, "status", CaptureStatus(self.status))
        object.__setattr__(self, "warnings", _coerce_strings(self.warnings))
        object.__setattr__(self, "errors", tuple(self.errors))
        if self.requested_frame_index is None and self.requested_seconds is None:
            raise ValueError("capture point requires requested position data")
        if self.actual_timecode_source is not None:
            object.__setattr__(self, "actual_timecode_source", TimecodeSource(self.actual_timecode_source))
        for field_name in ("image_path_temp", "image_path_exported", "duplicate_of"):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(self, field_name, _require_text(value, field_name))
        if self.status != CaptureStatus.DECODE_FAILED and (
            self.actual_frame_index is None and self.actual_seconds is None and self.duplicate_of is None
        ):
            raise ValueError("capture points require actual data or duplicate_of unless decode_failed")

    @classmethod
    def from_capture_result(
        cls,
        result: CaptureResult,
        *,
        image_path_exported: str | None = None,
    ) -> CapturePoint:
        return cls(
            label=result.label,
            requested_ratio=result.requested_ratio,
            requested_frame_index=result.requested_frame_index,
            requested_seconds=result.requested_seconds,
            actual_frame_index=result.actual_frame_index,
            actual_seconds=result.actual_seconds,
            actual_timecode=result.actual_timecode,
            actual_timecode_source=result.actual_timecode_source,
            image_path_temp=result.image_path_temp,
            image_path_exported=image_path_exported,
            duplicate_of=result.duplicate_of,
            status=result.status,
            warnings=result.warnings,
            errors=result.errors,
        )


@dataclass(frozen=True)
class ProbeResult:
    ok: bool
    adapter_name: str
    format_family: FormatFamily
    clip: ClipInfo | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[AdapterError, ...] = ()
    status: ClipStatus = ClipStatus.SUCCESS
    metadata_raw: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "adapter_name", _require_text(self.adapter_name, "adapter_name"))
        object.__setattr__(self, "format_family", FormatFamily(self.format_family))
        object.__setattr__(self, "warnings", _coerce_strings(self.warnings))
        object.__setattr__(self, "errors", tuple(self.errors))
        object.__setattr__(self, "status", ClipStatus(self.status))
        object.__setattr__(self, "metadata_raw", _coerce_mapping(self.metadata_raw))
        if self.ok and self.clip is None:
            raise ValueError("ok probe results require clip metadata")


@dataclass(frozen=True)
class ReportItem:
    clip: ClipInfo
    captures: tuple[CapturePoint, ...]
    status: ClipStatus
    adapter_name: str = "unknown"
    warnings: tuple[str, ...] = ()
    errors: tuple[AdapterError, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "captures", tuple(self.captures))
        object.__setattr__(self, "status", ClipStatus(self.status))
        object.__setattr__(self, "adapter_name", _require_text(self.adapter_name, "adapter_name"))
        object.__setattr__(self, "warnings", _coerce_strings(self.warnings))
        object.__setattr__(self, "errors", tuple(self.errors))
        labels = tuple(capture.label for capture in self.captures)
        valid_prefixes = {()} | {capture_labels_for_middle_count(middle_count) for middle_count in range(4)}
        if labels not in valid_prefixes:
            raise ValueError("report item captures must preserve the canonical Start/Mid*/End order")


@dataclass(frozen=True)
class BatchSummary:
    total_clips: int
    success_count: int
    partial_success_count: int
    probe_failed_count: int
    decode_failed_count: int
    skipped_count: int
    status: BatchStatus

    def __post_init__(self) -> None:
        for field_name in (
            "total_clips",
            "success_count",
            "partial_success_count",
            "probe_failed_count",
            "decode_failed_count",
            "skipped_count",
        ):
            value = getattr(self, field_name)
            if value < 0:
                raise ValueError(f"{field_name} must be >= 0")
        object.__setattr__(self, "status", BatchStatus(self.status))
