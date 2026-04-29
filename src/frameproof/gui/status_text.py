from __future__ import annotations

from frameproof.core.dependency_inspector import DependencyRecord
from frameproof.core.models import AdapterDependencyState

_DEPENDENCY_STATE_LABELS: dict[AdapterDependencyState, str] = {
    AdapterDependencyState.AVAILABLE: "available",
    AdapterDependencyState.CONFIGURED_MISSING: "configured path missing",
    AdapterDependencyState.NOT_CONFIGURED: "not configured",
    AdapterDependencyState.RUNTIME_ERROR: "runtime startup failure",
}


def dependency_state_label(state: AdapterDependencyState) -> str:
    return _DEPENDENCY_STATE_LABELS[AdapterDependencyState(state)]


def dependency_status_summary(records: tuple[DependencyRecord, ...]) -> str:
    return ", ".join(f"{record.name}={dependency_state_label(record.state)}" for record in records)
