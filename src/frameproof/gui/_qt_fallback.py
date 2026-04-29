from __future__ import annotations

import configparser
import json
import threading
from enum import Enum, IntEnum, IntFlag
from pathlib import Path
from typing import ClassVar, cast, overload


class _BoundSignal:
    def __init__(self) -> None:
        self._callbacks: list[object] = []

    def connect(self, callback: object) -> None:
        self._callbacks.append(callback)

    def emit(self, *args: object, **kwargs: object) -> None:
        for callback in list(self._callbacks):
            assert callable(callback)
            try:
                callback(*args, **kwargs)
            except TypeError:
                callback()


class _SignalDescriptor:
    def __set_name__(self, owner: type[object], name: str) -> None:
        del owner
        self._name = f"__signal_{name}"

    @overload
    def __get__(self, instance: None, owner: type[object] | None = None) -> _SignalDescriptor: ...

    @overload
    def __get__(self, instance: object, owner: type[object] | None = None) -> _BoundSignal: ...

    def __get__(self, instance: object | None, owner: type[object] | None = None) -> _BoundSignal | _SignalDescriptor:
        del owner
        if instance is None:
            return self
        signal = cast(_BoundSignal | None, getattr(instance, self._name, None))
        if signal is None:
            signal = _BoundSignal()
            setattr(instance, self._name, signal)
        return signal


def Signal(*_args: object) -> _SignalDescriptor:
    return _SignalDescriptor()


class QObject:
    def __init__(self, parent: object | None = None) -> None:
        self._parent = parent

    def moveToThread(self, thread: object) -> None:
        self._thread = thread

    def deleteLater(self) -> None:
        return None


class QThread(QObject):
    started = Signal()
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            self.started.emit()
        finally:
            self.finished.emit()

    def quit(self, *_args: object, **_kwargs: object) -> None:
        return None


class Qt:
    class TextInteractionFlag(IntFlag):
        NoTextInteraction = 0
        TextSelectableByMouse = 1

    class TextElideMode(IntEnum):
        ElideMiddle = 0

    class AlignmentFlag(IntFlag):
        AlignLeft = 1
        AlignRight = 2
        AlignHCenter = 4
        AlignTop = 8
        AlignBottom = 16
        AlignVCenter = 32
        AlignCenter = AlignHCenter | AlignVCenter


class QColor:
    def __init__(self, value: str) -> None:
        self.value = value


class QFont:
    def __init__(self, family: str | QFont = "", point_size: int = 10) -> None:
        self.family: str
        self.point_size: int
        self.bold: bool
        if isinstance(family, QFont):
            self.family = family.family
            self.point_size = family.point_size
            self.bold = family.bold
            return
        self.family = family
        self.point_size = point_size
        self.bold = False

    def setBold(self, value: bool) -> None:
        self.bold = value


class _Style:
    def unpolish(self, widget: object) -> None:
        del widget

    def polish(self, widget: object) -> None:
        del widget


class QSize:
    def __init__(self, width: int = 0, height: int = 0) -> None:
        self._width = width
        self._height = height

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height


class QSizePolicy:
    class Policy(IntEnum):
        Ignored = 0
        Preferred = 1


class QApplication(QObject):
    _instance: ClassVar[QApplication | None] = None

    def __init__(self, args: list[str]) -> None:
        super().__init__()
        self._args = args
        self._style_sheet = ""
        self._font = QFont()
        self._application_name = ""
        self._organization_name = ""
        QApplication._instance = self

    @classmethod
    def instance(cls) -> QApplication | None:
        return cls._instance

    def setApplicationName(self, name: str) -> None:
        self._application_name = name

    def setOrganizationName(self, name: str) -> None:
        self._organization_name = name

    def setFont(self, font: QFont) -> None:
        self._font = font

    def setStyleSheet(self, style_sheet: str) -> None:
        self._style_sheet = style_sheet

    def processEvents(self) -> None:
        return None

    def exec(self) -> int:
        return 0


