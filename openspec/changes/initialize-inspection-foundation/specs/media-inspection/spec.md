# Delta for Media Inspection

## ADDED Requirements

### Requirement: Inspect targeted Apple spatial media

The system SHALL provide `spatial3d inspect FILE` that inspects evidence from Apple Spatial MOV/MV-HEVC and Apple Spatial HEIC sources on Linux, where necessary configured tools are available.

#### Scenario: Spatial Video evidence is available

- **GIVEN** an Apple Spatial MOV whose probe output exposes multilayer HEVC view evidence
- **WHEN** the user runs `spatial3d inspect FILE`
- **THEN** output identifies the source as spatial-video evidence when warranted
- **AND** reports container/codec, available view evidence, per-view geometry, frame rate, audio facts, and available spatial metadata
- **AND** presents raw source values and warnings for fields it cannot normalize.

#### Scenario: Spatial Photo evidence is available

- **GIVEN** an Apple Spatial HEIC whose metadata exposes a primary image and spatial-related image/auxiliary evidence
- **WHEN** the user runs `spatial3d inspect FILE`
- **THEN** output identifies the source as spatial-photo evidence when warranted
- **AND** reports primary representation, stereo-related candidates, depth/disparity and auxiliary candidates, and available camera facts
- **AND** does not extract, crop, or rewrite the source.

### Requirement: No silent stereo-order inference

The system MUST NOT label source representations as semantic left/right unless the mapping is supported by documented parser evidence and a validated rule.

#### Scenario: Two views without a proven mapping

- **GIVEN** a probe exposes two distinct view IDs but no validated left/right mapping
- **WHEN** the asset is inspected
- **THEN** output reports both available views and raw ordering evidence
- **AND** marks semantic ordering as ambiguous or available-unmapped
- **AND** emits no left/right label.

### Requirement: Versioned machine-readable inspection result

The system SHALL support `spatial3d inspect FILE --json` and emit a single versioned JSON result on stdout.

#### Scenario: JSON and human results agree

- **GIVEN** a successfully inspected file
- **WHEN** the command is run with and without `--json`
- **THEN** both outputs convey the same classification, normalized facts, raw observations, and warnings
- **AND** JSON contains `schema_version`.

### Requirement: Disparity metadata is inspected but not applied

The system SHALL preserve and normalize a horizontal disparity adjustment only when its numeric unit is evidenced, and SHALL not calculate a pixel shift or modify a view in M1.

#### Scenario: Disparity value with unresolved semantics

- **GIVEN** a source reports a horizontal disparity-adjustment ratio whose interpretation is not fully confirmed
- **WHEN** it is inspected
- **THEN** output includes raw ratio and any safe normalized fraction
- **AND** labels semantic status as uncertain
- **AND** reports no pixel offset or applied adjustment.

