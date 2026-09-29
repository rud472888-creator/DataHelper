from __future__ import annotations

from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

import pytest

from frameproof.config.settings import PathDisplayMode, ReportLayout
from frameproof.core.models import BatchStatus, BatchSummary, CaptureStatus
from frameproof.core.report_builder import build_batch_summary
from frameproof.render import pdf_renderer as renderer
from frameproof.output.manifest_writer import build_manifest_rows
from density_fixtures import make_density_cases
from pressure_fixtures import IDENTIFIER, PHRASE, TITLE, make_cases, settings


@pytest.fixture(scope="module")
def cases(tmp_path_factory):
    return make_cases(tmp_path_factory.mktemp("pressure-images"))


@pytest.fixture(scope="module")
def density(tmp_path_factory):
    return make_density_cases(tmp_path_factory.mktemp("density-images"))


def pdf_text(path: Path, option="-raw") -> str:
    executable = shutil.which("pdftotext")
    if executable is None:
        pytest.skip("Poppler pdftotext is needed for PDF extraction checks")
    return subprocess.run([executable, option, str(path), "-"], check=True, capture_output=True, text=True).stdout


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


def page_count(path: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", path.read_bytes()))


def assert_bounds(path: Path):
    text = pdf_text(path, "-bbox")
    pages = ET.fromstring(text).findall(".//{*}page")
    for page in pages:
        width, height = float(page.attrib["width"]), float(page.attrib["height"])
        for word in page.findall(".//{*}word"):
            x0, x1, y0, y1 = [float(word.attrib[key]) for key in ("xMin", "xMax", "yMin", "yMax")]
            assert 39 <= x0 <= x1 <= width - 39, word.text
            assert 12 <= y0 <= y1 <= height - 12, word.text


@pytest.mark.parametrize("layout", list(ReportLayout))
@pytest.mark.parametrize("count", [9, 10])
def test_three_complete_clips_per_page_including_first_and_partial_last(tmp_path, density, layout, count):
    items = density["ten-clips"][:count]
    before = [asdict(item) for item in items]
    path = tmp_path / "DEBUG-DATA-density.pdf"
    renderer.render_pdf(path, settings(path, layout=layout), iter(items), build_batch_summary(items))
    text = pdf_text(path)
    pages = text.split("\f")[:-1]
    assert page_count(path) == len(pages) == (count + 2) // 3
    assert "부록" not in text and "이슈 색인" not in text and "RAW-ONLY" not in text
    for index, page in enumerate(pages):
        expected = items[index * 3:index * 3 + 3]
        assert re.findall(r"ID (DEBUG-DENSITY-\d+)", page) == [item.clip.clip_id for item in expected]
        assert all(compact(item.clip.clip_name) in compact(page) for item in expected)
        actual_tcs = Counter(c.actual_timecode for item in expected for c in item.captures if c.actual_timecode)
        assert all(page.count(tc) >= amount for tc, amount in actual_tcs.items())
        for value in ["30000/1001", "29.970 fps", "ProRes 422 HQ", "47,200,000 bytes", "카메라 제작사", "시네마 모델",
                      "A-CAM", "A001", "01:00:00;00", "01:00:02;09", "아니요 / false"]:
            assert compact(value) in compact(page)
        assert f"클립 {index * 3 + 1:03d} / 클립 {min(index * 3 + 3, count):03d}" in page or len(expected) == 1
    assert "start_timecode_missing" in text and "시작 타임코드 수동 확인 필요" in text
    assert [asdict(item) for item in items] == before
    assert_bounds(path)


@pytest.mark.parametrize("layout", list(ReportLayout))
def test_pdf_capture_order_positions_and_states_match_manifest_including_zero_capture(tmp_path, cases, layout):
    items = cases["capture-and-image-edges"]
    path = tmp_path / "DEBUG-DATA-sequence.pdf"
    renderer.render_pdf(path, settings(path, layout=layout), items, build_batch_summary(items))
    text = pdf_text(path)
    identities = list(re.finditer(r"ID (clip-\d+)", text))
    observed = []
    for index, match in enumerate(identities):
        item = items[index]
        segment = text[match.end():identities[index + 1].start() if index + 1 < len(identities) else len(text)]
        if not item.captures:
            assert "캡처 지점: 0" in segment
            observed.append((match[1], ""))
            continue
        timing = segment.split("캡처 / 상태", 1)[1]
        labels = re.findall(r"^(Start|Mid[123]|End)(?:\s+(?:정상|실패|미완|중복))?(?=\s|$)", timing, re.MULTILINE)
        assert labels[:len(item.captures)] == [c.label for c in item.captures]
        observed.extend((match[1], label) for label in labels[:len(item.captures)])
        # Real actual/requested values are deliberately different in the source.
        for capture in item.captures:
            if capture.actual_seconds is not None:
                assert f"{capture.actual_seconds:.3f} s" in timing
            if capture.requested_seconds is not None:
                assert f"{capture.requested_seconds:.3f} s" in timing
            if capture.actual_timecode:
                assert capture.actual_timecode in timing
        if item.captures[-1].duplicate_of:
            assert "중복" in timing and "Start" in timing
    assert observed == [(row["clip_id"], row["capture_label"]) for row in build_manifest_rows(items)]
    assert "미리보기 없음" in text and "이미지 읽기 실패" in text
    assert "중간 캡처 미설정" in text or layout is ReportLayout.CLIP_DETAIL
    assert_bounds(path)


@pytest.mark.parametrize("layout", list(ReportLayout))
def test_bounded_main_body_pressure_keeps_failures_messages_zero_and_korean(tmp_path, density, layout):
    items = density["pressure-no-companions"]
    original = [asdict(item) for item in items]
    path = tmp_path / "DEBUG-DATA-pressure.pdf"
    config = settings(path, layout=layout)
    config = replace(config, output=replace(config.output, write_csv=False, write_json=False))
    renderer.render_pdf(path, config, items, build_batch_summary(items))
    text = pdf_text(path)
    flattened = compact(text)
    assert page_count(path) == 4
    for expected in [TITLE, PHRASE, IDENTIFIER, "IDENTITY-FINAL-SUFFIX.mov", "decode_failed", "오류 [Mid2]",
                     "프레임 디코딩 실패", "경고 [Mid2]", "외 3건", "외 1건", "partial_success", "probe_failed",
                     "98.7%", "2.3초", "47,200건", "0 bytes", "0.000 s", "아니요 / false", "캡처 지점: 0",
                     "논리 클립 촬영본 A", "분할 2개", '<b>literal message</b>', "축약"]:
        assert compact(expected) in flattened, expected
    for omitted in ["RAW-ONLY", "OMITTED-STRUCTURED-DETAIL", "/private/secret", "OMITTED-MESSAGE-TAIL", "CSV", "JSON", "부록"]:
        assert omitted not in text
    assert [asdict(item) for item in items] == original
    assert_bounds(path)


@pytest.mark.parametrize("layout", list(ReportLayout))
@pytest.mark.parametrize("summary", [True, False])
@pytest.mark.parametrize("emphasis", [True, False])
def test_flags_keep_inline_failures_and_never_add_pages(tmp_path, density, layout, summary, emphasis):
    items = density["pressure-no-companions"][:6]
    path = tmp_path / "DEBUG-DATA-flags.pdf"
    config = settings(path, layout=layout, include_summary_page=summary, include_failed_section=emphasis)
    renderer.render_pdf(path, config, items, build_batch_summary(items))
    text = pdf_text(path)
    assert page_count(path) == 2
    assert compact(TITLE) in compact(text)
    assert "DEBUG-DENSITY-001" in text.split("\f")[0]
    assert "오류 [Mid2] decode_failed" in text
    assert "partial_success" in text
    assert ("배치 partial_success" in text) is summary
    assert ("| 확인 필요" in text) is emphasis
    assert "부록" not in text and "이슈 색인" not in text
    assert_bounds(path)


@pytest.mark.parametrize("mode", list(PathDisplayMode))
@pytest.mark.parametrize("layout", list(ReportLayout))
def test_path_policy_precedes_abbreviation_and_covers_message_references_without_mutation(tmp_path, density, mode, layout):
    current = density["nine-clips"][0]
    path = tmp_path / "DEBUG-DATA-path-policy.pdf"
    source = "/private/secret/clip.mov"
    exported = current.captures[0].image_path_exported
    current = replace(current, clip=replace(current.clip, source_path=source),
                      warnings=(f"미디어 경로 {source}; 스틸 {exported}",))
    before = asdict(current)
    renderer.render_pdf(path, settings(path, layout=layout, path_display=mode), (current,), build_batch_summary((current,)))
    text = pdf_text(path)
    if mode is PathDisplayMode.FULL:
        assert source in text
    else:
        assert "/private/secret" not in text
        assert str(Path(exported).parent) not in text
    assert ("hidden (clip.mov)" in text) is (mode is PathDisplayMode.HIDDEN)
    assert "clip.mov" in text
    assert current.captures[0].image_path_temp not in text
    assert before == asdict(current)
    assert_bounds(path)


@pytest.mark.parametrize("layout", list(ReportLayout))
def test_superseded_raw_and_detail_payloads_are_not_embedded(tmp_path, cases, layout):
    items = cases["issues-overflow"][:3]
    path = tmp_path / "DEBUG-DATA-compact-omissions.pdf"
    renderer.render_pdf(path, settings(path, layout=layout), items, build_batch_summary(items))
    text = pdf_text(path)
    assert page_count(path) == 1
    assert "decode_failed" in text and "축약" in text and "외 " in text
    for sentinel in ["LONG-RAW-FINAL-SENTINEL", "ERROR-DETAIL-END", "RAW-COLLECTION-END", "raw-key-14", "부록", "원시 메타데이터"]:
        assert sentinel not in text
    assert "경고가 있는 클립: 3" in text
    assert_bounds(path)


@pytest.mark.parametrize("layout", list(ReportLayout))
def test_empty_report_and_provided_summary_mismatch_remain_explicit(tmp_path, layout):
    path = tmp_path / "DEBUG-DATA-empty.pdf"
    summary = BatchSummary(99, 97, 1, 0, 1, 0, BatchStatus.PARTIAL_SUCCESS)
    renderer.render_pdf(path, settings(path, layout=layout), (), summary)
    text = compact(pdf_text(path))
    assert "보고서에포함할클립이없습니다." in text
    assert "수록범위가다릅니다" in text
    assert "99" in text and "97" in text
    assert page_count(path) == 1
    assert_bounds(path)


def test_image_precedence_orientation_fit_and_corrupt_placeholder(tmp_path, cases):
    renderer._register_fonts()
    current = cases["korean-full-evidence"][0]
    exported = Path(current.captures[0].image_path_exported)
    assert renderer._display_image_path(current.captures[0]) == exported
    image, reason = renderer._preview(current.captures[0], 150, 150, renderer._styles())
    assert reason is None
    assert image.drawWidth / image.drawHeight == pytest.approx(16 / 9)
    rotated = Path(current.captures[3].image_path_exported)
    assert renderer._fit_image(rotated, 150, 150) == pytest.approx((75, 150))
    broken = replace(current.captures[0], image_path_exported=current.captures[0].image_path_temp)
    image, reason = renderer._preview(broken, 150, 150, renderer._styles())
    assert reason == "이미지 읽기 실패"
    assert broken.status is CaptureStatus.SUCCESS
    temp_only = replace(current.captures[0], image_path_exported=None, image_path_temp=str(exported))
    assert renderer._display_image_path(temp_only) == exported


def test_representative_middle_selection_and_ties_keep_tuple_order(cases):
    no_mid = cases["capture-and-image-edges"][0]
    assert renderer._start_middle_end_captures(no_mid.captures)[1] is None
    full = cases["korean-full-evidence"][0]
    assert renderer._start_middle_end_captures(full.captures)[1].label == "Mid2"
    two = cases["capture-and-image-edges"][2]
    caps = list(two.captures)
    caps[1] = replace(caps[1], requested_ratio=.25)
    caps[2] = replace(caps[2], requested_ratio=.75)
    assert renderer._start_middle_end_captures(tuple(caps))[1].label == "Mid1"


def test_dispatch_keeps_public_api_and_output_layout(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(renderer, "render_contact_sheet_pdf", lambda *args: calls.append("contact"))
    monkeypatch.setattr(renderer, "render_detail_pdf", lambda *args: calls.append("detail"))
    path = tmp_path / "debug.pdf"
    for layout in ReportLayout:
        renderer.render_pdf(path, settings(path, layout=layout), (), build_batch_summary(()))
    assert calls == ["contact", "detail"]


@pytest.mark.parametrize("layout", list(ReportLayout))
def test_bundled_fonts_are_embedded_and_page_dimensions_are_preserved(tmp_path, density, layout):
    if shutil.which("pdffonts") is None:
        pytest.skip("Poppler pdffonts is needed for embedding inspection")
    path = tmp_path / "DEBUG-DATA-fonts.pdf"
    items = density["nine-clips"][:3]
    renderer.render_pdf(path, settings(path, layout=layout), items, build_batch_summary(items))
    fonts = subprocess.run(["pdffonts", str(path)], check=True, capture_output=True, text=True).stdout
    lines = [line for line in fonts.splitlines() if "DataHandlerSans" in line]
    assert len(lines) >= 2
    assert all("yes yes yes" in line for line in lines)
    info = subprocess.run(["pdfinfo", str(path)], check=True, text=True, capture_output=True).stdout
    assert TITLE in info
    assert ("595.276 x 841.89" if layout is ReportLayout.CONTACT_SHEET else "792 x 612") in info
    for name in ["DataHandlerSans-Regular.ttf", "DataHandlerSans-Bold.ttf", "OFL.txt"]:
        assert (renderer.FONT_DIRECTORY / name).is_file()
    assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}", pdf_text(path))
