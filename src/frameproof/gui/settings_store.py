from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from frameproof.config.settings import PathDisplayMode, ReportLayout
from frameproof.gui.qt import QSettings, QStandardPaths


@dataclass(frozen=True)
class GuiStoredSettings:
    source_paths: tuple[str, ...] = ()
    include_subfolders: bool = True
    output_pdf_path: str | None = None
    last_output_dir: str | None = None
    project_name: str | None = None
    middle_count: int = 3
    layout: str = ReportLayout.CONTACT_SHEET.value
    export_stills: bool = False
    write_csv: bool = True
    write_json: bool = True
    include_failed_section: bool = True
    path_display: str = PathDisplayMode.BASENAME.value
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    mediainfo_path: str = "mediainfo"
    braw_adapter_path: str | None = None
    r3d_adapter_path: str | None = None
    arri_art_cmd_path: str | None = None


def default_settings_path() -> Path:
    candidates = [
        Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)),
        Path.home() / ".frameproof",
        Path(tempfile.gettempdir()) / "frameproof",
    ]
    for candidate in candidates:
        if _can_create_directory(candidate):
            return candidate / "frameproof-gui.ini"
    return Path.cwd() / ".frameproof" / "frameproof-gui.ini"


class SettingsStore:
    def __init__(self, settings_path: Path | None = None) -> None:
        self._settings_path = settings_path or default_settings_path()

    @property
    def settings_path(self) -> Path:
        return self._settings_path

    def load(self) -> GuiStoredSettings:
        settings = self._open()
        return GuiStoredSettings(
            source_paths=_string_list_value(settings, "input/source_paths"),
            include_subfolders=_bool_value(settings, "input/include_subfolders", True),
            output_pdf_path=_optional_text(settings.value("output/pdf_path")),
            last_output_dir=_optional_text(settings.value("output/last_output_dir")),
            project_name=_optional_text(settings.value("report/project_name")),
            middle_count=_int_value(settings, "capture/middle_count", 3),
            layout=str(settings.value("report/layout", ReportLayout.CONTACT_SHEET.value)),
            export_stills=_bool_value(settings, "output/export_stills", False),
            write_csv=_bool_value(settings, "output/write_csv", True),
            write_json=_bool_value(settings, "output/write_json", True),
            include_failed_section=_bool_value(settings, "report/include_failed_section", True),
            path_display=str(settings.value("report/path_display", PathDisplayMode.BASENAME.value)),
            ffmpeg_path=str(settings.value("adapters/ffmpeg_path", "ffmpeg")),
            ffprobe_path=str(settings.value("adapters/ffprobe_path", "ffprobe")),
            mediainfo_path=str(settings.value("adapters/mediainfo_path", "mediainfo")),
            braw_adapter_path=_optional_text(settings.value("adapters/braw_adapter_path")),
            r3d_adapter_path=_optional_text(settings.value("adapters/r3d_adapter_path")),
            arri_art_cmd_path=_optional_text(settings.value("adapters/arri_art_cmd_path")),
        )

    def save(self, data: GuiStoredSettings) -> None:
        settings = self._open()
        settings.setValue("input/source_paths", list(data.source_paths))
        settings.setValue("input/include_subfolders", data.include_subfolders)
        settings.setValue("output/pdf_path", data.output_pdf_path or "")
        settings.setValue("output/last_output_dir", data.last_output_dir or "")
        settings.setValue("report/project_name", data.project_name or "")
        settings.setValue("capture/middle_count", data.middle_count)
        settings.setValue("report/layout", data.layout)
        settings.setValue("output/export_stills", data.export_stills)
        settings.setValue("output/write_csv", data.write_csv)
        settings.setValue("output/write_json", data.write_json)
        settings.setValue("report/include_failed_section", data.include_failed_section)
        settings.setValue("report/path_display", data.path_display)
        settings.setValue("adapters/ffmpeg_path", data.ffmpeg_path)
        settings.setValue("adapters/ffprobe_path", data.ffprobe_path)
        settings.setValue("adapters/mediainfo_path", data.mediainfo_path)
        settings.setValue("adapters/braw_adapter_path", data.braw_adapter_path or "")
        settings.setValue("adapters/r3d_adapter_path", data.r3d_adapter_path or "")
        settings.setValue("adapters/arri_art_cmd_path", data.arri_art_cmd_path or "")
        settings.sync()

    def _open(self) -> QSettings:
        self._settings_path.parent.mkdir(parents=True, exist_ok=True)
        return QSettings(str(self._settings_path), QSettings.Format.IniFormat)


def _bool_value(settings: QSettings, key: str, default: bool) -> bool:
    raw = settings.value(key, default)
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return raw.lower() in {"1", "true", "yes"}
    return bool(raw)


def _string_list_value(settings: QSettings, key: str) -> tuple[str, ...]:
    raw = settings.value(key, [])
    if isinstance(raw, list):
        return tuple(str(value) for value in raw)
    if raw is None:
        return ()
    return (str(raw),)


def _int_value(settings: QSettings, key: str, default: int) -> int:
    raw = settings.value(key, default)
    if isinstance(raw, int):
        return raw
    return int(str(raw))


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _can_create_directory(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False
    return True
