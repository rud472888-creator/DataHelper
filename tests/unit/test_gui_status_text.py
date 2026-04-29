from __future__ import annotations

from frameproof.core.dependency_inspector import DependencyRecord
from frameproof.core.models import AdapterDependencyState
from frameproof.gui.status_text import dependency_state_label, dependency_status_summary


def test_dependency_state_label_matches_stage_4d_ui_spec() -> None:
    assert dependency_state_label(AdapterDependencyState.AVAILABLE) == "available"
    assert dependency_state_label(AdapterDependencyState.CONFIGURED_MISSING) == "configured path missing"
    assert dependency_state_label(AdapterDependencyState.NOT_CONFIGURED) == "not configured"
    assert dependency_state_label(AdapterDependencyState.RUNTIME_ERROR) == "runtime startup failure"


def test_dependency_status_summary_uses_operator_facing_labels() -> None:
    records = (
        DependencyRecord(
            name="ffmpeg",
            state=AdapterDependencyState.AVAILABLE,
            configured_path="ffmpeg",
            resolved_path="/usr/bin/ffmpeg",
        ),
        DependencyRecord(
            name="braw_adapter",
            state=AdapterDependencyState.CONFIGURED_MISSING,
            configured_path="/missing/braw_adapter",
            resolved_path=None,
        ),
        DependencyRecord(
            name="r3d_adapter",
            state=AdapterDependencyState.NOT_CONFIGURED,
            configured_path=None,
            resolved_path=None,
        ),
        DependencyRecord(
            name="arri_art_cmd",
            state=AdapterDependencyState.RUNTIME_ERROR,
            configured_path="/usr/local/bin/arri_art_cmd",
            resolved_path="/usr/local/bin/arri_art_cmd",
        ),
    )

    assert dependency_status_summary(records) == (
        "ffmpeg=available, "
        "braw_adapter=configured path missing, "
        "r3d_adapter=not configured, "
        "arri_art_cmd=runtime startup failure"
    )
