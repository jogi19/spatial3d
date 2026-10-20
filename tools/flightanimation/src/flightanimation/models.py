from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class FlightPoint:
    timestamp: datetime
    latitude: float
    longitude: float
    altitude_ft: Optional[float] = None
    speed_kt: Optional[float] = None
    course_deg: Optional[float] = None


@dataclass(frozen=True)
class FlightMetadata:
    flight_number: str = ""
    airline: str = ""
    aircraft_type: str = ""
    registration: str = ""


@dataclass(frozen=True)
class FlightTrack:
    points: tuple[FlightPoint, ...]
    metadata: FlightMetadata = field(default_factory=FlightMetadata)
    warnings: tuple[str, ...] = ()
    cumulative_km: tuple[float, ...] = ()

    @property
    def distance_km(self) -> float:
        return self.cumulative_km[-1] if self.cumulative_km else 0.0


@dataclass
class RenderSettings:
    width: int = 1920
    height: int = 1080
    fps: int = 25
    duration_s: float = 5.0
    lead_in_s: float = 3.0
    lead_out_s: float = 3.0
    map_parallax_px: float = -1.0
    map_tilt_px: float = 4.0
    aircraft_parallax_px: float = 3.5
    overlay_parallax_px: float = 0.0
    altitude_gain: float = 1.0
    distance_offset_km: float = 0.0
    show_full_route: bool = True
    show_overlay: bool = True
    attribution: str = "© OpenStreetMap-Mitwirkende"
    aircraft_color: str = "white"
    overlay_style: str = "white"
    grayscale: bool = False

    def frame_count(self) -> int:
        if self.fps not in (25, 30):
            raise ValueError("fps must be 25 or 30")
        if self.duration_s <= 0:
            raise ValueError("duration_s must be positive")
        if self.lead_in_s < 0 or self.lead_out_s < 0:
            raise ValueError("lead_in_s and lead_out_s must not be negative")
        return round((self.lead_in_s + self.duration_s + self.lead_out_s) * self.fps)

    def content_progress(self, video_progress: float) -> float:
        """Map total-video progress to the moving flight content."""
        total = self.lead_in_s + self.duration_s + self.lead_out_s
        elapsed = max(0.0, min(total, video_progress * total))
        if elapsed <= self.lead_in_s:
            return 0.0
        if elapsed >= self.lead_in_s + self.duration_s:
            return 1.0
        return (elapsed - self.lead_in_s) / self.duration_s

    def clamped_parallax(self, value: float) -> int:
        limit = max(1, int(self.width * 0.03))
        return int(max(-limit, min(limit, round(value))))
