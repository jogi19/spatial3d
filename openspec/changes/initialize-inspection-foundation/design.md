# Design: M0/M1 inspection foundation

## Exploration outcome

The repository is a new Git workspace with no source, package configuration, or prior OpenSpec artifacts. Therefore this proposal establishes a baseline rather than modifies existing behavior. The proposed M0/M1 boundary is inspection only: discover and normalize evidence, but never transform media.

## Goals and terminology

| Term | Meaning in this project |
| --- | --- |
| Asset | An immutable source file plus its inspection result. |
| Primary image | The ordinary 2D image intended for backwards-compatible display; it is not automatically a stereo view. |
| Stereo view pair | Two separately addressable source views. Their semantic left/right labels are assigned only when evidence supports them. |
| Spatial metadata | Metadata describing spatial capture/presentation, including baseline, FOV, view information, and disparity adjustment. |
| Raw observation | Tool- or container-specific value preserved verbatim (or structurally equivalent) for diagnostics. |
| Normalized value | A typed, documented value with a project-defined unit. It never replaces the raw observation. |
| Disparity adjustment | A source-specified horizontal stereo-placement adjustment. Its semantics are not yet confirmed for all Apple assets. |
| SBS / HSBS / anaglyph | Derived output or preview representations, never the internal stereo representation. |

## Initial architecture

```text
CLI presentation
    -> application service: inspect(path)
        -> dependency discovery / tool runners
        -> source adapters (ffprobe, ExifTool, future native parsers)
        -> source recognizers and parsers
        -> normalized domain model + warnings
    -> text formatter or JSON serializer
```

The application service owns orchestration and error translation. Tool adapters own command construction, process execution, version discovery, and structured-output parsing. Domain models and normalizers contain no subprocess calls. A future decoder/export backend follows the same adapter contract and is optional.

Suggested package boundaries for implementation (not created by this change):

```text
src/spatial3d/{cli,application,domain,adapters,inspection}
tests/{unit,integration,fixtures}
```

## External tools and adapter policy

| Tool/backend | M1 role | Availability policy |
| --- | --- | --- |
| `ffprobe` from FFmpeg | Primary structured probe for MOV/HEVC streams, multiview side data, frame/audio/container facts. | Required for Spatial Video inspection. Version and capability are reported. |
| `exiftool` | HEIC/HEIF metadata and auxiliary-image-oriented inspection; corroborates fields where useful. | Required only for the HEIC capabilities it supplies. Its absence is a clear capability error, never a crash. |
| FFmpeg decode/encode | None in M1 beyond `ffprobe`. | Deferred to conversion/viewing adapters. |
| Blender Python | None. | Deferred and optional. |
| Apple `spatial` CLI / Apple frameworks | None. | Never a core dependency; possible optional comparison/export backend later. |

M1 adapters execute configured tool binaries directly (no shell), request machine-readable output, apply time/error limits, and return typed results or structured diagnostics. No domain object may expose a subprocess object.

## Normalized domain model

The model below is an evaluated refinement of the suggested models. It keeps the generic `SpatialAsset` root and uses `SpatialVideo`/`SpatialPhoto` only as typed inspection variants. Container-specific maps stay in `raw_metadata`.

```text
SpatialAsset
  source: SourceDescriptor(path, byte_size?, media_kind, container?, codec?)
  classification: ordinary | spatial_video | spatial_photo | unknown
  primary_2d: ImageRepresentation?        # photo only when known
  stereo: StereoViewPair?                 # absent when unproven
  spatial_metadata: SpatialMetadata?
  depth_map: DepthMapInfo?
  audio: tuple[AudioStreamInfo, ...]
  cameras: tuple[CameraMetadata, ...]
  observations: tuple[RawObservation, ...]
  warnings: tuple[InspectionWarning, ...]

StereoViewPair
  views: tuple[ViewRepresentation, ViewRepresentation]
  ordering: confirmed | available_unmapped | ambiguous
  semantic_mapping: left/right only when confirmed
  evidence: tuple[Evidence, ...]

SpatialMetadata
  baseline: Length?                        # millimetres
  horizontal_fov: Angle?                   # degrees
  horizontal_disparity_adjustment: DisparityAdjustment?

DisparityAdjustment
  normalized_fraction: Decimal             # dimensionless, e.g. 0.0200
  source_value: RawObservation
  semantic_status: confirmed | value_known_semantics_uncertain
```

`Length` uses millimetres in normalized public output. `Angle` uses degrees. `Decimal` (serialized as a JSON string) is preferred for source ratios so values such as `200/10000` are not needlessly rounded. JSON includes `schema_version: 1` from its first implementation. New optional fields are additive; breaking interpretation changes require a new schema version.

### Provisional view and disparity rules

M1 may report view IDs and positions exactly as supplied by `ffprobe`, with raw side-data evidence. It must **not** turn `view_pos_available` or stream order into left/right unless the mapping is proven by documented semantics and fixtures.

M1 may normalize a reported disparity numeric ratio into a dimensionless fraction when the source unit is evidenced. It must label the semantic status as uncertain until sign convention, reference view, width basis, and virtual-camera/application semantics are resolved. Pixel offsets and application to views are explicitly deferred to M2 after this contract is approved and unit-tested.

