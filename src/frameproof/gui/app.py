from __future__ import annotations

import sys
from pathlib import Path
from typing import cast

from frameproof.gui.batch_controller import BatchController
from frameproof.gui.main_window import MainWindow
from frameproof.gui.qt import QApplication, QFont, qt_runtime_available
from frameproof.gui.settings_store import SettingsStore


def create_application() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    else:
        app = cast(QApplication, app)
    app.setApplicationName("Frame Proof")
    app.setOrganizationName("FrameProof")
    app.setFont(QFont("IBM Plex Sans", 10))
    app.setStyleSheet(
        """
        QWidget {
            background: #F3F1EA;
            color: #1F2328;
        }
        QMainWindow {
            background: #F3F1EA;
        }
        QGroupBox {
            background: #FBFAF7;
            border: 1px solid #C9C2B8;
            border-radius: 10px;
            font-weight: 600;
            margin-top: 10px;
            padding: 12px 12px 12px 12px;
            padding-top: 16px;
        }
        QGroupBox::title {
            left: 12px;
            padding: 0 4px;
            color: #5D6470;
        }
        QLabel[role="summary"] {
            background: #F6F1E8;
            border: 1px solid #DED6C9;
            border-radius: 8px;
            color: #1F2328;
            padding: 8px 10px;
        }
        QPushButton {
            background: #E7E0D5;
            border: 1px solid #C9C2B8;
            border-radius: 6px;
            padding: 7px 14px;
            min-height: 18px;
        }
        QPushButton[variant="primary"] {
            background: #1D5F8C;
            color: #FBFAF7;
            border-color: #184D72;
            font-weight: 700;
        }
        QPushButton[variant="danger"] {
            background: #B42318;
            color: #FBFAF7;
            border-color: #8F1B12;
            font-weight: 700;
        }
        QPushButton[variant="quiet"] {
            background: #F6F1E8;
            color: #1F2328;
        }
        QPushButton:hover {
            border-color: #9C917F;
        }
        QPushButton:focus {
            border: 2px solid #1D5F8C;
            padding: 6px 13px;
        }
        QPushButton:disabled {
            color: #8A8F98;
            background: #EFEAE2;
            border-color: #D8D2C7;
        }
        QLineEdit, QListWidget, QTableWidget, QComboBox, QSpinBox {
            background: #FBFAF7;
            border: 1px solid #C9C2B8;
            border-radius: 6px;
            padding: 5px 6px;
            selection-background-color: #D5E6F2;
        }
        QLineEdit:focus, QListWidget:focus, QTableWidget:focus, QComboBox:focus, QSpinBox:focus {
            border: 2px solid #1D5F8C;
        }
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox:focus {
            outline: 2px solid #1D5F8C;
        }
        QListWidget::item {
            padding: 5px 4px;
        }
        QListWidget::item:selected, QTableWidget::item:selected {
            background: #DCE9EF;
            color: #1F2328;
        }
        QHeaderView::section {
            background: #EEE7DC;
            color: #5D6470;
            border: none;
            border-bottom: 1px solid #C9C2B8;
            padding: 8px 6px;
            font-weight: 700;
        }
        QTableWidget {
            gridline-color: transparent;
            alternate-background-color: #F7F4ED;
        }
        QLabel[role="helper"] {
            color: #5D6470;
        }
        QLabel[tone="info"] {
            background: #EAF3F8;
            border: 1px solid #A7C6D8;
            border-radius: 8px;
            padding: 10px 12px;
        }
        QLabel[tone="success"] {
            background: #EAF6EF;
            border: 1px solid #A5CDB3;
            border-radius: 8px;
            padding: 10px 12px;
        }
        QLabel[tone="warning"] {
            background: #FFF3E8;
            border: 1px solid #E1BF96;
            border-radius: 8px;
            padding: 10px 12px;
        }
        QLabel[tone="error"] {
            background: #FDECEC;
            border: 1px solid #E2A8A8;
            border-radius: 8px;
            padding: 10px 12px;
        }
        QLabel[state="available"] {
            color: #1E7A46;
            font-weight: 700;
        }
        QLabel[state="configured_missing"], QLabel[state="not_configured"] {
            color: #A35A00;
            font-weight: 700;
        }
        QLabel[state="runtime_error"] {
            color: #B42318;
            font-weight: 700;
        }
        """
    )
    return app


def create_main_window(settings_path: Path | None = None) -> MainWindow:
    store = SettingsStore(settings_path)
    controller = BatchController()
    return MainWindow(store, controller)


def launch_gui(settings_path: Path | None = None) -> int:
    if not qt_runtime_available():
        print(
            "PySide6 runtime is unavailable on this host. Use --smoke-test for structure-only GUI validation.",
            file=sys.stderr,
        )
        return 2
    app = create_application()
    window = create_main_window(settings_path)
    window.show()
    return app.exec()
