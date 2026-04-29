from __future__ import annotations

from dataclasses import dataclass

from frameproof.core.adapter_resolver import AdapterSelection
from frameproof.core.models import (
    AdapterDependencyState,
    AdapterError,
    AdapterErrorCode,
    ClipStatus,
    ProbeResult,
)


@dataclass(frozen=True)
class ProbeExecution:
    selection: AdapterSelection
    result: ProbeResult


def run_probe(selection: AdapterSelection) -> ProbeExecution:
    candidate_metadata = {
        "candidate_id": selection.candidate.candidate_id,
        "source_path": selection.candidate.source_path,
        "clip_name": selection.candidate.source_path.rsplit("/", 1)[-1],
    }
    if selection.adapter is None:
        message = selection.terminal_message or "Unsupported format"
        return ProbeExecution(
            selection=selection,
            result=ProbeResult(
                ok=False,
                adapter_name=selection.adapter_name,
                format_family=selection.format_family,
                status=selection.terminal_status or ClipStatus.UNSUPPORTED_FORMAT,
                errors=(
                    AdapterError(
                        code=AdapterErrorCode.UNSUPPORTED_FORMAT,
                        message=message,
                    ),
                ),
                metadata_raw=candidate_metadata,
            ),
        )

    availability = selection.adapter.is_available()
    if availability is not AdapterDependencyState.AVAILABLE:
        detail = dict(selection.adapter.dependency_details())
        dependency_name = detail.get("dependency_name")
        message = (
            f"{dependency_name} is not available"
            if isinstance(dependency_name, str) and dependency_name
            else f"{selection.adapter_name} dependencies are unavailable"
        )
        return ProbeExecution(
            selection=selection,
            result=ProbeResult(
                ok=False,
                adapter_name=selection.adapter_name,
                format_family=selection.format_family,
                status=ClipStatus.DEPENDENCY_MISSING,
                errors=(
                    AdapterError(
                        code=AdapterErrorCode.DEPENDENCY_MISSING,
                        message=message,
                        detail=detail,
                    ),
                ),
                metadata_raw=candidate_metadata,
            ),
        )

    try:
        return ProbeExecution(selection=selection, result=selection.adapter.probe(selection.candidate))
    except Exception as exc:
        return ProbeExecution(
            selection=selection,
            result=ProbeResult(
                ok=False,
                adapter_name=selection.adapter_name,
                format_family=selection.format_family,
                status=ClipStatus.PROBE_FAILED,
                errors=(
                    AdapterError(
                        code=AdapterErrorCode.PROBE_FAILED,
                        message="Probe execution failed",
                        detail={"exception": str(exc)},
                    ),
                ),
                metadata_raw=candidate_metadata,
            ),
        )
