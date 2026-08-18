# Proposal: Establish the spatial-media inspection foundation

## Intent

Create the smallest safe foundation for `spatial3d`: a Linux-first Python CLI whose first useful command is `spatial3d inspect FILE`. The command will identify and report Apple Spatial MOV/MV-HEVC and Apple Spatial HEIC metadata in a normalized, understandable form, without changing source files or pretending uncertain metadata is understood.

This change is planning only. It deliberately does **not** implement M0 or M1 until this proposal is approved.

## Problem summary

Spatial media is routinely reduced to side-by-side (SBS) before its structure can be examined. That loses the distinction between source views, spatial metadata, optional depth/disparity data, audio, and the ordinary 2D primary image. Apple Spatial formats are important initial inputs, but the core must work on Linux and must not depend on Apple frameworks.

`spatial3d` will make automatic workflows possible while retaining an inspectable path: users can see source facts, raw metadata, normalized values, warnings, and eventually each processing step.

## Scope

M0/M1 will establish:

- a typed Python package and `spatial3d` CLI entry point;
- adapter boundaries for `ffprobe` and `exiftool` (and future tools);
- immutable normalized inspection models plus retained raw observations;
- `spatial3d inspect FILE` human output and `--json` output;
- initial Apple Spatial MOV/MV-HEVC and Apple Spatial HEIC recognition;
- diagnostics for missing tools, invalid files, unknown/ambiguous metadata, and unsupported formats;
- metadata fixtures and unit/integration-test separation.

M0/M1 will **not** decode views, extract HEIC imagery, crop, alter disparity, render previews, write output media, or modify originals.

## Success criterion

On Linux, with supported external tools installed, these commands return useful normalized facts and explicit warnings rather than guesses or crashes:

```text
spatial3d inspect <real Apple Spatial MOV>
spatial3d inspect <real Apple Spatial HEIC>
```

`spatial3d inspect FILE --json` additionally emits one documented, machine-readable object on stdout.

## Why this boundary

Inspection precedes conversion/viewing because it gives us fixture-backed evidence about view ordering, container fields, units, and HEIC auxiliary-image conventions. It also prevents a later output pipeline from embedding assumptions that cannot be audited.

## Approval requested

Before implementation, approve or amend the decisions listed in the companion `design.md`, particularly the conservative ambiguity policy, provisional normalization conventions, output schema compatibility policy, and scope of M1 HEIC support.

