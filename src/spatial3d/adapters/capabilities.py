"""External tool capability discovery, isolated from domain logic."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from shutil import which


class ToolCapability(str, Enum):
    """Capabilities that later inspection adapters may require."""

    VIDEO_PROBE = "video_probe"
    PHOTO_METADATA = "photo_metadata"


@dataclass(frozen=True, slots=True)
class ToolStatus:
    """Availability of one configured external executable."""

    capability: ToolCapability
    executable: str
    available: bool
    path: Path | None = None
    version: str | None = None


class ToolLocator:
    """Filesystem-only tool lookup; command execution belongs to a runner."""

    def locate(self, capability: ToolCapability, executable: str) -> ToolStatus:
        resolved = which(executable)
        return ToolStatus(
            capability=capability,
            executable=executable,
            available=resolved is not None,
            path=Path(resolved) if resolved else None,
        )

