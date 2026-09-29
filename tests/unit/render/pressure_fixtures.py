"""Deterministic, source-model PDF pressure fixtures; runnable without media probing."""
from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

from frameproof.config.settings import AppSettings, CaptureSettings, InputSettings, OutputSettings, ReportSettings
from frameproof.core.models import (
    AdapterError, AdapterErrorCode, CapturePoint, CaptureStatus, ClipInfo, ClipStatus,
    ReportItem, TimecodeSource, capture_labels_for_middle_count,
)
from frameproof.core.report_builder import build_batch_summary

TITLE = "DEBUG DATA - 무선 카메라 제어 및 현장 스크립트 기록 통합 검증 보고서"
PHRASE = "촬영감독과 스크립터가 동시에 확인해야 하는 상태값"
IDENTIFIER = "A-CAM_take-2026_05_18_FINAL_v003"


def images(root: Path) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, size in {"landscape": (960, 540), "portrait": (540, 960), "panorama": (1600, 200),
                       "tiny": (1, 1), "large": (4200, 2800), "rotated": (720, 360)}.items():
        path = root / f"DEBUG-DATA-{name}.jpg"
        picture = Image.new("RGB", size, "#667d82")
        draw = ImageDraw.Draw(picture)
        w, h = size
        edge = max(1, min(w, h) // 12)
        draw.rectangle((0, 0, max(0, w - 1), max(0, h - 1)), outline="white", width=edge)
        draw.rectangle((0, 0, w // 4, h // 3), fill="red")
        draw.rectangle((w * 3 // 4, h * 2 // 3, max(0, w - 1), max(0, h - 1)), fill="yellow")
        draw.text((w // 3, h // 2), name.upper(), fill="white")
        exif = Image.Exif()
        if name == "rotated":
            exif[274] = 6
        picture.save(path, exif=exif)
        results[name] = str(path)
    corrupt = root / "DEBUG-DATA-corrupt.jpg"
    corrupt.write_bytes(b"not an image")
    results["corrupt"] = str(corrupt)
    results["missing"] = str(root / "DEBUG-DATA-missing.jpg")
    return results


def item(index: int, paths: dict[str, str], middle_count: int = 3) -> ReportItem:
    suffix = f"TAIL-{index:03d}"
    clip = ClipInfo(
        clip_id=f"clip-{index:03d}", clip_name=f"{IDENTIFIER}_촬영감독_확인용_원본_{suffix}.mov",
        logical_clip_name=f"논리 클립 {suffix}", source_path=f"/private/production/테스트 데이터/{suffix}.mov",
        part_files=(f"/private/production/part-one/{suffix}.mov", f"/private/production/part-two/{suffix}.mov"),
        container="QuickTime", codec=None, file_size_bytes=47200000, duration_seconds=2.3,
        frame_count=72, fps_num=30000, fps_den=1001, width=1920, height=1080,
        camera_make="카메라 제작사", camera_model="시네마 모델", reel="A001", camera_id="A-CAM",
        start_timecode="01:00:00;00", end_timecode="01:00:02;09",
        timecode_source=TimecodeSource.CONTAINER_METADATA, tc_drop_frame=False,
        metadata_raw={"fixture": "DEBUG DATA / 테스트 데이터", "phrase": PHRASE,
                      "numeric": ["98.7%", "2.3초", "47,200건", 0, False, None, {}, []],
                      "escaped": '<>& "quotes"\n<b>literal markup</b>',
                      "url": "https://example.test/reports/" + IDENTIFIER * 3,
                      "email": "script-supervisor@example-production.test",
                      "nested": {"source_path": f"/private/production/raw/{suffix}.mov", "tail": "RAW-NESTED-END"}},
    )
    labels = capture_labels_for_middle_count(middle_count)
    picture_names = ("landscape", "portrait", "panorama", "rotated", "large")
    sources = tuple(TimecodeSource)
    captures = tuple(CapturePoint(
        label=label, requested_ratio=i / (len(labels) - 1), requested_frame_index=i * 12,
        requested_seconds=i * 0.400, actual_frame_index=i * 12 + 1, actual_seconds=i * 0.400 + 0.033,
        actual_timecode=f"01:00:0{i};01" if i != 3 else "elapsed:1.233s",
        actual_timecode_source=sources[i % len(sources)], image_path_temp=paths["corrupt"],
        image_path_exported=paths[picture_names[i]],
    ) for i, label in enumerate(labels))
    return ReportItem(clip, captures, ClipStatus.SUCCESS, "DEBUG DATA synthetic-adapter")


def make_cases(root: Path) -> dict[str, tuple[ReportItem, ...]]:
    paths = images(root / "images")
    full = (item(1, paths), item(2, paths))
    edges = []
    for middle in range(4):
        current = item(10 + middle, paths, middle)
        caps = list(current.captures)
        names = ("tiny", "missing", "corrupt", "rotated", "panorama")
        caps = [replace(capture, image_path_exported=paths[names[i]]) for i, capture in enumerate(caps)]
        caps[-1] = replace(caps[-1], status=CaptureStatus.SKIPPED_DUPLICATE, duplicate_of="Start",
                           actual_frame_index=None, actual_seconds=None, actual_timecode=None,
                           actual_timecode_source=None, image_path_exported=None, image_path_temp=None)
        edges.append(replace(current, captures=tuple(caps)))
    edges.append(replace(item(14, paths), captures=()))
    edges.append(replace(item(15, paths), captures=tuple(
        replace(c, image_path_exported=None, image_path_temp=None, status=CaptureStatus.DECODE_FAILED,
                actual_frame_index=None, actual_seconds=None) for c in item(15, paths).captures)))
    warning_item = replace(item(20, paths), warnings=("DEBUG DATA: success with warning - start_timecode_missing",))
    issues = [warning_item]
    for index in range(1, 17):
        current = item(20 + index, paths, 0)
        status = tuple(ClipStatus)[1 + (index - 1) % (len(ClipStatus) - 1)]
        warning = f"DEBUG DATA {index}: {PHRASE}입니다. 다음 테이크 전에 수동 확인이 필요합니다."
        warnings = tuple(f"{warning} / 메시지 {n} ITEM-WARNING-{index}-{n}" for n in range(8))
        raw = {f"raw-key-{n:02d}": f"값 {n}" for n in range(15)}
        raw["zz-tail"] = f"RAW-COLLECTION-END-{index}"
        if index == 1:
            warnings += ((PHRASE + "입니다. ") * 240 + "LONG-MESSAGE-FINAL-SENTINEL",)
            raw["long-value"] = (PHRASE + "을 기록합니다. ") * 240 + "LONG-RAW-FINAL-SENTINEL"
        error = AdapterError(AdapterErrorCode.DECODE_FAILED, f"{warning} ERROR-MESSAGE-END-{index}",
                             {"nested": {"false": False, "missing": None, "list": [1, "ERROR-DETAIL-END"]}})
        capture = replace(current.captures[0], warnings=warnings[:8] + ("CAPTURE-WARNING-END",), errors=(error,))
        issues.append(replace(current, status=status, warnings=warnings + (f"ITEM-WARNING-END-{index}",),
                              errors=(error,), captures=(capture, current.captures[-1]),
                              clip=replace(current.clip, metadata_raw=raw)))
    pagination = tuple(replace(item(50 + i, paths, 1), captures=()) for i in range(5))
    return {"korean-full-evidence": full, "issues-overflow": tuple(issues),
            "capture-and-image-edges": tuple(edges), "pagination-and-paths": pagination}


def settings(path: Path, **report_options: object) -> AppSettings:
    return AppSettings(
        input=InputSettings((Path("/private/production/테스트 데이터/첫째 입력.mov"), Path("/private/production/둘째 입력"))),
        capture=CaptureSettings(middle_count=3), output=OutputSettings(pdf_path=path),
        report=ReportSettings(project_name=TITLE, **report_options),
    )


def build_artifacts(root: Path, *, sources_only: bool = False) -> None:
    cases = make_cases(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / "DEBUG-DATA-source-fixtures.json").write_text(json.dumps(
        {name: [asdict(entry) for entry in entries] for name, entries in cases.items()},
        ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    if sources_only:
        return
    from frameproof.render.pdf_renderer import render_pdf
    for name, entries in cases.items():
        for layout in ("contact_sheet", "detail"):
            path = root / f"DEBUG-DATA-{name}-{'contact' if layout == 'contact_sheet' else 'detail'}.pdf"
            render_pdf(path, settings(path, layout=layout), entries, build_batch_summary(entries))
            print(path)


def inspect_artifacts(root: Path) -> None:
    """Persist extraction, font inventory, page rasters and overview sheets."""
    inventory = []
    for path in sorted(root.glob("DEBUG-DATA-*.pdf")):
        info = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True).stdout
        fonts = subprocess.run(["pdffonts", str(path)], check=True, capture_output=True, text=True).stdout
        path.with_suffix(".info.txt").write_text(info)
        path.with_suffix(".fonts.txt").write_text(fonts)
        for option, suffix in [("-layout", ".txt"), ("-raw", ".raw.txt"), ("-bbox-layout", ".bbox.html")]:
            subprocess.run(["pdftotext", option, str(path), str(path.with_suffix(suffix))], check=True)
        bbox = ET.parse(path.with_suffix(".bbox.html"))
        violations = []
        for page_number, page in enumerate(bbox.findall(".//{*}page"), 1):
            width, height = float(page.attrib["width"]), float(page.attrib["height"])
            for word in page.findall(".//{*}word"):
                x0, x1, y0, y1 = (float(word.attrib[k]) for k in ("xMin", "xMax", "yMin", "yMax"))
                if x0 < 40 or x1 > width - 40 or y0 < 12 or y1 > height - 12:
                    violations.append({"page": page_number, "text": word.text, "bounds": [x0, y0, x1, y1]})
        raster_dir = root / "raster" / path.stem
        raster_dir.mkdir(parents=True, exist_ok=True)
        for old in raster_dir.glob("page-*.png"):
            old.unlink()
        for old in root.glob(f"{path.stem}-sheet-*.png"):
            old.unlink()
        scale = "700" if "issues-overflow" in path.name else "1300"
        subprocess.run(["pdftoppm", "-scale-to", scale, "-png", str(path), str(raster_dir / "page")],
                       check=True, capture_output=True)
        pages = sorted(raster_dir.glob("page-*.png"), key=lambda p: int(p.stem.rsplit("-", 1)[1]))
        for offset in range(0, len(pages), 20):
            selected = pages[offset:offset + 20]
            sheet = Image.new("RGB", (5 * 220, ((len(selected) + 4) // 5) * 320), "#e3e7e7")
            draw = ImageDraw.Draw(sheet)
            for index, png in enumerate(selected):
                with Image.open(png) as picture:
                    picture.thumbnail((208, 294))
                    x, y = (index % 5) * 220 + 6, (index // 5) * 320 + 20
                    sheet.paste(picture, (x, y))
                    draw.text((x, y - 15), f"Page {offset + index + 1}", fill="black")
            sheet.save(root / f"{path.stem}-sheet-{offset // 20 + 1:02d}.png")
        inventory.append({"pdf": str(path), "pages": len(pages), "bbox_violations": violations,
                          "font_faces": [line for line in fonts.splitlines() if "DataHandlerSans" in line]})
        print(path.name, len(pages), "pages; bounds violations:", len(violations))
    (root / "artifact-inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build_artifacts(Path(sys.argv[1]), sources_only="--sources-only" in sys.argv)
    if "--inspect" in sys.argv:
        inspect_artifacts(Path(sys.argv[1]))
