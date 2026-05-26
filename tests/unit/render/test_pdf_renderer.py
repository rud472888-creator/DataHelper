from __future__ import annotations

from pathlib import Path
import base64
import re
import zlib

from PIL import Image

from frameproof.config.settings import AppSettings, PathDisplayMode
from frameproof.core.models import (
    AdapterError,
    AdapterErrorCode,
    BatchStatus,
    BatchSummary,
    CapturePoint,
    CaptureStatus,
    ClipInfo,
    ClipStatus,
    FormatFamily,
    ReportItem,
    TimecodeSource,
)
from frameproof.render import render_pdf
from frameproof.render.pdf_renderer import (
    CONTACT_FRAME_CAPTION_HEIGHT,
    CONTACT_FRAME_INSET,
    CONTACT_SHEET_PAGE_SIZE,
    _clips_per_page,
    _contact_usable_height,
    _display_image_path,
    _display_path,
    _fit_image,
    _measure_contact_clip_card,
    _measure_contact_frame,
    _measure_contact_preview,
    _pack_contact_pages,
    _draw_contact_preview_block,
    _draw_contact_preview_triptych,
    _input_summary,
    _start_middle_end_captures,
)


def make_png(path: Path, size: tuple[int, int] = (48, 27)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(220, 180, 90)).save(path)


def pdf_text(path: Path) -> str:
    data = path.read_bytes()
    chunks = [data.decode("latin-1", errors="ignore")]
    cursor = 0
    while True:
        stream_at = data.find(b"stream", cursor)
        if stream_at == -1:
            break
        stream_start = stream_at + len(b"stream")
        if data[stream_start : stream_start + 2] == b"\r\n":
            stream_start += 2
        elif data[stream_start : stream_start + 1] in {b"\r", b"\n"}:
            stream_start += 1
        stream_end = data.find(b"endstream", stream_start)
        if stream_end == -1:
            break
        payload = data[stream_start:stream_end].strip()
        object_header = data[max(0, data.rfind(b"<<", 0, stream_at)) : stream_at]
        try:
            if b"ASCII85Decode" in object_header:
                payload = base64.a85decode(payload, adobe=True)
            if b"FlateDecode" in object_header:
                payload = zlib.decompress(payload)
            chunks.append(payload.decode("latin-1", errors="ignore"))
        except Exception:
            pass
        cursor = stream_end + len(b"endstream")
    return "\n".join(chunks)


