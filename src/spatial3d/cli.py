"""M0 command-line presentation layer."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path

from spatial3d.adapters.ffprobe import FfprobeAdapter, ProbeError
from spatial3d.adapters.process import SubprocessCommandRunner
from spatial3d import __version__
from spatial3d.inspection.inspect import inspect_file


def build_parser() -> argparse.ArgumentParser:
    """Build the M0 parser without registering media operations."""
    parser = argparse.ArgumentParser(
        prog="spatial3d",
        description="Linux-first, inspectable tooling for spatial media.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    inspect_parser = subparsers.add_parser("inspect", help="Inspect one media file.")
    inspect_parser.add_argument("file", type=Path)
    inspect_parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return a process exit status."""
    args = build_parser().parse_args(argv)
    if args.command == "inspect":
        try:
            result = inspect_file(args.file, ffprobe=FfprobeAdapter(SubprocessCommandRunner()))
        except (FileNotFoundError, ProbeError) as exc:
            print(f"spatial3d: inspect failed: {exc}")
            return 2
        if args.as_json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"classification: {result['classification']}")
            print(f"source: {result['source']['path']}")
            if "summary" in result:
                print(f"streams: {result['summary']['video_streams']} video, {result['summary']['audio_streams']} audio")
            stereo = result.get("stereo", {})
            if stereo.get("view_ids_available"):
                print(f"view ids available: {','.join(stereo['view_ids_available'])}")
                print(f"view positions available: {','.join(stereo['view_positions_available'])}")
                print(f"view ordering: {stereo['ordering']}")
            metadata = result.get("spatial_metadata", {})
            baseline = metadata.get("baseline")
            if baseline:
                print(f"baseline: {baseline['millimetres']} mm (raw {baseline['raw']})")
            fov = metadata.get("horizontal_field_of_view")
            if fov:
                print(f"horizontal FOV: {fov['normalized']} degrees (raw {fov['raw']})")
            disparity = metadata.get("horizontal_disparity_adjustment")
            if disparity:
                print(f"horizontal disparity adjustment: {disparity['normalized']} (raw {disparity['raw']})")
            for warning in result.get("warnings", []):
                print(f"warning [{warning['code']}]: {warning['message']}")
    return 0
