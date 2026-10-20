from __future__ import annotations

import math
import urllib.request
from pathlib import Path

from PIL import Image


def _tile_xy(lon: float, lat: float, zoom: int) -> tuple[int, int]:
    n = 2**zoom
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(max(-85.0511, min(85.0511, lat))))) / math.pi) / 2 * n)
    return max(0, min(n - 1, x)), max(0, min(n - 1, y))


def download_osm_map(bounds: tuple[float, float, float, float], size: tuple[int, int], cache_dir: str | Path, zoom: int = 7) -> Image.Image:
    """Download and stitch standard OSM tiles, using a local cache and attribution."""
    min_lon, min_lat, max_lon, max_lat = bounds
    cache = Path(cache_dir); cache.mkdir(parents=True, exist_ok=True)
    x0, y1 = _tile_xy(min_lon, min_lat, zoom)
    x1, y0 = _tile_xy(max_lon, max_lat, zoom)
    if x1 < x0: x1 += 2**zoom
    mosaic = Image.new("RGB", ((x1 - x0 + 1) * 256, (y1 - y0 + 1) * 256))
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            tx = x % (2**zoom)
            path = cache / f"{zoom}-{tx}-{y}.png"
            if not path.exists():
                url = f"https://tile.openstreetmap.org/{zoom}/{tx}/{y}.png"
                request = urllib.request.Request(url, headers={"User-Agent": "spatial3d-flightanimation/0.1 (local export)"})
                with urllib.request.urlopen(request, timeout=15) as response:
                    path.write_bytes(response.read())
            mosaic.paste(Image.open(path).convert("RGB"), ((x - x0) * 256, (y - y0) * 256))
    # Crop to the exact geographic bounds before resizing. Resizing the full
    # tile block would include outer tile margins and shift the route relative
    # to the map labels.
    n = 2**zoom * 256
    def world_x(lon: float) -> float:
        return (lon + 180) / 360 * n
    def world_y(lat: float) -> float:
        lat = max(-85.0511, min(85.0511, lat))
        return (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    left = round(world_x(min_lon) - x0 * 256)
    right = round(world_x(max_lon) - x0 * 256)
    top = round(world_y(max_lat) - y0 * 256)
    bottom = round(world_y(min_lat) - y0 * 256)
    cropped = mosaic.crop((max(0, left), max(0, top), min(mosaic.width, right), min(mosaic.height, bottom)))
    return cropped.resize(size)
