from __future__ import annotations

import os
import subprocess
import sys
from functools import lru_cache
from typing import TYPE_CHECKING, Any, cast


@lru_cache(maxsize=1)
def _qt_runtime_available() -> bool:
    if os.environ.get("FRAMEPROOF_FORCE_QT_FALLBACK") == "1":
        return False
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "from PySide6.QtWidgets import QApplication; app = QApplication([]); print('ok')",
        ],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "QT_QPA_PLATFORM": os.environ.get("QT_QPA_PLATFORM", "offscreen")},
    )
    return completed.returncode == 0 and "ok" in completed.stdout


QT_RUNTIME_AVAILABLE = _qt_runtime_available()

if TYPE_CHECKING:
    from PySide6.QtCore import QObject, QSettings, QStandardPaths, QThread, Qt, Signal
    from PySide6.QtGui import QColor, QFont
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QFileDialog,
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
        QVBoxLayout,
        QWidget,
    )
else:
    if QT_RUNTIME_AVAILABLE:
        from PySide6 import QtCore as _QtCore
        from PySide6 import QtGui as _QtGui
        from PySide6 import QtWidgets as _QtWidgets
    else:
        from . import _qt_fallback as _fallback

        _QtCore = cast(Any, _fallback)
        _QtGui = cast(Any, _fallback)
        _QtWidgets = cast(Any, _fallback)

    QObject = _QtCore.QObject
    QSettings = _QtCore.QSettings
    QStandardPaths = _QtCore.QStandardPaths
    QThread = _QtCore.QThread
    Qt = _QtCore.Qt
    Signal = _QtCore.Signal

    QColor = _QtGui.QColor
    QFont = _QtGui.QFont

    QAbstractItemView = _QtWidgets.QAbstractItemView
    QApplication = _QtWidgets.QApplication
    QCheckBox = _QtWidgets.QCheckBox
    QComboBox = _QtWidgets.QComboBox
    QDialog = _QtWidgets.QDialog
    QFileDialog = _QtWidgets.QFileDialog
    QGridLayout = _QtWidgets.QGridLayout
    QGroupBox = _QtWidgets.QGroupBox
    QHeaderView = _QtWidgets.QHeaderView
    QHBoxLayout = _QtWidgets.QHBoxLayout
    QLabel = _QtWidgets.QLabel
    QLineEdit = _QtWidgets.QLineEdit
    QListWidget = _QtWidgets.QListWidget
    QListWidgetItem = _QtWidgets.QListWidgetItem
    QMainWindow = _QtWidgets.QMainWindow
    QMessageBox = _QtWidgets.QMessageBox
    QPushButton = _QtWidgets.QPushButton
    QSizePolicy = _QtWidgets.QSizePolicy
    QSpinBox = _QtWidgets.QSpinBox
    QTableWidget = _QtWidgets.QTableWidget
    QTableWidgetItem = _QtWidgets.QTableWidgetItem
    QVBoxLayout = _QtWidgets.QVBoxLayout
    QWidget = _QtWidgets.QWidget

__all__ = [
    "QAbstractItemView",
    "QApplication",
    "QCheckBox",
    "QColor",
    "QComboBox",
    "QDialog",
    "QFileDialog",
    "QFont",
    "QGridLayout",
    "QGroupBox",
    "QHeaderView",
    "QHBoxLayout",
    "QLabel",
    "QLineEdit",
    "QListWidget",
    "QListWidgetItem",
    "QMainWindow",
    "QMessageBox",
    "QObject",
    "QPushButton",
    "QSettings",
    "QSizePolicy",
    "QSpinBox",
    "QStandardPaths",
    "QTableWidget",
    "QTableWidgetItem",
    "QThread",
    "Qt",
    "QVBoxLayout",
    "QWidget",
    "Signal",
    "QT_RUNTIME_AVAILABLE",
    "qt_runtime_available",
]


def qt_runtime_available() -> bool:
    return QT_RUNTIME_AVAILABLE
