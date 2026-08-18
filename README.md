# spatial3d

spatial3d is a Linux-first, cross-platform toolkit for understanding,
inspecting, viewing, converting, and processing stereoscopic/spatial media.

The project principle is **automatic when wanted, inspectable when wanted**.
SBS, HSBS, and anaglyph are future derived outputs, not the internal stereo
model. Source media is always treated as immutable.

## Status

M0 (project foundation) is complete. No media parsing or processing is
implemented yet. The approved design and unstarted M1 inspection work are in
openspec/changes/initialize-inspection-foundation/.

## Development

Python 3.11 or newer is required. M0 intentionally provides only project
identity and help.

    python3 -m spatial3d --help
    PYTHONPATH=src python3 -m unittest discover -s tests -v

FFmpeg/ffprobe and ExifTool are external tools, not Python dependencies. M1
will discover and report their availability through adapters.

## Contributing test data

Do not commit personal photos or videos. See docs/fixture-policy.md.
