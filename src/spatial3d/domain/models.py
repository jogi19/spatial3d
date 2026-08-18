"""M0 domain-model seeds; no container or media parsing occurs here."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class AssetKind(str, Enum):
    """High-level classification states reserved for M1 inspection."""

    UNKNOWN = "unknown"
    ORDINARY = "ordinary"
    SPATIAL_VIDEO = "spatial_video"
    SPATIAL_PHOTO = "spatial_photo"


@dataclass(frozen=True, slots=True)
class SourceDescriptor:
    """A read-only source identity without parsed media facts."""

    path: Path
    byte_size: int | None = None
    media_kind: AssetKind = AssetKind.UNKNOWN

