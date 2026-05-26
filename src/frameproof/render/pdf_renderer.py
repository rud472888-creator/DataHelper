from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
import os
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps
from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import A4, landscape, letter  # type: ignore[import-untyped]
from reportlab.lib.utils import ImageReader  # type: ignore[import-untyped]
from reportlab.pdfbase import pdfmetrics  # type: ignore[import-untyped]
from reportlab.pdfbase.cidfonts import UnicodeCIDFont  # type: ignore[import-untyped]
from reportlab.pdfbase.ttfonts import TTFont  # type: ignore[import-untyped]
from reportlab.pdfgen import canvas  # type: ignore[import-untyped]

from frameproof.config.settings import AppSettings, PathDisplayMode, ReportLayout
from frameproof.core.models import BatchSummary, CapturePoint, CaptureStatus, ClipInfo, ClipStatus, ReportItem

CONTACT_SHEET_PAGE_SIZE = A4
DETAIL_PAGE_SIZE = landscape(letter)
MARGIN = 20.0
HEADER_HEIGHT = 84.0
FOOTER_HEIGHT = 24.0
BLOCK_GAP = 8.0
FAILED_SECTION_TOP = 64.0
CONTACT_CLIPS_PER_PAGE = 1
CONTACT_PREVIEW_GAP = 10.0
CONTACT_PREVIEW_MAX_WIDTH = 505.0
CONTACT_FRAME_CAPTION_HEIGHT = 26.0
CONTACT_FRAME_INSET = 12.0
PDF_IMAGE_MAX_PIXELS = 1600
PDF_IMAGE_QUALITY = 86
KOREAN_FONT_NAME = "FrameProofKorean"
KOREAN_CID_FONT_NAME = "HYGothic-Medium"
KOREAN_FONT_PATHS = (
    Path("/System/Library/Fonts/Supplemental/AppleGothic.ttf"),
    Path("/Library/Fonts/NotoSansCJKkr-Regular.otf"),
    Path("/Library/Fonts/NotoSansKR-Regular.ttf"),
)


@dataclass(frozen=True)
class ContactFrameMeasurement:
    label: str
    capture: CapturePoint | None
    x: float
    card_width: float
    caption_height: float
    image_width: float
    image_height: float
    total_height: float
    aspect_ratio: float


@dataclass(frozen=True)
class ContactPreviewMeasurement:
    width: float
    height: float
    frame_top_y: float
    frames: tuple[ContactFrameMeasurement, ...]


@dataclass(frozen=True)
class ContactClipMeasurement:
    item: ReportItem
    width: float
    height: float
    preview: ContactPreviewMeasurement


@dataclass(frozen=True)
class ContactPage:
    items: tuple[ContactClipMeasurement, ...]


def render_pdf(
    output_path: Path,
    settings: AppSettings,
    items: Iterable[ReportItem],
    summary: BatchSummary,
) -> None:
    if settings.report.layout is ReportLayout.CLIP_DETAIL:
        render_detail_pdf(output_path, settings, items, summary)
        return
    render_contact_sheet_pdf(output_path, settings, items, summary)


