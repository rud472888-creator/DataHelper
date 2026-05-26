from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from frameproof.config.settings import AdapterSettings, AppSettings, PathDisplayMode, ReportLayout
from frameproof.core.batch_runner import BatchRunOutcome
from frameproof.core.dependency_inspector import DependencyInspector, DependencyRecord
from frameproof.core.models import AdapterDependencyState, ClipStatus, TimecodeSource
from frameproof.core.progress_events import BatchStageEvent, DependencyStatusEvent, RowDiscoveredEvent, RowUpdatedEvent
from frameproof.gui.batch_controller import BatchController
from frameproof.gui.dependency_dialog import DependencyDialog
from frameproof.gui.qt import (
    QAbstractItemView,
    QCheckBox,
    QColor,
    QComboBox,
    QFileDialog,
    QFont,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    Qt,
    QVBoxLayout,
    QWidget,
)
from frameproof.gui.settings_store import GuiStoredSettings, SettingsStore
from frameproof.gui.view_state import BannerState, ProgressRowState

_LAYOUT_OPTIONS: tuple[tuple[str, str], ...] = (
    ("Contact Sheet (Layout B)", ReportLayout.CONTACT_SHEET.value),
    ("Detailed File Report (Layout A)", ReportLayout.CLIP_DETAIL.value),
)
_PATH_DISPLAY_OPTIONS: tuple[tuple[str, str], ...] = (
    ("Basename Only", PathDisplayMode.BASENAME.value),
    ("Full Path", PathDisplayMode.FULL.value),
    ("Hidden", PathDisplayMode.HIDDEN.value),
)
_DEPENDENCY_LABELS: dict[str, str] = {
    "ffmpeg": "FFmpeg",
    "ffprobe": "FFprobe",
    "mediainfo": "MediaInfo",
    "braw_adapter": "BRAW",
    "r3d_adapter": "R3D",
    "arri_art_cmd": "ARRI ART CMD",
}


