from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

from . import __version__
from .config.settings import AppSettings, ReportLayout
from .core.batch_runner import BatchRunOutcome, run_batch
from .core.models import AdapterErrorCode, ClipStatus
from .core.report_builder import BatchReport
from .settings import collect_runtime_snapshot

PIPELINE_DESCRIPTION = "Frame Proof standard video CLI pipeline."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="frameproof", description=PIPELINE_DESCRIPTION)
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Show the package version and exit.",
    )
    parser.add_argument(
        "--input",
        action="append",
        dest="inputs",
        metavar="PATH",
        help="Input file or directory. Repeat to provide multiple roots.",
    )
    parser.add_argument(
        "--recursive",
        dest="recursive",
        action="store_true",
        default=True,
        help="Recurse into input directories (default).",
    )
    parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="Do not recurse into input directories.",
    )
    parser.add_argument(
        "--middle-count",
        type=int,
        default=3,
        choices=(0, 1, 2, 3),
        help="Number of middle capture points to request.",
    )
    parser.add_argument(
        "--layout",
        default=ReportLayout.CONTACT_SHEET.value,
        choices=(ReportLayout.CONTACT_SHEET.value, ReportLayout.CLIP_DETAIL.value),
        help="PDF layout to render: contact_sheet (Layout B) or detail (Layout A).",
    )
    parser.add_argument(
        "--output",
        metavar="PDF_PATH",
        help="Output PDF path.",
    )
    parser.add_argument(
        "--csv",
        metavar="CSV_PATH",
        help="Optional CSV manifest path. Defaults to the PDF stem with .csv.",
    )
    parser.add_argument(
        "--json",
        metavar="JSON_PATH",
        help="Optional JSON manifest path. Defaults to the PDF stem with .json.",
    )
    parser.add_argument(
        "--export-stills",
        action="store_true",
        help="Export PNG stills for successful capture points. Off by default.",
    )
    parser.add_argument(
        "--stills-dir",
        metavar="PATH",
        help="Output directory for exported PNG stills. Required with --export-stills.",
    )
    parser.add_argument(
        "--project-name",
        metavar="NAME",
        help="Optional project name used in the PDF header.",
    )
    parser.add_argument(
        "--ffmpeg-path",
        default="ffmpeg",
        help="Override the ffmpeg executable path.",
    )
    parser.add_argument(
        "--ffprobe-path",
        default="ffprobe",
        help="Override the ffprobe executable path.",
    )
    parser.add_argument(
        "--mediainfo-path",
        default="mediainfo",
        help="Override the mediainfo executable path.",
    )
    parser.add_argument(
        "--braw-adapter-path",
        metavar="PATH",
        help="Override the BRAW adapter executable path.",
    )
    parser.add_argument(
        "--r3d-adapter-path",
        metavar="PATH",
        help="Override the R3D adapter executable path.",
    )
    parser.add_argument(
        "--arri-art-cmd-path",
        metavar="PATH",
        help="Override the ARRI ART CMD executable path.",
    )
    return parser


def build_config_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="frameproof config",
        description="Print runtime configuration diagnostics.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Choose text or JSON diagnostics output.",
    )
    return parser


