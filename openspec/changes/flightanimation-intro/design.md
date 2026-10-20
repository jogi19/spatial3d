# Design: FR24 flight animation intro

```text
KML file -> parser -> FlightTrack -> timeline/interpolation
                                      |             |
                                projection      renderer
                                      |             |
                              Pillow stereo frames -> FFmpeg
                                      |
                              PySide6 preview/config UI
```

`FlightTrack` stores validated measurements and cumulative along-track
distance. `Timeline` maps real timestamps to a user-selected clip duration and
linearly interpolates numeric values, while longitude interpolation handles
the antimeridian. `Projection` maps geographic bounds to pixels without making
altitude a physical camera coordinate.

Stereo is created from independently rendered eye canvases. A signed pixel
offset is applied per layer: map, aircraft, and overlay. Values are clamped to
a conservative fraction of image width. The aircraft visual depth is derived
from normalized altitude and a user gain, not from a claim of physical scale.

The initial map provider is `BlankMapProvider` plus an optional local raster
image. A future provider can implement the same `MapProvider` protocol for
cached OSM tiles or local vector rendering. No network access is performed by
the prototype.
