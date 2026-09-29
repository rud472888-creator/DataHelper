"""Compact, Korean-capable sampled-frame reports: three clips on every full page.

The supplied models are the sole source of truth. PDF deliberately projects
normalized metadata, previews, capture positions and bounded messages; raw and
structured error payloads are outside this compact report. CSV/JSON are untouched.
Canvas is used only for bounded running furniture; content uses Platypus.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from io import BytesIO
from pathlib import Path
import re
from xml.sax.saxutils import escape

from PIL import Image, ImageOps
from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import A4, landscape, letter  # type: ignore[import-untyped]
from reportlab.lib.styles import ParagraphStyle  # type: ignore[import-untyped]
from reportlab.pdfbase import pdfmetrics  # type: ignore[import-untyped]
from reportlab.pdfbase.ttfonts import TTFont  # type: ignore[import-untyped]
from reportlab.pdfgen.canvas import Canvas  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    BaseDocTemplate, Frame, Image as PDFImage, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

from frameproof.config.settings import AppSettings, PathDisplayMode, ReportLayout
from frameproof.core.models import (
    BatchSummary, CapturePoint, CaptureStatus, ClipInfo, ReportItem, TimecodeSource,
)

CONTACT_SHEET_PAGE_SIZE = A4
DETAIL_PAGE_SIZE = landscape(letter)
MARGIN = 42.0
PDF_IMAGE_MAX_PIXELS = 1600
PDF_IMAGE_QUALITY = 86
FONT_REGULAR = "DataHandlerSans"
FONT_BOLD = "DataHandlerSans-Bold"
FONT_DIRECTORY = Path(__file__).with_name("fonts")
INK = colors.HexColor("#20282B")
MUTED = colors.HexColor("#5C696C")
TEAL = colors.HexColor("#0B5B61")
RULE = colors.HexColor("#D4DEDF")
CAPTURE_STATES = {
    CaptureStatus.SUCCESS: "정상", CaptureStatus.DECODE_FAILED: "실패",
    CaptureStatus.METADATA_INCOMPLETE: "미완", CaptureStatus.SKIPPED_DUPLICATE: "중복",
}
TC_SOURCES: dict[TimecodeSource | None, str] = {
    TimecodeSource.NATIVE_ADAPTER: "N", TimecodeSource.CALCULATED: "C",
    TimecodeSource.CONTAINER_METADATA: "M", TimecodeSource.ELAPSED_FALLBACK: "E",
}


@dataclass(frozen=True)
class ClipPresentation:
    number: int
    item: ReportItem


@dataclass(frozen=True)
class ReportPresentation:
    title: str
    generated_at: str
    clips: tuple[ClipPresentation, ...]
    warning_clips: int
    error_clips: int
    capture_counts: tuple[tuple[str, int], ...]


def _value(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "예 / true" if value else "아니요 / false"
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def _integer(value: int | None) -> str:
    return f"{value:,}" if value is not None else "-"


def _seconds_display(value: float | None) -> str:
    return f"{value:.3f} s" if value is not None else "-"


def _fps_display(clip: ClipInfo) -> str:
    if clip.fps_num is None or clip.fps_den is None:
        return "-"
    return f"{clip.fps_num}/{clip.fps_den} ({clip.fps_num / clip.fps_den:.3f} fps)"


def _display_path(source_path: str, mode: PathDisplayMode) -> str:
    path = Path(source_path)
    if mode is PathDisplayMode.FULL:
        return str(path)
    if mode is PathDisplayMode.BASENAME:
        return path.name
    return f"hidden ({path.name})"


def _project_report(output_path: Path, settings: AppSettings, items: tuple[ReportItem, ...]) -> ReportPresentation:
    counts = Counter(c.status.value for item in items for c in item.captures)
    return ReportPresentation(
        settings.report.project_name or output_path.stem,
        datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
        tuple(ClipPresentation(number, item) for number, item in enumerate(items, 1)),
        sum(bool(item.warnings or any(c.warnings for c in item.captures)) for item in items),
        sum(bool(item.errors or any(c.errors for c in item.captures)) for item in items),
        tuple((status.value, counts[status.value]) for status in CaptureStatus),
    )


def _register_fonts() -> None:
    for name, filename in ((FONT_REGULAR, "DataHandlerSans-Regular.ttf"), (FONT_BOLD, "DataHandlerSans-Bold.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(FONT_DIRECTORY / filename)))
    pdfmetrics.registerFontFamily(FONT_REGULAR, normal=FONT_REGULAR, bold=FONT_BOLD, italic=FONT_REGULAR, boldItalic=FONT_BOLD)


def _styles() -> dict[str, ParagraphStyle]:
    base = ParagraphStyle("body", fontName=FONT_REGULAR, fontSize=8.3, leading=10.8,
                          textColor=INK, spaceAfter=0, splitLongWords=0, allowWidows=1, allowOrphans=1)
    return {
        "body": base,
        "small": ParagraphStyle("small", parent=base, fontSize=8, leading=10.5, textColor=MUTED),
        "label": ParagraphStyle("label", parent=base, fontSize=8, leading=10.5, fontName=FONT_BOLD, textColor=TEAL),
        "title": ParagraphStyle("title", parent=base, fontSize=12, leading=14, fontName=FONT_BOLD),
        "clip": ParagraphStyle("clip", parent=base, fontSize=10.5, leading=13.5, fontName=FONT_BOLD),
        "issue": ParagraphStyle("issue", parent=base, fontName=FONT_BOLD, textColor=TEAL),
    }


def _p(text: object, style: ParagraphStyle, width: float | None = None) -> Paragraph:
    value = str(text)
    # Korean prose keeps word boundaries; oversized paths and identifiers may
    # split. Everything is escaped, including literal markup in source messages.
    if width and not style.splitLongWords and any(pdfmetrics.stringWidth(token, style.fontName, style.fontSize) > width for token in value.split()):
        style = ParagraphStyle(style.name + "-oversized-token", parent=style, splitLongWords=1)
    return Paragraph(escape(value).replace("\n", "<br/>"), style)


def _bounded(text: object, style: ParagraphStyle, width: float, lines: int = 1, *, suffix: bool = False) -> Paragraph:
    """Measure before eliding; never clip, reduce fonts, or conceal omissions.

    Paths/identifiers retain a recognizable suffix. Prose ends at a word boundary
    when possible. The same measured paragraph is passed to Platypus for drawing.
    """
    value = " ".join(str(text).split())
    height = style.leading * lines + .01

    def fits(candidate: str) -> bool:
        return bool(_p(candidate, style, width).wrap(width, height)[1] <= height)

    if fits(value):
        return _p(value, style, width)
    marker = " …(축약) "

    def excerpt(length: int) -> str:
        if suffix:
            tail = min(length // 2, 32)
            return value[:length - tail].rstrip() + marker + (value[-tail:] if tail else "")
        head = value[:length]
        if " " in head and length < len(value) and value[length:length + 1] != " ":
            head = head.rsplit(" ", 1)[0]
        return head.rstrip() + marker.rstrip()

    low, high = 0, len(value)
    while low < high:
        middle = (low + high + 1) // 2
        if fits(excerpt(middle)):
            low = middle
        else:
            high = middle - 1
    result = _p(excerpt(low), style, width)
    if result.wrap(width, height)[1] > height:
        raise ValueError("The compact PDF field is too narrow for its abbreviation marker")
    return result


def _table(rows: list[list[object]], widths: list[float], heights: list[float] | None = None) -> Table:
    table = Table(rows, colWidths=widths, rowHeights=heights, hAlign="LEFT", splitByRow=0, splitInRow=0)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), FONT_REGULAR),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("LEADING", (0, 0), (-1, -1), 10.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


class _ReportDocument(BaseDocTemplate):  # type: ignore[misc]
    def __init__(self, filename: str, title: str, page_size: tuple[float, float], styles: dict[str, ParagraphStyle]):
        super().__init__(filename, pagesize=page_size, leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=52, bottomMargin=45, title=title,
                         author="Data Handler", creator="DataHelper", subject="Sampled frame review / 샘플 프레임 검토")
        self.project_title = title
        self.page_sections: list[str] = []
        self.styles = styles
        frame = Frame(MARGIN, 45, page_size[0] - 2 * MARGIN, page_size[1] - 97,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id="report", frames=[frame], onPageEnd=self._furniture))

    def beforePage(self) -> None:
        self.page_sections = []

    def _furniture(self, pdf: Canvas, doc: BaseDocTemplate) -> None:
        width, height = self.pagesize
        pdf.saveState()
        pdf.setStrokeColor(RULE)
        pdf.setLineWidth(.5)
        pdf.line(MARGIN, height - 35, width - MARGIN, height - 35)
        section = "수록 클립 없음"
        if self.page_sections:
            first, last = self.page_sections[0], self.page_sections[-1]
            section = first if first == last else f"{first} / {last}"
        heading = self.project_title
        available = width - 2 * MARGIN - pdfmetrics.stringWidth(section, FONT_REGULAR, 8) - 20
        if pdfmetrics.stringWidth(heading, FONT_REGULAR, 8) > available:
            heading = "Data Handler / 샘플 프레임 검토"
        pdf.setFont(FONT_REGULAR, 8)
        pdf.setFillColor(MUTED)
        pdf.drawString(MARGIN, height - 26, heading)
        pdf.drawRightString(width - MARGIN, height - 26, section)
        pdf.line(MARGIN, 39, width - MARGIN, 39)
        pdf.drawString(MARGIN, 27, "캡처 상태: 정상(success) · 실패(decode_failed) · 미완(metadata_incomplete) · 중복(skipped_duplicate)")
        pdf.drawString(MARGIN, 15, "TC 출처: N native_adapter · C calculated · M container_metadata · E elapsed_fallback")
        pdf.drawRightString(width - MARGIN, 15, f"Page {doc.page}")
        pdf.restoreState()

    def afterFlowable(self, flowable: object) -> None:
        section = getattr(flowable, "report_section", None)
        if section:
            self.page_sections.append(section)


def _intro(presentation: ReportPresentation, settings: AppSettings, summary: BatchSummary,
           width: float, styles: dict[str, ParagraphStyle], height: float) -> Table:
    count = len(presentation.clips)
    scope = f"수록 {count}클립"
    if summary.total_clips != count:
        scope += " (배치 집계와 수록 범위가 다릅니다)"
    if settings.report.include_summary_page:
        scope += (f" | 배치 {summary.status.value} · 전체 {summary.total_clips} · 정상 {summary.success_count}"
                  f" · 부분 {summary.partial_success_count} · 조회 실패 {summary.probe_failed_count}"
                  f" · 추출 실패 {summary.decode_failed_count} · 건너뜀 {summary.skipped_count}")
    info = (f"{presentation.generated_at}"
            f" | 캡처 {sum(n for _, n in presentation.capture_counts)}"
            f" | 경고가 있는 클립: {presentation.warning_clips} · 오류가 있는 클립: {presentation.error_clips}")
    if settings.report.include_failed_section:
        info += f" | 확인 필요 {sum(c.item.status.value != 'success' for c in presentation.clips)}"
    legend = "표본 캡처 검토 · - 값 없음 · 초/비율 소수 셋째 자리 · 경고/오류 건수는 중복을 포함한 기록 수"
    parts = [_bounded(presentation.title, styles["title"], width, 2),
             _bounded(scope, styles["small"], width, 2 if width < 600 else 1),
             _bounded(info, styles["small"], width), _bounded(legend, styles["small"], width)]
    natural = sum(p.wrap(width, height)[1] for p in parts)
    if settings.report.include_summary_page:
        profile = _bounded(
            f"설정: 입력 {len(settings.input.paths)}곳 · {settings.capture.profile} · 중간 {settings.capture.middle_count}개"
            f" · {'프레임' if settings.capture.prefer_frame_index else '초'} 우선 · 경로 {settings.report.path_display.value}",
            styles["small"], width)
        profile_height = profile.wrap(width, height)[1]
        if natural + profile_height <= height:
            parts.append(profile)
            natural += profile_height
    if natural > height:
        raise ValueError("Compact PDF introduction exceeds its measured page budget")
    return _table([[parts]], [width], [height])


def _display_image_path(capture: CapturePoint | None) -> Path | None:
    if capture is None:
        return None
    for value in (capture.image_path_exported, capture.image_path_temp):
        if value:
            return Path(value)
    return None


def _fit_dimensions(size: tuple[int, int], max_width: float, max_height: float) -> tuple[float, float]:
    scale = min(max_width / size[0], max_height / size[1])
    return size[0] * scale, size[1] * scale


def _fit_image(path: Path, max_width: float, max_height: float) -> tuple[float, float]:
    try:
        with Image.open(path) as image:
            oriented = ImageOps.exif_transpose(image)
            return _fit_dimensions(oriented.size, max_width, max_height)
    except (OSError, ValueError):
        return max_width, max_height


def _preview(capture: CapturePoint | None, width: float, height: float,
             styles: dict[str, ParagraphStyle]) -> tuple[object, str | None]:
    path = _display_image_path(capture)
    reason = "캡처 미설정" if capture is None else "파일 없음"
    if path is not None:
        try:
            with Image.open(path) as image:
                oriented = ImageOps.exif_transpose(image)
                dimensions = _fit_dimensions(oriented.size, width, height)
                target = max(96, min(PDF_IMAGE_MAX_PIXELS, int(max(width, height) * 2)))
                oriented.thumbnail((target, target), Image.Resampling.LANCZOS)
                prepared = oriented if oriented.mode in {"RGB", "L"} else oriented.convert("RGB")
                buffer = BytesIO()
                prepared.save(buffer, format="JPEG", quality=PDF_IMAGE_QUALITY, optimize=True)
                buffer.seek(0)
            return PDFImage(buffer, width=dimensions[0], height=dimensions[1], hAlign="LEFT"), None
        except FileNotFoundError:
            reason = "파일 없음"
        except (OSError, ValueError):
            reason = "이미지 읽기 실패"
    if reason == "파일 없음" and capture is not None and capture.status is not CaptureStatus.SUCCESS:
        reason = capture.status.value
    placeholder = Table([[_p("미리보기 없음\n" + reason, styles["small"], width - 16)]],
                        colWidths=[width], rowHeights=[min(height, 88)], hAlign="LEFT")
    placeholder.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                    ("LINEABOVE", (0, 0), (-1, -1), .5, RULE),
                                    ("LINEBELOW", (0, 0), (-1, -1), .5, RULE)]))
    return placeholder, reason


def _start_middle_end_captures(captures: tuple[CapturePoint, ...]) -> tuple[CapturePoint | None, CapturePoint | None, CapturePoint | None]:
    start = next((c for c in captures if c.label == "Start"), None)
    end = next((c for c in captures if c.label == "End"), None)
    middle = [c for c in captures if c.label.startswith("Mid")]
    return start, min(middle, key=lambda c: abs(c.requested_ratio - .5)) if middle else None, end


def _gallery(item: ReportItem, layout: ReportLayout, width: float, styles: dict[str, ParagraphStyle]) -> Table:
    portrait = layout is ReportLayout.CONTACT_SHEET
    if portrait:
        start, middle, end = _start_middle_end_captures(item.captures)
        selected = [(start, "Start"), (middle, f"{middle.label} (대표)" if middle else "중간 캡처 미설정"), (end, "End")]
    else:
        selected = [(capture, capture.label) for capture in item.captures]
    if not selected:
        return _table([[_p("캡처 지점: 0 · 미리보기 없음", styles["small"], width)]], [width], [56])
    gap, max_height = 5.0, 49.0 if portrait else 43.0
    cell_width = (width - gap * (len(selected) - 1)) / len(selected)
    widths = [entry for i in range(len(selected)) for entry in ([gap, cell_width] if i else [cell_width])]
    captions: list[object] = []
    pictures: list[object] = []
    for index, (capture, label) in enumerate(selected):
        if index:
            captions.append("")
            pictures.append("")
        captions.append(_bounded(label, styles["label"], cell_width))
        preview, _ = _preview(capture, cell_width, max_height, styles)
        pictures.append(preview)
    return _table([captions, pictures], widths, [10.5, max_height])


def _capture_table(item: ReportItem, layout: ReportLayout, width: float, styles: dict[str, ParagraphStyle]) -> Table:
    if not item.captures:
        return _table([[_p("캡처 지점: 0", styles["small"], width)]], [width])
    portrait = layout is ReportLayout.CONTACT_SHEET
    widths = ([40.0, 59.0, 60.0, width - 159] if portrait else [53.0, 100.0, 77.0, width - 289, 59.0])
    headers = (["캡처 / 상태", "요청 f / s", "실제 f / s", "실제 TC / 출처"] if portrait
               else ["캡처 / 상태", "요청 f / s (비율)", "실제 f / s", "실제 TC / 출처", "중복 대상"])
    rows: list[list[object]] = [[_bounded(label, styles["label"], w - 3) for label, w in zip(headers, widths)]]
    for capture in item.captures:
        source = TC_SOURCES.get(capture.actual_timecode_source, "-")
        status = CAPTURE_STATES[capture.status]
        requested = f"{_integer(capture.requested_frame_index)} f"
        actual = f"{_integer(capture.actual_frame_index)} f"
        if portrait:
            values = [
                (capture.label, status),
                (f"{requested} · r{capture.requested_ratio:.3f}", _seconds_display(capture.requested_seconds)),
                (actual, _seconds_display(capture.actual_seconds)),
                (_value(capture.actual_timecode), f"출처 {source}" + (f" · 중복 {capture.duplicate_of}" if capture.duplicate_of else "")),
            ]
            cells: list[object] = [[_bounded(line, styles["small"], w - 3) for line in pair] for pair, w in zip(values, widths)]
        else:
            texts = [f"{capture.label} {status}",
                     f"{requested} / {_seconds_display(capture.requested_seconds)} ({capture.requested_ratio:.3f})",
                     f"{actual} / {_seconds_display(capture.actual_seconds)}",
                     f"{_value(capture.actual_timecode)} · {source}", _value(capture.duplicate_of)]
            cells = [_bounded(text, styles["small"], w - 3) for text, w in zip(texts, widths)]
        rows.append(cells)
    heights = [11.5] + ([22.0] if portrait else [11.0]) * len(item.captures)
    table = _table(rows, widths, heights)
    table.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), .3, RULE)]))
    return table


def _safe_message(text: str, item: ReportItem, settings: AppSettings) -> str:
    mode = settings.report.path_display
    if mode is PathDisplayMode.FULL:
        return text
    # Replace known paths as units first, including names containing spaces.
    paths = [str(p) for p in settings.input.paths] + [item.clip.source_path, *item.clip.part_files]
    paths.extend(p for c in item.captures for p in (c.image_path_temp, c.image_path_exported) if p)
    replacements: dict[str, str] = {}
    for index, path in enumerate(sorted(set(paths), key=len, reverse=True)):
        token = f"__PDF_PATH_{index}__"
        if path in text:
            text = text.replace(path, token)
            replacements[token] = _display_path(path, mode)
    text = re.sub(r"(?<![\w:/<])/(?:[^\s<>\"']+/)*[^\s<>\"']+", lambda m: _display_path(m[0], mode), text)
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def _message_counts(item: ReportItem) -> tuple[int, int]:
    return (len(item.warnings) + sum(len(c.warnings) for c in item.captures),
            len(item.errors) + sum(len(c.errors) for c in item.captures))


def _messages(item: ReportItem, settings: AppSettings, width: float, styles: dict[str, ParagraphStyle],
              layout: ReportLayout) -> Table:
    # Capture location takes precedence over the aggregate copy of the same
    # error. Counts are explicitly stored records, never distinct incidents.
    groups = [(c.label, c.warnings, c.errors) for c in item.captures]
    groups.append(("클립", item.warnings, item.errors))
    warnings = [(scope, message) for scope, entries, _ in groups for message in entries]
    errors = [(scope, error) for scope, _, entries in groups for error in entries]
    texts = []
    if errors:
        scope, error = errors[0]
        remaining = f" 외 {len(errors) - 1}건" if len(errors) > 1 else ""
        text = f"오류 [{scope}] {error.code.value}{remaining}: {_safe_message(error.message, item, settings)}"
        texts.append(text)
    if warnings:
        scope, message = warnings[0]
        remaining = f" 외 {len(warnings) - 1}건" if len(warnings) > 1 else ""
        text = f"경고 [{scope}]{remaining}: {_safe_message(message, item, settings)}"
        texts.append(text)
    if not texts:
        return _table([[_p("기록된 경고·오류 없음", styles["small"], width)]], [width])
    if layout is ReportLayout.CLIP_DETAIL and len(texts) == 2:
        half = (width - 10) / 2
        return _table([[_bounded(texts[0], styles["issue"], half), "",
                        _bounded(texts[1], styles["issue"], half)]], [half, 10, half])
    lines = 2 if layout is ReportLayout.CONTACT_SHEET and len(texts) == 1 else 1
    return _table([[_bounded(text, styles["issue"], width, lines)] for text in texts], [width])


def _metadata(clip: ClipPresentation, layout: ReportLayout, settings: AppSettings,
              width: float, styles: dict[str, ParagraphStyle]) -> list[object]:
    item, media = clip.item, clip.item.clip
    warnings, errors = _message_counts(item)
    portrait = layout is ReportLayout.CONTACT_SHEET
    identity = f"ID {media.clip_id}"
    counts = f"경고 {warnings} · 오류 {errors}"
    size = f"{_integer(media.file_size_bytes)} bytes" if media.file_size_bytes is not None else "-"
    format_line = f"형식 {media.format_family.value} / {_value(media.container)} / {_value(media.codec)}"
    resolution = f"{_value(media.width)} × {_value(media.height)}"
    duration = f"{_seconds_display(media.duration_seconds)} · {_integer(media.frame_count)} frames"
    camera = f"카메라 {_value(media.camera_make)} / {_value(media.camera_model)}"
    camera_id = f"ID {_value(media.camera_id)} · 릴 {_value(media.reel)}"
    timecodes = f"TC {_value(media.start_timecode)} → {_value(media.end_timecode)}"
    tc_source = f"TC 출처 {TC_SOURCES.get(media.timecode_source, '-')} · DF {_value(media.tc_drop_frame)}"
    source = f"소스 {_display_path(media.source_path, settings.report.path_display)}"
    logical = (f"논리 {_value(media.logical_clip_name)} · "
               if media.logical_clip_name and media.logical_clip_name != media.clip_name else "") + f"분할 {len(media.part_files)}개"
    if portrait:
        fields = [(identity, 1, True), (counts, 1, False), (format_line, 2, False),
                  (f"해상도 {resolution}", 1, False), (f"FPS {_fps_display(media)}", 1, False),
                  (duration, 1, False), (f"크기 {size}", 1, False), (camera, 1, False),
                  (camera_id, 1, False), (timecodes, 1, False), (tc_source, 1, False),
                  (f"어댑터 {item.adapter_name}", 1, False), (source, 1, True), (logical, 1, True)]
    else:
        fields = [(f"{identity} · {counts}", 1, True), (format_line, 1, False),
                  (f"{resolution} · {_fps_display(media)}", 1, False), (f"{duration} · {size}", 1, False),
                  (camera, 1, False), (f"{camera_id} · {tc_source}", 1, False),
                  (timecodes, 1, False), (f"어댑터 {item.adapter_name}", 1, False),
                  (source, 1, True), (logical, 1, True)]
    return [_bounded(value, styles["body"], width, lines, suffix=suffix) for value, lines, suffix in fields]


def _clip_story(clip: ClipPresentation, layout: ReportLayout, settings: AppSettings,
                width: float, styles: dict[str, ParagraphStyle], height: float) -> Table:
    portrait = layout is ReportLayout.CONTACT_SHEET
    metadata_width = 195.0 if portrait else 252.0
    gallery_width = width - metadata_width - 10
    status_width = 113.0
    warnings, errors = _message_counts(clip.item)
    issue = bool(warnings or errors or clip.item.status.value != "success")
    heading = _table([[_bounded(f"{clip.number:03d} / {clip.item.clip.clip_name}", styles["clip"], width - status_width - 5, suffix=True),
                      _p(clip.item.status.value, styles["issue" if issue else "body"], status_width)]], [width - status_width, status_width])
    left = _metadata(clip, layout, settings, metadata_width, styles)
    right = [_gallery(clip.item, layout, gallery_width, styles), Spacer(1, 1),
             _capture_table(clip.item, layout, gallery_width, styles)]
    content = [heading, Spacer(1, 1), _table([[left, "", right]], [metadata_width, 10, gallery_width]),
               _messages(clip.item, settings, width, styles, layout)]
    natural = sum(flowable.wrap(width, height)[1] for flowable in content)
    if natural > height - 3.5:
        raise ValueError(f"Clip {clip.number} exceeds compact PDF row budget: {natural:.1f} > {height - 3.5:.1f}")
    result = _table([[content]], [width], [height])
    result.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), .7, TEAL),
                               ("TOPPADDING", (0, 0), (-1, -1), 3)]))
    result.report_section = f"클립 {clip.number:03d}"
    return result


def _render(output_path: Path, settings: AppSettings, items: Iterable[ReportItem], summary: BatchSummary, layout: ReportLayout) -> None:
    presentation = _project_report(output_path, settings, tuple(items))
    _register_fonts()
    styles = _styles()
    portrait = layout is ReportLayout.CONTACT_SHEET
    page_size = CONTACT_SHEET_PAGE_SIZE if portrait else DETAIL_PAGE_SIZE
    width = page_size[0] - 2 * MARGIN
    intro_height, row_height = (75.0, 222.0) if portrait else (64.0, 150.0)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document = _ReportDocument(str(output_path), presentation.title, page_size, styles)
    story: list[object] = []
    if not presentation.clips:
        story.extend((_intro(presentation, settings, summary, width, styles, intro_height),
                      _p("보고서에 포함할 클립이 없습니다.", styles["clip"], width)))
    for offset in range(0, len(presentation.clips), 3):
        if offset:
            story.append(PageBreak())
        story.append(_intro(presentation, settings, summary, width, styles, intro_height))
        story.extend(_clip_story(clip, layout, settings, width, styles, row_height)
                     for clip in presentation.clips[offset:offset + 3])
    document.build(story)


def render_pdf(output_path: Path, settings: AppSettings, items: Iterable[ReportItem], summary: BatchSummary) -> None:
    if settings.report.layout is ReportLayout.CLIP_DETAIL:
        render_detail_pdf(output_path, settings, items, summary)
    else:
        render_contact_sheet_pdf(output_path, settings, items, summary)


def render_contact_sheet_pdf(output_path: Path, settings: AppSettings, items: Iterable[ReportItem], summary: BatchSummary) -> None:
    _render(output_path, settings, items, summary, ReportLayout.CONTACT_SHEET)


def render_detail_pdf(output_path: Path, settings: AppSettings, items: Iterable[ReportItem], summary: BatchSummary) -> None:
    _render(output_path, settings, items, summary, ReportLayout.CLIP_DETAIL)