def render_snapshot(snapshot: dict[str, object], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(snapshot, indent=2, sort_keys=True)

    lines = [
        "Frame Proof runtime diagnostics",
        f"config_source: {snapshot['config_source']}",
        f"config_path: {snapshot['config_path']}",
        f"config_exists: {snapshot['config_exists']}",
        f"working_directory: {snapshot['working_directory']}",
        f"python_executable: {snapshot['python_executable']}",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args_list = list(argv) if argv is not None else sys.argv[1:]
    if args_list and args_list[0] == "config":
        config_args = build_config_parser().parse_args(args_list[1:])
        snapshot = collect_runtime_snapshot(env=os.environ).to_dict()
        print(render_snapshot(snapshot, config_args.format))
        return 0

    parser = build_parser()
    args = parser.parse_args(args_list)
    if not args.inputs:
        parser.print_help()
        return 0
    if args.output is None:
        parser.error("--output is required for pipeline runs")
    if args.export_stills and args.stills_dir is None:
        parser.error("--stills-dir is required when --export-stills is enabled")

    settings = AppSettings.from_mapping(
        {
            "input": {
                "paths": args.inputs,
                "recursive": args.recursive,
            },
            "capture": {
                "middle_count": args.middle_count,
                "profile": "preview_rec709_sdr",
                "prefer_frame_index": True,
            },
            "report": {
                "layout": args.layout,
                "project_name": args.project_name,
            },
            "output": {
                "pdf_path": args.output,
                "export_stills": args.export_stills,
                "stills_dir": args.stills_dir,
                "write_csv": True,
                "write_json": True,
                "csv_path": args.csv,
                "json_path": args.json,
            },
            "adapters": {
                "ffmpeg_path": args.ffmpeg_path,
                "ffprobe_path": args.ffprobe_path,
                "mediainfo_path": args.mediainfo_path,
                "braw_adapter_path": args.braw_adapter_path,
                "r3d_adapter_path": args.r3d_adapter_path,
                "arri_art_cmd_path": args.arri_art_cmd_path,
            },
        }
    )

    outcome = run_batch(settings)
    _print_summary(outcome)
    return outcome.exit_code


def _print_summary(outcome: BatchRunOutcome) -> None:
    summary = outcome.report.summary
    print(f"status: {summary.status.value}")
    print(f"total_clips: {summary.total_clips}")
    print(f"success_count: {summary.success_count}")
    print(f"partial_success_count: {summary.partial_success_count}")
    print(f"probe_failed_count: {summary.probe_failed_count}")
    print(f"decode_failed_count: {summary.decode_failed_count}")
    print(f"skipped_count: {summary.skipped_count}")
    for diagnostic in _dependency_diagnostics(outcome.report):
        print(diagnostic)
    if outcome.pdf_path is not None:
        print(f"pdf_path: {outcome.pdf_path}")
    if outcome.csv_path is not None:
        print(f"csv_path: {outcome.csv_path}")
    if outcome.json_path is not None:
        print(f"json_path: {outcome.json_path}")
    if outcome.fatal_error is not None:
        print(f"fatal_code: {outcome.fatal_error.code.value}")
        fatal_stage = outcome.fatal_error.detail.get("stage")
        if isinstance(fatal_stage, str) and fatal_stage:
            print(f"fatal_stage: {fatal_stage}")
    if outcome.error_message is not None:
        print(f"fatal_reason: {outcome.error_message}")
    if outcome.exit_code != 0:
        print("fatal: batch could not produce a report")


def _dependency_diagnostics(report: BatchReport) -> tuple[str, ...]:
    diagnostics: list[str] = []
    seen: set[str] = set()
    for item in report.items:
        if item.status is not ClipStatus.DEPENDENCY_MISSING:
            continue

        dependency_state = "unknown"
        required_tools = item.adapter_name
        for error in item.errors:
            if error.code is AdapterErrorCode.DEPENDENCY_MISSING:
                detail_state = error.detail.get("dependency_state")
                if isinstance(detail_state, str) and detail_state:
                    dependency_state = detail_state
                detail_required_tools = error.detail.get("required_tools")
                if isinstance(detail_required_tools, list) and all(
                    isinstance(tool_name, str) and tool_name for tool_name in detail_required_tools
                ):
                    required_tools = ",".join(detail_required_tools)
                break

        diagnostic = (
            "dependency_missing: "
            f"clip={item.clip.clip_name} "
            f"status={item.status.value} "
            f"adapter={item.adapter_name} "
            f"required_tools={required_tools} "
            f"dependency_state={dependency_state}"
        )
        if diagnostic not in seen:
            seen.add(diagnostic)
            diagnostics.append(diagnostic)
    return tuple(diagnostics)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
