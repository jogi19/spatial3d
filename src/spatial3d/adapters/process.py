"""Concrete, shell-free process runner for external tool adapters."""

from __future__ import annotations

import subprocess
from pathlib import Path

from spatial3d.adapters.runner import CommandResult


class SubprocessCommandRunner:
    """Run an explicit command with bounded, text-mode process handling."""

    def run(self, arguments: tuple[str, ...], *, working_directory: Path | None = None) -> CommandResult:
        completed = subprocess.run(
            list(arguments),
            cwd=working_directory,
            capture_output=True,
            text=True,
            check=False,
            shell=False,
        )
        return CommandResult(
            arguments=arguments,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

