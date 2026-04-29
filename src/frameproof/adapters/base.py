from __future__ import annotations

from pathlib import Path
from typing import Mapping, Protocol, Sequence, runtime_checkable

from frameproof.core.models import (
    AdapterDependencyState,
    CapturePlan,
    CaptureProfile,
    CaptureResult,
    ClipCandidate,
    ProbeResult,
)


@runtime_checkable
class ProbeAdapter(Protocol):
    name: str
    format_families: tuple[str, ...]
    required_tools: tuple[str, ...]

    def is_available(self) -> AdapterDependencyState:
        ...

    def dependency_details(self) -> Mapping[str, object]:
        ...

    def probe(self, candidate: ClipCandidate) -> ProbeResult:
        ...


@runtime_checkable
class CaptureAdapter(ProbeAdapter, Protocol):
    def capture(
        self,
        candidate: ClipCandidate,
        plan: CapturePlan,
        profile: CaptureProfile,
        staging_dir: Path,
    ) -> Sequence[CaptureResult]:
        ...
