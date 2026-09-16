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

Purpose: provide a small PySide6 application for selecting iPhone MOV/HEIC
files, inspecting them, assembling compatible clips and exporting derived
FSBS/HSBS previews.

Suggested increments:

1. File picker and M1 inspection results.
2. Compatibility checks and clip list.
3. View extraction and preview.
4. FSBS/HSBS export through ffmpeg, with an explicitly simple global depth
   offset slider.
5. Batch processing and, where safe, stream-copy concatenation.

FSBS/HSBS output requires decoding and re-encoding; it cannot generally be
created by stream-copying an Apple Spatial source. Lossless Apple-Spatial
joining and Apple-compatible Spatial output are later goals and require
separate validation of MV-HEVC metadata preservation.

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
