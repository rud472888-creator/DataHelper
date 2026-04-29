from __future__ import annotations

from pathlib import Path

from frameproof.adapters.base import CaptureAdapter
from frameproof.core.models import (
    AdapterError,
    AdapterErrorCode,
    CapturePlan,
    CaptureProfile,
    CaptureResult,
    CaptureStatus,
    ClipCandidate,
)


def run_captures(
    adapter: CaptureAdapter,
    candidate: ClipCandidate,
    plan: CapturePlan,
    *,
    profile_name: str,
    staging_dir: Path,
) -> tuple[CaptureResult, ...]:
    profile = CaptureProfile(name=profile_name)
    staging_dir.mkdir(parents=True, exist_ok=True)

    try:
        results = tuple(adapter.capture(candidate, plan, profile, staging_dir))
    except Exception as exc:
        return _decode_failed_results(plan, f"Capture execution failed: {exc}")

    if len(results) != len(plan.requests):
        return _decode_failed_results(plan, "Adapter returned an unexpected number of capture results")

    actual_labels = tuple(result.label for result in results)
    expected_labels = tuple(request.label for request in plan.requests)
    if actual_labels != expected_labels:
        return _decode_failed_results(plan, "Adapter returned capture results with an invalid label sequence")

    return results


def _decode_failed_results(plan: CapturePlan, message: str) -> tuple[CaptureResult, ...]:
    error = AdapterError(code=AdapterErrorCode.DECODE_FAILED, message=message)
    return tuple(
        CaptureResult(
            label=request.label,
            requested_ratio=request.requested_ratio,
            requested_frame_index=request.requested_frame_index,
            requested_seconds=request.requested_seconds,
            duplicate_of=request.duplicate_of,
            status=CaptureStatus.DECODE_FAILED,
            errors=(error,),
        )
        for request in plan.requests
    )
