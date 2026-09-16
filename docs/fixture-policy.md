# Fixture and local-media policy

The normal test suite must be small, reproducible, and safe to run in public
CI. It must not require a personal source photo or video, FFmpeg, or ExifTool.

## Committed fixtures

Commit only:

- redacted machine-readable output captured from tools such as ffprobe and
  exiftool;
- small synthetic data that does not derive from a personal asset; and
- public samples whose redistribution licence is recorded next to the fixture.

Before committing captured output, remove source paths, GPS coordinates,
timestamps if sensitive, device serial numbers, owner/author fields, and
unnecessary identifiers. Preserve the structural metadata and values required
by the parser test. Give each fixture a short provenance/redaction note.

Opt-in smoke tests can be run with `SPATIAL3D_SMOKE_MOV=/path/sample.MOV`
and/or `SPATIAL3D_SMOKE_HEIC=/path/sample.HEIC` before the normal unittest
command. They skip automatically when the variable or required tool is absent.

## Local smoke tests

Real Apple Spatial MOV/HEIC files stay outside Git. Future integration tests
will be opt-in, require an explicit path/environment variable, and skip when
the necessary external tool is unavailable. They must be read-only and must
not create derived media beside the original.