def render_contact_sheet_pdf(
    output_path: Path,
    settings: AppSettings,
    items: Iterable[ReportItem],
    summary: BatchSummary,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    item_list = tuple(items)
    pdf = canvas.Canvas(str(output_path), pagesize=CONTACT_SHEET_PAGE_SIZE, pageCompression=1)
    page_width, page_height = CONTACT_SHEET_PAGE_SIZE
    project_name = settings.report.project_name or output_path.stem
    input_summary = _input_summary(settings)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    failed_items = tuple(item for item in item_list if item.status is not ClipStatus.SUCCESS)
    has_failed_section = settings.report.include_failed_section and bool(failed_items)

    if not item_list:
        total_pages = 1 + (1 if has_failed_section else 0)
        _draw_contact_sheet_header(pdf, project_name, input_summary, settings, summary, generated_at, 1, total_pages)
        pdf.setFont("Helvetica", 11)
        pdf.setFillColor(colors.HexColor("#5D6470"))
        pdf.drawString(MARGIN, page_height - MARGIN - HEADER_HEIGHT - 18, "No clips were available for the report.")
        _draw_footer(pdf, output_path.name, 1, CONTACT_SHEET_PAGE_SIZE)
        pdf.save()
        return

    usable_height = _contact_usable_height(CONTACT_SHEET_PAGE_SIZE)
    card_width = page_width - (MARGIN * 2)
    measured_clips = tuple(_measure_contact_clip_card(item, card_width, usable_height) for item in item_list)
    regular_contact_pages = _pack_contact_pages(measured_clips, usable_height)
    regular_pages = max(1, len(regular_contact_pages))
    total_pages = regular_pages + (1 if has_failed_section else 0)
    content_top = page_height - MARGIN - HEADER_HEIGHT

    for page_index, contact_page in enumerate(regular_contact_pages):
        _draw_contact_sheet_header(
            pdf,
            project_name,
            input_summary,
            settings,
            summary,
            generated_at,
            page_index + 1,
            total_pages,
        )
        cursor_y = content_top
        for measurement in contact_page.items:
            _draw_clip_block(pdf, measurement, MARGIN, cursor_y)
            cursor_y -= measurement.height + BLOCK_GAP
        _draw_footer(pdf, output_path.name, page_index + 1, CONTACT_SHEET_PAGE_SIZE)
        if page_index + 1 < regular_pages or has_failed_section:
            pdf.showPage()

    if has_failed_section:
        _draw_failed_section(
            pdf,
            failed_items,
            output_path.name,
            regular_pages,
            CONTACT_SHEET_PAGE_SIZE,
            settings.report.path_display,
        )

    pdf.save()


def render_detail_pdf(
    output_path: Path,
    settings: AppSettings,
    items: Iterable[ReportItem],
    summary: BatchSummary,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    item_list = tuple(items)
    pdf = canvas.Canvas(str(output_path), pagesize=DETAIL_PAGE_SIZE, pageCompression=1)
    project_name = settings.report.project_name or output_path.stem
    input_summary = _input_summary(settings)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    failed_items = tuple(item for item in item_list if item.status is not ClipStatus.SUCCESS)
    has_failed_section = settings.report.include_failed_section and bool(failed_items)

    if not item_list:
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(MARGIN, DETAIL_PAGE_SIZE[1] - MARGIN - 8, "Layout A / detail")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(MARGIN, DETAIL_PAGE_SIZE[1] - MARGIN - 30, "No clips were available for the report.")
        _draw_footer(pdf, output_path.name, 1, DETAIL_PAGE_SIZE)
        pdf.save()
        return

    for page_number, item in enumerate(item_list, start=1):
        _draw_detail_page(pdf, item, settings, summary, project_name, input_summary, generated_at, page_number)
        if page_number < len(item_list) or has_failed_section:
            pdf.showPage()

    if has_failed_section:
        _draw_failed_section(
            pdf,
            failed_items,
            output_path.name,
            len(item_list),
            DETAIL_PAGE_SIZE,
            settings.report.path_display,
        )

    pdf.save()


def _draw_contact_sheet_header(
    pdf: canvas.Canvas,
    project_name: str,
    input_summary: str,
    settings: AppSettings,
    summary: BatchSummary,
    generated_at: str,
    page_number: int,
    total_pages: int,
) -> None:
    page_width, page_height = CONTACT_SHEET_PAGE_SIZE
    top = page_height - MARGIN
    card_x = MARGIN
    card_y = page_height - MARGIN - HEADER_HEIGHT
    card_w = page_width - (MARGIN * 2)

    pdf.setFillColor(colors.HexColor("#F4F6F8"))
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(colors.HexColor("#E4E8EE"))
    pdf.roundRect(card_x, card_y, card_w, HEADER_HEIGHT, 8, fill=1, stroke=1)

    left_x = card_x + 18
    right_edge = card_x + card_w - 18
    right_col_w = 238.0
    title_x = left_x
    pdf.setFillColor(colors.HexColor("#111820"))
    pdf.setFont("Helvetica-Bold", 15.5)
    _draw_string(pdf, title_x, top - 22, _ellipsize_for_width(pdf, project_name, right_edge - right_col_w - title_x - 8))
    pdf.setFillColor(colors.HexColor("#69717D"))
    pdf.setFont("Helvetica-Bold", 7.6)
    pdf.drawString(left_x, top - 45, "CLIP REVIEW PDF PREVIEW ONLY, NOT COLOR-CRITICAL")
    pdf.setFont("Helvetica", 7.4)
    pdf.drawString(left_x, top - 60, f"Generated {generated_at}  -  Layout B / contact_sheet")

    failed_count = summary.probe_failed_count + summary.decode_failed_count + summary.skipped_count
    warnings_count = summary.partial_success_count + failed_count
    badge_y = top - 21
    badge_specs = (
        (f"{summary.total_clips} CLIPS", "#E9F4F8", "#26778C"),
        (f"{summary.success_count} SUCCESS", "#E8F4EC", "#1E7A46"),
        (f"{warnings_count} WARNINGS", "#EFEFF1" if not warnings_count else "#FFF3E8", "#A35A00" if warnings_count else "#69717D"),
    )
    cursor_x = right_edge
    for label, fill, text_color in reversed(badge_specs):
        badge_w = max(57.0, pdf.stringWidth(label, "Helvetica-Bold", 6.7) + 15)
        cursor_x -= badge_w
        _draw_pill(pdf, cursor_x, badge_y - 10, badge_w, 16, label, fill, text_color, font_size=6.7)
        cursor_x -= 5

    pdf.setFillColor(colors.HexColor("#5F6670"))
    pdf.setFont("Helvetica", 7.3)
    right_text_x = right_edge - right_col_w
    _draw_string(pdf, right_text_x, top - 48, f"Source: {_ellipsize_for_width(pdf, input_summary, right_col_w)}")
    pdf.drawString(right_text_x, top - 62, f"Page {page_number} of {total_pages}  -  Middle preview: 1 of {settings.capture.middle_count}")


def _draw_clip_block(
    pdf: canvas.Canvas,
    measurement: ContactClipMeasurement,
    x: float,
    y: float,
) -> None:
    item = measurement.item
    width = measurement.width
    height = measurement.height
    bottom = y - height
    pad = 11.0
    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(colors.HexColor("#E5E9EF"))
    pdf.roundRect(x, bottom, width, height, 8, fill=1, stroke=1)

    status_fill = _status_color(item.status)
    badge_w = max(64.0, pdf.stringWidth(item.status.value.upper(), "Helvetica-Bold", 6.3) + 14)
    _draw_pill(pdf, x + width - pad - badge_w, y - 21, badge_w, 14, item.status.value.upper(), status_fill, "#FFFFFF", font_size=6.3)

    pdf.setFillColor(colors.HexColor("#111820"))
    pdf.setFont("Helvetica-Bold", 9.7)
    _draw_string(pdf, x + pad, y - 16, _ellipsize_for_width(pdf, item.clip.clip_name, width - (pad * 3) - badge_w))
    pdf.setFillColor(colors.HexColor("#4D5561"))
    pdf.setFont("Helvetica", 6.7)
    pdf.drawString(x + pad, y - 29, "TIMECODE")
    pdf.setFillColor(colors.HexColor("#111820"))
    pdf.setFont("Helvetica", 6.7)
    _draw_string(pdf, x + pad + 43, y - 29, _ellipsize_for_width(pdf, _timecode_line(item).replace("Timecode: ", ""), width - (pad * 3) - badge_w - 43))

    pdf.setStrokeColor(colors.HexColor("#D9DEE5"))
    pdf.setLineWidth(0.7)
    pdf.line(x + pad, y - 36, x + width - pad, y - 36)

    grid_top = y - 45
    _draw_contact_metadata_grid(pdf, item.clip, x + pad, grid_top, width - (pad * 2), 22)

    note_top = grid_top - 28
    note_h = 14.0
    _draw_status_bar(pdf, item, x + pad, note_top, width - (pad * 2), note_h)

    preview_x = x + ((width - measurement.preview.width) / 2)
    preview_top = note_top - note_h - 11
    _draw_contact_preview_triptych(pdf, measurement.preview, preview_x, preview_top)


def _draw_contact_metadata_grid(pdf: canvas.Canvas, clip: ClipInfo, x: float, y: float, width: float, height: float) -> None:
    columns = (
        ("FORMAT", clip.format_family.value),
        ("DECODER", clip.codec or clip.container or "unknown"),
        ("RESOLUTION", f"{clip.width or '?'}x{clip.height or '?'}"),
        ("RATE / DURATION", f"{_fps_display(clip)} / {_seconds_display(clip.duration_seconds)}"),
    )
    gap = 8.0
    cell_w = (width - (gap * 3)) / 4
    for index, (label, value) in enumerate(columns):
        cell_x = x + (index * (cell_w + gap))
        if index:
            divider_x = cell_x - (gap / 2)
            pdf.setStrokeColor(colors.HexColor("#D9DEE5"))
            pdf.setLineWidth(0.7)
            pdf.line(divider_x, y - height + 2, divider_x, y - 2)
        pdf.setFillColor(colors.HexColor("#6B717A"))
        pdf.setFont("Helvetica-Bold", 5.2)
        pdf.drawString(cell_x + 5, y - 7, label)
        pdf.setFillColor(colors.HexColor("#111820"))
        pdf.setFont("Helvetica-Bold", 6.0)
        _draw_string(pdf, cell_x + 5, y - 17, _ellipsize_for_width(pdf, value, cell_w - 10))


def _draw_status_bar(pdf: canvas.Canvas, item: ReportItem, x: float, y: float, width: float, height: float) -> None:
    warningish = item.status in {ClipStatus.PARTIAL_SUCCESS, ClipStatus.METADATA_INCOMPLETE}
    ok = item.status is ClipStatus.SUCCESS and not item.warnings and not item.errors
    fill = "#F0F7F4" if ok else "#FFF7EA" if warningish else "#FDECEC"
    text_color = "#3C744F" if ok else "#A35A00" if warningish else "#B42318"
    pdf.setFillColor(colors.HexColor(fill))
    pdf.setStrokeColor(colors.HexColor("#D8E6DE" if ok else "#E8D7BD" if warningish else "#E7C4C1"))
    pdf.roundRect(x, y - height, width, height, 3, fill=1, stroke=1)
    pdf.setFillColor(colors.HexColor(text_color))
    pdf.setFont("Helvetica", 6.4)
    note = _report_note_lines(item)[0]
    _draw_string(pdf, x + 9, y - 9.5, _ellipsize_for_width(pdf, note, width - 18))


def _draw_contact_preview_triptych(
    pdf: canvas.Canvas,
    measurement: ContactPreviewMeasurement,
    x: float,
    y: float,
) -> None:
    offset_x = x - measurement.frames[0].x
    offset_y = y - measurement.frame_top_y
    for frame in measurement.frames:
        _draw_contact_preview_block(pdf, frame, frame.x + offset_x, measurement.frame_top_y + offset_y)


def _draw_contact_preview_block(
    pdf: canvas.Canvas,
    frame: ContactFrameMeasurement,
    x: float,
    y: float,
) -> None:
    caption_h = frame.caption_height
    total_h = frame.total_height
    image_y = y - caption_h - frame.image_height
    image_x = x + CONTACT_FRAME_INSET

    pdf.setFillColor(colors.HexColor("#FCFCFD"))
    pdf.setStrokeColor(colors.HexColor("#DDE2EA"))
    pdf.roundRect(x, y - total_h, frame.card_width, total_h, 5, fill=1, stroke=1)

    pdf.setFillColor(colors.HexColor("#111820"))
    pdf.setFont("Helvetica-Bold", 6.6)
    _draw_string(pdf, x + 7, y - 15, frame.label)
    pdf.setFont("Helvetica", 6.2)
    timecode = frame.capture.actual_timecode if frame.capture is not None and frame.capture.actual_timecode else "TC N/A"
    _draw_right_string(pdf, x + frame.card_width - 7, y - 15, timecode)

    image_path = _display_image_path(frame.capture) if frame.capture is not None else None
    if image_path is not None and image_path.is_file():
        image_reader = _pdf_image_reader(image_path, frame.image_width, frame.image_height)
        if image_reader is not None:
            pdf.drawImage(
                image_reader,
                image_x,
                image_y,
                frame.image_width,
                frame.image_height,
                preserveAspectRatio=False,
                mask="auto",
            )
            pdf.setStrokeColor(colors.HexColor("#C7CDD6"))
            pdf.setLineWidth(0.8)
            pdf.roundRect(image_x, image_y, frame.image_width, frame.image_height, 3, fill=0, stroke=1)
            return

    pdf.setFillColor(colors.HexColor("#F8F6F2"))
    pdf.setStrokeColor(colors.HexColor("#D8D2CA"))
    pdf.setLineWidth(0.8)
    pdf.roundRect(image_x, image_y, frame.image_width, frame.image_height, 3, fill=1, stroke=1)
    pdf.setFillColor(colors.HexColor("#8A8178"))
    pdf.setFont("Helvetica", 8.5)
    _draw_centred_string(
        pdf,
        image_x + (frame.image_width / 2),
        image_y + (frame.image_height / 2) - 3,
        _preview_placeholder_text(frame.capture, image_path),
    )



def _draw_detail_page(
    pdf: canvas.Canvas,
    item: ReportItem,
    settings: AppSettings,
    summary: BatchSummary,
    project_name: str,
    input_summary: str,
    generated_at: str,
    page_number: int,
) -> None:
    page_width, page_height = DETAIL_PAGE_SIZE
    pdf.setFillColor(colors.HexColor("#F4F6F8"))
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#1F2328"))

    top = page_height - MARGIN
    pdf.setFont("Helvetica-Bold", 16)
    _draw_string(pdf, MARGIN, top - 10, _ellipsize_for_width(pdf, item.clip.clip_name, page_width - (MARGIN * 2)))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(MARGIN, top - 26, "Layout A / detail")
    pdf.setFont("Helvetica", 9.5)
    pdf.setFillColor(colors.HexColor("#5D6470"))
    _draw_string(pdf, MARGIN, top - 40, _ellipsize_for_width(pdf, f"Project: {project_name}", 168))
    pdf.drawString(MARGIN + 180, top - 40, f"Generated: {generated_at}")
    _draw_string(pdf, MARGIN + 360, top - 40, _ellipsize_for_width(pdf, f"Input summary: {input_summary}", page_width - MARGIN - (MARGIN + 360)))
    _draw_string(
        pdf,
        MARGIN,
        top - 54,
        _ellipsize_for_width(
            pdf,
            "Counts snapshot: "
            f"total={summary.total_clips} success={summary.success_count} "
            f"partial={summary.partial_success_count} failed={summary.probe_failed_count + summary.decode_failed_count}",
            page_width - (MARGIN * 2),
        ),
    )
    _draw_string(
        pdf,
        MARGIN,
        top - 68,
        _ellipsize_for_width(pdf, f"Source path: {_display_path(item.clip.source_path, settings.report.path_display)}", page_width - (MARGIN * 2)),
    )

    left_x = MARGIN
    content_top = top - 84
    left_width = 220.0
    right_x = left_x + left_width + 16
    right_width = page_width - right_x - MARGIN

    _draw_metadata_table(pdf, item.clip, left_x, content_top, left_width, 164)
    _draw_detail_capture_grid(pdf, item, right_x, content_top, right_width)
    _draw_detail_notes(pdf, item, left_x, content_top - 182, page_width - (MARGIN * 2))
    _draw_footer(pdf, project_name, page_number, DETAIL_PAGE_SIZE)


def _draw_detail_capture_grid(
    pdf: canvas.Canvas,
    item: ReportItem,
    x: float,
    top_y: float,
    width: float,
) -> None:
    captures = item.captures
    if not captures:
        pdf.setFillColor(colors.HexColor("#FBFAF7"))
        pdf.roundRect(x, top_y - 154, width, 154, 8, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor("#5D6470"))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(x + 16, top_y - 24, "No capture thumbnails were available for this clip.")
        return

    columns = 2 if len(captures) > 1 else 1
    gap = 12.0
    card_width = (width - (gap * (columns - 1))) / columns
    card_height = 154.0
    for index, capture in enumerate(captures):
        row = index // columns
        column = index % columns
        card_x = x + (column * (card_width + gap))
        card_y = top_y - (row * (card_height + gap))
        _draw_capture_card(pdf, capture, card_x, card_y, card_width, card_height)


def _draw_capture_card(
    pdf: canvas.Canvas,
    capture: CapturePoint,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    bottom = y - height
    pdf.setFillColor(colors.HexColor("#FBFAF7"))
    pdf.setStrokeColor(colors.HexColor("#C9C2B8"))
    pdf.roundRect(x, bottom, width, height, 8, fill=1, stroke=1)

    pdf.setFillColor(colors.HexColor("#1F2328"))
    pdf.setFont("Helvetica-Bold", 10)
    _draw_string(pdf, x + 12, y - 18, capture.label)
    pdf.setFillColor(colors.HexColor("#5D6470"))
    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(x + 12, y - 32, f"Requested ratio: {_ratio_display(capture.requested_ratio)}")
    pdf.drawString(x + 12, y - 44, f"Requested frame: {_frame_display(capture.requested_frame_index)}")
    pdf.drawString(x + 12, y - 56, f"Requested time: {_seconds_display(capture.requested_seconds)}")
    pdf.drawString(x + 12, y - 68, f"Actual frame: {_actual_frame_display(capture)}")
    pdf.drawString(x + 12, y - 80, f"Actual time: {_actual_seconds_display(capture)}")
    pdf.setFont("Helvetica-Bold", 8.5)
    _draw_string(pdf, x + 12, y - 92, _ellipsize_for_width(pdf, f"Actual timecode: {capture.actual_timecode or 'N/A'}", width - 24))

    image_top = y - 102
    image_height = 44.0
    image_width = width - 24
    image_path = _display_image_path(capture)
    image_drawn = False
    if image_path is not None and image_path.is_file():
        draw_width, draw_height = _fit_image(image_path, image_width, image_height)
        image_x = x + 12 + ((image_width - draw_width) / 2)
        image_y = image_top - draw_height
        image_reader = _pdf_image_reader(image_path, image_width, image_height)
        if image_reader is not None:
            pdf.drawImage(image_reader, image_x, image_y, draw_width, draw_height, preserveAspectRatio=True, mask="auto")
            image_drawn = True
    if not image_drawn:
        pdf.setFillColor(colors.HexColor("#EEE7DC"))
        pdf.roundRect(x + 12, image_top - image_height, image_width, image_height, 6, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor("#5D6470"))
        pdf.setFont("Helvetica", 8)
        _draw_centred_string(pdf, x + (width / 2), image_top - 20, _preview_placeholder_text(capture, image_path))

    pdf.setFillColor(colors.HexColor("#A35A00" if capture.warnings else "#5D6470"))
    pdf.setFont("Helvetica", 8)
    note = _capture_note(capture)
    _draw_string(pdf, x + 12, bottom + 10, _ellipsize_for_width(pdf, note, width - 24))


def _draw_detail_notes(
    pdf: canvas.Canvas,
    item: ReportItem,
    x: float,
    top_y: float,
    width: float,
) -> None:
    note_width = (width - 12) / 2
    _draw_note_box(pdf, "Warnings And Errors", _report_note_lines(item), x, top_y, note_width, 120)
    _draw_note_box(pdf, "Raw Metadata Summary", _raw_metadata_lines(item.clip), x + note_width + 12, top_y, note_width, 120)


def _draw_note_box(
    pdf: canvas.Canvas,
    title: str,
    lines: tuple[str, ...],
    x: float,
    top_y: float,
    width: float,
    height: float,
) -> None:
    bottom = top_y - height
    pdf.setFillColor(colors.HexColor("#FBFAF7"))
    pdf.setStrokeColor(colors.HexColor("#C9C2B8"))
    pdf.roundRect(x, bottom, width, height, 8, fill=1, stroke=1)
    pdf.setFillColor(colors.HexColor("#1F2328"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x + 12, top_y - 18, title)
    pdf.setFillColor(colors.HexColor("#5D6470"))
    pdf.setFont("Helvetica", 8.5)
    cursor_y = top_y - 34
    for line in lines[:6]:
        cursor_y = _draw_wrapped_text(pdf, line, x + 12, cursor_y, width - 24, 10)
        if cursor_y <= bottom + 8:
            break


def _draw_metadata_table(
    pdf: canvas.Canvas,
    clip: ClipInfo,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    bottom = y - height
    pdf.setFillColor(colors.HexColor("#FBFAF7"))
    pdf.setStrokeColor(colors.HexColor("#C9C2B8"))
    pdf.roundRect(x, bottom, width, height, 8, fill=1, stroke=1)
    pdf.setFillColor(colors.HexColor("#1F2328"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x + 12, y - 18, "Metadata")
    pdf.setFillColor(colors.HexColor("#5D6470"))
    pdf.setFont("Helvetica", 8.5)
    cursor_y = y - 34
    for line in _metadata_lines(clip):
        cursor_y = _draw_wrapped_text(pdf, line, x + 12, cursor_y, width - 24, 10)


def _draw_thumbnails(
    pdf: canvas.Canvas,
    captures: tuple[CapturePoint, ...],
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    if not captures:
        pdf.setFillColor(colors.HexColor("#EEE7DC"))
        pdf.roundRect(x, y - height, width, height, 8, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor("#5D6470"))
        pdf.setFont("Helvetica", 9)
        _draw_centred_string(pdf, x + (width / 2), y - (height / 2), "No thumbnails captured")
        return

    gap = 8.0
    thumb_width = (width - (gap * (len(captures) - 1))) / len(captures)
    for index, capture in enumerate(captures):
        thumb_x = x + (index * (thumb_width + gap))
        _draw_single_thumbnail(pdf, capture, thumb_x, y, thumb_width, height)


def _draw_single_thumbnail(
    pdf: canvas.Canvas,
    capture: CapturePoint,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    bottom = y - height
    pdf.setFillColor(colors.HexColor("#FBFAF7"))
    pdf.setStrokeColor(colors.HexColor("#C9C2B8"))
    pdf.roundRect(x, bottom, width, height, 8, fill=1, stroke=1)

    pdf.setFillColor(colors.HexColor("#1F2328"))
    pdf.setFont("Helvetica-Bold", 8.5)
    _draw_string(pdf, x + 8, y - 12, capture.label)
    pdf.setFillColor(colors.HexColor("#5D6470"))
    pdf.setFont("Helvetica", 7.8)
    _draw_string(pdf, x + 8, y - 24, _ellipsize_for_width(pdf, capture.actual_timecode or "Timecode: N/A", width - 16))

    image_height = max(height - 44, 24)
    image_top = y - 30
    image_path = _display_image_path(capture)
    image_drawn = False
    if image_path is not None and image_path.is_file():
        draw_width, draw_height = _fit_image(image_path, width - 12, image_height)
        image_x = x + ((width - draw_width) / 2)
        image_y = image_top - draw_height
        image_reader = _pdf_image_reader(image_path, width - 12, image_height)
        if image_reader is not None:
            pdf.drawImage(image_reader, image_x, image_y, draw_width, draw_height, preserveAspectRatio=True, mask="auto")
            image_drawn = True
    if not image_drawn:
        pdf.setFillColor(colors.HexColor("#EEE7DC"))
        pdf.roundRect(x + 6, bottom + 18, width - 12, image_height, 6, fill=1, stroke=0)
        pdf.setFillColor(colors.HexColor("#5D6470"))
        pdf.setFont("Helvetica", 8)
        _draw_centred_string(pdf, x + (width / 2), bottom + 18 + (image_height / 2), _preview_placeholder_text(capture, image_path))

    pdf.setFillColor(colors.HexColor("#5D6470"))
    pdf.setFont("Helvetica", 7.5)
    note = _capture_note(capture)
    _draw_string(pdf, x + 8, bottom + 8, _ellipsize_for_width(pdf, note, width - 16))


def _draw_failed_section(
    pdf: canvas.Canvas,
    items: tuple[ReportItem, ...],
    report_filename: str,
    regular_pages: int,
    page_size: tuple[float, float],
    path_display: PathDisplayMode,
) -> None:
    page_width, page_height = page_size
    pdf.setFillColor(colors.HexColor("#F4F6F8"))
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#1F2328"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(MARGIN, page_height - MARGIN - 6, "Failed / Partial Clips")
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.HexColor("#5D6470"))
    pdf.drawString(MARGIN, page_height - MARGIN - 22, "Failures, partial clips, and skipped clips remain visible for operator review.")

    cursor_y = page_height - MARGIN - FAILED_SECTION_TOP
    line_height = 11.0
    for item in items:
        lines = _failed_section_lines(item, path_display)
        box_height = max(34.0, (line_height * (len(lines) + 1)) + 8)
        if cursor_y - box_height < MARGIN + FOOTER_HEIGHT:
            _draw_footer(pdf, report_filename, regular_pages + 1, page_size)
            pdf.showPage()
            pdf.setFillColor(colors.HexColor("#F4F6F8"))
            pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)
            pdf.setFillColor(colors.HexColor("#1F2328"))
            pdf.setFont("Helvetica-Bold", 15)
            pdf.drawString(MARGIN, page_height - MARGIN - 6, "Failed / Partial Clips")
            cursor_y = page_height - MARGIN - FAILED_SECTION_TOP

        fill = "#FFF3E8" if item.status in {ClipStatus.PARTIAL_SUCCESS, ClipStatus.METADATA_INCOMPLETE} else "#FDECEC"
        pdf.setFillColor(colors.HexColor(fill))
        pdf.setStrokeColor(colors.HexColor("#C9C2B8"))
        pdf.roundRect(MARGIN, cursor_y - box_height, page_width - (MARGIN * 2), box_height, 8, fill=1, stroke=1)
        pdf.setFillColor(colors.HexColor("#1F2328"))
        pdf.setFont("Helvetica-Bold", 9)
        line_y = cursor_y - 16
        _draw_string(pdf, MARGIN + 12, line_y, _ellipsize_for_width(pdf, lines[0], page_width - (MARGIN * 2) - 24))
        pdf.setFillColor(colors.HexColor("#5D6470"))
        pdf.setFont("Helvetica", 8.5)
        for line in lines[1:]:
            line_y = _draw_wrapped_text(pdf, line, MARGIN + 12, line_y - 11, page_width - (MARGIN * 2) - 24, line_height)
        cursor_y -= box_height + 8

    _draw_footer(pdf, report_filename, regular_pages + 1, page_size)


def _draw_footer(
    pdf: canvas.Canvas,
    report_filename: str,
    page_number: int,
    page_size: tuple[float, float],
) -> None:
    page_width, _page_height = page_size
    pdf.setStrokeColor(colors.HexColor("#C9C2B8"))
    pdf.line(MARGIN, MARGIN + 8, page_width - MARGIN, MARGIN + 8)
    pdf.setFillColor(colors.HexColor("#5D6470"))
    pdf.setFont("Helvetica", 8)
    _draw_string(pdf, MARGIN, MARGIN - 2, _ellipsize_for_width(pdf, f"Report file: {report_filename}", (page_width / 2) - MARGIN - 20))
    pdf.drawRightString(page_width - MARGIN, MARGIN - 2, f"Page {page_number}")
    _draw_centred_string(pdf, page_width / 2, MARGIN + 13, "Original media untouched; PDF uses embedded preview frames only.")


def _failed_section_lines(
    item: ReportItem,
    path_display: PathDisplayMode,
) -> tuple[str, ...]:
    lines = [
        f"{item.clip.clip_name} [{item.status.value}]",
        f"Source: {_display_path(item.clip.source_path, path_display)}",
    ]
    for warning in item.warnings:
        lines.append(f"Warning: {warning}")
    for error in item.errors:
        lines.append(f"Error: {error.message}")
    return tuple(lines)


def _metadata_lines(clip: ClipInfo) -> tuple[str, ...]:
    return (
        f"Format: {clip.format_family.value}",
        f"Container: {clip.container or 'unknown'}",
        f"Codec: {clip.codec or 'unknown'}",
        f"Resolution: {clip.width or '?'}x{clip.height or '?'}",
        f"Frame count: {clip.frame_count or 'unknown'}",
        f"FPS: {_fps_display(clip)}",
        f"Duration: {_seconds_display(clip.duration_seconds)}",
        f"Timecode range: {(clip.start_timecode or 'N/A')} -> {(clip.end_timecode or 'N/A')}",
        f"Camera: {clip.camera_make or '-'} {clip.camera_model or ''}".strip(),
        f"Reel / Camera ID: {clip.reel or '-'} / {clip.camera_id or '-'}",
    )


def _report_note_lines(item: ReportItem) -> tuple[str, ...]:
    lines: list[str] = []
    for warning in item.warnings:
        lines.append(f"Warning: {warning}")
    for error in item.errors:
        lines.append(f"Error: {error.message}")
    for capture in item.captures:
        for warning in capture.warnings:
            lines.append(f"{capture.label} warning: {warning}")
        for error in capture.errors:
            lines.append(f"{capture.label} error: {error.message}")
    if not lines:
        lines.append("No clip-level warnings or errors.")
    return tuple(lines)


def _raw_metadata_lines(clip: ClipInfo) -> tuple[str, ...]:
    if not clip.metadata_raw:
        return ("No raw metadata was captured.",)
    lines = [f"{key}: {value}" for key, value in sorted(clip.metadata_raw.items())]
    return tuple(lines[:10])


def _frame_display(frame_index: int | None) -> str:
    return str(frame_index) if frame_index is not None else "N/A"


def _seconds_display(seconds: float | None) -> str:
    return f"{seconds:.3f}s" if seconds is not None else "N/A"


def _ratio_display(ratio: float) -> str:
    return f"{ratio:.3f}"


def _actual_frame_display(capture: CapturePoint) -> str:
    if capture.actual_frame_index is not None:
        return str(capture.actual_frame_index)
    if capture.duplicate_of is not None:
        return f"duplicate of {capture.duplicate_of}"
    return "N/A"


def _actual_seconds_display(capture: CapturePoint) -> str:
    if capture.actual_seconds is not None:
        return f"{capture.actual_seconds:.3f}s"
    if capture.duplicate_of is not None:
        return f"duplicate of {capture.duplicate_of}"
    return "N/A"


def _capture_note(capture: CapturePoint) -> str:
    if capture.errors:
        return capture.errors[0].message
    if capture.warnings:
        return capture.warnings[0]
    if capture.duplicate_of is not None:
        return f"duplicate of {capture.duplicate_of}"
    return "none"


def _display_path(source_path: str, mode: PathDisplayMode) -> str:
    path = Path(source_path)
    if mode is PathDisplayMode.FULL:
        return str(path)
    if mode is PathDisplayMode.BASENAME:
        return path.name
    return f"hidden ({path.name})"


def _display_image_path(capture: CapturePoint | None) -> Path | None:
    if capture is None:
        return None
    for value in (capture.image_path_exported, capture.image_path_temp):
        if value:
            return Path(value)
    return None


def _preview_placeholder_text(capture: CapturePoint | None, image_path: Path | None) -> str:
    if capture is None:
        return "not captured"
    if capture.status is CaptureStatus.SUCCESS:
        return "preview unavailable" if image_path is not None else "not captured"
    return capture.status.value


def _contact_usable_height(page_size: tuple[float, float] = CONTACT_SHEET_PAGE_SIZE) -> float:
    _page_width, page_height = page_size
    return page_height - (MARGIN * 2) - HEADER_HEIGHT - FOOTER_HEIGHT


def _image_aspect_ratio(path: Path | None, fallback: float = 16 / 9) -> float:
    if path is None or not path.is_file():
        return fallback
    try:
        with Image.open(path) as image:
            transposed = ImageOps.exif_transpose(image)
            width, height = transposed.size
    except (OSError, ValueError):
        return fallback
    if width <= 0 or height <= 0:
        return fallback
    return float(width / height)


def _measure_contact_frame(
    capture: CapturePoint | None,
    label: str,
    x: float,
    column_width: float,
    caption_height: float = CONTACT_FRAME_CAPTION_HEIGHT,
) -> ContactFrameMeasurement:
    aspect_ratio = _image_aspect_ratio(_display_image_path(capture))
    image_width = max(24.0, column_width - (CONTACT_FRAME_INSET * 2))
    image_height = image_width / aspect_ratio
    return ContactFrameMeasurement(
        label=label,
        capture=capture,
        x=x,
        card_width=column_width,
        caption_height=caption_height,
        image_width=image_width,
        image_height=image_height,
        total_height=caption_height + image_height + CONTACT_FRAME_INSET,
        aspect_ratio=aspect_ratio,
    )


def _measure_contact_preview(
    item: ReportItem,
    available_width: float,
    *,
    max_height: float | None = None,
) -> ContactPreviewMeasurement:
    start_capture, middle_capture, end_capture = _start_middle_end_captures(item.captures)
    captures = ((start_capture, "START"), (middle_capture, "MIDDLE"), (end_capture, "END"))
    preview_width = min(available_width, CONTACT_PREVIEW_MAX_WIDTH)
    if max_height is not None:
        min_aspect = min(_image_aspect_ratio(_display_image_path(capture)) for capture, _label in captures)
        max_image_height = max(36.0, max_height - CONTACT_FRAME_CAPTION_HEIGHT - CONTACT_FRAME_INSET)
        max_column_width = (max_image_height * min_aspect) + (CONTACT_FRAME_INSET * 2)
        preview_width = min(preview_width, (max_column_width * 3) + (CONTACT_PREVIEW_GAP * 2))
    column_width = (preview_width - (CONTACT_PREVIEW_GAP * 2)) / 3
    frames = tuple(
        _measure_contact_frame(
            capture,
            label,
            index * (column_width + CONTACT_PREVIEW_GAP),
            column_width,
        )
        for index, (capture, label) in enumerate(captures)
    )
    return ContactPreviewMeasurement(
        width=preview_width,
        height=max(frame.total_height for frame in frames),
        frame_top_y=0.0,
        frames=frames,
    )


def _measure_contact_clip_card(
    item: ReportItem,
    width: float,
    max_height: float | None = None,
) -> ContactClipMeasurement:
    chrome_height = 103.0
    available_preview_width = width - 34.0
    preview = _measure_contact_preview(item, available_preview_width)
    height = chrome_height + preview.height
    if max_height is not None and height > max_height:
        preview = _measure_contact_preview(item, available_preview_width, max_height=max_height - chrome_height)
        height = min(max_height, chrome_height + preview.height)
    return ContactClipMeasurement(item=item, width=width, height=height, preview=preview)


def _pack_contact_pages(
    measurements: tuple[ContactClipMeasurement, ...],
    usable_height: float,
) -> tuple[ContactPage, ...]:
    pages: list[ContactPage] = []
    current: list[ContactClipMeasurement] = []
    used_height = 0.0
    for measurement in measurements:
        next_height = measurement.height if not current else used_height + BLOCK_GAP + measurement.height
        if current and next_height > usable_height:
            pages.append(ContactPage(tuple(current)))
            current = [measurement]
            used_height = measurement.height
            continue
        current.append(measurement)
        used_height = next_height
    if current:
        pages.append(ContactPage(tuple(current)))
    return tuple(pages)


def _fit_image(path: Path, max_width: float, max_height: float) -> tuple[float, float]:
    try:
        with Image.open(path) as image:
            width, height = image.size
    except (OSError, ValueError):
        return max_width, max_height
    if width <= 0 or height <= 0:
        return max_width, max_height
    scale = min(max_width / width, max_height / height)
    return width * scale, height * scale


def _pdf_image_reader(path: Path, max_width_points: float, max_height_points: float) -> ImageReader | None:
    # ReportLab treats one image pixel roughly as one PDF point at 72dpi. Embed only
    # enough pixels for the drawn preview area, capped to avoid bloating PDFs while
    # leaving exported still PNGs and source media untouched.
    target_px = max(96, min(PDF_IMAGE_MAX_PIXELS, int(max(max_width_points, max_height_points) * 2)))
    buffer = BytesIO()
    try:
        with Image.open(path) as image:
            transposed = ImageOps.exif_transpose(image)
            transposed.thumbnail((target_px, target_px), Image.Resampling.LANCZOS)
            prepared = transposed if transposed.mode in {"RGB", "L"} else transposed.convert("RGB")
            prepared.save(buffer, format="JPEG", quality=PDF_IMAGE_QUALITY, optimize=True)
    except (OSError, ValueError):
        return None
    buffer.seek(0)
    return ImageReader(buffer)


def _start_middle_end_captures(captures: tuple[CapturePoint, ...]) -> tuple[CapturePoint | None, CapturePoint | None, CapturePoint | None]:
    if not captures:
        return None, None, None
    start = next((capture for capture in captures if capture.label.lower().startswith("start")), captures[0])
    end = next((capture for capture in reversed(captures) if capture.label.lower().startswith("end")), captures[-1])
    middle = _middle_capture(captures, start, end)
    return start, middle, end


def _middle_capture(
    captures: tuple[CapturePoint, ...],
    start: CapturePoint | None,
    end: CapturePoint | None,
) -> CapturePoint | None:
    middle_candidates = [capture for capture in captures if capture is not start and capture is not end]
    labelled_middle = [
        capture
        for capture in middle_candidates
        if capture.label.lower().startswith(("mid", "middle"))
    ]
    candidates = labelled_middle or middle_candidates
    if not candidates:
        return None

    def distance_from_middle(capture: CapturePoint) -> float:
        if capture.requested_ratio is not None:
            return abs(capture.requested_ratio - 0.5)
        if capture.actual_seconds is not None:
            return abs(capture.actual_seconds)
        if capture.requested_seconds is not None:
            return abs(capture.requested_seconds)
        if capture.actual_frame_index is not None:
            return abs(capture.actual_frame_index)
        if capture.requested_frame_index is not None:
            return abs(capture.requested_frame_index)
        return 1.0

    return min(candidates, key=distance_from_middle)


def _status_color(status: ClipStatus) -> str:
    return {
        ClipStatus.SUCCESS: "#3D8652",
        ClipStatus.PARTIAL_SUCCESS: "#A35A00",
        ClipStatus.METADATA_INCOMPLETE: "#A35A00",
    }.get(status, "#B42318")


def _draw_pill(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    fill_color: str,
    text_color: str,
    font_size: float = 8.0,
) -> None:
    pdf.setFillColor(colors.HexColor(fill_color))
    pdf.roundRect(x, y, width, height, height / 2, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor(text_color))
    pdf.setFont("Helvetica-Bold", font_size)
    pdf.drawCentredString(x + (width / 2), y + ((height - font_size) / 2) + 2, text)


def _needs_korean_font(text: str) -> bool:
    return any(
        "\u1100" <= char <= "\u11ff"
        or "\u3130" <= char <= "\u318f"
        or "\uac00" <= char <= "\ud7af"
        for char in text
    )


def _korean_font_name() -> str:
    try:
        pdfmetrics.getFont(KOREAN_FONT_NAME)
        return KOREAN_FONT_NAME
    except KeyError:
        pass

    for font_path in KOREAN_FONT_PATHS:
        if not font_path.is_file():
            continue
        try:
            pdfmetrics.registerFont(TTFont(KOREAN_FONT_NAME, str(font_path)))
            return KOREAN_FONT_NAME
        except Exception:
            continue

    try:
        pdfmetrics.getFont(KOREAN_CID_FONT_NAME)
    except KeyError:
        pdfmetrics.registerFont(UnicodeCIDFont(KOREAN_CID_FONT_NAME))
    return KOREAN_CID_FONT_NAME


def _font_for_text(text: str, font_name: str) -> str:
    if _needs_korean_font(text):
        return _korean_font_name()
    return font_name


def _text_width(
    pdf: canvas.Canvas,
    text: str,
    font_name: str | None = None,
    font_size: float | None = None,
) -> float:
    base_font = font_name or pdf._fontname
    size = font_size or pdf._fontsize
    return float(pdf.stringWidth(text, _font_for_text(text, base_font), size))


def _draw_string(pdf: canvas.Canvas, x: float, y: float, text: str) -> None:
    original_font = getattr(pdf, "_fontname", "Helvetica")
    original_size = getattr(pdf, "_fontsize", 10)
    font_name = _font_for_text(text, original_font)
    if font_name != original_font:
        pdf.setFont(font_name, original_size)
    pdf.drawString(x, y, text)
    if font_name != original_font:
        pdf.setFont(original_font, original_size)


def _draw_right_string(pdf: canvas.Canvas, x: float, y: float, text: str) -> None:
    original_font = getattr(pdf, "_fontname", "Helvetica")
    original_size = getattr(pdf, "_fontsize", 10)
    font_name = _font_for_text(text, original_font)
    if font_name != original_font:
        pdf.setFont(font_name, original_size)
    pdf.drawRightString(x, y, text)
    if font_name != original_font:
        pdf.setFont(original_font, original_size)


def _draw_centred_string(pdf: canvas.Canvas, x: float, y: float, text: str) -> None:
    original_font = getattr(pdf, "_fontname", "Helvetica")
    original_size = getattr(pdf, "_fontsize", 10)
    font_name = _font_for_text(text, original_font)
    if font_name != original_font:
        pdf.setFont(font_name, original_size)
    pdf.drawCentredString(x, y, text)
    if font_name != original_font:
        pdf.setFont(original_font, original_size)


def _ellipsize_for_width(pdf: canvas.Canvas, text: str, max_width: float) -> str:
    font_name = pdf._fontname
    font_size = pdf._fontsize
    if max_width <= 0 or _text_width(pdf, text, font_name, font_size) <= max_width:
        return text
    ellipsis = "..."
    if _text_width(pdf, ellipsis, font_name, font_size) > max_width:
        return ""
    lo = 0
    hi = len(text)
    best = ellipsis
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = text[:mid].rstrip() + ellipsis
        if _text_width(pdf, candidate, font_name, font_size) <= max_width:
            best = candidate
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def _timecode_line(item: ReportItem) -> str:
    if not item.captures:
        return f"Timecode: {item.clip.start_timecode or 'N/A'}"
    start = item.captures[0].actual_timecode or item.clip.start_timecode or "N/A"
    end = item.captures[-1].actual_timecode or item.clip.end_timecode or "N/A"
    return f"Timecode: {start} -> {end}"


def _metadata_line(clip: ClipInfo) -> str:
    resolution = f"{clip.width or '?'}x{clip.height or '?'}"
    duration = f"{clip.duration_seconds:.3f}s" if clip.duration_seconds is not None else "duration?"
    return (
        f"{clip.format_family.value} | {clip.container or 'container?'} | {clip.codec or 'codec?'} | "
        f"{resolution} | {_fps_display(clip)} | {duration}"
    )


def _fps_display(clip: ClipInfo) -> str:
    if clip.fps_num is None or clip.fps_den is None:
        return "fps?"
    return f"{clip.fps_num / clip.fps_den:.3f}fps"


def _clips_per_page(items: tuple[ReportItem, ...]) -> int:
    return 2 if items else CONTACT_CLIPS_PER_PAGE


def _input_summary(settings: AppSettings) -> str:
    roots = [_source_root(path) for path in settings.input.paths]
    if not roots:
        return "unknown"

    try:
        common = Path(os.path.commonpath([str(root) for root in roots]))
    except ValueError:
        common = None

    if common is not None and common != Path("/"):
        if all(root == common or common in root.parents for root in roots):
            return _compact_source_root(common)

    unique_roots: list[Path] = []
    for root in roots:
        if root not in unique_roots:
            unique_roots.append(root)
    first = _compact_source_root(unique_roots[0])
    if len(unique_roots) > 1:
        return f"{first} +{len(unique_roots) - 1} more sources"
    return first


def _source_root(path: Path) -> Path:
    # CLI inputs may be files that do not exist in unit tests, so use a suffix as
    # the stable signal for file inputs and collapse them to their parent folder.
    if path.suffix:
        return path.parent
    return path


def _compact_source_root(path: Path) -> str:
    parts = path.parts
    if not parts:
        return str(path)
    if len(parts) <= 3:
        return str(path)
    return ".../" + "/".join(parts[-3:])


def _draw_wrapped_text(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    line_height: float,
) -> float:
    lines = _wrap_text_lines(pdf, text, max_width)
    if not lines:
        return y - line_height

    cursor_y = y
    for line in lines:
        _draw_string(pdf, x, cursor_y, line)
        cursor_y -= line_height
    return cursor_y


def _wrap_text_lines(pdf: canvas.Canvas, text: str, max_width: float) -> tuple[str, ...]:
    words = text.split()
    if not words:
        return ()

    lines: list[str] = []
    current = ""
    for word in words:
        chunks = _break_long_token(pdf, word, max_width)
        for chunk in chunks:
            candidate = chunk if not current else f"{current} {chunk}"
            if not current or _text_width(pdf, candidate) <= max_width:
                current = candidate
                continue
            lines.append(current)
            current = chunk
    if current:
        lines.append(current)
    return tuple(lines)


def _break_long_token(pdf: canvas.Canvas, token: str, max_width: float) -> tuple[str, ...]:
    if _text_width(pdf, token) <= max_width:
        return (token,)
    if _needs_korean_font(token):
        return (_ellipsize_for_width(pdf, token, max_width),)

    chunks: list[str] = []
    current = ""
    for char in token:
        candidate = current + char
        if not current or _text_width(pdf, candidate) <= max_width:
            current = candidate
            continue
        chunks.append(current)
        current = char
    if current:
        chunks.append(current)
    return tuple(chunks)
