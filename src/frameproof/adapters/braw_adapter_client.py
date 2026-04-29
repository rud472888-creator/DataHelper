from __future__ import annotations

from frameproof.adapters._json_subprocess_adapter import JsonSubprocessAdapterClient
from frameproof.core.models import FormatFamily


class BRAWAdapterClient(JsonSubprocessAdapterClient):
    name = "braw_adapter"
    format_families = (FormatFamily.BRAW.value,)
    required_tools = ("braw_adapter",)
    format_family = FormatFamily.BRAW
