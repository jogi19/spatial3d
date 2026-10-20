# Proposal: FR24 flight animation subproject

## Intent

Add an isolated Python subproject at `tools/flightanimation/` that imports
Flightradar24 KML tracks, interpolates a flight path, renders a map-based
stereo animation, and exports deterministic side-by-side video through FFmpeg.

## Scope

The first slice includes robust KML/HTML parsing, geodesic distance and
interpolation, a flat equirectangular map renderer, Pillow-based deterministic
frames, left/right parallax and anaglyph previews, a small PySide6 GUI, and a
safe FFmpeg export adapter. It deliberately keeps the subproject's dependencies
and packaging separate from the root `spatial3d` package.

## Mapping decision

The prototype uses a supplied/local raster map or a generated neutral map and
an equirectangular projection. This avoids automated OSM tile downloading,
rate-limit and attribution risks during tests. The renderer boundary leaves
room for an OSM tile provider or local OSM vector renderer later. Any OSM-backed
output must show `© OpenStreetMap-Mitwirkende` and comply with the selected
provider's terms.

## Acceptance

Synthetic fixtures cover parsing, interpolation, route distance, projection,
depth, SBS dimensions/order, frame counts, and safe FFmpeg command construction.
The GUI and export remain optional at import time so core tests run without a
desktop session or FFmpeg binary.
