from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from frameproof.config.settings import AdapterSettings
from frameproof.core.dependency_inspector import DependencyInspector, DependencyRecord
from frameproof.gui.qt import (
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    Qt,
    QVBoxLayout,
    QWidget,
    Signal,
)
from frameproof.gui.settings_store import GuiStoredSettings, SettingsStore
from frameproof.gui.status_text import dependency_state_label

_TOOL_FIELDS: tuple[tuple[str, str, bool, str], ...] = (
    ("FFmpeg", "ffmpeg_path", False, "Required for standard video capture and PDF previews"),
    ("FFprobe", "ffprobe_path", False, "Required for standard video probe metadata"),
    ("MediaInfo", "mediainfo_path", False, "Optional metadata enrichment where available"),
    ("BRAW Adapter", "braw_adapter_path", True, "Used only for BRAW-family clips"),
    ("R3D Adapter", "r3d_adapter_path", True, "Used only for R3D-family clips"),
    ("ARRI ART CMD", "arri_art_cmd_path", True, "Used only for ARRIRAW-family clips"),
)


class DependencyDialog(QDialog):
    settings_changed = Signal(object)

    def __init__(self, settings_store: SettingsStore, stored_settings: GuiStoredSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings_store = settings_store
        self._stored_settings = stored_settings
        self._path_edits: dict[str, QLineEdit] = {}
        self._status_labels: dict[str, QLabel] = {}
        self._resolved_labels: dict[str, QLabel] = {}
        self.setWindowTitle("Dependencies")
        self.resize(920, 470)
        self._build_ui()
        self._load_fields()
        self._refresh_statuses()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        intro = QLabel(
            "Missing RAW tools disable only their affected format families. FFmpeg and FFprobe remain required for standard video."
        )
        intro.setWordWrap(True)
        intro.setProperty("role", "helper")
        layout.addWidget(intro)

        secondary_intro = QLabel(
            "Save stores the configured paths in the GUI settings. Re-check refreshes the exact required state labels without closing this dialog."
        )
        secondary_intro.setWordWrap(True)
        secondary_intro.setProperty("role", "helper")
        layout.addWidget(secondary_intro)

        group = QGroupBox("Tool Paths And Status")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.addWidget(QLabel("Tool"), 0, 0)
        grid.addWidget(QLabel("Configured Path"), 0, 1)
        grid.addWidget(QLabel("Applies To"), 0, 3)
        grid.addWidget(QLabel("Status"), 0, 4)
        grid.addWidget(QLabel("Resolved"), 0, 5)
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(3, 2)
        grid.setColumnStretch(5, 3)

        for row_index, (label, key, browse_only_path, usage_text) in enumerate(_TOOL_FIELDS, start=1):
            edit = QLineEdit()
            edit.setPlaceholderText("Auto-detect from PATH" if not browse_only_path else "Set an explicit executable path")
            edit.setClearButtonEnabled(True)
            status_label = QLabel("-")
            status_label.setWordWrap(True)
            usage_label = QLabel(usage_text)
            usage_label.setWordWrap(True)
            usage_label.setProperty("role", "helper")
            resolved_label = QLabel("-")
            resolved_label.setWordWrap(True)
            resolved_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            browse_button = QPushButton("Browse")
            browse_button.setProperty("variant", "quiet")
            browse_button.clicked.connect(lambda _checked=False, item=key, path_only=browse_only_path: self._browse(item, path_only))

            grid.addWidget(QLabel(label), row_index, 0)
            grid.addWidget(edit, row_index, 1)
            grid.addWidget(browse_button, row_index, 2)
            grid.addWidget(usage_label, row_index, 3)
            grid.addWidget(status_label, row_index, 4)
            grid.addWidget(resolved_label, row_index, 5)

            self._path_edits[key] = edit
            self._status_labels[key] = status_label
            self._resolved_labels[key] = resolved_label

        layout.addWidget(group)

        footer = QHBoxLayout()
        footer.addStretch(1)
        recheck_button = QPushButton("Re-check")
        recheck_button.setProperty("variant", "quiet")
        recheck_button.clicked.connect(self._refresh_statuses)
        save_button = QPushButton("Save")
        save_button.setProperty("variant", "primary")
        save_button.clicked.connect(self._save)
        close_button = QPushButton("Close")
        close_button.setProperty("variant", "danger")
        close_button.clicked.connect(self.reject)
        footer.addWidget(recheck_button)
        footer.addWidget(save_button)
        footer.addWidget(close_button)
        layout.addLayout(footer)

    def _load_fields(self) -> None:
        for _label, key, _browse_only_path, _usage_text in _TOOL_FIELDS:
            value = getattr(self._stored_settings, key)
            self._path_edits[key].setText("" if value is None else value)

    def _browse(self, key: str, browse_only_path: bool) -> None:
        if browse_only_path:
            path, _selected_filter = QFileDialog.getOpenFileName(self, "Select Executable")
        else:
            path, _selected_filter = QFileDialog.getOpenFileName(self, "Select Executable")
        if path:
            self._path_edits[key].setText(path)

    def _refresh_statuses(self) -> None:
        inspector = DependencyInspector(self._adapter_settings_from_fields())
        records = {
            "ffmpeg_path": inspector.ffmpeg(),
            "ffprobe_path": inspector.ffprobe(),
            "mediainfo_path": inspector.mediainfo(),
            "braw_adapter_path": inspector.braw_adapter(),
            "r3d_adapter_path": inspector.r3d_adapter(),
            "arri_art_cmd_path": inspector.arri_art_cmd(),
        }
        for key, record in records.items():
            self._apply_record(key, record)

    def _apply_record(self, key: str, record: DependencyRecord) -> None:
        self._status_labels[key].setText(dependency_state_label(record.state))
        self._status_labels[key].setProperty("state", record.state.value)
        self._resolved_labels[key].setText(record.resolved_path or "-")
        self._status_labels[key].style().unpolish(self._status_labels[key])
        self._status_labels[key].style().polish(self._status_labels[key])

    def _save(self) -> None:
        updated = replace(
            self._stored_settings,
            ffmpeg_path=self._path_edits["ffmpeg_path"].text().strip() or "ffmpeg",
            ffprobe_path=self._path_edits["ffprobe_path"].text().strip() or "ffprobe",
            mediainfo_path=self._path_edits["mediainfo_path"].text().strip() or "mediainfo",
            braw_adapter_path=_optional_text(self._path_edits["braw_adapter_path"].text()),
            r3d_adapter_path=_optional_text(self._path_edits["r3d_adapter_path"].text()),
            arri_art_cmd_path=_optional_text(self._path_edits["arri_art_cmd_path"].text()),
        )
        self._settings_store.save(updated)
        self.settings_changed.emit(updated)
        self.accept()

    def _adapter_settings_from_fields(self) -> AdapterSettings:
        return AdapterSettings(
            ffmpeg_path=self._path_edits["ffmpeg_path"].text().strip() or "ffmpeg",
            ffprobe_path=self._path_edits["ffprobe_path"].text().strip() or "ffprobe",
            mediainfo_path=self._path_edits["mediainfo_path"].text().strip() or "mediainfo",
            braw_adapter_path=_optional_path(self._path_edits["braw_adapter_path"].text()),
            r3d_adapter_path=_optional_path(self._path_edits["r3d_adapter_path"].text()),
            arri_art_cmd_path=_optional_path(self._path_edits["arri_art_cmd_path"].text()),
        )


def _optional_text(value: str) -> str | None:
    text = value.strip()
    return text or None


def _optional_path(value: str) -> Path | None:
    text = _optional_text(value)
    if text is None:
        return None
    return Path(text).expanduser()
