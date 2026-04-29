from __future__ import annotations

from pathlib import Path
from typing import Mapping

from frameproof.adapters._json_subprocess_adapter import JsonSubprocessAdapterClient
from frameproof.core.models import ClipCandidate, FormatFamily


class R3DAdapterClient(JsonSubprocessAdapterClient):
    name = "r3d_adapter"
    format_families = (FormatFamily.R3D.value,)
    required_tools = ("r3d_adapter",)
    format_family = FormatFamily.R3D

    def _logical_clip_name(
        self,
        candidate: ClipCandidate,
        response: Mapping[str, object],
    ) -> str | None:
        clip_payload = response.get("clip")
        if isinstance(clip_payload, dict):
            raw_name = clip_payload.get("logical_clip_name")
            if isinstance(raw_name, str) and raw_name.strip():
                return raw_name.strip()
        if len(candidate.part_files) <= 1:
            return None
        stem = Path(candidate.source_path).stem
        base, _, suffix = stem.rpartition("_")
        return base if suffix.isdigit() and base else stem
