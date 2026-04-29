from __future__ import annotations

import pytest

from frameproof.core.capture_planner import build_capture_plan
from frameproof.core.models import ClipInfo, FormatFamily


def make_clip(**overrides: object) -> ClipInfo:
    payload: dict[str, object] = {
        "clip_id": "clip-1",
        "clip_name": "A001_C001.mov",
        "source_path": "/clips/A001_C001.mov",
        "format_family": FormatFamily.STANDARD,
        "frame_count": 1000,
        "duration_seconds": 40.0,
        "fps_num": 25,
        "fps_den": 1,
    }
    payload.update(overrides)
    return ClipInfo(**payload)


def test_middle_count_zero_produces_start_and_end_only() -> None:
    plan = build_capture_plan(make_clip(), middle_count=0)

    assert [request.label for request in plan.requests] == ["Start", "End"]
    assert [request.requested_frame_index for request in plan.requests] == [0, 999]
    assert plan.used_frame_count is True


def test_middle_count_three_uses_expected_labels() -> None:
    plan = build_capture_plan(make_clip(), middle_count=3)

    assert [request.label for request in plan.requests] == ["Start", "Mid1", "Mid2", "Mid3", "End"]
    assert [request.requested_frame_index for request in plan.requests] == [0, 250, 500, 749, 999]


def test_frame_count_priority_wins_over_duration_when_both_are_present() -> None:
    plan = build_capture_plan(make_clip(frame_count=6, duration_seconds=100.0), middle_count=1)

    assert [request.requested_frame_index for request in plan.requests] == [0, 3, 5]
    assert all(request.requested_seconds is None for request in plan.requests)


def test_frame_count_rounding_uses_floor_plus_half() -> None:
    plan = build_capture_plan(make_clip(frame_count=6), middle_count=1)

    assert [request.requested_frame_index for request in plan.requests] == [0, 3, 5]


def test_duration_fallback_uses_end_epsilon_and_seconds() -> None:
    plan = build_capture_plan(
        make_clip(frame_count=None, duration_seconds=10.0, fps_num=25, fps_den=1),
        middle_count=2,
    )

    assert plan.used_frame_count is False
    assert [request.label for request in plan.requests] == ["Start", "Mid1", "Mid2", "End"]
    assert [request.requested_seconds for request in plan.requests] == pytest.approx(
        [0.0, 10.0 / 3.0, 20.0 / 3.0, 9.96]
    )


def test_short_clips_preserve_duplicate_slots() -> None:
    plan = build_capture_plan(make_clip(frame_count=1), middle_count=3)

    assert [request.requested_frame_index for request in plan.requests] == [0, 0, 0, 0, 0]
    assert [request.duplicate_of for request in plan.requests] == [None, "Start", "Start", "Start", "Start"]
    assert plan.collapse_warning is True