class MainWindow(QMainWindow):
    def __init__(self, settings_store: SettingsStore, controller: BatchController | None = None) -> None:
        super().__init__()
        self._settings_store = settings_store
        self._controller = controller or BatchController()
        self._stored_settings = self._settings_store.load()
        self._row_indexes: dict[str, int] = {}
        self._row_states: dict[str, ProgressRowState] = {}
        self._last_dependencies: tuple[DependencyRecord, ...] = ()

        self.setWindowTitle("Frame Proof")
        self.resize(1180, 760)
        self._build_ui()
        self._connect_controller()
        self._load_form()
        self._refresh_dependency_summary()
        self._refresh_form_guidance()
        self._set_banner(
            BannerState(
                "info",
                "Select source files or folders to begin.",
                "Layout B is the default report mode. PNG export is optional and source media stays read-only.",
            )
        )
        self._set_running(False)

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)
        self.setCentralWidget(central)

        overview_intro = QLabel("GUI and CLI runs use the same shared scan, capture, report, and manifest pipeline.")
        overview_intro.setWordWrap(True)
        overview_intro.setProperty("role", "helper")
        _allow_compact_wrap(overview_intro)

        self._overview_status_label = QLabel()
        self._overview_status_label.setWordWrap(True)
        self._overview_status_label.setProperty("role", "summary")
        self._overview_status_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        _allow_compact_wrap(self._overview_status_label)

        self._dependency_summary = QLabel()
        self._dependency_summary.setWordWrap(True)
        self._dependency_summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._dependency_summary.setProperty("tone", "info")
        _allow_compact_wrap(self._dependency_summary)

        source_group = QGroupBox("Sources")
        source_layout = QVBoxLayout(source_group)
        source_layout.setSpacing(5)
        source_layout.addWidget(_section_label("Session Overview"))
        source_layout.addWidget(overview_intro)
        source_layout.addWidget(self._overview_status_label)
        source_layout.addWidget(self._dependency_summary)

        source_buttons = QGridLayout()
        source_buttons.setContentsMargins(0, 0, 0, 0)
        source_buttons.setHorizontalSpacing(8)
        source_buttons.setVerticalSpacing(4)
        self._add_files_button = QPushButton("Add Files")
        self._add_folder_button = QPushButton("Add Folder")
        self._remove_source_button = QPushButton("Remove Selected")
        self._clear_sources_button = QPushButton("Clear")
        self._clear_sources_button.setProperty("variant", "quiet")
        source_buttons.addWidget(self._add_files_button, 0, 0)
        source_buttons.addWidget(self._add_folder_button, 0, 1)
        source_buttons.addWidget(self._remove_source_button, 1, 0)
        source_buttons.addWidget(self._clear_sources_button, 1, 1)
        source_layout.addLayout(source_buttons)

        self._source_help_label = QLabel()
        self._source_help_label.setWordWrap(True)
        self._source_help_label.setProperty("role", "helper")
        _allow_compact_wrap(self._source_help_label)
        source_layout.addWidget(self._source_help_label)

        self._source_summary_label = QLabel()
        self._source_summary_label.setWordWrap(True)
        self._source_summary_label.setProperty("role", "summary")
        self._source_summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        _allow_compact_wrap(self._source_summary_label)
        source_layout.addWidget(self._source_summary_label)

        self._sources_list = QListWidget()
        self._sources_list.setMinimumHeight(96)
        self._sources_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._sources_list.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        source_layout.addWidget(self._sources_list, 1)

        self._include_subfolders_checkbox = QCheckBox("Include subfolders")
        source_layout.addWidget(self._include_subfolders_checkbox)

        settings_group = QGroupBox("Output And Report")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(5)

        settings_intro = QLabel("Choose one PDF destination. Layout B is denser; Layout A shows more per-frame detail.")
        settings_intro.setWordWrap(True)
        settings_intro.setProperty("role", "helper")
        _allow_compact_wrap(settings_intro)
        settings_layout.addWidget(settings_intro)

        output_label = QLabel("Output PDF")
        output_label.setProperty("role", "summary")
        settings_layout.addWidget(output_label)
        output_row = QHBoxLayout()
        output_row.setSpacing(8)
        self._output_pdf_edit = QLineEdit()
        self._output_pdf_edit.setPlaceholderText("/path/to/frameproof-report.pdf")
        self._output_pdf_button = QPushButton("Browse")
        output_row.addWidget(self._output_pdf_edit)
        output_row.addWidget(self._output_pdf_button)
        settings_layout.addLayout(output_row)

        self._project_name_edit = QLineEdit()
        self._project_name_edit.setPlaceholderText("Defaults to the PDF filename")
        self._middle_count_spin = QSpinBox()
        self._middle_count_spin.setRange(0, 3)
        settings_layout.addWidget(_field_label("Project Name"))
        settings_layout.addWidget(self._project_name_edit)
        middle_frames_row = QHBoxLayout()
        middle_frames_row.setContentsMargins(0, 0, 0, 0)
        middle_frames_row.setSpacing(8)
        middle_frames_row.addWidget(_field_label("Middle Frames"))
        middle_frames_row.addStretch(1)
        middle_frames_row.addWidget(self._middle_count_spin)
        settings_layout.addLayout(middle_frames_row)

        self._layout_combo = QComboBox()
        for label, value in _LAYOUT_OPTIONS:
            self._layout_combo.addItem(label, value)
        self._layout_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self._layout_combo.setMinimumContentsLength(14)
        self._path_display_combo = QComboBox()
        for label, value in _PATH_DISPLAY_OPTIONS:
            self._path_display_combo.addItem(label, value)
        self._path_display_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self._path_display_combo.setMinimumContentsLength(10)
        settings_layout.addWidget(_field_label("Layout"))
        settings_layout.addWidget(self._layout_combo)
        settings_layout.addWidget(_field_label("Path Privacy"))
        settings_layout.addWidget(self._path_display_combo)

        self._export_stills_checkbox = QCheckBox("Export still PNGs")
        self._write_csv_checkbox = QCheckBox("Include CSV manifest")
        self._write_json_checkbox = QCheckBox("Include JSON manifest")
        self._include_failed_checkbox = QCheckBox("Include failed files section")
        outputs_label = QLabel("Outputs")
        outputs_label.setProperty("role", "summary")
        settings_layout.addWidget(outputs_label)
        output_options_widget = QWidget()
        output_options_layout = QVBoxLayout(output_options_widget)
        output_options_layout.setContentsMargins(0, 0, 0, 0)
        output_options_layout.setSpacing(4)
        output_options_layout.addWidget(self._export_stills_checkbox)
        output_options_layout.addWidget(self._write_csv_checkbox)
        output_options_layout.addWidget(self._write_json_checkbox)
        output_options_layout.addWidget(self._include_failed_checkbox)
        settings_layout.addWidget(output_options_widget)

        self._output_note_label = QLabel()
        self._output_note_label.setWordWrap(True)
        self._output_note_label.setProperty("role", "helper")
        self._output_note_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        _allow_compact_wrap(self._output_note_label)
        settings_layout.addWidget(self._output_note_label)

        run_group = QGroupBox("Run")
        run_layout = QVBoxLayout(run_group)
        run_layout.setSpacing(5)

        self._run_note_label = QLabel(
            "Start refreshes dependency status before launch. Cancel stops after the current in-flight step."
        )
        self._run_note_label.setWordWrap(True)
        self._run_note_label.setProperty("role", "helper")
        _allow_compact_wrap(self._run_note_label)
        run_layout.addWidget(self._run_note_label)

        self._run_readiness_label = QLabel()
        self._run_readiness_label.setWordWrap(True)
        self._run_readiness_label.setProperty("role", "summary")
        self._run_readiness_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        _allow_compact_wrap(self._run_readiness_label)
        run_layout.addWidget(self._run_readiness_label)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)
        self._dependency_button = QPushButton("Dependencies")
        self._dependency_button.setProperty("variant", "quiet")
        self._start_button = QPushButton("Start")
        self._start_button.setProperty("variant", "primary")
        self._start_button.setDefault(True)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.setProperty("variant", "danger")
        action_row.addWidget(self._dependency_button)
        action_row.addStretch(1)
        action_row.addWidget(self._start_button)
        action_row.addWidget(self._cancel_button)
        run_layout.addLayout(action_row)

        self._banner_label = QLabel()
        self._banner_label.setWordWrap(True)
        self._banner_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        _allow_compact_wrap(self._banner_label)

        self._run_summary_label = QLabel()
        self._run_summary_label.setWordWrap(True)
        self._run_summary_label.setProperty("role", "helper")
        self._run_summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        _allow_compact_wrap(self._run_summary_label)
        self._run_summary_label.hide()

        run_layout.addWidget(_section_label("Batch Status"))
        run_layout.addWidget(self._banner_label)
        run_layout.addWidget(self._run_summary_label)

        content_row = QHBoxLayout()
        content_row.setSpacing(10)
        content_row.addWidget(source_group, 5)
        content_row.addWidget(settings_group, 5)
        content_row.addWidget(run_group, 4)
        root.addLayout(content_row, 1)

        progress_group = QGroupBox("Clip Progress")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(6)

        self._progress_caption_label = QLabel()
        self._progress_caption_label.setWordWrap(True)
        self._progress_caption_label.setProperty("role", "helper")
        _allow_compact_wrap(self._progress_caption_label)
        progress_layout.addWidget(self._progress_caption_label)

        self._progress_table = QTableWidget(0, 6)
        self._progress_table.setHorizontalHeaderLabels(["Clip", "Format", "Probe", "Capture", "PDF", "Warning"])
        self._progress_table.verticalHeader().setVisible(False)
        self._progress_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._progress_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._progress_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._progress_table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self._progress_table.setShowGrid(False)
        self._progress_table.setAlternatingRowColors(False)
        self._progress_table.setWordWrap(True)
        self._progress_table.setMinimumHeight(100)
        header = self._progress_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self._progress_table.verticalHeader().setDefaultSectionSize(28)
        progress_layout.addWidget(self._progress_table, 1)
        root.addWidget(progress_group, 1)

        self._add_files_button.clicked.connect(self._choose_files)
        self._add_folder_button.clicked.connect(self._choose_folder)
        self._remove_source_button.clicked.connect(self._remove_selected_sources)
        self._clear_sources_button.clicked.connect(self._clear_sources)
        self._output_pdf_button.clicked.connect(self._choose_output_pdf)
        self._dependency_button.clicked.connect(self._open_dependency_dialog)
        self._start_button.clicked.connect(self._start_batch)
        self._cancel_button.clicked.connect(self._cancel_batch)
        self._output_pdf_edit.textChanged.connect(self._refresh_form_guidance)
        self._layout_combo.currentIndexChanged.connect(lambda _index: self._refresh_form_guidance())
        self._path_display_combo.currentIndexChanged.connect(lambda _index: self._refresh_form_guidance())
        self._export_stills_checkbox.toggled.connect(lambda _checked: self._refresh_form_guidance())
        self._include_subfolders_checkbox.toggled.connect(lambda _checked: self._refresh_form_guidance())
        self._configure_tab_order()

    def _connect_controller(self) -> None:
        self._controller.progress_event.connect(self._handle_progress_event)
        self._controller.batch_finished.connect(self._handle_batch_finished)
        self._controller.batch_failed.connect(self._handle_batch_failed)
        self._controller.running_changed.connect(self._set_running)

    def _load_form(self) -> None:
        self._set_source_paths(self._stored_settings.source_paths)
        self._include_subfolders_checkbox.setChecked(self._stored_settings.include_subfolders)
        self._output_pdf_edit.setText(self._stored_settings.output_pdf_path or "")
        self._project_name_edit.setText(self._stored_settings.project_name or "")
        self._middle_count_spin.setValue(self._stored_settings.middle_count)
        self._select_combo_data(self._layout_combo, self._stored_settings.layout)
        self._select_combo_data(self._path_display_combo, self._stored_settings.path_display)
        self._export_stills_checkbox.setChecked(self._stored_settings.export_stills)
        self._write_csv_checkbox.setChecked(self._stored_settings.write_csv)
        self._write_json_checkbox.setChecked(self._stored_settings.write_json)
        self._include_failed_checkbox.setChecked(self._stored_settings.include_failed_section)

    def _configure_tab_order(self) -> None:
        QWidget.setTabOrder(self._add_files_button, self._add_folder_button)
        QWidget.setTabOrder(self._add_folder_button, self._remove_source_button)
        QWidget.setTabOrder(self._remove_source_button, self._clear_sources_button)
        QWidget.setTabOrder(self._clear_sources_button, self._sources_list)
        QWidget.setTabOrder(self._sources_list, self._include_subfolders_checkbox)
        QWidget.setTabOrder(self._include_subfolders_checkbox, self._output_pdf_edit)
        QWidget.setTabOrder(self._output_pdf_edit, self._output_pdf_button)
        QWidget.setTabOrder(self._output_pdf_button, self._project_name_edit)
        QWidget.setTabOrder(self._project_name_edit, self._middle_count_spin)
        QWidget.setTabOrder(self._middle_count_spin, self._layout_combo)
        QWidget.setTabOrder(self._layout_combo, self._path_display_combo)
        QWidget.setTabOrder(self._path_display_combo, self._export_stills_checkbox)
        QWidget.setTabOrder(self._export_stills_checkbox, self._write_csv_checkbox)
        QWidget.setTabOrder(self._write_csv_checkbox, self._write_json_checkbox)
        QWidget.setTabOrder(self._write_json_checkbox, self._include_failed_checkbox)
        QWidget.setTabOrder(self._include_failed_checkbox, self._dependency_button)
        QWidget.setTabOrder(self._dependency_button, self._start_button)
        QWidget.setTabOrder(self._start_button, self._cancel_button)
        QWidget.setTabOrder(self._cancel_button, self._progress_table)

    def _set_source_paths(self, paths: tuple[str, ...]) -> None:
        self._sources_list.clear()
        for path in paths:
            self._sources_list.addItem(_source_item(path))
        self._refresh_form_guidance()

    def _choose_files(self) -> None:
        paths, _selected_filter = QFileDialog.getOpenFileNames(self, "Select Source Files")
        for path in paths:
            self._append_source(path)

    def _choose_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if path:
            self._append_source(path)

    def _append_source(self, path: str) -> None:
        existing = set(self._source_paths())
        if path not in existing:
            self._sources_list.addItem(_source_item(path))
            self._refresh_form_guidance()

    def _clear_sources(self) -> None:
        self._sources_list.clear()
        self._refresh_form_guidance()

    def _remove_selected_sources(self) -> None:
        for item in self._sources_list.selectedItems():
            self._sources_list.takeItem(self._sources_list.row(item))
        self._refresh_form_guidance()

    def _choose_output_pdf(self) -> None:
        start_dir = self._stored_settings.last_output_dir or str(Path.home())
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Select Output PDF",
            str(Path(start_dir) / "frameproof-report.pdf"),
            "PDF Files (*.pdf)",
        )
        if path:
            if not path.lower().endswith(".pdf"):
                path = f"{path}.pdf"
            self._output_pdf_edit.setText(path)

    def _open_dependency_dialog(self) -> None:
        dialog = DependencyDialog(self._settings_store, self._stored_settings, self)
        dialog.settings_changed.connect(self._handle_settings_changed)
        dialog.exec()

    def _handle_settings_changed(self, settings: GuiStoredSettings) -> None:
        self._stored_settings = settings
        self._refresh_dependency_summary()
        self._refresh_form_guidance()

    def _refresh_dependency_summary(self) -> None:
        inspector = DependencyInspector(self._adapter_settings())
        records = inspector.all_dependencies()
        self._last_dependencies = records
        available_count = sum(1 for record in records if record.state is AdapterDependencyState.AVAILABLE)
        core_blockers = [
            _DEPENDENCY_LABELS.get(record.name, record.name)
            for record in records
            if record.name in {"ffmpeg", "ffprobe"} and record.state is not AdapterDependencyState.AVAILABLE
        ]
        raw_gaps = [
            _DEPENDENCY_LABELS.get(record.name, record.name)
            for record in records
            if record.name in {"braw_adapter", "r3d_adapter", "arri_art_cmd"}
            and record.state is not AdapterDependencyState.AVAILABLE
        ]
        other_gaps = [
            _DEPENDENCY_LABELS.get(record.name, record.name)
            for record in records
            if record.name not in {"ffmpeg", "ffprobe", "braw_adapter", "r3d_adapter", "arri_art_cmd"}
            and record.state is not AdapterDependencyState.AVAILABLE
        ]
        notes = [f"{available_count}/{len(records)} tools resolved."]
        if core_blockers:
            notes.append("Core blockers: " + ", ".join(core_blockers) + ".")
        else:
            notes.append("Core FFmpeg and FFprobe checks are clear.")
        if raw_gaps:
            notes.append("RAW-only gaps: " + ", ".join(raw_gaps) + ".")
        if other_gaps:
            notes.append("Additional gaps: " + ", ".join(other_gaps) + ".")
        notes.append("Open Dependencies for per-tool status labels and paths.")
        self._dependency_summary.setText("Dependency status: " + " ".join(notes))
        self._dependency_summary.setProperty("tone", _dependency_tone(records))
        self._dependency_summary.style().unpolish(self._dependency_summary)
        self._dependency_summary.style().polish(self._dependency_summary)

    def _refresh_form_guidance(self) -> None:
        source_paths = self._source_paths()
        source_count = len(source_paths)
        if source_count == 0:
            self._source_help_label.show()
            self._source_help_label.setText("Add folders for batch review or individual files for a focused proof.")
            self._source_summary_label.setText("No sources selected yet. Inputs stay read-only.")
        else:
            self._source_help_label.hide()
            recursive_text = "with subfolders" if self._include_subfolders_checkbox.isChecked() else "without subfolders"
            preview_sources = ", ".join(Path(path).name or path for path in source_paths[:3])
            if source_count > 3:
                preview_sources = f"{preview_sources}, +{source_count - 3} more"
            self._source_summary_label.setText(
                f"Loaded {source_count} source item(s) {recursive_text}: {preview_sources}. Source media stays read-only."
            )

        notes: list[str] = []
        output_pdf = self._output_pdf_edit.text().strip()
        if not output_pdf:
            notes.append("Choose the PDF destination. CSV and JSON manifests write beside it when enabled.")
        else:
            pdf_path = Path(output_pdf).expanduser()
            notes.append("Preview-only PDF output is shareable. The app does not modify source media.")
            if self._export_stills_checkbox.isChecked():
                notes.append(f"PNG stills write to {pdf_path.parent / f'{pdf_path.stem}_stills'}.")
            if _output_inside_source_tree(pdf_path, source_paths):
                notes.append("Caution: this output is inside a selected source tree. Keep exports separate to avoid rescans.")

        path_mode = PathDisplayMode(str(self._path_display_combo.currentData()))
        if path_mode is PathDisplayMode.HIDDEN:
            notes.append("Path Privacy is Hidden. PDFs hide full source paths but keep clip identity.")
        elif path_mode is PathDisplayMode.BASENAME:
            notes.append("Path Privacy is Basename Only. PDFs keep filenames but omit parent folders.")
        else:
            notes.append("Path Privacy is Full Path for operator-facing review PDFs.")

        if str(self._layout_combo.currentData()) == ReportLayout.CLIP_DETAIL.value:
            notes.append("Layout A expands requested and actual capture detail for each clip.")
        else:
            notes.append("Layout B keeps the denser contact-sheet view with readable timecode labels and warnings.")

        self._output_note_label.setText(" ".join(notes))
        layout_label = self._layout_combo.currentText()
        privacy_label = self._path_display_combo.currentText()
        self._overview_status_label.setText(
            f"Layout: {layout_label} | Privacy: {privacy_label} | Sources: {source_count} | PDF: {'set' if output_pdf else 'missing'}"
        )
        readiness_lines: list[str] = []
        if source_count == 0:
            readiness_lines.append("Readiness: add at least one source file or folder.")
        elif not output_pdf:
            readiness_lines.append("Readiness: choose the output PDF path.")
        else:
            readiness_lines.append("Readiness: inputs and output are set. Start refreshes dependencies before launch.")

        hard_blockers = [
            _DEPENDENCY_LABELS.get(record.name, record.name)
            for record in self._last_dependencies
            if record.name in {"ffmpeg", "ffprobe"} and record.state is not AdapterDependencyState.AVAILABLE
        ]
        raw_gaps = [
            _DEPENDENCY_LABELS.get(record.name, record.name)
            for record in self._last_dependencies
            if record.name not in {"ffmpeg", "ffprobe", "mediainfo"} and record.state is not AdapterDependencyState.AVAILABLE
        ]
        if hard_blockers:
            readiness_lines.append(
                "Standard video is blocked until these core tools are available: " + ", ".join(hard_blockers) + "."
            )
        elif raw_gaps:
            readiness_lines.append(
                "RAW-only gaps remain visible without blocking standard clips: " + ", ".join(raw_gaps) + "."
            )
        else:
            readiness_lines.append("Dependency check is clear for the configured tool paths.")
        self._run_readiness_label.setText(" ".join(readiness_lines))
        self._update_progress_caption()

    def _adapter_settings(self) -> AdapterSettings:
        return AdapterSettings(
            ffmpeg_path=self._stored_settings.ffmpeg_path,
            ffprobe_path=self._stored_settings.ffprobe_path,
            mediainfo_path=self._stored_settings.mediainfo_path,
            braw_adapter_path=Path(self._stored_settings.braw_adapter_path).expanduser() if self._stored_settings.braw_adapter_path else None,
            r3d_adapter_path=Path(self._stored_settings.r3d_adapter_path).expanduser() if self._stored_settings.r3d_adapter_path else None,
            arri_art_cmd_path=Path(self._stored_settings.arri_art_cmd_path).expanduser() if self._stored_settings.arri_art_cmd_path else None,
        )

    def _start_batch(self) -> None:
        try:
            settings = self._build_app_settings()
        except ValueError as exc:
            self._set_banner(BannerState("error", "Cannot start batch.", str(exc)))
            QMessageBox.warning(self, "Invalid Settings", str(exc))
            return

        self._stored_settings = self._collect_form_settings()
        self._settings_store.save(self._stored_settings)
        self._refresh_dependency_summary()
        self._reset_progress()
        self._set_banner(BannerState("info", "Starting batch run...", "Dependency status refreshed before launch."))
        self._controller.start_batch(settings)

    def _cancel_batch(self) -> None:
        self._controller.cancel()
        self._set_banner(
            BannerState(
                "warning",
                "Cancel requested.",
                "No new clip work will start after the current in-flight step completes.",
            )
        )

    def _build_app_settings(self) -> AppSettings:
        source_paths = self._source_paths()
        if not source_paths:
            raise ValueError("Select at least one source file or folder.")
        output_pdf = self._output_pdf_edit.text().strip()
        if not output_pdf:
            raise ValueError("Select an output PDF path.")
        pdf_path = Path(output_pdf).expanduser()
        stills_dir = pdf_path.parent / f"{pdf_path.stem}_stills"
        return AppSettings.from_mapping(
            {
                "input": {
                    "paths": source_paths,
                    "recursive": self._include_subfolders_checkbox.isChecked(),
                },
                "capture": {
                    "middle_count": self._middle_count_spin.value(),
                    "profile": "preview_rec709_sdr",
                    "prefer_frame_index": True,
                },
                "report": {
                    "layout": str(self._layout_combo.currentData()),
                    "project_name": self._project_name_edit.text().strip() or None,
                    "include_failed_section": self._include_failed_checkbox.isChecked(),
                    "path_display": str(self._path_display_combo.currentData()),
                },
                "output": {
                    "pdf_path": str(pdf_path),
                    "export_stills": self._export_stills_checkbox.isChecked(),
                    "stills_dir": str(stills_dir) if self._export_stills_checkbox.isChecked() else None,
                    "write_csv": self._write_csv_checkbox.isChecked(),
                    "write_json": self._write_json_checkbox.isChecked(),
                },
                "adapters": {
                    "ffmpeg_path": self._stored_settings.ffmpeg_path,
                    "ffprobe_path": self._stored_settings.ffprobe_path,
                    "mediainfo_path": self._stored_settings.mediainfo_path,
                    "braw_adapter_path": self._stored_settings.braw_adapter_path,
                    "r3d_adapter_path": self._stored_settings.r3d_adapter_path,
                    "arri_art_cmd_path": self._stored_settings.arri_art_cmd_path,
                },
            }
        )

    def _collect_form_settings(self) -> GuiStoredSettings:
        output_pdf = self._output_pdf_edit.text().strip()
        return replace(
            self._stored_settings,
            source_paths=tuple(self._source_paths()),
            include_subfolders=self._include_subfolders_checkbox.isChecked(),
            output_pdf_path=output_pdf or None,
            last_output_dir=str(Path(output_pdf).expanduser().parent) if output_pdf else self._stored_settings.last_output_dir,
            project_name=self._project_name_edit.text().strip() or None,
            middle_count=self._middle_count_spin.value(),
            layout=str(self._layout_combo.currentData()),
            export_stills=self._export_stills_checkbox.isChecked(),
            write_csv=self._write_csv_checkbox.isChecked(),
            write_json=self._write_json_checkbox.isChecked(),
            include_failed_section=self._include_failed_checkbox.isChecked(),
            path_display=str(self._path_display_combo.currentData()),
        )

    def _reset_progress(self) -> None:
        self._progress_table.setRowCount(0)
        self._row_indexes.clear()
        self._row_states.clear()
        self._update_progress_caption()

    def _handle_progress_event(self, event: object) -> None:
        if isinstance(event, BatchStageEvent):
            detail = ""
            if event.total_clips is not None:
                remaining = max(event.total_clips - event.processed_clips, 0)
                detail = (
                    f"Processed {event.processed_clips} of {event.total_clips} clip(s). "
                    f"Remaining: {remaining}. Row order stays fixed as statuses stream."
                )
            tone = "warning" if event.event_type == "stage_cancelled" else "info"
            self._set_banner(BannerState(tone, event.message, detail))
            return

        if isinstance(event, DependencyStatusEvent):
            self._last_dependencies = event.dependencies
            self._refresh_dependency_summary()
            return

        if isinstance(event, RowDiscoveredEvent):
            self._upsert_row(ProgressRowState.from_progress_row(event.row), event.row_index)
            return

        if isinstance(event, RowUpdatedEvent):
            self._upsert_row(ProgressRowState.from_progress_row(event.row), event.row_index)

    def _upsert_row(self, state: ProgressRowState, row_index: int) -> None:
        self._row_indexes[state.candidate_id] = row_index
        self._row_states[state.candidate_id] = state
        while self._progress_table.rowCount() <= row_index:
            self._progress_table.insertRow(self._progress_table.rowCount())

        values = [state.clip_name, state.format_label, state.probe, state.capture, state.pdf, state.warning]
        background = _row_background(state)
        for column, value in enumerate(values):
            item = self._progress_table.item(row_index, column)
            if item is None:
                item = QTableWidgetItem()
                self._progress_table.setItem(row_index, column, item)
            item.setText(value)
            item.setToolTip(value or "No warning recorded.")
            item.setForeground(_status_color(value))
            item.setBackground(background)
            if column in {2, 3, 4}:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                font = QFont(item.font())
                font.setBold(True)
                item.setFont(font)
            elif column == 0:
                font = QFont(item.font())
                font.setBold(True)
                item.setFont(font)
            else:
                alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                if column == 5 and value:
                    alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
                item.setTextAlignment(alignment)

        self._progress_table.setRowHeight(row_index, 46 if state.warning else 34)
        self._update_progress_caption()

    def _handle_batch_finished(self, outcome: BatchRunOutcome) -> None:
        summary = outcome.report.summary
        failed_count = summary.probe_failed_count + summary.decode_failed_count

        summary_lines = [
            (
                "Counts: "
                f"total={summary.total_clips} success={summary.success_count} "
                f"partial={summary.partial_success_count} failed={failed_count} skipped={summary.skipped_count}"
            )
        ]
        if outcome.pdf_path is not None:
            summary_lines.append(f"PDF: {outcome.pdf_path}")
        if outcome.csv_path is not None:
            summary_lines.append(f"CSV: {outcome.csv_path}")
        if outcome.json_path is not None:
            summary_lines.append(f"JSON: {outcome.json_path}")
        if _uses_fallback_timecode(outcome):
            summary_lines.append("Timecode note: one or more captures used fallback sources instead of native adapter timecode.")

        if summary.status.value == "cancelled":
            summary_lines.insert(1, "No new work was started after cancel. Existing diagnostics remain visible in the table.")
            self._set_banner(BannerState("warning", "Batch cancelled.", "\n".join(summary_lines)))
            return

        if outcome.exit_code != 0:
            error_detail = outcome.error_message or "Fatal output generation failure."
            self._set_banner(BannerState("error", "Batch failed.", "\n".join([error_detail, *summary_lines])))
            return

        if failed_count > 0 or summary.partial_success_count > 0:
            summary_lines.insert(1, "Completed outputs remain valid, but partial or failed clips are still visible below and in the report.")
        self._set_banner(BannerState("success", "Batch complete.", "\n".join(summary_lines)))

    def _handle_batch_failed(self, message: str) -> None:
        self._set_banner(BannerState("error", "Worker failure.", message))

    def _set_running(self, running: bool) -> None:
        controls = (
            self._add_files_button,
            self._add_folder_button,
            self._remove_source_button,
            self._clear_sources_button,
            self._output_pdf_button,
            self._dependency_button,
            self._start_button,
            self._sources_list,
            self._include_subfolders_checkbox,
            self._output_pdf_edit,
            self._project_name_edit,
            self._middle_count_spin,
            self._layout_combo,
            self._path_display_combo,
            self._export_stills_checkbox,
            self._write_csv_checkbox,
            self._write_json_checkbox,
            self._include_failed_checkbox,
        )
        for widget in controls:
            widget.setEnabled(not running)
        self._cancel_button.setEnabled(running)

    def _set_banner(self, state: BannerState) -> None:
        self._banner_label.setText(state.message)
        self._banner_label.setProperty("tone", state.tone)
        self._banner_label.style().unpolish(self._banner_label)
        self._banner_label.style().polish(self._banner_label)
        if state.detail:
            self._run_summary_label.setText(state.detail)
            self._run_summary_label.show()
        else:
            self._run_summary_label.hide()
            self._run_summary_label.clear()

    def _update_progress_caption(self) -> None:
        total_rows = len(self._row_states)
        if total_rows == 0:
            self._progress_caption_label.setText(
                "Rows appear as clips are discovered. Text labels remain authoritative; row tinting only reinforces status."
            )
            return

        success_count = 0
        partial_count = 0
        failed_count = 0
        for state in self._row_states.values():
            if state.report_status is ClipStatus.SUCCESS:
                success_count += 1
            elif state.report_status in {ClipStatus.PARTIAL_SUCCESS, ClipStatus.METADATA_INCOMPLETE}:
                partial_count += 1
            elif state.report_status is not None:
                failed_count += 1

        self._progress_caption_label.setText(
            f"{total_rows} row(s) discovered. Completed so far: success={success_count} "
            f"partial={partial_count} failed={failed_count}. Text labels are authoritative; color is supplemental."
        )

    def _source_paths(self) -> list[str]:
        return [self._sources_list.item(index).text() for index in range(self._sources_list.count())]

    @staticmethod
    def _select_combo_data(combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)


