"""ExifTool adapter for structured HEIC/HEIF metadata."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from spatial3d.adapters.runner import CommandRunner


class ExifToolError(RuntimeError):
    """Raised when ExifTool cannot produce structured output."""


class ExifToolAdapter:
    """Read HEIC/HEIF metadata without extracting or modifying image data."""

    def __init__(self, runner: CommandRunner) -> None:
        self._runner = runner

    def inspect(self, source: Path) -> dict[str, Any]:
        executable = os.environ.get("SPATIAL3D_EXIFTOOL", "exiftool")
        result = self._runner.run((executable, "-j", "-G1", "-a", "-s", str(source)))
        if result.return_code != 0:
            raise ExifToolError(result.stderr.strip() or "exiftool failed")
        try:
            decoded = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ExifToolError("exiftool returned invalid JSON") from exc
        if not isinstance(decoded, list) or not decoded or not isinstance(decoded[0], dict):
            raise ExifToolError("exiftool returned no metadata object")
        return decoded[0]

    def version(self) -> str | None:
        executable = os.environ.get("SPATIAL3D_EXIFTOOL", "exiftool")
        result = self._runner.run((executable, "-ver"))
        return result.stdout.strip() or None if result.return_code == 0 else None