def pdf_page_count(path: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", path.read_bytes()))


def make_clip(**overrides: object) -> ClipInfo:
    payload: dict[str, object] = {
        "clip_id": "clip-1",
        "clip_name": "A001_C001.mov",
        "source_path": "/show/day01/A001_C001.mov",
        "format_family": FormatFamily.STANDARD,
        "frame_count": 48,
        "duration_seconds": 2.0,
        "fps_num": 24,
        "fps_den": 1,
        "width": 1920,
        "height": 1080,
        "metadata_raw": {"iso": 800, "scene": "Day01"},
    }
    payload.update(overrides)
    return ClipInfo(**payload)


def make_settings(tmp_path: Path, *, layout: str, path_display: str = "basename") -> AppSettings:
    return AppSettings.from_mapping(
        {
            "input": {"paths": ["/show/day01"]},
            "capture": {"middle_count": 2},
            "report": {"layout": layout, "path_display": path_display},
            "output": {"pdf_path": str(tmp_path / "report.pdf")},
        }
    )


def make_summary() -> BatchSummary:
    return BatchSummary(
        total_clips=2,
        success_count=1,
        partial_success_count=1,
        probe_failed_count=0,
        decode_failed_count=0,
        skipped_count=0,
        status=BatchStatus.PARTIAL_SUCCESS,
    )


def make_capture(
    label: str,
    image_path: Path,
    *,
    ratio: float,
    frame_index: int,
    seconds: float,
    timecode: str,
) -> CapturePoint:
    return CapturePoint(
        label=label,
        requested_ratio=ratio,
        requested_frame_index=frame_index,
        requested_seconds=seconds,
        actual_frame_index=frame_index,
        actual_seconds=seconds,
        actual_timecode=timecode,
        actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
        image_path_temp=str(image_path),
        status=CaptureStatus.SUCCESS,
    )


def make_triptych_item(tmp_path: Path, clip_id: str, *, size: tuple[int, int] = (1920, 1080)) -> ReportItem:
    start_png = tmp_path / f"{clip_id}-start.png"
    mid_png = tmp_path / f"{clip_id}-mid.png"
    end_png = tmp_path / f"{clip_id}-end.png"
    for png_path in (start_png, mid_png, end_png):
        make_png(png_path, size)
    captures = (
        make_capture("Start", start_png, ratio=0.0, frame_index=0, seconds=0.0, timecode="01:00:00:00"),
        make_capture("Mid1", mid_png, ratio=0.5, frame_index=24, seconds=1.0, timecode="01:00:01:00"),
        make_capture("End", end_png, ratio=1.0, frame_index=47, seconds=1.958, timecode="01:00:01:23"),
    )
    return ReportItem(
        clip=make_clip(clip_id=clip_id, clip_name=f"{clip_id}.mov"),
        captures=captures,
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
    )


def test_render_pdf_detail_layout_includes_clip_and_capture_details(tmp_path: Path) -> None:
    start_png = tmp_path / "start.png"
    mid_png = tmp_path / "mid.png"
    make_png(start_png)
    make_png(mid_png)
    item = ReportItem(
        clip=make_clip(start_timecode="01:00:00:00", end_timecode="01:00:01:23"),
        captures=(
            CapturePoint(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=0,
                actual_seconds=0.0,
                actual_timecode="01:00:00:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(start_png),
                status=CaptureStatus.SUCCESS,
            ),
            CapturePoint(
                label="Mid1",
                requested_ratio=0.5,
                requested_frame_index=24,
                requested_seconds=1.0,
                actual_frame_index=24,
                actual_seconds=1.0,
                actual_timecode="01:00:01:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(mid_png),
                status=CaptureStatus.SUCCESS,
                warnings=("fallback tc",),
            ),
            CapturePoint(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=47,
                requested_seconds=1.958,
                status=CaptureStatus.DECODE_FAILED,
                errors=(AdapterError(code=AdapterErrorCode.DECODE_FAILED, message="end decode failed"),),
            ),
        ),
        status=ClipStatus.PARTIAL_SUCCESS,
        adapter_name="ffmpeg",
        warnings=("clip warning",),
        errors=(AdapterError(code=AdapterErrorCode.DECODE_FAILED, message="end decode failed"),),
    )
    failed_item = ReportItem(
        clip=make_clip(clip_id="clip-2", clip_name="broken.mov", source_path="/show/day01/broken.mov"),
        captures=(),
        status=ClipStatus.PROBE_FAILED,
        adapter_name="ffmpeg",
        errors=(AdapterError(code=AdapterErrorCode.PROBE_FAILED, message="probe failed"),),
    )
    pdf_path = tmp_path / "detail.pdf"

    render_pdf(pdf_path, make_settings(tmp_path, layout="detail"), (item, failed_item), make_summary())

    text = pdf_text(pdf_path)
    assert "Layout A / detail" in text
    assert "A001_C001.mov" in text
    assert "Source path: A001_C001.mov" in text
    assert "Requested ratio: 0.500" in text
    assert "Requested frame: 24" in text
    assert "Requested time: 1.000s" in text
    assert "Actual frame: 24" in text
    assert "Actual time: 1.000s" in text
    assert "Raw Metadata Summary" in text
    assert "clip warning" in text
    assert "Mid1 warning: fallback tc" in text
    assert "End error: end decode failed" in text
    assert "Failed / Partial Clips" in text
    assert "broken.mov [probe_failed]" in text


def test_render_pdf_contact_sheet_failed_section_shows_full_path_when_requested(tmp_path: Path) -> None:
    item = ReportItem(
        clip=make_clip(),
        captures=(),
        status=ClipStatus.DEPENDENCY_MISSING,
        adapter_name="ffmpeg",
        errors=(AdapterError(code=AdapterErrorCode.DEPENDENCY_MISSING, message="ffmpeg missing"),),
    )
    pdf_path = tmp_path / "contact.pdf"

    render_pdf(pdf_path, make_settings(tmp_path, layout="contact_sheet", path_display="full"), (item,), make_summary())

    text = pdf_text(pdf_path)
    assert "Layout B / contact_sheet" in text
    assert "CLIP REVIEW PDF PREVIEW ONLY, NOT COLOR-CRITICAL" in text
    assert "Original media untouched; PDF uses embedded preview frames only." in text
    assert "Failed / Partial Clips" in text
    assert "Source: /show/day01/A001_C001.mov" in text
    assert "Error: ffmpeg missing" in text


def test_render_pdf_contact_sheet_handles_korean_pressure_fixture_and_corrupt_image(tmp_path: Path) -> None:
    corrupt_png = tmp_path / "corrupt.png"
    corrupt_png.write_bytes(b"not an image")
    item = ReportItem(
        clip=make_clip(
            clip_name="무선 카메라 제어 및 현장 스크립트 기록 통합 검증 보고서.mov",
            source_path="/Volumes/HOTDRIVE/촬영감독과 스크립터가 동시에 확인해야 하는 상태값/A-CAM_take-2026_05_18_FINAL_v003.mov",
            codec=None,
            metadata_raw={
                "identifier": "A-CAM_take-2026_05_18_FINAL_v003",
                "검증률": "98.7%",
                "처리 시간": "2.3초",
                "row_count": "47,200건",
                "review_url": "https://example.com/reports/blackmagician/session/day-01/take/A-CAM_take-2026_05_18_FINAL_v003",
                "missing_note": "-",
            },
        ),
        captures=(
            CapturePoint(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=0,
                actual_seconds=0.0,
                actual_timecode="01:00:00:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(corrupt_png),
                status=CaptureStatus.SUCCESS,
            ),
            CapturePoint(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=47,
                requested_seconds=1.958,
                actual_frame_index=47,
                actual_seconds=1.958,
                actual_timecode="01:00:01:23",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                status=CaptureStatus.SUCCESS,
            ),
        ),
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
        warnings=("촬영감독과 스크립터가 동시에 확인해야 하는 상태값 확인 필요",),
    )
    settings = AppSettings.from_mapping(
        {
            "input": {"paths": ["/Volumes/HOTDRIVE/촬영감독과 스크립터가 동시에 확인해야 하는 상태값"]},
            "capture": {"middle_count": 0},
            "report": {
                "layout": "contact_sheet",
                "path_display": "basename",
                "project_name": "무선 카메라 제어 및 현장 스크립트 기록 통합 검증 보고서",
            },
            "output": {"pdf_path": str(tmp_path / "korean-pressure.pdf")},
        }
    )
    pdf_path = tmp_path / "korean-pressure.pdf"

    render_pdf(pdf_path, settings, (item,), make_summary())

    data = pdf_path.read_bytes()
    assert data.startswith(b"%PDF")
    assert b"AppleGothic" in data or b"HYGothic-Medium" in data
    assert pdf_page_count(pdf_path) == 1
    assert "preview unavailable" in pdf_text(pdf_path)


def test_contact_sheet_renders_start_middle_end_preview_labels(tmp_path: Path) -> None:
    start_png = tmp_path / "start.png"
    mid1_png = tmp_path / "mid1.png"
    mid2_png = tmp_path / "mid2.png"
    end_png = tmp_path / "end.png"
    for png_path in (start_png, mid1_png, mid2_png, end_png):
        make_png(png_path)

    captures = (
        CapturePoint(
            label="Start",
            requested_ratio=0.0,
            requested_frame_index=0,
            requested_seconds=0.0,
            actual_frame_index=0,
            actual_seconds=0.0,
            actual_timecode="01:00:00:00",
            actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
            image_path_temp=str(start_png),
            status=CaptureStatus.SUCCESS,
        ),
        CapturePoint(
            label="Mid1",
            requested_ratio=0.33,
            requested_frame_index=16,
            requested_seconds=0.666,
            actual_frame_index=16,
            actual_seconds=0.666,
            actual_timecode="01:00:00:16",
            actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
            image_path_temp=str(mid1_png),
            status=CaptureStatus.SUCCESS,
        ),
        CapturePoint(
            label="Mid2",
            requested_ratio=0.66,
            requested_frame_index=32,
            requested_seconds=1.333,
            actual_frame_index=32,
            actual_seconds=1.333,
            actual_timecode="01:00:01:08",
            actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
            image_path_temp=str(mid2_png),
            status=CaptureStatus.SUCCESS,
        ),
        CapturePoint(
            label="End",
            requested_ratio=1.0,
            requested_frame_index=47,
            requested_seconds=1.958,
            actual_frame_index=47,
            actual_seconds=1.958,
            actual_timecode="01:00:01:23",
            actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
            image_path_temp=str(end_png),
            status=CaptureStatus.SUCCESS,
        ),
    )
    item = ReportItem(clip=make_clip(), captures=captures, status=ClipStatus.SUCCESS, adapter_name="ffmpeg")
    pdf_path = tmp_path / "contact-triptych.pdf"

    render_pdf(pdf_path, make_settings(tmp_path, layout="contact_sheet"), (item,), make_summary())

    text = pdf_text(pdf_path)
    assert "START" in text
    assert "MIDDLE" in text
    assert "END" in text
    assert "Middle preview: 1 of 2" in text
    assert _start_middle_end_captures(captures) == (captures[0], captures[2], captures[3])


def test_display_image_path_prefers_exported_images_when_available(tmp_path: Path) -> None:
    temp_png = tmp_path / "temp.png"
    exported_png = tmp_path / "exported.png"
    make_png(temp_png)
    make_png(exported_png)
    capture = CapturePoint(
        label="Start",
        requested_ratio=0.0,
        requested_frame_index=0,
        requested_seconds=0.0,
        actual_frame_index=0,
        actual_seconds=0.0,
        actual_timecode="01:00:00:00",
        actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
        image_path_temp=str(temp_png),
        image_path_exported=str(exported_png),
        status=CaptureStatus.SUCCESS,
    )
    assert _display_image_path(capture) == exported_png


def test_display_path_hidden_mode_preserves_clip_identity() -> None:
    assert _display_path("/show/day01/A001_C001.mov", PathDisplayMode.HIDDEN) == "hidden (A001_C001.mov)"


def test_input_summary_collapses_same_parent_file_inputs(tmp_path: Path) -> None:
    settings = AppSettings.from_mapping(
        {
            "input": {
                "paths": [
                    "/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151557_C002.braw",
                    "/Volumes/HOTDRIVE/오븐마루/001_video/260215/R#1/A001_02151601_C003.braw",
                ]
            },
            "output": {"pdf_path": str(tmp_path / "report.pdf")},
        }
    )

    summary = _input_summary(settings)

    assert summary.endswith("260215/R#1")
    assert "A001_02151557_C002.braw" not in summary
    assert "A001_02151601_C003.braw" not in summary


def test_input_summary_reports_unrelated_sources_without_full_file_list(tmp_path: Path) -> None:
    settings = AppSettings.from_mapping(
        {
            "input": {
                "paths": [
                    "/show/day01/A001.mov",
                    "/other/day02/B001.mov",
                    "/third/day03/C001.mov",
                ]
            },
            "output": {"pdf_path": str(tmp_path / "report.pdf")},
        }
    )

    summary = _input_summary(settings)

    assert summary == "/show/day01 +2 more sources"
    assert "A001.mov" not in summary
    assert "B001.mov" not in summary


def test_clips_per_page_tracks_no_crop_preview_page_flow_policy(tmp_path: Path) -> None:
    start_png = tmp_path / "start.png"
    mid_png = tmp_path / "mid.png"
    extra_png = tmp_path / "extra.png"
    make_png(start_png)
    make_png(mid_png)
    make_png(extra_png)

    two_frame_item = ReportItem(
        clip=make_clip(),
        captures=(
            CapturePoint(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=0,
                actual_seconds=0.0,
                actual_timecode="01:00:00:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(start_png),
                status=CaptureStatus.SUCCESS,
            ),
            CapturePoint(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=47,
                requested_seconds=1.958,
                actual_frame_index=47,
                actual_seconds=1.958,
                actual_timecode="01:00:01:23",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(mid_png),
                status=CaptureStatus.SUCCESS,
            ),
        ),
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
    )
    four_frame_item = ReportItem(
        clip=make_clip(),
        captures=(
            two_frame_item.captures[0],
            CapturePoint(
                label="Mid1",
                requested_ratio=0.33,
                requested_frame_index=16,
                requested_seconds=0.666,
                actual_frame_index=16,
                actual_seconds=0.666,
                actual_timecode="01:00:00:16",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(extra_png),
                status=CaptureStatus.SUCCESS,
            ),
            CapturePoint(
                label="Mid2",
                requested_ratio=0.66,
                requested_frame_index=32,
                requested_seconds=1.333,
                actual_frame_index=32,
                actual_seconds=1.333,
                actual_timecode="01:00:01:08",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(extra_png),
                status=CaptureStatus.SUCCESS,
            ),
            two_frame_item.captures[1],
        ),
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
    )

    assert _clips_per_page((two_frame_item,)) == 2
    assert _clips_per_page((four_frame_item,)) == 2


def test_contact_sheet_preview_aspect_fit_preserves_wide_frame_width(tmp_path: Path) -> None:
    wide_png = tmp_path / "wide.png"
    Image.new("RGB", (1920, 1080), color=(220, 180, 90)).save(wide_png)

    draw_width, draw_height = _fit_image(wide_png, 353.0, 293.0)

    assert round(draw_width, 1) == 353.0
    assert round(draw_height, 1) == 198.6
    assert draw_height <= 293.0


def test_contact_frame_measurement_uses_actual_image_aspect_ratio(tmp_path: Path) -> None:
    wide_png = tmp_path / "wide.png"
    make_png(wide_png, (2000, 1000))
    capture = make_capture("Start", wide_png, ratio=0.0, frame_index=0, seconds=0.0, timecode="01:00:00:00")

    frame = _measure_contact_frame(capture, "START", 0, 180.0)

    assert frame.aspect_ratio == 2.0
    assert frame.card_width == 180.0
    assert frame.image_width == 180.0 - (CONTACT_FRAME_INSET * 2)
    assert frame.image_height == 78.0
    assert frame.total_height == frame.caption_height + frame.image_height + CONTACT_FRAME_INSET


def test_contact_sheet_page_size_is_a4_portrait_document() -> None:
    width, height = CONTACT_SHEET_PAGE_SIZE

    assert round(width / height, 4) == 0.7071


def test_two_normal_contact_sheet_cards_pack_on_one_page(tmp_path: Path) -> None:
    items = (
        make_triptych_item(tmp_path, "clip-1"),
        make_triptych_item(tmp_path, "clip-2"),
    )
    card_width = CONTACT_SHEET_PAGE_SIZE[0] - 48.0
    usable_height = _contact_usable_height(CONTACT_SHEET_PAGE_SIZE)
    measurements = tuple(_measure_contact_clip_card(item, card_width, usable_height) for item in items)

    pages = _pack_contact_pages(measurements, usable_height)

    assert len(pages) == 1
    assert len(pages[0].items) == 2


def test_three_normal_portrait_contact_sheet_cards_fit_without_stretching(tmp_path: Path) -> None:
    items = tuple(make_triptych_item(tmp_path, f"clip-{index}") for index in range(1, 4))
    pdf_path = tmp_path / "three-clips.pdf"

    render_pdf(pdf_path, make_settings(tmp_path, layout="contact_sheet"), items, make_summary())

    assert pdf_page_count(pdf_path) == 1
    measurements = tuple(
        _measure_contact_clip_card(item, CONTACT_SHEET_PAGE_SIZE[0] - 48.0, _contact_usable_height(CONTACT_SHEET_PAGE_SIZE))
        for item in items
    )
    assert measurements[2].height == measurements[0].height


def test_mixed_aspect_contact_frames_share_top_with_natural_bottoms(tmp_path: Path) -> None:
    wide_png = tmp_path / "wide.png"
    square_png = tmp_path / "square.png"
    tall_png = tmp_path / "tall.png"
    make_png(wide_png, (1920, 1080))
    make_png(square_png, (1000, 1000))
    make_png(tall_png, (900, 1600))
    item = ReportItem(
        clip=make_clip(),
        captures=(
            make_capture("Start", wide_png, ratio=0.0, frame_index=0, seconds=0.0, timecode="01:00:00:00"),
            make_capture("Mid1", square_png, ratio=0.5, frame_index=24, seconds=1.0, timecode="01:00:01:00"),
            make_capture("End", tall_png, ratio=1.0, frame_index=47, seconds=1.958, timecode="01:00:01:23"),
        ),
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
    )

    preview = _measure_contact_preview(item, 580.0)

    assert {frame.caption_height for frame in preview.frames} == {CONTACT_FRAME_CAPTION_HEIGHT}
    assert len({round(frame.total_height, 3) for frame in preview.frames}) == 3
    assert preview.height == max(frame.total_height for frame in preview.frames)


class FakeCanvas:
    def __init__(self) -> None:
        self.images: list[dict[str, object]] = []
        self.rects: list[dict[str, object]] = []
        self.round_rects: list[dict[str, object]] = []
        self.line_widths: list[float] = []

    def setFillColor(self, color: object) -> None:
        pass

    def setStrokeColor(self, color: object) -> None:
        pass

    def setFont(self, name: str, size: float) -> None:
        pass

    def drawString(self, x: float, y: float, text: str) -> None:
        pass

    def drawRightString(self, x: float, y: float, text: str) -> None:
        pass

    def drawCentredString(self, x: float, y: float, text: str) -> None:
        pass

    def setLineWidth(self, width: float) -> None:
        self.line_widths.append(width)

    def rect(self, x: float, y: float, width: float, height: float, *, fill: int = 0, stroke: int = 1) -> None:
        self.rects.append({"x": x, "y": y, "width": width, "height": height, "fill": fill, "stroke": stroke})

    def roundRect(self, *args: object, **kwargs: object) -> None:
        self.round_rects.append({"args": args, "kwargs": kwargs})

    def drawImage(
        self,
        image: object,
        x: float,
        y: float,
        width: float,
        height: float,
        *,
        preserveAspectRatio: bool,
        mask: str,
    ) -> None:
        self.images.append(
            {
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "preserveAspectRatio": preserveAspectRatio,
                "mask": mask,
            }
        )


def test_preview_draw_path_uses_direct_image_and_one_point_border(tmp_path: Path, monkeypatch) -> None:
    wide_png = tmp_path / "wide.png"
    make_png(wide_png, (1920, 1080))
    capture = make_capture("Start", wide_png, ratio=0.0, frame_index=0, seconds=0.0, timecode="01:00:00:00")
    frame = _measure_contact_frame(capture, "START", 0.0, 180.0)
    fake = FakeCanvas()
    monkeypatch.setattr("frameproof.render.pdf_renderer._pdf_image_reader", lambda *args: object())

    _draw_contact_preview_block(fake, frame, 12.0, 200.0)

    assert len(fake.round_rects) == 2
    assert fake.images == [
        {
            "x": 12.0 + CONTACT_FRAME_INSET,
            "y": 200.0 - frame.caption_height - frame.image_height,
            "width": 156.0,
            "height": 87.75,
            "preserveAspectRatio": False,
            "mask": "auto",
        }
    ]
    assert 0.8 in fake.line_widths


def test_triptych_draws_mixed_aspect_images_from_same_top_y(tmp_path: Path, monkeypatch) -> None:
    item = ReportItem(
        clip=make_clip(),
        captures=(
            make_capture("Start", tmp_path / "wide.png", ratio=0.0, frame_index=0, seconds=0.0, timecode="01:00:00:00"),
            make_capture("Mid1", tmp_path / "square.png", ratio=0.5, frame_index=24, seconds=1.0, timecode="01:00:01:00"),
            make_capture("End", tmp_path / "tall.png", ratio=1.0, frame_index=47, seconds=1.958, timecode="01:00:01:23"),
        ),
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
    )
    make_png(Path(item.captures[0].image_path_temp), (1920, 1080))
    make_png(Path(item.captures[1].image_path_temp), (1000, 1000))
    make_png(Path(item.captures[2].image_path_temp), (900, 1600))
    preview = _measure_contact_preview(item, 580.0)
    fake = FakeCanvas()
    monkeypatch.setattr("frameproof.render.pdf_renderer._pdf_image_reader", lambda *args: object())

    _draw_contact_preview_triptych(fake, preview, 20.0, 300.0)

    image_tops = {round(image["y"] + image["height"], 3) for image in fake.images}
    image_bottoms = {round(image["y"], 3) for image in fake.images}
    assert image_tops == {274.0}
    assert len(image_bottoms) == 3
