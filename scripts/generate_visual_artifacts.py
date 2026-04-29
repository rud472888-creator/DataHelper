from __future__ import annotations
# ruff: noqa: E402

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    candidate_text = str(candidate)
    if candidate_text not in sys.path:
        sys.path.insert(0, candidate_text)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image  # noqa: E402

from frameproof.config.settings import AppSettings  # noqa: E402
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
)  # noqa: E402
from frameproof.core.progress_events import ProgressRow  # noqa: E402
from frameproof.gui.dependency_dialog import DependencyDialog  # noqa: E402
from frameproof.gui.main_window import MainWindow  # noqa: E402
from frameproof.gui.settings_store import GuiStoredSettings, SettingsStore  # noqa: E402
from frameproof.render import render_pdf  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Stage 5 visual verification artifacts.")
    parser.add_argument(
        "--output-dir",
        default="artifacts/stage-05",
        help="Directory where PDFs, screenshots, and the verification report will be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    pdf_dir = output_dir / "pdf"
    gui_dir = output_dir / "gui"
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    gui_dir.mkdir(parents=True, exist_ok=True)

    report_lines = [
        "Stage 5 visual artifact generation",
        f"Output directory: {output_dir}",
        "",
    ]

    items = _sample_items(output_dir)
    summary = BatchSummary(
        total_clips=3,
        success_count=1,
        partial_success_count=1,
        probe_failed_count=1,
        decode_failed_count=0,
        skipped_count=0,
        status=BatchStatus.PARTIAL_SUCCESS,
    )

    layout_b_path = pdf_dir / "layout-b-stage5.pdf"
    render_pdf(layout_b_path, _sample_settings(layout_b_path, layout="contact_sheet"), items, summary)
    report_lines.append(f"Generated PDF artifact: {layout_b_path}")

    layout_a_path = pdf_dir / "layout-a-stage5.pdf"
    render_pdf(layout_a_path, _sample_settings(layout_a_path, layout="detail"), items, summary)
    report_lines.append(f"Generated PDF artifact: {layout_a_path}")

    if _qt_runtime_available():
        report_lines.extend(_generate_gui_artifacts(gui_dir, layout_b_path))
        report_lines.append(f"Generated GUI artifact directory: {gui_dir}")
    else:
        report_lines.append("GUI screenshots skipped: the local Qt runtime is not executable on this host.")

    report_path = output_dir / "verification-summary.txt"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(report_path)
    return 0


def _sample_settings(pdf_path: Path, *, layout: str) -> AppSettings:
    return AppSettings.from_mapping(
        {
            "input": {"paths": ["/show/day01", "/show/day02"]},
            "capture": {"middle_count": 2},
            "report": {"layout": layout, "path_display": "basename"},
            "output": {"pdf_path": str(pdf_path)},
        }
    )


def _sample_items(output_dir: Path) -> tuple[ReportItem, ...]:
    image_dir = output_dir / "sample-images"
    image_dir.mkdir(parents=True, exist_ok=True)
    start_png = image_dir / "start.png"
    mid_png = image_dir / "mid.png"
    end_png = image_dir / "end.png"
    for path, color in ((start_png, (210, 170, 85)), (mid_png, (88, 126, 188)), (end_png, (104, 156, 112))):
        Image.new("RGB", (640, 360), color=color).save(path)

    partial_item = ReportItem(
        clip=_sample_clip(
            clip_id="clip-1",
            clip_name="A001_C001.mov",
            source_path="/show/day01/A001_C001.mov",
            metadata_raw={"scene": "Day01", "iso": 800},
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
                actual_timecode_source=TimecodeSource.CONTAINER_METADATA,
                image_path_temp=str(mid_png),
                status=CaptureStatus.SUCCESS,
                warnings=("fallback tc",),
            ),
            CapturePoint(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=47,
                requested_seconds=1.958,
                actual_frame_index=47,
                actual_seconds=1.958,
                actual_timecode="01:00:01:23",
                actual_timecode_source=TimecodeSource.ELAPSED_FALLBACK,
                image_path_temp=str(end_png),
                status=CaptureStatus.METADATA_INCOMPLETE,
                warnings=("elapsed fallback",),
            ),
        ),
        status=ClipStatus.PARTIAL_SUCCESS,
        adapter_name="ffmpeg",
        warnings=("clip warning",),
        errors=(),
    )

    success_item = ReportItem(
        clip=_sample_clip(
            clip_id="clip-2",
            clip_name="A002_C014.mov",
            source_path="/show/day01/A002_C014.mov",
            metadata_raw={"scene": "Day01", "iso": 1250},
        ),
        captures=(
            CapturePoint(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                requested_seconds=0.0,
                actual_frame_index=0,
                actual_seconds=0.0,
                actual_timecode="02:10:00:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(start_png),
                status=CaptureStatus.SUCCESS,
            ),
            CapturePoint(
                label="Mid1",
                requested_ratio=0.5,
                requested_frame_index=96,
                requested_seconds=4.0,
                actual_frame_index=96,
                actual_seconds=4.0,
                actual_timecode="02:10:04:00",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(mid_png),
                status=CaptureStatus.SUCCESS,
            ),
            CapturePoint(
                label="End",
                requested_ratio=1.0,
                requested_frame_index=191,
                requested_seconds=7.958,
                actual_frame_index=191,
                actual_seconds=7.958,
                actual_timecode="02:10:07:23",
                actual_timecode_source=TimecodeSource.NATIVE_ADAPTER,
                image_path_temp=str(end_png),
                status=CaptureStatus.SUCCESS,
            ),
        ),
        status=ClipStatus.SUCCESS,
        adapter_name="ffmpeg",
    )

    failed_item = ReportItem(
        clip=_sample_clip(
            clip_id="clip-3",
            clip_name="B010_R001.braw",
            source_path="/show/day02/B010_R001.braw",
            format_family=FormatFamily.BRAW,
            metadata_raw={"scene": "Day02", "iso": 1600},
        ),
        captures=(),
        status=ClipStatus.PROBE_FAILED,
        adapter_name="braw",
        errors=(AdapterError(code=AdapterErrorCode.PROBE_FAILED, message="probe failed"),),
    )

    return (partial_item, success_item, failed_item)


