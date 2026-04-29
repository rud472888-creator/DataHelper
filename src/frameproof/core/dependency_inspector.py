from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from frameproof.config.settings import AdapterSettings
from frameproof.core.models import AdapterDependencyState

_RUNTIME_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class DependencyRecord:
    name: str
    state: AdapterDependencyState
    configured_path: str | None
    resolved_path: str | None
    detail: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "state", AdapterDependencyState(self.state))
        object.__setattr__(self, "detail", dict(self.detail))

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "state": self.state.value,
            "configured_path": self.configured_path,
            "resolved_path": self.resolved_path,
            "detail": dict(self.detail),
        }


@dataclass(frozen=True)
class AdapterAvailability:
    adapter_name: str
    required_tools: tuple[str, ...]
    state: AdapterDependencyState
    dependencies: tuple[DependencyRecord, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "required_tools", tuple(self.required_tools))
        object.__setattr__(self, "state", AdapterDependencyState(self.state))
        object.__setattr__(self, "dependencies", tuple(self.dependencies))

    def error_detail(self) -> dict[str, object]:
        primary = next(
            (dependency for dependency in self.dependencies if dependency.state is not AdapterDependencyState.AVAILABLE),
            self.dependencies[0],
        )
        return {
            "adapter_name": self.adapter_name,
            "dependency_name": primary.name,
            "dependency_state": self.state.value,
            "required_tools": list(self.required_tools),
            "configured_path": primary.configured_path,
            "resolved_path": primary.resolved_path,
            "dependencies": [dependency.to_dict() for dependency in self.dependencies],
        }


class DependencyInspector:
    def __init__(self, settings: AdapterSettings) -> None:
        self._settings = settings
        self._cache: dict[str, DependencyRecord] = {}

    def ffmpeg(self) -> DependencyRecord:
        return self._inspect_command(
            cache_key="ffmpeg",
            name="ffmpeg",
            command=self._settings.ffmpeg_path,
            required_configuration=True,
        )

    def ffprobe(self) -> DependencyRecord:
        return self._inspect_command(
            cache_key="ffprobe",
            name="ffprobe",
            command=self._settings.ffprobe_path,
            required_configuration=True,
        )

    def mediainfo(self) -> DependencyRecord:
        return self._inspect_command(
            cache_key="mediainfo",
            name="mediainfo",
            command=self._settings.mediainfo_path,
            required_configuration=True,
        )

    def braw_adapter(self) -> DependencyRecord:
        return self._inspect_command(
            cache_key="braw_adapter",
            name="braw_adapter",
            command=self._settings.braw_adapter_path,
            required_configuration=False,
            runtime_check="json_version",
        )

    def r3d_adapter(self) -> DependencyRecord:
        return self._inspect_command(
            cache_key="r3d_adapter",
            name="r3d_adapter",
            command=self._settings.r3d_adapter_path,
            required_configuration=False,
            runtime_check="json_version",
        )

    def arri_art_cmd(self) -> DependencyRecord:
        return self._inspect_command(
            cache_key="arri_art_cmd",
            name="arri_art_cmd",
            command=self._settings.arri_art_cmd_path,
            required_configuration=False,
            runtime_check="help",
        )

    def all_dependencies(self) -> tuple[DependencyRecord, ...]:
        return (
            self.ffmpeg(),
            self.ffprobe(),
            self.mediainfo(),
            self.braw_adapter(),
            self.r3d_adapter(),
            self.arri_art_cmd(),
        )

    def availability_for_adapter(self, adapter_name: str) -> AdapterAvailability:
        dependency_map: dict[str, tuple[tuple[str, ...], tuple[DependencyRecord, ...]]] = {
            "ffmpeg": (("ffmpeg", "ffprobe"), (self.ffmpeg(), self.ffprobe())),
            "braw_adapter": (("braw_adapter",), (self.braw_adapter(),)),
            "r3d_adapter": (("r3d_adapter",), (self.r3d_adapter(),)),
            "arriraw_art_adapter": (("arri_art_cmd",), (self.arri_art_cmd(),)),
        }
        try:
            required_tools, dependencies = dependency_map[adapter_name]
        except KeyError as exc:
            raise ValueError(f"Unsupported adapter for dependency inspection: {adapter_name}") from exc

        return AdapterAvailability(
            adapter_name=adapter_name,
            required_tools=required_tools,
            state=_combine_states(dependencies),
            dependencies=dependencies,
        )

    def _inspect_command(
        self,
        *,
        cache_key: str,
        name: str,
        command: str | Path | None,
        required_configuration: bool,
        runtime_check: str = "none",
    ) -> DependencyRecord:
        if cache_key in self._cache:
            return self._cache[cache_key]

        configured_path = None if command is None else str(Path(command).expanduser() if isinstance(command, Path) else command)
        if command is None:
            record = DependencyRecord(
                name=name,
                state=AdapterDependencyState.NOT_CONFIGURED if not required_configuration else AdapterDependencyState.CONFIGURED_MISSING,
                configured_path=None,
                resolved_path=None,
            )
            self._cache[cache_key] = record
            return record

        resolved_path, state = _resolve_executable(command)
        if state is not AdapterDependencyState.AVAILABLE or resolved_path is None:
            record = DependencyRecord(
                name=name,
                state=state,
                configured_path=configured_path,
                resolved_path=resolved_path,
            )
            self._cache[cache_key] = record
            return record

        detail: dict[str, object] = {}
        runtime_state = _run_runtime_check(resolved_path, runtime_check)
        if runtime_state is not None:
            state, detail = runtime_state

        record = DependencyRecord(
            name=name,
            state=state,
            configured_path=configured_path,
            resolved_path=resolved_path,
            detail=detail,
        )
        self._cache[cache_key] = record
        return record


