from __future__ import annotations

from dataclasses import dataclass

from frameproof.core.models import ClipStatus
from frameproof.core.progress_events import ProgressRow


@dataclass(frozen=True)
class ProgressRowState:
    candidate_id: str
    clip_name: str
    format_label: str
    probe: str
    capture: str
    pdf: str
    warning: str
    report_status: ClipStatus | None

    @classmethod
    def from_progress_row(cls, row: ProgressRow) -> ProgressRowState:
        return cls(
            candidate_id=row.candidate_id,
            clip_name=row.clip_name,
            format_label=row.format_family.value,
            probe=row.probe,
            capture=row.capture,
            pdf=row.pdf,
            warning=row.warning,
            report_status=row.report_status,
        )


@dataclass(frozen=True)
class BannerState:
    tone: str
    message: str
    detail: str = ""

    def text(self) -> str:
        if not self.detail:
            return self.message
        return f"{self.message}\n{self.detail}"
