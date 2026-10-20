from datetime import datetime, timezone

import pytest

from flightanimation.export import ffmpeg_command
from flightanimation.geo import bearing_deg, interpolate, project
from flightanimation.kml import parse_kml
from flightanimation.models import FlightPoint, FlightTrack, RenderSettings
from flightanimation.render import Renderer


KML = '''<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>
<Placemark><description><![CDATA[Flight: VL2015 | Airline: Test Air | Aircraft type: A319 | Registration: D-TEST<br>Altitude: 10000 ft | Speed: 430 kt | Course: 90]]></description><TimeStamp><when>2026-10-03T12:01:00Z</when></TimeStamp><Point><coordinates>10.0,50.0,0</coordinates></Point></Placemark>
<Placemark><description>Altitude: 12000 ft; Speed: 450 kt; Course: 100</description><TimeStamp><when>2026-10-03T12:03:00Z</when></TimeStamp><Point><coordinates>11.0,51.0,999</coordinates></Point></Placemark>
</Document></kml>'''


def test_kml_parses_description_values_not_coordinate_height(tmp_path):
    path = tmp_path / "route.kml"
    path.write_text(KML)
    track = parse_kml(path)
    assert len(track.points) == 2
    assert track.points[0].altitude_ft == 10000
    assert track.points[1].altitude_ft == 12000
    assert track.metadata.flight_number == "VL2015"
    assert track.distance_km > 100


def test_number_keeps_thousands_separator(tmp_path):
    path = tmp_path / "thousands.kml"
    path.write_text(KML.replace("10000 ft", "6,925 ft"))
    assert parse_kml(path).points[0].altitude_ft == 6925


def test_sort_and_interpolate():
    points = (
        FlightPoint(datetime(2026, 1, 1, tzinfo=timezone.utc), 0, 0, 100, 200),
        FlightPoint(datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc), 1, 2, 200, 300),
    )
    middle = interpolate(points, datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc))
    assert middle.latitude == pytest.approx(.5)
    assert middle.altitude_ft == pytest.approx(150)


def test_heading_interpolation_wraps_and_missing_heading_uses_track():
    points = (
        FlightPoint(datetime(2026, 1, 1, tzinfo=timezone.utc), 50, 10, course_deg=359),
        FlightPoint(datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc), 50, 11, course_deg=1),
    )
    assert interpolate(points, datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc)).course_deg == pytest.approx(0)
    missing = (FlightPoint(points[0].timestamp, 50, 10), FlightPoint(points[1].timestamp, 50, 11))
    assert interpolate(missing, datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc)).course_deg == pytest.approx(bearing_deg(*missing))


def test_projection_and_settings():
    assert project(50, 10, (10, 50, 20, 60), 1000, 500) == (40, 500 - 40)
    settings = RenderSettings(duration_s=4, fps=25)
    assert settings.frame_count() == 250
    assert settings.content_progress(0) == 0
    assert settings.content_progress(1) == 1
    with pytest.raises(ValueError): RenderSettings(duration_s=1, fps=24).frame_count()


def test_sbs_dimensions_and_safe_command():
    points = (FlightPoint(datetime(2026, 1, 1), 50, 10), FlightPoint(datetime(2026, 1, 1, 0, 1), 51, 11))
    renderer = Renderer(FlightTrack(points, cumulative_km=(0, 100)), RenderSettings(width=320, height=180, duration_s=1, fps=25))
    frame = renderer.frame(.5)
    assert frame.size == (640, 180)
    assert renderer.anaglyph(.5).size == (320, 180)
    command = ffmpeg_command("/tmp/frame-%06d.png", "out file.mp4", 25)
    assert "out file.mp4" in command and "-i" in command
    assert all(not isinstance(value, bytes) for value in command)
    gray = Renderer(FlightTrack(points, cumulative_km=(0, 100)), RenderSettings(width=64, height=36, grayscale=True)).frame(.5)
    assert gray.getpixel((10, 10))[0] == gray.getpixel((10, 10))[1] == gray.getpixel((10, 10))[2]
