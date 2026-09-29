from __future__ import annotations

from frameproof.core.models import TimecodeSource
from frameproof.core.timecode import (
    calculate_timecode_display,
    format_elapsed,
    parse_timecode,
    resolve_timecode_display,
)


def test_parse_timecode_detects_drop_frame_separator() -> None:
    parsed = parse_timecode("01:00:00;00")

    assert parsed is not None
    assert parsed.drop_frame is True


def test_calculated_timecode_uses_calculated_suffix() -> None:
    display = calculate_timecode_display(
        start_timecode="01:00:00:00",
        frame_offset=12,
        fps_num=24,
        fps_den=1,
        tc_drop_frame=False,
    )

    assert display is not None
    assert display.value == "01:00:00:12 (calculated)"
    assert display.source is TimecodeSource.CALCULATED


def test_ntsc_unknown_drop_frame_leaves_warning_and_non_drop_output() -> None:
    display = calculate_timecode_display(
        start_timecode="01:00:00:00",
        frame_offset=30,
        fps_num=30000,
        fps_den=1001,
        tc_drop_frame=None,
    )

    assert display is not None
    assert display.value == "01:00:01:00 (calculated)"
    assert display.warnings == ("tc_drop_frame_unknown=true",)


def test_elapsed_fallback_is_used_when_timecode_cannot_be_calculated() -> None:
    display = resolve_timecode_display(
        actual_timecode=None,
        actual_timecode_source=None,
        start_timecode="01:00:00:00",
        container_timecode=None,
        actual_frame_index=100,
        actual_seconds=12.345,
        fps_num=None,
        fps_den=None,
        tc_drop_frame=None,
    )

    assert display.source is TimecodeSource.ELAPSED_FALLBACK
    assert display.value == "+00:00:12.345"


def test_container_metadata_beats_elapsed_fallback_when_present() -> None:
    display = resolve_timecode_display(
        actual_timecode=None,
        actual_timecode_source=None,
        start_timecode=None,
        container_timecode="02:00:00:00",
        actual_frame_index=None,
        actual_seconds=2.5,
        fps_num=None,
        fps_den=None,
        tc_drop_frame=False,
    )

    assert display.source is TimecodeSource.CONTAINER_METADATA
    assert display.value == "02:00:00:00"


def test_format_elapsed_matches_display_spec() -> None:
    assert format_elapsed(3661.007) == "+01:01:01.007"


def test_drop_frame_calculation_matches_smpte_minute_boundaries() -> None:
    def calculated(start: str, offset: int) -> str:
        display = calculate_timecode_display(
            start_timecode=start,
            frame_offset=offset,
            fps_num=30000,
            fps_den=1001,
            tc_drop_frame=True,
        )
        assert display is not None
        return display.value.removesuffix(" (calculated)")

    assert calculated("00:00:00;00", 1799) == "00:00:59;29"
    assert calculated("00:00:00;00", 1800) == "00:01:00;02"
    assert calculated("00:00:00;00", 17981) == "00:09:59;29"
    assert calculated("00:00:00;00", 17982) == "00:10:00;00"
    assert calculated("00:59:30;00", 0) == "00:59:30;00"
    assert calculated("00:59:30;00", 900) == "01:00:00;00"


def test_drop_frame_frame_numbers_round_trip_through_a_full_day() -> None:
    from frameproof.core.timecode import _frames_to_timecode, _timecode_to_frames

    for nominal_fps, day in ((30, 2589408), (60, 5178816)):
        for frame in range(0, day, 997):
            assert _timecode_to_frames(_frames_to_timecode(frame, nominal_fps, True), nominal_fps, True) == frame
        assert _frames_to_timecode(day, nominal_fps, True).format() == ("00:00:00;00")


def test_calculated_timecode_uses_seconds_when_frame_index_is_unknown() -> None:
    display = resolve_timecode_display(
        actual_timecode=None,
        actual_timecode_source=None,
        start_timecode="01:00:00:00",
        container_timecode="01:00:00:00",
        actual_frame_index=None,
        actual_seconds=2.5,
        fps_num=24,
        fps_den=1,
        tc_drop_frame=False,
    )

    assert display.source is TimecodeSource.CALCULATED
    assert display.value == "01:00:02:12 (calculated)"