## Confirmed facts supplied for planning

- Linux (MX Linux initially) is primary; macOS matters but Apple frameworks cannot be core dependencies.
- The tested iPhone 16 Spatial Video is recognized by FFmpeg 8.x as multilayer HEVC / MV-HEVC with two available views. Its observed per-view geometry is 1920x1080 at 30 fps.
- That sample exposes baseline `17737`, horizontal FOV `63400/1000`, and horizontal disparity adjustment `200/10000`; these are sample facts, not defaults.
- Observed Spatial HEIC has a 5712x4284 primary image and two 2688x2016 stereo-related images, plus depth/disparity, camera, distortion, gain-map, and auxiliary data.
- Spatial photo paired views may originate from different cameras and may require later photometric matching.

## Assumptions to validate, not encode as truth

- `ffprobe` structured output exposes enough multiview evidence on target FFmpeg versions to identify two available MV-HEVC views.
- ExifTool can expose enough HEIC/HEIF structure to report primary and stereo-related images without extracting/re-encoding them.
- Apple fields named like baseline, horizontal FOV, and disparity adjustment retain observed units across assets. Every parser must retain evidence and warn when units are not known.
- HEIC auxiliary-image naming/order is stable enough to classify candidates; otherwise M1 reports candidates, not a confirmed stereo pair.

## Technical uncertainties / research backlog

1. Authoritative mapping of MV-HEVC view IDs/positions to left/right, including whether Apple files ever reverse storage order.
2. Complete Apple horizontal-disparity-adjustment semantics: units, sign, zero-plane intent, width basis, and exact application to each view.
3. Exact HEIC item-reference/property conventions that distinguish primary image, stereo pair, depth/disparity, gain map, and auxiliary images.
4. Whether Apple playback performs documented/observable photometric or lens matching on Spatial Photos.
5. Minimum supported FFmpeg and ExifTool versions and capability matrix on MX Linux and macOS.
6. Linux-native MV-HEVC encode/decode support and round-trip Apple compatibility (deferred past M1).
7. A privacy-safe way to collect redacted real-tool outputs and tiny derived fixtures without committing personal media.

## M0: project foundation (precise scope)

M0 creates package/tooling/documentation infrastructure only. It selects a supported Python version, packaging/build tool, formatter/linter/type-checker, test runner, CLI library, and a documented fixture policy. It creates adapter interfaces, capability discovery, error taxonomy, and a placeholder CLI capable of showing help/version. It does not parse media.

Small, testable M0 checkpoints:

1. Bootstrap: package installs in an isolated environment; `spatial3d --help` and test collection run.
2. Boundaries: fake-tool unit tests prove the application service does not call subprocesses directly; missing-tool diagnostics are predictable.
3. Fixtures: a documented redaction/capture procedure, JSON schema snapshots, and no personal binary asset required by the normal test suite.

## M1: inspect (precise scope)

M1 implements `spatial3d inspect FILE [--json]` for the two targeted Apple source families. It invokes M0 adapters, classifies only when evidence supports classification, normalizes known units, preserves raw evidence, and emits warnings for unknown/ambiguous fields. Human output prioritizes classification, representations, streams, stereo evidence, spatial values plus units, auxiliary/depth candidates, camera facts, and warnings. JSON returns the same information structurally.

M1's HEIC promise is metadata inspection, not pixel extraction or view decoding. “Stereo-related images” may remain candidates until their semantics are validated. An ordinary HEIC/MOV is a valid input and must be reported as non-spatial/unsupported-in-M1 rather than misclassified.

Small, testable M1 checkpoints:

1. Video evidence: fixture-driven MV-HEVC parsing reports per-view dimensions, rate, audio and raw view evidence.
2. Photo evidence: fixture-driven HEIC parsing reports primary, auxiliary, depth/disparity and camera candidates.
3. Presentation: text and versioned JSON outputs agree; real-media smoke tests are opt-in and validate on Linux.

## Deferred functionality

- video/photo decoding, extraction, conversion, crop, preview, viewer and manual/Apple/zero disparity modes;
- calculation or application of a disparity pixel offset;
- output encoding, stream-copy concat, audio preservation in output;
- batch workflows, Kdenlive/MLT, Blender, GUI, and distribution;
- MV-HEVC output and optional Apple `spatial` backend.

## Decisions requiring approval

1. Approve the conservative rule: unknown or ambiguous view order is reported as such, never silently labelled left/right.
2. Approve millimetres, degrees, and dimensionless `Decimal` fraction as normalized inspection units, with original values retained.
3. Approve a JSON `schema_version` and decimal-as-string compatibility policy.
4. Approve ExifTool as the initial HEIC metadata adapter, with no guarantee of extracted stereo imagery in M1.
5. Approve the exact M0 tooling choices when proposed at implementation time, or specify preferences now (Python version, `pytest`, `typer`, `ruff`, `mypy`/`pyright`, build backend).
6. Approve fixture policy: commit redacted command-output fixtures and small synthetic/public samples only; keep personal originals outside Git and run opt-in local smoke tests.

