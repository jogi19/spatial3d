"""FFprobe adapter; all container-specific knowledge stays here."""

from __future__ import annotations

import json
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
        result = self._runner.run(
            (
                "ffprobe",
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

