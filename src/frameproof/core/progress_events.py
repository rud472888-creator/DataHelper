from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeAlias

from frameproof.core.dependency_inspector import DependencyRecord
from frameproof.core.models import ClipStatus, FormatFamily, ReportItem


@dataclass(frozen=True)
class ProgressRow:
    candidate_id: str
    clip_name: str
    format_family: FormatFamily
    probe: str = "waiting"
    capture: str = "waiting"
    pdf: str = ""
    warning: str = ""
    report_status: ClipStatus | None = None


@dataclass(frozen=True)
class BatchStageEvent:
    event_type: str
    stage: str
    message: str
    processed_clips: int = 0
    total_clips: int | None = None


@dataclass(frozen=True)
class DependencyStatusEvent:
    dependencies: tuple[DependencyRecord, ...]
    event_type: str = "dependencies_refreshed"


@dataclass(frozen=True)
class RowDiscoveredEvent:
    row_index: int
    row: ProgressRow
    event_type: str = "row_discovered"


@dataclass(frozen=True)
class RowUpdatedEvent:
    row_index: int
    row: ProgressRow
    report_item: ReportItem | None = None
    event_type: str = "row_updated"


BatchProgressEvent: TypeAlias = BatchStageEvent | DependencyStatusEvent | RowDiscoveredEvent | RowUpdatedEvent
BatchProgressCallback: TypeAlias = Callable[[BatchProgressEvent], None]


def warning_summary(warnings: tuple[str, ...], error_messages: tuple[str, ...]) -> str:
    values = [*warnings, *error_messages]
    if not values:
        return ""
    return " | ".join(values[:2])
