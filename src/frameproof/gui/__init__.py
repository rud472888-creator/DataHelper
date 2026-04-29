from __future__ import annotations

from pathlib import Path

__all__ = ["create_application", "create_main_window", "launch_gui"]


def create_application() -> object:
    from .app import create_application as _create_application

    return _create_application()


def create_main_window(settings_path: Path | None = None) -> object:
    from .app import create_main_window as _create_main_window

    return _create_main_window(settings_path)


def launch_gui(settings_path: Path | None = None) -> int:
    from .app import launch_gui as _launch_gui

    return _launch_gui(settings_path)
