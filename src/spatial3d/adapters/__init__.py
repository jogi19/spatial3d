"""Replaceable boundaries for external programs and platform backends."""

from spatial3d.adapters.capabilities import ToolCapability, ToolStatus
from spatial3d.adapters.runner import CommandResult, CommandRunner

__all__ = ["CommandResult", "CommandRunner", "ToolCapability", "ToolStatus"]

