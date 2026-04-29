from __future__ import annotations

from pathlib import Path

from frameproof.adapters.base import CaptureAdapter
from frameproof.core.models import (
    AdapterDependencyState,
    CapturePlan,
    CaptureProfile,
    CaptureRequest,
    CaptureResult,
    CaptureStatus,
    ClipCandidate,
    ClipStatus,
    FormatFamily,
    ProbeResult,
)


class DummyAdapter:
    name = "dummy"
    format_families = ("standard",)
    required_tools = ("dummy",)

    def is_available(self) -> AdapterDependencyState:
        return AdapterDependencyState.AVAILABLE

    def dependency_details(self) -> dict[str, object]:
        return {"required_tools": ["dummy"], "dependency_state": AdapterDependencyState.AVAILABLE.value}

    def probe(self, candidate: ClipCandidate) -> ProbeResult:
        return ProbeResult(
            ok=False,
            adapter_name=self.name,
            format_family=FormatFamily.STANDARD,
            status=ClipStatus.METADATA_INCOMPLETE,
        )

    def capture(
        self,
        candidate: ClipCandidate,
        plan: CapturePlan,
        profile: CaptureProfile,
        staging_dir: Path,
    ) -> tuple[CaptureResult, ...]:
        return (
            CaptureResult(
                label="Start",
                requested_ratio=0.0,
                requested_frame_index=0,
                actual_frame_index=0,
                status=CaptureStatus.SUCCESS,
            ),
        )


def test_capture_adapter_protocol_is_runtime_checkable() -> None:
    adapter = DummyAdapter()

    assert isinstance(adapter, CaptureAdapter)
    assert adapter.is_available() is AdapterDependencyState.AVAILABLE


def test_probe_and_capture_contract_models_cover_stage_three_statuses() -> None:
    adapter = DummyAdapter()
    candidate = ClipCandidate(candidate_id="candidate-1", source_path="/clips/A001_C001.mov")
    plan = CapturePlan(
        clip_id="clip-1",
        requests=(
            CaptureRequest(label="Start", requested_ratio=0.0, requested_frame_index=0),
            CaptureRequest(label="End", requested_ratio=1.0, requested_frame_index=9),
        ),
        middle_count=0,
        used_frame_count=True,
    )

    probe = adapter.probe(candidate)
    captures = adapter.capture(candidate, plan, CaptureProfile(name="preview"), Path("/tmp"))

    assert probe.status is ClipStatus.METADATA_INCOMPLETE
    assert captures[0].status is CaptureStatus.SUCCESS


def test_base_contract_import_is_side_effect_free() -> None:
    from frameproof.adapters import base

    assert base.ProbeAdapter.__name__ == "ProbeAdapter"
