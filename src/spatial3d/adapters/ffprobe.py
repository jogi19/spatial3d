"""FFprobe adapter; all container-specific knowledge stays here."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from spatial3d.adapters.runner import CommandResult, CommandRunner


class ProbeError(RuntimeError):
    """Raised when FFprobe cannot produce structured output."""


class FfprobeAdapter:
    """Probe MOV/MP4-family assets using FFprobe's JSON output."""

    def __init__(self, runner: CommandRunner) -> None:
        self._runner = runner

    def probe(self, source: Path) -> dict[str, Any]:
        executable = os.environ.get("SPATIAL3D_FFPROBE", "ffprobe")
        result = self._runner.run(
            (
                executable,
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-show_programs",
                "-of",
                "json",
                str(source),
            )
        )
        if result.return_code != 0:
            raise ProbeError(result.stderr.strip() or "ffprobe failed")
        try:
            decoded = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ProbeError("ffprobe returned invalid JSON") from exc
        if not isinstance(decoded, dict):
            raise ProbeError("ffprobe returned a non-object JSON result")
        return decoded

    def version(self) -> str | None:
        executable = os.environ.get("SPATIAL3D_FFPROBE", "ffprobe")
        result = self._runner.run((executable, "-version"))
        if result.return_code != 0:
            return None
        first = result.stdout.splitlines()[0] if result.stdout else ""
        return first.removeprefix("ffprobe version ").split(" ", 1)[0] or None