class QWidget(QObject):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._visible = True
        self._enabled = True
        self._text = ""
        self._tool_tip = ""
        self._properties: dict[str, object] = {}
        self._style = _Style()
        self._layout: object | None = None
        self._width = 640
        self._height = 480
        self._minimum_size = QSize()
        self._window_title = ""

    def show(self) -> None:
        self._visible = True

    def hide(self) -> None:
        self._visible = False

    def close(self) -> None:
        self.hide()

    def isVisible(self) -> bool:
        return self._visible

    def setEnabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def setProperty(self, key: str, value: object) -> None:
        self._properties[key] = value

    def property(self, key: str) -> object | None:
        return self._properties.get(key)

    def style(self) -> _Style:
        return self._style

    def resize(self, width: int, height: int) -> None:
        self._width = width
        self._height = height

    def width(self) -> int:
        return self._width

    def height(self) -> int:
        return self._height

    def minimumSizeHint(self) -> QSize:
        return self._minimum_size

    def setMinimumHeight(self, height: int) -> None:
        if height > self._minimum_size.height():
            self._minimum_size = QSize(self._minimum_size.width(), height)

    def setSizePolicy(self, horizontal: object, vertical: object) -> None:
        del horizontal, vertical

    def setWordWrap(self, enabled: bool) -> None:
        del enabled

    def setTextInteractionFlags(self, flags: object) -> None:
        del flags

    def setToolTip(self, text: str) -> None:
        self._tool_tip = text

    def toolTip(self) -> str:
        return self._tool_tip

    def setWindowTitle(self, title: str) -> None:
        self._window_title = title

    def setLayout(self, layout: object) -> None:
        self._layout = layout

    @staticmethod
    def setTabOrder(first: object, second: object) -> None:
        del first, second