def _source_item(path: str) -> QListWidgetItem:
    item = QListWidgetItem(path)
    item.setToolTip(path)
    return item


def _field_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setProperty("role", "helper")
    return label


def _section_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setProperty("role", "summary")
    return label


def _allow_compact_wrap(label: QLabel) -> None:
    label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)


def _dependency_tone(records: tuple[DependencyRecord, ...]) -> str:
    if all(record.state is AdapterDependencyState.AVAILABLE for record in records):
        return "success"

    hard_blockers = {
        record.name
        for record in records
        if record.name in {"ffmpeg", "ffprobe"} and record.state is not AdapterDependencyState.AVAILABLE
    }
    if hard_blockers:
        return "error"
    return "warning"


def _status_color(value: str) -> QColor:
    palette = {
        "running": QColor("#1D5F8C"),
        "success": QColor("#1E7A46"),
        "included": QColor("#1E7A46"),
        "partial": QColor("#A35A00"),
        "skipped": QColor("#5D6470"),
        "waiting": QColor("#5D6470"),
        "fail": QColor("#B42318"),
        "failed": QColor("#B42318"),
    }
    return palette.get(value, QColor("#1F2328"))


def _row_background(state: ProgressRowState) -> QColor:
    if state.report_status is ClipStatus.SUCCESS:
        return QColor("#EEF7F1")
    if state.report_status in {ClipStatus.PARTIAL_SUCCESS, ClipStatus.METADATA_INCOMPLETE}:
        return QColor("#FFF5EA")
    if state.report_status is not None:
        return QColor("#FDEEEE")
    if state.warning:
        return QColor("#FFF9F1")
    return QColor("#FBFAF7")


def _output_inside_source_tree(output_pdf: Path, source_paths: list[str]) -> bool:
    output_parent = _safe_resolve(output_pdf.parent)
    for source_text in source_paths:
        source_path = Path(source_text).expanduser()
        source_root = source_path if source_path.suffix == "" else source_path.parent
        if _is_relative_to(output_parent, _safe_resolve(source_root)):
            return True
    return False


def _safe_resolve(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return path


def _is_relative_to(candidate: Path, target: Path) -> bool:
    try:
        candidate.relative_to(target)
    except ValueError:
        return False
    return True


def _uses_fallback_timecode(outcome: BatchRunOutcome) -> bool:
    for item in outcome.report.items:
        for capture in item.captures:
            if capture.actual_timecode and capture.actual_timecode_source not in {None, TimecodeSource.NATIVE_ADAPTER}:
                return True
    return False
