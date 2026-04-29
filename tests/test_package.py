from __future__ import annotations

from frameproof import __version__
from frameproof.settings import collect_runtime_snapshot


def test_package_exports_version() -> None:
    assert __version__ == "0.1.0"


def test_runtime_snapshot_contains_truthful_bootstrap_fields() -> None:
    snapshot = collect_runtime_snapshot(env={}, home=None).to_dict()

    assert snapshot["config_source"] == "default"
    assert isinstance(snapshot["config_exists"], bool)
    assert str(snapshot["config_path"]).endswith("frameproof/config.toml")