def _resolve_executable(command: str | Path) -> tuple[str | None, AdapterDependencyState]:
    raw_command = str(command)
    candidate = Path(raw_command).expanduser()
    if candidate.parent != Path(".") or os.sep in raw_command:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate), AdapterDependencyState.AVAILABLE
        return None, AdapterDependencyState.CONFIGURED_MISSING

    resolved = shutil.which(raw_command)
    if resolved is None:
        return None, AdapterDependencyState.CONFIGURED_MISSING
    return resolved, AdapterDependencyState.AVAILABLE


def _run_runtime_check(
    executable_path: str,
    runtime_check: str,
) -> tuple[AdapterDependencyState, dict[str, object]] | None:
    if runtime_check == "none":
        return None

    try:
        if runtime_check == "help":
            subprocess.run(
                [executable_path, "--help"],
                capture_output=True,
                text=True,
                check=True,
                timeout=_RUNTIME_TIMEOUT_SECONDS,
            )
        elif runtime_check == "json_version":
            payload = json.dumps(
                {
                    "request_id": "dependency-check",
                    "command": "version",
                    "input": {},
                    "options": {},
                }
            )
            completed = subprocess.run(
                [executable_path],
                input=payload,
                capture_output=True,
                text=True,
                check=True,
                timeout=_RUNTIME_TIMEOUT_SECONDS,
            )
            response = json.loads(completed.stdout or "{}")
            if not isinstance(response, dict):
                raise ValueError("version check did not return a JSON object")
            if response.get("ok") is False:
                return AdapterDependencyState.RUNTIME_ERROR, {
                    "runtime_check": runtime_check,
                    "stderr": completed.stderr.strip(),
                    "response": response,
                }
        else:
            raise ValueError(f"Unsupported runtime check mode: {runtime_check}")
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        return AdapterDependencyState.RUNTIME_ERROR, {
            "runtime_check": runtime_check,
            "error": str(exc),
        }

    return AdapterDependencyState.AVAILABLE, {}


def _combine_states(dependencies: tuple[DependencyRecord, ...]) -> AdapterDependencyState:
    states = {dependency.state for dependency in dependencies}
    if states == {AdapterDependencyState.AVAILABLE}:
        return AdapterDependencyState.AVAILABLE
    if AdapterDependencyState.RUNTIME_ERROR in states:
        return AdapterDependencyState.RUNTIME_ERROR
    if AdapterDependencyState.CONFIGURED_MISSING in states:
        return AdapterDependencyState.CONFIGURED_MISSING
    return AdapterDependencyState.NOT_CONFIGURED
