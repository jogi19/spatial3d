from __future__ import annotations

import math
from datetime import datetime

from .models import FlightPoint

EARTH_KM = 6371.0088


def haversine_km(a: FlightPoint, b: FlightPoint) -> float:
    p1, p2 = math.radians(a.latitude), math.radians(b.latitude)
    dp = p2 - p1
    dl = math.radians(b.longitude - a.longitude)
    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(x))


def bearing_deg(a: FlightPoint, b: FlightPoint) -> float:
    """Initial great-circle bearing from point a to point b, clockwise from north."""
    lat1, lat2 = math.radians(a.latitude), math.radians(b.latitude)
    dl = math.radians(b.longitude - a.longitude)
    x = math.sin(dl) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def route_distances(points: list[FlightPoint] | tuple[FlightPoint, ...]) -> list[float]:
    total, result = 0.0, []
    for i, point in enumerate(points):
        if i:
            total += haversine_km(points[i - 1], point)
        result.append(total)
    return result


def _lerp(a: float | None, b: float | None, fraction: float) -> float | None:
    return None if a is None or b is None else a + (b - a) * fraction


def _angle_lerp(a: float | None, b: float | None, fraction: float) -> float | None:
    if a is None or b is None:
        return None
    delta = (b - a + 180) % 360 - 180
    return (a + delta * fraction) % 360


def interpolate(points: tuple[FlightPoint, ...], at: datetime) -> FlightPoint:
    if not points:
        raise ValueError("cannot interpolate an empty track")
    if at <= points[0].timestamp:
        return points[0]
    if at >= points[-1].timestamp:
        return points[-1]
    for left, right in zip(points, points[1:]):
        if left.timestamp <= at <= right.timestamp:
            span = (right.timestamp - left.timestamp).total_seconds() or 1
            f = (at - left.timestamp).total_seconds() / span
            dlon = (right.longitude - left.longitude + 180) % 360 - 180
            course = _angle_lerp(left.course_deg, right.course_deg, f)
            if course is None:
                course = bearing_deg(left, right)
            return FlightPoint(at, left.latitude + (right.latitude - left.latitude) * f, left.longitude + dlon * f, _lerp(left.altitude_ft, right.altitude_ft, f), _lerp(left.speed_kt, right.speed_kt, f), course)
    return points[-1]


def timeline_time(points: tuple[FlightPoint, ...], progress: float, duration_s: float) -> datetime:
    if not points:
        raise ValueError("empty track")
    progress = max(0.0, min(1.0, progress))
    return points[0].timestamp + (points[-1].timestamp - points[0].timestamp) * progress


def project(lat: float, lon: float, bounds: tuple[float, float, float, float], width: int, height: int, margin: int = 40) -> tuple[int, int]:
    min_lon, min_lat, max_lon, max_lat = bounds
    x = margin + (lon - min_lon) / max(1e-9, max_lon - min_lon) * (width - 2 * margin)
    y = margin + (max_lat - lat) / max(1e-9, max_lat - min_lat) * (height - 2 * margin)
    return round(x), round(y)


def project_web_mercator(lat: float, lon: float, bounds: tuple[float, float, float, float], width: int, height: int, margin: int = 40) -> tuple[int, int]:
    """Project to the same Web Mercator geometry used by OSM slippy tiles."""
    min_lon, min_lat, max_lon, max_lat = bounds
    def mercator_y(value: float) -> float:
        value = max(-85.0511, min(85.0511, value))
        return math.log(math.tan(math.pi / 4 + math.radians(value) / 2))
    top, bottom = mercator_y(max_lat), mercator_y(min_lat)
    x = margin + (lon - min_lon) / max(1e-9, max_lon - min_lon) * (width - 2 * margin)
    y = margin + (top - mercator_y(lat)) / max(1e-9, top - bottom) * (height - 2 * margin)
    return round(x), round(y)
