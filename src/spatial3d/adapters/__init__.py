"""Replaceable boundaries for external programs and platform backends."""

from spatial3d.adapters.capabilities import ToolCapability, ToolStatus
from spatial3d.adapters.ffprobe import FfprobeAdapter, ProbeError
from spatial3d.adapters.exiftool import ExifToolAdapter, ExifToolError
from spatial3d.adapters.process import SubprocessCommandRunner
from spatial3d.adapters.runner import CommandResult, CommandRunner

__all__ = [
    "CommandResult",
    "CommandRunner",
    "FfprobeAdapter",
    "ProbeError",
    "ExifToolAdapter",
    "ExifToolError",
    "SubprocessCommandRunner",
    "ToolCapability",
    "ToolStatus",
]
