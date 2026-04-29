from __future__ import annotations

import os
import time
from collections.abc import Callable

import pytest

from frameproof.gui.app import create_application

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def qapp() -> object:
    return create_application()


def wait_until(app: object, predicate: Callable[[], bool], timeout_ms: int = 3000) -> None:
    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline:
        assert hasattr(app, "processEvents")
        app.processEvents()
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("Timed out waiting for Qt condition")
