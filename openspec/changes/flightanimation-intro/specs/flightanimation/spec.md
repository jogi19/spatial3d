# Flight animation requirements

## Scenario: Import FR24 KML

- **WHEN** a KML contains timestamped Placemarks and height/speed in HTML
  descriptions
- **THEN** the importer extracts available metadata, sorts points by time,
  validates coordinates, and reports missing optional values without failing
  the complete track.

## Scenario: Render stereo route

- **WHEN** a frame is requested at a timeline position
- **THEN** the renderer produces independently shifted left and right views,
  with optional complete and travelled routes, one course-oriented aircraft,
  and visible attribution.

## Scenario: Export

- **WHEN** a duration and 25/30 fps are selected
- **THEN** the exporter generates exactly `round(duration * fps)` frames and
  invokes FFmpeg with argument arrays, never shell interpolation.
