"""Source-first fixtures for the compact, no-appendix PDF contract.

Run with the project environment to persist source models and pressure PDFs.
The older full-evidence fixtures remain available for image and migration checks.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path
import sys

from frameproof.config.settings import ReportLayout
from frameproof.core.models import AdapterError, AdapterErrorCode, CaptureStatus, ClipStatus
from frameproof.core.report_builder import build_batch_summary
from frameproof.render.pdf_renderer import render_pdf
from pressure_fixtures import IDENTIFIER, PHRASE, images, item, settings


def make_density_cases(root: Path):
    root = root.resolve()
    paths = images(root / "images")
    ordinary = []
    for index in range(1, 11):
        original = item(index, paths, (index - 1) % 4)
        name = f"A001_C{index:03d}_촬영감독_확인용.mov"
        clip = replace(original.clip, clip_id=f"DEBUG-DENSITY-{index:03d}", clip_name=name,
                       logical_clip_name=name, source_path=f"/DEBUG DATA/카메라 A/{name}",
                       codec="ProRes 422 HQ", part_files=(),
                       metadata_raw={"fixture": "DEBUG DATA", "omitted": f"RAW-ONLY-{index:03d}"})
        warning = ("DEBUG DATA: start_timecode_missing - 시작 타임코드 수동 확인 필요",) if index == 2 else ()
        ordinary.append(replace(original, clip=clip, warnings=warning))
    pressure = list(ordinary)
    warning = f"{PHRASE}입니다. 98.7% · 2.3초 · 47,200건 수동 확인이 필요합니다."
    pressure[0] = replace(pressure[0], clip=replace(pressure[0].clip, clip_name=f"{IDENTIFIER}.mov"), warnings=(warning,))
    current = pressure[3]
    error = AdapterError(AdapterErrorCode.DECODE_FAILED, "프레임 디코딩 실패: 소스 미디어를 다시 확인하세요. " + (PHRASE + "입니다. ") * 20,
                         {"debug": "OMITTED-STRUCTURED-DETAIL", "path": "/private/secret/error-detail.mov"})
    captures = list(current.captures)
    captures[1] = replace(captures[1], image_path_exported=paths["missing"], image_path_temp=None)
    captures[2] = replace(captures[2], image_path_exported=paths["corrupt"], status=CaptureStatus.DECODE_FAILED,
                          actual_frame_index=None, actual_seconds=None, actual_timecode=None,
                          actual_timecode_source=None, errors=(error,), warnings=(warning,))
    captures[-1] = replace(captures[-1], status=CaptureStatus.SKIPPED_DUPLICATE, duplicate_of="Start",
                           image_path_exported=None, image_path_temp=None, actual_frame_index=None,
                           actual_seconds=None, actual_timecode=None, actual_timecode_source=None)
    pressure[3] = replace(current, status=ClipStatus.PARTIAL_SUCCESS, captures=tuple(captures),
                          errors=(error,), warnings=(warning, "또 다른 경고", "마지막 경고"))
    huge_name = "예외적으로긴이름_" * 250 + "IDENTITY-FINAL-SUFFIX.mov"
    pressure[5] = replace(pressure[5], clip=replace(pressure[5].clip, clip_name=huge_name,
                         logical_clip_name="논리 클립 " + huge_name, source_path="/private/secret/" + huge_name),
                         warnings=(warning * 40 + "OMITTED-MESSAGE-TAIL",))
    pressure[6] = replace(pressure[6], captures=(), status=ClipStatus.PROBE_FAILED,
                         clip=replace(pressure[6].clip, file_size_bytes=0, duration_seconds=0,
                                      frame_count=None, width=None, height=None, fps_num=None, fps_den=None,
                                      camera_make=None, camera_model=None, start_timecode=None,
                                      end_timecode=None, timecode_source=None, tc_drop_frame=None))
    pressure[8] = replace(pressure[8], clip=replace(pressure[8].clip, logical_clip_name="논리 클립 촬영본 A",
                          part_files=("/private/split/part-01.mov", "/private/split/part-02.mov")),
                          warnings=('문자 <>& "quotes" <b>literal message</b> escaped correctly',))
    return {"nine-clips": tuple(ordinary[:9]), "ten-clips": tuple(ordinary), "pressure-no-companions": tuple(pressure)}


def build_artifacts(root: Path) -> None:
    cases = make_density_cases(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / "DEBUG-DATA-source-fixtures.json").write_text(json.dumps(
        {name: [asdict(entry) for entry in entries] for name, entries in cases.items()},
        ensure_ascii=False, indent=2, default=str) + "\n")
    for name, entries in cases.items():
        for layout in ReportLayout:
            path = root / f"DEBUG-DATA-{name}-{layout.value}.pdf"
            config = settings(path, layout=layout)
            if name == "pressure-no-companions":
                config = replace(config, output=replace(config.output, write_csv=False, write_json=False))
            render_pdf(path, config, entries, build_batch_summary(entries))
            print(path)


if __name__ == "__main__":
    build_artifacts(Path(sys.argv[1]))
