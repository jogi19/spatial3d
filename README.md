# spatial3d

spatial3d is a Linux-first, cross-platform toolkit for understanding,
inspecting, viewing, converting, and processing stereoscopic/spatial media.

The project principle is **automatic when wanted, inspectable when wanted**.
SBS, HSBS, and anaglyph are future derived outputs, not the internal stereo
model. Source media is always treated as immutable.

## Status

The M0 foundation and the first M1 video-inspection slice are implemented.
`spatial3d inspect FILE` can probe MOV/MP4-family inputs through `ffprobe`,
report stream and spatial evidence, normalize the currently evidenced ratio
fields, and preserve unresolved view ordering as a warning. HEIC inspection
uses ExifTool to report primary and auxiliary image evidence, depth and gain
map metadata, while preserving unresolved auxiliary ordering. Decoding,
conversion, and output writing remain out of scope. The design and remaining
M1 work are tracked in
`openspec/changes/initialize-inspection-foundation/`.

## Development

Python 3.11 or newer is required. M0 intentionally provides only project
identity and help.

    python3 -m spatial3d --help
    PYTHONPATH=src python3 -m unittest discover -s tests -v

FFmpeg/ffprobe and ExifTool are external tools, not Python dependencies. M1
will discover and report their availability through adapters.

### Inspection JSON contract

`spatial3d inspect FILE --json` emits one JSON object with `schema_version: 1`.
Successful results include classification, source facts, normalized values and
warnings. Failures return exit code 2 with `classification: "inspection_error"`
and an `error` object containing a code and message.

## Contributing test data

Do not commit personal photos or videos. See docs/fixture-policy.md.