def _sample_clip(
    *,
    clip_id: str,
    clip_name: str,
    source_path: str,
    format_family: FormatFamily = FormatFamily.STANDARD,
    metadata_raw: dict[str, object],
) -> ClipInfo:
    return ClipInfo(
        clip_id=clip_id,
        clip_name=clip_name,
        source_path=source_path,
        format_family=format_family,
        container="mov" if format_family is FormatFamily.STANDARD else "braw",
        codec="prores" if format_family is FormatFamily.STANDARD else "braw",
        frame_count=192,
        duration_seconds=8.0,
        fps_num=24,
        fps_den=1,
        width=1920,
        height=1080,
        start_timecode="01:00:00:00",
        end_timecode="01:00:07:23",
        metadata_raw=metadata_raw,
    )


def _generate_gui_artifacts(output_dir: Path, pdf_path: Path) -> list[str]:
    from PySide6.QtCore import QObject, Signal

    class _StaticController(QObject):
        progress_event = Signal(object)
        batch_finished = Signal(object)
        batch_failed = Signal(str)
        running_changed = Signal(bool)

        def start_batch(self, settings: object) -> None:
            del settings

        def cancel(self) -> None:
            return None

    from frameproof.gui.app import create_application
    from frameproof.gui.view_state import BannerState, ProgressRowState

    store = SettingsStore(output_dir / "stage5-gui.ini")
    store.save(
        GuiStoredSettings(
            source_paths=("/show/day01", "/show/day02/B010_R001.braw"),
            output_pdf_path=str(pdf_path),
            project_name="Stage 5 Artifact Run",
            middle_count=2,
            layout="contact_sheet",
            export_stills=True,
        )
    )
    app = create_application()
    window = MainWindow(store, _StaticController())
    requested_artifact_size = (1280, 860)
    requested_compact_size = (1024, 720)
    summary_lines = []
    summary_lines.extend(_probe_widget_geometry(app, window, requested_compact_size, label="Main window 1024x720"))
    summary_lines.extend(_probe_widget_geometry(app, window, requested_artifact_size, label="Main window 1280x860"))
    _save_widget_screenshot(window, output_dir / "gui-empty.png")

    window._upsert_row(
        ProgressRowState.from_progress_row(
            ProgressRow(
                candidate_id="clip-1",
                clip_name="A001_C001.mov",
                format_family=FormatFamily.STANDARD,
                probe="success",
                capture="partial",
                pdf="included",
                warning="fallback tc | elapsed fallback",
                report_status=ClipStatus.PARTIAL_SUCCESS,
            )
        ),
        0,
    )
    window._set_banner(
        BannerState(
            "warning",
            "Batch finished with partial results.",
            "Counts: total=3 success=1 partial=1 failed=1 skipped=0\nPDF: " + str(pdf_path),
        )
    )
    app.processEvents()
    _save_widget_screenshot(window, output_dir / "gui-partial.png")

    window._set_banner(
        BannerState("error", "Cannot start batch.", "Select an output PDF path.")
    )
    app.processEvents()
    _save_widget_screenshot(window, output_dir / "gui-error.png")

    dialog = DependencyDialog(store, store.load(), window)
    dialog.resize(1180, 520)
    dialog.show()
    app.processEvents()
    summary_lines.extend(_probe_widget_geometry(app, dialog, (1180, 520), label="Dependency dialog 1180x520"))
    _save_widget_screenshot(dialog, output_dir / "dependency-dialog.png")
    dialog.close()
    window.close()
    return summary_lines


def _probe_widget_geometry(
    app: object, widget: object, requested_size: tuple[int, int], *, label: str
) -> list[str]:
    width, height = requested_size
    assert hasattr(widget, "resize")
    assert hasattr(widget, "show")
    assert hasattr(widget, "size")
    assert hasattr(widget, "minimumSizeHint")
    assert hasattr(app, "processEvents")
    widget.resize(width, height)
    widget.show()
    app.processEvents()
    actual_size = widget.size()
    minimum_size = widget.minimumSizeHint()
    return [
        (
            f"{label}: requested={width}x{height} "
            f"actual={actual_size.width()}x{actual_size.height()} "
            f"minimumSizeHint={minimum_size.width()}x{minimum_size.height()}"
        )
    ]


def _save_widget_screenshot(widget: object, path: Path) -> None:
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QImage, QPainter

    assert hasattr(widget, "size")
    assert hasattr(widget, "render")
    image = QImage(widget.size(), QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(0xFFFFFFFF)
    painter = QPainter(image)
    widget.render(painter, QPoint())
    painter.end()
    image.save(str(path))


def _qt_runtime_available() -> bool:
    completed = subprocess.run(
        [sys.executable, "-c", "from PySide6.QtWidgets import QApplication; app = QApplication([]); print('ok')"],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )
    return completed.returncode == 0 and "ok" in completed.stdout


if __name__ == "__main__":
    raise SystemExit(main())