class QMainWindow(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._central_widget: QWidget | None = None

    def setCentralWidget(self, widget: QWidget) -> None:
        self._central_widget = widget


class QDialog(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._result = 0

    def exec(self) -> int:
        self.show()
        return self._result

    def accept(self) -> None:
        self._result = 1
        self.close()

    def reject(self) -> None:
        self._result = 0
        self.close()


class QLabel(QWidget):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._text = text

    def setText(self, text: str) -> None:
        self._text = text

    def text(self) -> str:
        return self._text

    def clear(self) -> None:
        self._text = ""


class QPushButton(QWidget):
    clicked = Signal(object)

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._text = text
        self._default = False

    def setDefault(self, value: bool) -> None:
        self._default = value

    def click(self) -> None:
        if self._enabled:
            self.clicked.emit(False)


class QCheckBox(QPushButton):
    toggled = Signal(bool)

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._checked = False

    def setChecked(self, value: bool) -> None:
        changed = self._checked != value
        self._checked = value
        if changed:
            self.toggled.emit(value)

    def isChecked(self) -> bool:
        return self._checked


class QLineEdit(QWidget):
    textChanged = Signal(str)

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._text = text
        self._placeholder = ""

    def setText(self, text: str) -> None:
        self._text = text
        self.textChanged.emit(text)

    def text(self) -> str:
        return self._text

    def setPlaceholderText(self, text: str) -> None:
        self._placeholder = text

    def setClearButtonEnabled(self, enabled: bool) -> None:
        del enabled


class QSpinBox(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._minimum = 0
        self._maximum = 99
        self._value = 0

    def setRange(self, minimum: int, maximum: int) -> None:
        self._minimum = minimum
        self._maximum = maximum
        self._value = min(max(self._value, minimum), maximum)

    def setValue(self, value: int) -> None:
        self._value = min(max(value, self._minimum), self._maximum)

    def value(self) -> int:
        return self._value


class QListWidgetItem:
    def __init__(self, text: str = "") -> None:
        self._text = text
        self._tool_tip = ""
        self._selected = False

    def text(self) -> str:
        return self._text

    def setToolTip(self, text: str) -> None:
        self._tool_tip = text


class QListWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._items: list[QListWidgetItem] = []

    def addItem(self, item: QListWidgetItem) -> None:
        self._items.append(item)

    def clear(self) -> None:
        self._items.clear()

    def count(self) -> int:
        return len(self._items)

    def item(self, index: int) -> QListWidgetItem:
        return self._items[index]

    def selectedItems(self) -> list[QListWidgetItem]:
        return [item for item in self._items if item._selected]

    def takeItem(self, index: int) -> QListWidgetItem:
        return self._items.pop(index)

    def row(self, item: QListWidgetItem) -> int:
        return self._items.index(item)

    def setSelectionMode(self, mode: object) -> None:
        del mode

    def setTextElideMode(self, mode: object) -> None:
        del mode


class QComboBox(QWidget):
    currentIndexChanged = Signal(int)

    class SizeAdjustPolicy(IntEnum):
        AdjustToMinimumContentsLengthWithIcon = 0

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._items: list[tuple[str, object]] = []
        self._current_index = -1

    def addItem(self, label: str, data: object = None) -> None:
        self._items.append((label, data))
        if self._current_index == -1:
            self._current_index = 0

    def setSizeAdjustPolicy(self, policy: object) -> None:
        del policy

    def setMinimumContentsLength(self, length: int) -> None:
        del length

    def currentData(self) -> object | None:
        if self._current_index < 0:
            return None
        return self._items[self._current_index][1]

    def currentText(self) -> str:
        if self._current_index < 0:
            return ""
        return self._items[self._current_index][0]

    def findData(self, value: object) -> int:
        for index, (_label, data) in enumerate(self._items):
            if data == value:
                return index
        return -1

    def setCurrentIndex(self, index: int) -> None:
        if 0 <= index < len(self._items):
            self._current_index = index
            self.currentIndexChanged.emit(index)


class QAbstractItemView:
    class EditTrigger(IntEnum):
        NoEditTriggers = 0

    class SelectionBehavior(IntEnum):
        SelectRows = 0

    class SelectionMode(IntEnum):
        SingleSelection = 0
        ExtendedSelection = 1


class QHeaderView:
    class ResizeMode(IntEnum):
        Stretch = 0
        ResizeToContents = 1

    def __init__(self) -> None:
        self._visible = True
        self._default_section_size = 0

    def setVisible(self, visible: bool) -> None:
        self._visible = visible

    def setDefaultSectionSize(self, size: int) -> None:
        self._default_section_size = size

    def setStretchLastSection(self, enabled: bool) -> None:
        del enabled

    def setSectionResizeMode(self, section: int, mode: object) -> None:
        del section, mode


class QTableWidgetItem:
    def __init__(self, text: str = "") -> None:
        self._text = text
        self._tool_tip = ""
        self._foreground: QColor | None = None
        self._background: QColor | None = None
        self._alignment = Qt.AlignmentFlag.AlignLeft
        self._font = QFont()

    def setText(self, text: str) -> None:
        self._text = text

    def text(self) -> str:
        return self._text

    def setToolTip(self, text: str) -> None:
        self._tool_tip = text

    def setForeground(self, color: QColor) -> None:
        self._foreground = color

    def setBackground(self, color: QColor) -> None:
        self._background = color

    def setTextAlignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._alignment = alignment

    def setFont(self, font: QFont) -> None:
        self._font = font

    def font(self) -> QFont:
        return self._font


class QTableWidget(QWidget):
    def __init__(self, rows: int, columns: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._row_count = rows
        self._column_count = columns
        self._items: dict[tuple[int, int], QTableWidgetItem] = {}
        self._horizontal_header = QHeaderView()
        self._vertical_header = QHeaderView()

    def setHorizontalHeaderLabels(self, labels: list[str]) -> None:
        self._horizontal_labels = labels

    def horizontalHeader(self) -> QHeaderView:
        return self._horizontal_header

    def verticalHeader(self) -> QHeaderView:
        return self._vertical_header

    def setEditTriggers(self, triggers: object) -> None:
        del triggers

    def setSelectionBehavior(self, behavior: object) -> None:
        del behavior

    def setSelectionMode(self, mode: object) -> None:
        del mode

    def setTextElideMode(self, mode: object) -> None:
        del mode

    def setShowGrid(self, show: bool) -> None:
        del show

    def setAlternatingRowColors(self, enabled: bool) -> None:
        del enabled

    def setWordWrap(self, enabled: bool) -> None:
        del enabled

    def rowCount(self) -> int:
        return self._row_count

    def insertRow(self, index: int) -> None:
        del index
        self._row_count += 1

    def setRowCount(self, count: int) -> None:
        self._row_count = count
        self._items = {
            (row, column): item
            for (row, column), item in self._items.items()
            if row < count
        }

    def setItem(self, row: int, column: int, item: QTableWidgetItem) -> None:
        self._items[(row, column)] = item

    def item(self, row: int, column: int) -> QTableWidgetItem | None:
        return self._items.get((row, column))

    def setRowHeight(self, row: int, height: int) -> None:
        del row, height


class QFileDialog:
    @staticmethod
    def getOpenFileNames(parent: object, title: str) -> tuple[list[str], str]:
        del parent, title
        return ([], "")

    @staticmethod
    def getExistingDirectory(parent: object, title: str) -> str:
        del parent, title
        return ""

    @staticmethod
    def getSaveFileName(parent: object, title: str, path: str, file_filter: str) -> tuple[str, str]:
        del parent, title, path, file_filter
        return ("", "")

    @staticmethod
    def getOpenFileName(parent: object, title: str) -> tuple[str, str]:
        del parent, title
        return ("", "")


class QMessageBox:
    class StandardButton(IntEnum):
        Ok = 0

    @staticmethod
    def warning(parent: object, title: str, text: str) -> StandardButton:
        del parent, title, text
        return QMessageBox.StandardButton.Ok


class _BaseLayout:
    def __init__(self, parent: QWidget | None = None) -> None:
        self._parent = parent
        self._items: list[object] = []
        if parent is not None:
            parent.setLayout(self)

    def addWidget(self, widget: QWidget, *args: object) -> None:
        del args
        self._items.append(widget)

    def addLayout(self, layout: _BaseLayout, stretch: int | None = None) -> None:
        del stretch
        self._items.append(layout)

    def addStretch(self, stretch: int = 0) -> None:
        self._items.append(("stretch", stretch))

    def setSpacing(self, spacing: int) -> None:
        del spacing

    def setContentsMargins(self, left: int, top: int, right: int, bottom: int) -> None:
        del left, top, right, bottom


class QVBoxLayout(_BaseLayout):
    pass


class QHBoxLayout(_BaseLayout):
    pass


class QGridLayout(_BaseLayout):
    def addWidget(self, widget: QWidget, *args: object) -> None:
        del args
        self._items.append(widget)

    def setHorizontalSpacing(self, spacing: int) -> None:
        del spacing

    def setVerticalSpacing(self, spacing: int) -> None:
        del spacing

    def setColumnStretch(self, column: int, stretch: int) -> None:
        del column, stretch


class QGroupBox(QWidget):
    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title


class QStandardPaths:
    class StandardLocation(IntEnum):
        AppConfigLocation = 0

    @staticmethod
    def writableLocation(location: StandardLocation) -> str:
        del location
        return str(Path.home() / ".frameproof")


class QSettings:
    class Format(Enum):
        IniFormat = "ini"

    def __init__(self, path: str, format_value: Format) -> None:
        del format_value
        self._path = Path(path)
        self._parser = configparser.ConfigParser()
        if self._path.exists():
            self._parser.read(self._path, encoding="utf-8")

    def value(self, key: str, default: object | None = None) -> object | None:
        section, option = key.split("/", 1)
        if not self._parser.has_option(section, option):
            return default
        raw = self._parser.get(section, option)
        try:
            loaded: object = json.loads(raw)
            return loaded
        except json.JSONDecodeError:
            return str(raw)

    def setValue(self, key: str, value: object) -> None:
        section, option = key.split("/", 1)
        if not self._parser.has_section(section):
            self._parser.add_section(section)
        self._parser.set(section, option, json.dumps(value))

    def sync(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as handle:
            self._parser.write(handle)
