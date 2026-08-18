"""A narrow command-execution protocol for future media-tool adapters."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CommandResult:
    """A process result represented without leaking a subprocess object."""

    arguments: tuple[str, ...]
    return_code: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    """Boundary used by adapters that need to execute an external tool."""

    def run(self, arguments: tuple[str, ...], *, working_directory: Path | None = None) -> CommandResult:
        """Run an explicit executable/argument tuple without a shell."""

