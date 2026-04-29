from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Mapping, cast

CONFIG_ENV_VAR = "FRAMEPROOF_CONFIG"
DEFAULT_CONFIG_RELATIVE_PATH = Path(".config") / "frameproof" / "config.toml"
DEFAULT_EXTENSIONS: tuple[str, ...] = ("mov", "mp4", "mxf", "avi", "braw", "r3d", "ari")


class ReportLayout(StrEnum):
    CONTACT_SHEET = "contact_sheet"
    CLIP_DETAIL = "detail"


class PathDisplayMode(StrEnum):
    FULL = "full"
    BASENAME = "basename"
    HIDDEN = "hidden"


def _require_text(value: str, field_name: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{field_name} must not be empty")
    return text


def _coerce_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    path = Path(value).expanduser()
    if str(path).strip() == "":
        raise ValueError("path values must not be empty")
    return path


def _coerce_paths(values: tuple[str | Path, ...] | list[str | Path]) -> tuple[Path, ...]:
    return tuple(path for path in (_coerce_path(value) for value in values) if path is not None)


def _require_mapping(value: object, field_name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    return cast(Mapping[str, object], value)


def _require_int(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


@dataclass(frozen=True)
class RuntimeSnapshot:
    config_path: str
    config_exists: bool
    config_source: str
    working_directory: str
    python_executable: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def resolve_config_path(
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> tuple[Path, str]:
    active_env = env if env is not None else {}
    if configured_path := active_env.get(CONFIG_ENV_VAR):
        return Path(configured_path).expanduser().resolve(), "env"

    base_home = home if home is not None else Path.home()
    return (base_home / DEFAULT_CONFIG_RELATIVE_PATH).resolve(), "default"


def collect_runtime_snapshot(
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
    home: Path | None = None,
    python_executable: Path | None = None,
) -> RuntimeSnapshot:
    config_path, config_source = resolve_config_path(env=env, home=home)
    active_cwd = cwd if cwd is not None else Path.cwd()
    active_python = python_executable if python_executable is not None else Path(__import__("sys").executable)

    return RuntimeSnapshot(
        config_path=str(config_path),
        config_exists=config_path.is_file(),
        config_source=config_source,
        working_directory=str(active_cwd.resolve()),
        python_executable=str(active_python.resolve()),
    )


@dataclass(frozen=True)
class InputSettings:
    paths: tuple[Path, ...]
    recursive: bool = True
    extensions: tuple[str, ...] = DEFAULT_EXTENSIONS

    def __post_init__(self) -> None:
        object.__setattr__(self, "paths", _coerce_paths(list(self.paths)))
        if not self.paths:
            raise ValueError("input.paths must contain at least one path")
        normalized_extensions = tuple(_require_text(extension.lstrip("."), "extensions").lower() for extension in self.extensions)
        if not normalized_extensions:
            raise ValueError("extensions must contain at least one value")
        object.__setattr__(self, "extensions", normalized_extensions)


@dataclass(frozen=True)
class CaptureSettings:
    middle_count: int = 3
    profile: str = "preview_rec709_sdr"
    prefer_frame_index: bool = True

    def __post_init__(self) -> None:
        if self.middle_count < 0 or self.middle_count > 3:
            raise ValueError("capture.middle_count must be between 0 and 3 inclusive")
        object.__setattr__(self, "profile", _require_text(self.profile, "capture.profile"))


@dataclass(frozen=True)
class ReportSettings:
    layout: ReportLayout = ReportLayout.CONTACT_SHEET
    project_name: str | None = None
    include_failed_section: bool = True
    include_summary_page: bool = True
    path_display: PathDisplayMode = PathDisplayMode.BASENAME

    def __post_init__(self) -> None:
        object.__setattr__(self, "layout", ReportLayout(self.layout))
        object.__setattr__(self, "path_display", PathDisplayMode(self.path_display))
        if self.project_name is not None:
            object.__setattr__(self, "project_name", _require_text(self.project_name, "report.project_name"))


@dataclass(frozen=True)
class OutputSettings:
    pdf_path: Path
    export_stills: bool = False
    stills_dir: Path | None = None
    write_csv: bool = True
    write_json: bool = True
    csv_path: Path | None = None
    json_path: Path | None = None
    staging_dir: Path | None = None

    def __post_init__(self) -> None:
        pdf_path = _coerce_path(self.pdf_path)
        assert pdf_path is not None
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError("output.pdf_path must point to a .pdf file")
        object.__setattr__(self, "pdf_path", pdf_path)
        object.__setattr__(self, "stills_dir", _coerce_path(self.stills_dir))
        object.__setattr__(self, "csv_path", _coerce_path(self.csv_path))
        object.__setattr__(self, "json_path", _coerce_path(self.json_path))
        object.__setattr__(self, "staging_dir", _coerce_path(self.staging_dir))
        if self.export_stills and self.stills_dir is None:
            raise ValueError("output.stills_dir is required when export_stills is enabled")
        if self.stills_dir is not None and self.stills_dir == self.pdf_path:
            raise ValueError("output.stills_dir must not equal output.pdf_path")
        if self.csv_path is not None and self.csv_path == self.pdf_path:
            raise ValueError("output.csv_path must not equal output.pdf_path")
        if self.json_path is not None and self.json_path == self.pdf_path:
            raise ValueError("output.json_path must not equal output.pdf_path")


@dataclass(frozen=True)
class AdapterSettings:
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    mediainfo_path: str = "mediainfo"
    braw_adapter_path: Path | None = None
    r3d_adapter_path: Path | None = None
    arri_art_cmd_path: Path | None = None

    def __post_init__(self) -> None:
        for field_name in ("ffmpeg_path", "ffprobe_path", "mediainfo_path"):
            value = getattr(self, field_name)
            object.__setattr__(self, field_name, _require_text(value, field_name))
        object.__setattr__(self, "braw_adapter_path", _coerce_path(self.braw_adapter_path))
        object.__setattr__(self, "r3d_adapter_path", _coerce_path(self.r3d_adapter_path))
        object.__setattr__(self, "arri_art_cmd_path", _coerce_path(self.arri_art_cmd_path))


@dataclass(frozen=True)
class AppSettings:
    input: InputSettings
    capture: CaptureSettings = field(default_factory=CaptureSettings)
    report: ReportSettings = field(default_factory=ReportSettings)
    output: OutputSettings = field(default_factory=lambda: OutputSettings(pdf_path=Path("frameproof.pdf")))
    adapters: AdapterSettings = field(default_factory=AdapterSettings)

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> AppSettings:
        input_mapping = _require_mapping(data.get("input", {}), "input")
        capture_mapping = _require_mapping(data.get("capture", {}), "capture")
        report_mapping = _require_mapping(data.get("report", {}), "report")
        output_mapping = _require_mapping(data.get("output", {}), "output")
        adapters_mapping = _require_mapping(data.get("adapters", {}), "adapters")

        input_paths_value = input_mapping.get("paths", [])
        if not isinstance(input_paths_value, list):
            raise ValueError("input.paths must be a list")
        extensions_value = input_mapping.get("extensions", list(DEFAULT_EXTENSIONS))
        if not isinstance(extensions_value, list):
            raise ValueError("input.extensions must be a list")
        middle_count_value = _require_int(capture_mapping.get("middle_count", 3), "capture.middle_count")

        return cls(
            input=InputSettings(
                paths=tuple(Path(str(path)) for path in input_paths_value),
                recursive=bool(input_mapping.get("recursive", True)),
                extensions=tuple(str(extension) for extension in extensions_value),
            ),
            capture=CaptureSettings(
                middle_count=middle_count_value,
                profile=str(capture_mapping.get("profile", "preview_rec709_sdr")),
                prefer_frame_index=bool(capture_mapping.get("prefer_frame_index", True)),
            ),
            report=ReportSettings(
                layout=ReportLayout(str(report_mapping.get("layout", ReportLayout.CONTACT_SHEET))),
                project_name=(
                    str(report_mapping["project_name"]) if report_mapping.get("project_name") is not None else None
                ),
                include_failed_section=bool(report_mapping.get("include_failed_section", True)),
                include_summary_page=bool(report_mapping.get("include_summary_page", True)),
                path_display=PathDisplayMode(str(report_mapping.get("path_display", PathDisplayMode.BASENAME))),
            ),
            output=OutputSettings(
                pdf_path=Path(str(output_mapping.get("pdf_path", "frameproof.pdf"))),
                export_stills=bool(output_mapping.get("export_stills", False)),
                stills_dir=(
                    Path(str(output_mapping["stills_dir"])) if output_mapping.get("stills_dir") is not None else None
                ),
                write_csv=bool(output_mapping.get("write_csv", True)),
                write_json=bool(output_mapping.get("write_json", True)),
                csv_path=Path(str(output_mapping["csv_path"])) if output_mapping.get("csv_path") is not None else None,
                json_path=Path(str(output_mapping["json_path"])) if output_mapping.get("json_path") is not None else None,
                staging_dir=(
                    Path(str(output_mapping["staging_dir"])) if output_mapping.get("staging_dir") is not None else None
                ),
            ),
            adapters=AdapterSettings(
                ffmpeg_path=str(adapters_mapping.get("ffmpeg_path", "ffmpeg")),
                ffprobe_path=str(adapters_mapping.get("ffprobe_path", "ffprobe")),
                mediainfo_path=str(adapters_mapping.get("mediainfo_path", "mediainfo")),
                braw_adapter_path=(
                    Path(str(adapters_mapping["braw_adapter_path"]))
                    if adapters_mapping.get("braw_adapter_path") is not None
                    else None
                ),
                r3d_adapter_path=(
                    Path(str(adapters_mapping["r3d_adapter_path"]))
                    if adapters_mapping.get("r3d_adapter_path") is not None
                    else None
                ),
                arri_art_cmd_path=(
                    Path(str(adapters_mapping["arri_art_cmd_path"]))
                    if adapters_mapping.get("arri_art_cmd_path") is not None
                    else None
                ),
            ),
        )
