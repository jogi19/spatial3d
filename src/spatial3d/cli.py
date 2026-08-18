"""M0 command-line presentation layer."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from spatial3d import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the M0 parser without registering media operations."""
    parser = argparse.ArgumentParser(
        prog="spatial3d",
        description="Linux-first, inspectable tooling for spatial media.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return a process exit status."""
    build_parser().parse_args(argv)
    return 0

