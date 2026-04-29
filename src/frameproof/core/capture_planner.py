from __future__ import annotations

from math import floor

from .models import CapturePlan, CaptureRequest, ClipInfo, capture_labels_for_middle_count

DEFAULT_DURATION_EPSILON_SECONDS = 0.001


def capture_ratios(middle_count: int) -> tuple[float, ...]:
    if middle_count < 0 or middle_count > 3:
        raise ValueError("middle_count must be between 0 and 3 inclusive")
    step_count = middle_count + 1
    ratios = [0.0]
    for step in range(1, step_count):
        ratios.append(step / step_count)
    ratios.append(1.0)
    return tuple(ratios)


def _round_half_up(value: float) -> int:
    return floor(value + 0.5)


def _frame_duration_seconds(clip: ClipInfo) -> float:
    if clip.fps_num is not None and clip.fps_den is not None:
        return clip.fps_den / clip.fps_num
    return DEFAULT_DURATION_EPSILON_SECONDS


def _build_frame_count_plan(clip: ClipInfo, middle_count: int) -> CapturePlan:
    assert clip.frame_count is not None
    end_index = clip.frame_count - 1
    requests: list[CaptureRequest] = []
    labels = capture_labels_for_middle_count(middle_count)
    seen: dict[int, str] = {}
    collapse_warning = False

    for label, ratio in zip(labels, capture_ratios(middle_count), strict=True):
        requested_frame_index = _round_half_up(ratio * end_index)
        duplicate_of = seen.get(requested_frame_index)
        if duplicate_of is None:
            seen[requested_frame_index] = label
        else:
            collapse_warning = True
        requests.append(
            CaptureRequest(
                label=label,
                requested_ratio=ratio,
                requested_frame_index=requested_frame_index,
                requested_seconds=None,
                duplicate_of=duplicate_of,
            )
        )

    return CapturePlan(
        clip_id=clip.clip_id,
        requests=tuple(requests),
        middle_count=middle_count,
        used_frame_count=True,
        collapse_warning=collapse_warning,
    )


def _build_duration_plan(clip: ClipInfo, middle_count: int) -> CapturePlan:
    duration_seconds = clip.duration_seconds if clip.duration_seconds is not None else 0.0
    end_bound = max(duration_seconds - _frame_duration_seconds(clip), 0.0)
    requests: list[CaptureRequest] = []
    labels = capture_labels_for_middle_count(middle_count)
    seen: dict[float, str] = {}
    collapse_warning = False

    for label, ratio in zip(labels, capture_ratios(middle_count), strict=True):
        raw_seconds = duration_seconds * ratio
        requested_seconds = min(max(raw_seconds, 0.0), end_bound)
        if label == "End":
            requested_seconds = end_bound
        duplicate_key = round(requested_seconds, 9)
        duplicate_of = seen.get(duplicate_key)
        if duplicate_of is None:
            seen[duplicate_key] = label
        else:
            collapse_warning = True
        requests.append(
            CaptureRequest(
                label=label,
                requested_ratio=ratio,
                requested_frame_index=None,
                requested_seconds=requested_seconds,
                duplicate_of=duplicate_of,
            )
        )

    return CapturePlan(
        clip_id=clip.clip_id,
        requests=tuple(requests),
        middle_count=middle_count,
        used_frame_count=False,
        collapse_warning=collapse_warning,
    )


def build_capture_plan(clip: ClipInfo, middle_count: int) -> CapturePlan:
    if clip.frame_count is not None:
        return _build_frame_count_plan(clip, middle_count)
    return _build_duration_plan(clip, middle_count)

