from __future__ import annotations

import re
from dataclasses import dataclass

from .models import TimecodeSource

_TIMECODE_RE = re.compile(r"^(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})(?P<sep>[:;])(?P<frames>\d{2})$")
_DROP_FRAME_RATES: dict[tuple[int, int], int] = {
    (30000, 1001): 30,
    (60000, 1001): 60,
}


@dataclass(frozen=True)
class ParsedTimecode:
    hours: int
    minutes: int
    seconds: int
    frames: int
    drop_frame: bool

    def format(self, *, suffix: str = "") -> str:
        separator = ";" if self.drop_frame else ":"
        return (
            f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"
            f"{separator}{self.frames:02d}{suffix}"
        )


@dataclass(frozen=True)
class TimecodeDisplay:
    value: str
    source: TimecodeSource | None
    drop_frame: bool | None
    warnings: tuple[str, ...] = ()


def parse_timecode(value: str) -> ParsedTimecode | None:
    match = _TIMECODE_RE.match(value.strip())
    if match is None:
        return None
    hours = int(match.group("hours"))
    minutes = int(match.group("minutes"))
    seconds = int(match.group("seconds"))
    frames = int(match.group("frames"))
    if minutes >= 60 or seconds >= 60:
        return None
    return ParsedTimecode(
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        frames=frames,
        drop_frame=match.group("sep") == ";",
    )


def is_supported_drop_frame_rate(fps_num: int | None, fps_den: int | None) -> bool:
    if fps_num is None or fps_den is None:
        return False
    return (fps_num, fps_den) in _DROP_FRAME_RATES


def _nominal_fps(fps_num: int | None, fps_den: int | None) -> int | None:
    if fps_num is None or fps_den is None or fps_num <= 0 or fps_den <= 0:
        return None
    if (fps_num, fps_den) in _DROP_FRAME_RATES:
        return _DROP_FRAME_RATES[(fps_num, fps_den)]
    rounded = round(fps_num / fps_den)
    if rounded <= 0:
        return None
    return rounded


def _drop_frame_count(nominal_fps: int) -> int:
    return 2 if nominal_fps == 30 else 4


