from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m frameproof.gui", description="Launch the Frame Proof PySide6 GUI.")
    parser.add_argument("--settings-file", metavar="PATH", help="Override the GUI settings INI file location.")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Create and show the GUI briefly, then exit without starting a batch.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else sys.argv[1:])
    settings_path = Path(args.settings_file).expanduser() if args.settings_file else None
    if args.smoke_test:
        from frameproof.gui.app import create_application, create_main_window

        app = create_application()
        window = create_main_window(settings_path)
        window.show()
        app.processEvents()
        window.close()
        return 0
    from frameproof.gui import launch_gui

    return launch_gui(settings_path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
