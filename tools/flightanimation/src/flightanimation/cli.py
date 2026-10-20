from __future__ import annotations

import argparse
import sys

from .kml import parse_kml
from .models import RenderSettings
from .render import Renderer
from .export import export_video
from .maps import download_osm_map


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="FR24 KML stereoscopic flight animation")
    parser.add_argument("kml")
    parser.add_argument("--output", required=True)
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--lead-in", type=float, default=3.0, help="Standbild vor dem Flug in Sekunden")
    parser.add_argument("--lead-out", type=float, default=3.0, help="Standbild nach dem Flug in Sekunden")
    parser.add_argument("--fps", type=int, choices=(25, 30), default=25)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--aircraft-color", choices=("white", "red", "yellow"), default="white")
    parser.add_argument("--overlay-style", choices=("white", "matrix"), default="white", help="Stil der Flugdaten-Tafel")
    parser.add_argument("--aircraft-parallax", type=float, default=3.5, help="Flugzeug-Tiefenwirkung in Pixeln")
    parser.add_argument("--altitude-gain", type=float, default=1.0, help="Verstärkung der Flughöhe für die Tiefe")
    parser.add_argument("--overlay-parallax", type=float, default=0.0, help="Tiefe der Infotafel; positiv vor, negativ hinter der Kartenebene")
    parser.add_argument("--map-tilt", type=float, default=4.0, help="subtile Tiefenstaffelung der Karte in Pixeln")
    parser.add_argument("--grayscale", action="store_true", help="Video in Schwarzweiß rendern")
    parser.add_argument("--no-map", action="store_true", help="keine OSM-Karte laden")
    parser.add_argument("--map-cache", default=".flightanimation-map-cache")
    args = parser.parse_args(argv)
    track = parse_kml(args.kml)
    settings = RenderSettings(width=args.width, height=args.height, duration_s=args.duration, fps=args.fps, lead_in_s=args.lead_in, lead_out_s=args.lead_out, aircraft_color=args.aircraft_color, overlay_style=args.overlay_style, aircraft_parallax_px=args.aircraft_parallax, altitude_gain=args.altitude_gain, overlay_parallax_px=args.overlay_parallax, map_tilt_px=args.map_tilt, grayscale=args.grayscale)
    map_image = None
    if not args.no_map:
        lats = [p.latitude for p in track.points]; lons = [p.longitude for p in track.points]
        pad_lat = max(0.1, (max(lats) - min(lats)) * 0.12)
        pad_lon = max(0.1, (max(lons) - min(lons)) * 0.12)
        bounds = (min(lons) - pad_lon, min(lats) - pad_lat, max(lons) + pad_lon, max(lats) + pad_lat)
        try:
            print("Lade/cache OSM-Karte …", flush=True)
            map_image = download_osm_map(bounds, (args.width, args.height), args.map_cache)
            print("OSM-Karte bereit.", flush=True)
        except Exception as exc:
            print(f"Hinweis: OSM-Karte nicht verfügbar ({exc}); neutraler Hintergrund wird verwendet.")
    last_report = -1
    def report(done: int, total: int) -> None:
        nonlocal last_report
        step = max(1, total // 20)
        if done == total or done - last_report >= step:
            percent = round(done / total * 100)
            sys.stdout.write(f"\rFrames: {done}/{total} ({percent:3d} %)" if done < total else f"\rFrames: {done}/{total} (100 %)\n")
            sys.stdout.flush()
            last_report = done

    count = export_video(Renderer(track, settings, map_image), args.output, progress=report, status=lambda message: print(message, flush=True))
    print(f"{len(track.points)} Punkte, {track.distance_km:.1f} km, {count} Frames -> {args.output}")
    return 0
