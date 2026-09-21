# Roadmap beyond M1

M1 remains the foundation for read-only, evidence-based inspection. Two
additional project tracks may proceed independently once their inputs and
outputs are clearly defined.

## Track A: Blender 3D text generator

Purpose: generate a parameterized 3D text scene through Blender's background
Python interface.

Initial interface:

    blender --background --python scripts/text_generator.py -- \
      --text "Hallo Welt" --output output/text.blend

Later this can be wrapped by a `spatial3d text3d` command. The first version
does not depend on Spatial Video or HEIC decoding. It may reuse project
configuration, logging and output conventions, but remains a separate Blender
script with its own tests and examples.

## Track B: spatial-video helper GUI

Purpose: provide a small PySide6 application for selecting iPhone Spatial
Video files and producing one ordered SBS video. Apple Spatial sources are
converted to SBS clips first; the resulting SBS clips are then concatenated.

Suggested increments:

1. File picker and M1 inspection results.
2. Ordered clip list and compatibility checks.
3. Convert each Spatial Video to a uniform SBS representation.
4. Concatenate the generated SBS clips in selection order.
5. Add optional mixing of already-SBS inputs.

The Spatial-to-SBS step requires decoding the views and re-encoding the SBS
result. Once every intermediate has identical codec, dimensions, frame rate,
pixel format and audio layout, the final concatenation can usually use
FFmpeg's concat demuxer with stream-copy and avoid another video
decode/encode cycle. The first version may use a single combined FFmpeg
pipeline if temporary clips are unnecessary, but it must preserve selection
order and report when stream-copy compatibility is unavailable.

Mixing already-SBS inputs with Spatial inputs is useful but optional for the
first version. It requires probing those inputs, verifying their SBS geometry
and normalizing them to the same output parameters.

## Shared boundaries and overlap

Both tracks can reuse the M1 CLI, tool discovery, process runner, diagnostics
and inspection JSON. The GUI should call application services rather than
duplicate ffprobe or ExifTool parsing. The Blender generator should not assume
that a Spatial asset is available.

The tracks intentionally do not change M1's conservative rules: no silent
left/right inference, no modification of source files, and no claim that a
disparity ratio is already a pixel shift. A future GUI slider may initially
offer a documented global offset mode while the per-pixel disparity pipeline
is researched separately.

Neither track blocks the other. M2 media extraction benefits from both the GUI
and the video helper, but the Blender text generator can be developed and
tested before M2 is complete.
