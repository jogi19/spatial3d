from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .geo import bearing_deg, interpolate, project, project_web_mercator, route_distances, timeline_time
from .models import FlightTrack, RenderSettings


def _font(size: int = 24):
    # A bare font name is not resolved consistently on macOS.  Without an
    # explicit fallback Pillow silently uses its tiny bitmap default font.
    candidates = (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


class Renderer:
    """Render three independently depth-controlled layers into two eye views."""

    def __init__(self, track: FlightTrack, settings: RenderSettings, map_image: str | Path | Image.Image | None = None):
        if not track.points:
            raise ValueError("cannot render an empty track")
        self.track, self.settings = track, settings
        self.map_image = (map_image.copy().convert("RGB") if isinstance(map_image, Image.Image) else Image.open(map_image).convert("RGB")) if map_image else None
        self._project = project_web_mercator if self.map_image else project
        lats, lons = [p.latitude for p in track.points], [p.longitude for p in track.points]
        pad_lat = max(0.1, (max(lats) - min(lats)) * 0.12)
        pad_lon = max(0.1, (max(lons) - min(lons)) * 0.12)
        self.bounds = (min(lons) - pad_lon, min(lats) - pad_lat, max(lons) + pad_lon, max(lats) + pad_lat)

    def _shift(self, image: Image.Image, dx: int) -> Image.Image:
        result = Image.new(image.mode, image.size, (0, 0, 0, 0) if image.mode == "RGBA" else (28, 43, 55))
        result.paste(image, (dx, 0), image if image.mode == "RGBA" else None)
        return result

    def _tilt_map(self, image: Image.Image, sign: int) -> Image.Image:
        """Apply a subtle depth gradient to the map plane over image height."""
        height = image.height
        tilt = self.settings.map_tilt_px
        base = self.settings.map_parallax_px
        # screen shift(y) = sign * (base + tilt * (y/height - 0.5)).
        # The upper/far part recedes, while the lower/near part comes forward.
        # Pillow's affine transform maps output pixels back to source pixels,
        # hence the sign is opposite to the desired visible shift gradient.
        affine_y = -sign * tilt / max(1, height)
        affine_x = -sign * (base - tilt * 0.5)
        return image.transform(
            image.size,
            Image.Transform.AFFINE,
            (1.0, affine_y, affine_x, 0.0, 1.0, 0.0),
            resample=Image.Resampling.BICUBIC,
            fillcolor=(28, 43, 55, 255),
        )

    def _layers(self, progress: float) -> tuple[Image.Image, Image.Image, Image.Image]:
        size = (self.settings.width, self.settings.height)
        base = self.map_image.resize(size) if self.map_image else Image.new("RGB", size, (28, 43, 55))
        map_layer = base.convert("RGBA")
        plane_layer, overlay_layer = Image.new("RGBA", size), Image.new("RGBA", size)
        md, pd, od = ImageDraw.Draw(map_layer), ImageDraw.Draw(plane_layer), ImageDraw.Draw(overlay_layer)
        route = [self._project(p.latitude, p.longitude, self.bounds, *size) for p in self.track.points]
        if self.settings.show_full_route and len(route) > 1:
            md.line(route, fill=(125, 145, 158, 255), width=3)
        current = interpolate(self.track.points, timeline_time(self.track.points, progress, self.settings.duration_s))
        if current.course_deg is None:
            if len(self.track.points) > 1:
                if current.timestamp <= self.track.points[0].timestamp:
                    course = bearing_deg(self.track.points[0], self.track.points[1])
                else:
                    course = bearing_deg(self.track.points[-2], self.track.points[-1])
                current = replace(current, course_deg=course)
            else:
                current = replace(current, course_deg=0.0)
        x, y = self._project(current.latitude, current.longitude, self.bounds, *size)
        # Build the travelled route from timestamps, then append the exact
        # interpolated aircraft position. This keeps line and aircraft synced
        # even when the KML samples are irregularly spaced in time.
        travelled = [self._project(p.latitude, p.longitude, self.bounds, *size) for p in self.track.points if p.timestamp <= current.timestamp]
        if not travelled or travelled[-1] != (x, y):
            travelled.append((x, y))
        if len(travelled) > 1:
            md.line(travelled, fill=(255, 205, 45, 255), width=6)
        panel_position = None
        import math
        # The new silhouette uses the geographic heading axis directly:
        # 0° = north, clockwise.
        angle = math.radians(current.course_deg or 0.0)
        icon_scale = max(0.9, size[0] / 1280)
        def aircraft_point(forward: float, right: float) -> tuple[int, int]:
            forward *= icon_scale
            right *= icon_scale
            return (x + round(forward * math.sin(angle) + right * math.cos(angle)), y + round(-forward * math.cos(angle) + right * math.sin(angle)))
        aircraft_colors = {
            "white": ((245, 245, 245, 255), (20, 20, 20, 255)),
            "red": ((230, 60, 55, 255), (255, 255, 255, 255)),
            "yellow": ((255, 210, 45, 255), (20, 20, 20, 255)),
        }
        fill, outline = aircraft_colors.get(self.settings.aircraft_color, aircraft_colors["white"])
        # Compose a clean airliner silhouette from separate, non-crossing
        # shapes. This remains recognizable when the two anaglyph channels are
        # slightly separated.
        fuselage = [aircraft_point(31, 0), aircraft_point(18, 3), aircraft_point(-24, 3), aircraft_point(-29, 0), aircraft_point(-24, -3), aircraft_point(18, -3)]
        main_wings = [aircraft_point(10, 3), aircraft_point(4, 5), aircraft_point(-7, 27), aircraft_point(-12, 25), aircraft_point(-2, 0), aircraft_point(-12, -25), aircraft_point(-7, -27), aircraft_point(4, -5)]
        tailplane = [aircraft_point(-15, 3), aircraft_point(-19, 5), aircraft_point(-26, 15), aircraft_point(-29, 13), aircraft_point(-22, 0), aircraft_point(-29, -13), aircraft_point(-26, -15), aircraft_point(-19, -5)]
        for shape in (main_wings, tailplane, fuselage):
            pd.polygon(shape, fill=fill, outline=outline)
        if self.settings.show_overlay:
            md_data = self.track.metadata
            title = " · ".join(v for v in (md_data.flight_number, md_data.airline, md_data.aircraft_type, md_data.registration) if v) or "Flight"
            lines = [title, current.timestamp.strftime("%d.%m.%Y · %H:%M UTC"), f"Position: {current.latitude:.4f}°, {current.longitude:.4f}°"]
            if current.altitude_ft is not None:
                lines.append(f"Höhe: {current.altitude_ft:,.0f} ft · {current.altitude_ft * 0.3048:,.0f} m")
            if current.speed_kt is not None:
                lines.append(f"Geschwindigkeit: {current.speed_kt:,.0f} kt · {current.speed_kt * 1.852:,.0f} km/h")
            distances = route_distances(self.track.points)
            km = distances[min(len(distances) - 1, round(progress * (len(distances) - 1)))] + self.settings.distance_offset_km
            lines.append(f"Zurückgelegt: {km:,.1f} km · {km / 1.852:,.1f} NM")
            text_size = max(19, round(19 * size[0] / 1280))
            line_height = round(text_size * 1.12)
            text_fonts = [_font(text_size + 4 if i == 0 else text_size) for i in range(len(lines))]
            text_width = max(od.textbbox((0, 0), line, font=font)[2] for line, font in zip(lines, text_fonts))
            margin = 25
            panel_width = min(size[0] - 2 * margin, max(300, text_width + 54))
            panel_height = line_height * len(lines) + 44
            candidates = [
                (margin, margin),
                (size[0] - panel_width - margin, margin),
                (margin, size[1] - panel_height - margin),
                (size[0] - panel_width - margin, size[1] - panel_height - margin),
            ]
            # Prefer a corner with the fewest route samples underneath it.
            def overlap_score(candidate: tuple[int, int]) -> int:
                x0, y0 = candidate
                x1, y1 = x0 + panel_width, y0 + panel_height
                return sum(x0 <= px <= x1 and y0 <= py <= y1 for px, py in route)
            panel_x, panel_y = min(candidates, key=overlap_score)
            panel_position = (panel_x, panel_y, panel_width, panel_height)
            if self.settings.overlay_style == "matrix":
                text_color, panel_fill, panel_outline = (85, 225, 105, 255), (0, 24, 8, 185), (55, 155, 75, 255)
            else:
                text_color, panel_fill, panel_outline = (245, 245, 245, 255), (0, 0, 0, 200), (220, 220, 220, 255)
            od.rectangle((panel_x, panel_y, panel_x + panel_width, panel_y + panel_height), fill=panel_fill, outline=panel_outline, width=1)
            for i, (line, font) in enumerate(zip(lines, text_fonts)):
                od.text((panel_x + 27, panel_y + 16 + i * line_height), line, fill=text_color, font=font)
        attribution_size = max(16, round(16 * size[0] / 1280))
        attribution_x, attribution_y = size[0] - 360, 14
        if panel_position and panel_position[0] + panel_position[2] > size[0] - 450 and panel_position[1] < 100:
            attribution_y = size[1] - attribution_size - 14
        od.text((attribution_x, attribution_y), self.settings.attribution, fill="white", font=_font(attribution_size))
        return map_layer, plane_layer, overlay_layer

    def _eye(self, progress: float, sign: int) -> Image.Image:
        map_layer, plane_layer, overlay_layer = self._layers(progress)
        current = interpolate(self.track.points, timeline_time(self.track.points, progress, self.settings.duration_s))
        x, y = self._project(current.latitude, current.longitude, self.bounds, self.settings.width, self.settings.height)
        map_dx = self.settings.map_parallax_px + self.settings.map_tilt_px * (y / max(1, self.settings.height) - 0.5)
        altitude = current.altitude_ft or 0.0
        altitude_factor = min(2.0, max(0.0, altitude / 10000.0)) * self.settings.altitude_gain
        # At ground level the aircraft shares the map plane. Altitude adds
        # only an incremental depth offset on top of the map's base parallax.
        plane_dx = self.settings.clamped_parallax(sign * (map_dx + self.settings.aircraft_parallax_px * altitude_factor))
        overlay_dx = self.settings.clamped_parallax(sign * self.settings.overlay_parallax_px)
        result = self._tilt_map(map_layer, sign)
        result.alpha_composite(self._shift(plane_layer, plane_dx))
        result.alpha_composite(self._shift(overlay_layer, overlay_dx))
        result = result.convert("RGB")
        return ImageOps.grayscale(result).convert("RGB") if self.settings.grayscale else result

    def frame(self, progress: float) -> Image.Image:
        content_progress = self.settings.content_progress(progress)
        left, right = self._eye(content_progress, 1), self._eye(content_progress, -1)
        out = Image.new("RGB", (self.settings.width * 2, self.settings.height))
        out.paste(left, (0, 0)); out.paste(right, (self.settings.width, 0))
        return out

    def anaglyph(self, progress: float) -> Image.Image:
        content_progress = self.settings.content_progress(progress)
        left, right = self._eye(content_progress, 1), self._eye(content_progress, -1)
        return Image.merge("RGB", (left.getchannel("R"), right.getchannel("G"), right.getchannel("B")))
