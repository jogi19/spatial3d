from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from .models import FlightMetadata, FlightPoint, FlightTrack
from .geo import route_distances

_TAG = re.compile(r"<[^>]*>")
_NUM = r"([-+]?\d+(?:[.,]\d+)?)"


def _clean(value: str) -> str:
    return " ".join(_TAG.sub(" ", html.unescape(value or "")).split())


def _number(text: str | None) -> float | None:
    if not text:
        return None
    m = re.search(r"[-+]?\d[\d.,]*", text.replace(" ", " "))
    if not m:
        return None
    value = m.group()
    # FR24 uses commas as thousands separators (e.g. 6,925 ft). Preserve
    # decimal commas only when they are not a three-digit grouping.
    sign = ""
    if value[:1] in "+-":
        sign, value = value[0], value[1:]
    if "," in value and "." not in value:
        parts = value.split(",")
        value = "".join(parts) if all(len(part) == 3 for part in parts[1:]) else ".".join(parts)
    elif "," in value and "." in value:
        value = value.replace(",", "")
    return float(sign + value)


def _field(text: str, names: tuple[str, ...]) -> str:
    pattern = r"(?:" + "|".join(re.escape(n) for n in names) + r")\s*[:=]\s*([^|;\n]+)"
    m = re.search(pattern, text, re.I)
    return m.group(1).strip() if m else ""


def _num_field(text: str, names: tuple[str, ...]) -> float | None:
    return _number(_field(text, names))


def _timestamp(raw: str) -> datetime:
    value = raw.strip().replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def parse_kml(path: str | Path) -> FlightTrack:
    root = ET.parse(path).getroot()
    placemarks = [e for e in root.iter() if e.tag.rsplit("}", 1)[-1] == "Placemark"]
    points: list[FlightPoint] = []
    warnings: list[str] = []
    metadata = FlightMetadata()
    document_text = " ".join(_clean(e.text or "") for e in root.iter() if e.tag.rsplit("}", 1)[-1] in {"description", "name"})
    document_name = next((e.text.strip() for e in root.iter() if e.tag.rsplit("}", 1)[-1] == "name" and e.text), "")
    flight_name = document_name.split("/", 1)[0].strip()
    registration_match = re.search(r"\b[A-Z0-9]{1,2}-[A-Z0-9]{3,5}\b", document_text)
    aircraft_match = re.search(r"\b((?:Airbus|Boeing|Embraer|Bombardier)\s+[A-Z0-9-]+)", document_text, re.I)
    metadata = FlightMetadata(
        flight_number=flight_name,
        airline=_field(document_text, ("Airline",)) or ("Lufthansa" if "Lufthansa" in document_text else ""),
        aircraft_type=aircraft_match.group(1) if aircraft_match else "",
        registration=registration_match.group(0) if registration_match else "",
    )
    for mark in placemarks:
        text = " ".join(_clean(e.text or "") for e in mark.iter() if e.tag.rsplit("}", 1)[-1] in {"description", "name"})
        coords = next((e.text for e in mark.iter() if e.tag.rsplit("}", 1)[-1] == "coordinates"), None)
        when = next((e.text for e in mark.iter() if e.tag.rsplit("}", 1)[-1] == "when"), None)
        if not coords or not when:
            warnings.append("Placemark without coordinates or timestamp ignored")
            continue
        try:
            values = [float(x.strip()) for x in coords.strip().split(",")]
            lon, lat = values[:2]
            timestamp = _timestamp(when)
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError("coordinate out of range")
        except (ValueError, TypeError) as exc:
            warnings.append(f"Invalid Placemark ignored: {exc}")
            continue
        point = FlightPoint(timestamp, lat, lon, _num_field(text, ("Altitude", "Height", "Höhe")), _num_field(text, ("Speed", "Geschwindigkeit")), _num_field(text, ("Course", "Heading", "Track", "Kurs")))
        points.append(point)
        if not metadata.flight_number:
            metadata = FlightMetadata(_field(text, ("Flight", "Flight number", "Flugnummer")), _field(text, ("Airline", "Airline")), _field(text, ("Aircraft type", "Aircraft", "Type", "Flugzeugtyp")), _field(text, ("Registration", "Reg", "Kennzeichen")))
    points.sort(key=lambda p: p.timestamp)
    if len(points) < 2:
        warnings.append("Track has fewer than two valid points")
    return FlightTrack(tuple(points), metadata, tuple(warnings), tuple(route_distances(points)))