def _timecode_to_frames(parsed: ParsedTimecode, nominal_fps: int, drop_frame: bool) -> int | None:
    if parsed.frames >= nominal_fps:
        return None
    if not drop_frame:
        total_seconds = ((parsed.hours * 60) + parsed.minutes) * 60 + parsed.seconds
        return total_seconds * nominal_fps + parsed.frames

    if nominal_fps not in (30, 60):
        return None
    if parsed.seconds == 0 and parsed.minutes % 10 != 0 and parsed.frames < _drop_frame_count(nominal_fps):
        return None

    total_minutes = parsed.hours * 60 + parsed.minutes
    dropped_frames = _drop_frame_count(nominal_fps) * (total_minutes - total_minutes // 10)
    total_seconds = ((parsed.hours * 60) + parsed.minutes) * 60 + parsed.seconds
    return total_seconds * nominal_fps + parsed.frames - dropped_frames


def _frames_to_timecode(total_frames: int, nominal_fps: int, drop_frame: bool) -> ParsedTimecode:
    if not drop_frame:
        seconds_total, frames = divmod(total_frames, nominal_fps)
        minutes_total, seconds = divmod(seconds_total, 60)
        hours, minutes = divmod(minutes_total, 60)
        return ParsedTimecode(hours=hours % 24, minutes=minutes, seconds=seconds, frames=frames, drop_frame=False)

    # SMPTE drop-frame: frame numbers 0..D-1 are skipped at the start of every
    # minute except each tenth minute, so re-insert them before splitting.
    drop_frames = _drop_frame_count(nominal_fps)
    frames_per_minute = nominal_fps * 60 - drop_frames
    frames_per_10_minutes = frames_per_minute * 10 + drop_frames
    frames_per_24_hours = frames_per_10_minutes * 6 * 24

    remaining = total_frames % frames_per_24_hours
    tens_of_minutes, frames_in_block = divmod(remaining, frames_per_10_minutes)
    remaining += drop_frames * 9 * tens_of_minutes
    if frames_in_block > drop_frames:
        remaining += drop_frames * ((frames_in_block - drop_frames) // frames_per_minute)

    seconds_total, frames = divmod(remaining, nominal_fps)
    minutes_total, seconds = divmod(seconds_total, 60)
    hours, minutes = divmod(minutes_total, 60)
    return ParsedTimecode(hours=hours, minutes=minutes, seconds=seconds, frames=frames, drop_frame=True)


def format_elapsed(seconds: float) -> str:
    total_milliseconds = max(round(seconds * 1000), 0)
    total_seconds, milliseconds = divmod(total_milliseconds, 1000)
    minutes_total, seconds_value = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes_total, 60)
    return f"+{hours:02d}:{minutes:02d}:{seconds_value:02d}.{milliseconds:03d}"


def _format_existing_timecode(
    value: str,
    *,
    source: TimecodeSource,
    tc_drop_frame: bool | None,
) -> TimecodeDisplay:
    parsed = parse_timecode(value)
    if parsed is None:
        suffix = " (calculated)" if source == TimecodeSource.CALCULATED else ""
        return TimecodeDisplay(value=f"{value}{suffix}", source=source, drop_frame=tc_drop_frame)

    drop_frame = parsed.drop_frame if tc_drop_frame is None else tc_drop_frame
    formatted = ParsedTimecode(
        hours=parsed.hours,
        minutes=parsed.minutes,
        seconds=parsed.seconds,
        frames=parsed.frames,
        drop_frame=drop_frame,
    ).format(suffix=" (calculated)" if source == TimecodeSource.CALCULATED else "")
    return TimecodeDisplay(value=formatted, source=source, drop_frame=drop_frame)


def calculate_timecode_display(
    *,
    start_timecode: str | None,
    frame_offset: int | None,
    fps_num: int | None,
    fps_den: int | None,
    tc_drop_frame: bool | None,
) -> TimecodeDisplay | None:
    if start_timecode is None or frame_offset is None:
        return None

    nominal_fps = _nominal_fps(fps_num, fps_den)
    if nominal_fps is None:
        return None

    parsed = parse_timecode(start_timecode)
    if parsed is None:
        return None

    warnings: list[str] = []
    if tc_drop_frame is True:
        if not is_supported_drop_frame_rate(fps_num, fps_den):
            return None
        drop_frame = True
    elif tc_drop_frame is False:
        drop_frame = False
    elif parsed.drop_frame:
        drop_frame = True
    elif is_supported_drop_frame_rate(fps_num, fps_den):
        drop_frame = False
        warnings.append("tc_drop_frame_unknown=true")
    else:
        drop_frame = False

    base_frames = _timecode_to_frames(parsed, nominal_fps, drop_frame)
    if base_frames is None:
        return None
    calculated = _frames_to_timecode(base_frames + frame_offset, nominal_fps, drop_frame)
    return TimecodeDisplay(
        value=calculated.format(suffix=" (calculated)"),
        source=TimecodeSource.CALCULATED,
        drop_frame=drop_frame,
        warnings=tuple(warnings),
    )


def _frame_offset(
    frame_index: int | None,
    seconds: float | None,
    fps_num: int | None,
    fps_den: int | None,
) -> int | None:
    if frame_index is not None:
        return frame_index
    if seconds is None or fps_num is None or fps_den is None or fps_num <= 0 or fps_den <= 0:
        return None
    return round(seconds * fps_num / fps_den)


def resolve_timecode_display(
    *,
    actual_timecode: str | None,
    actual_timecode_source: TimecodeSource | None,
    start_timecode: str | None,
    container_timecode: str | None,
    actual_frame_index: int | None,
    actual_seconds: float | None,
    fps_num: int | None,
    fps_den: int | None,
    tc_drop_frame: bool | None,
) -> TimecodeDisplay:
    if actual_timecode is not None and actual_timecode_source is not None:
        return _format_existing_timecode(
            actual_timecode,
            source=actual_timecode_source,
            tc_drop_frame=tc_drop_frame,
        )

    calculated = calculate_timecode_display(
        start_timecode=start_timecode,
        frame_offset=_frame_offset(actual_frame_index, actual_seconds, fps_num, fps_den),
        fps_num=fps_num,
        fps_den=fps_den,
        tc_drop_frame=tc_drop_frame,
    )
    if calculated is not None:
        return calculated

    if container_timecode is not None:
        return _format_existing_timecode(
            container_timecode,
            source=TimecodeSource.CONTAINER_METADATA,
            tc_drop_frame=tc_drop_frame,
        )

    if actual_seconds is not None:
        return TimecodeDisplay(
            value=format_elapsed(actual_seconds),
            source=TimecodeSource.ELAPSED_FALLBACK,
            drop_frame=None,
        )

    return TimecodeDisplay(value="N/A", source=None, drop_frame=None)

