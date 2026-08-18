# Delta for Project Foundation

## ADDED Requirements

### Requirement: Linux-first, replaceable integrations

The system SHALL keep external media-tool execution behind replaceable adapters. Core domain, normalization, and CLI orchestration code MUST NOT depend on Apple-only frameworks or direct subprocess calls.

#### Scenario: Missing optional tool

- **GIVEN** a requested inspection capability requires an unavailable tool
- **WHEN** the user runs the inspection command
- **THEN** the command returns a helpful structured diagnostic naming the capability and tool
- **AND** it does not crash or claim an unsupported result.

### Requirement: Source preservation

The system SHALL treat every inspected source file as immutable.

#### Scenario: Inspection of a source asset

- **GIVEN** a readable media source file
- **WHEN** the user runs `spatial3d inspect FILE`
- **THEN** no source bytes, timestamps, metadata, or adjacent derived media are modified by the inspection operation.

### Requirement: Evidence-preserving normalization

The system SHALL retain raw observations alongside normalized metadata and shall make uncertainty visible.

#### Scenario: Unknown metadata unit

- **GIVEN** an adapter returns a spatial-looking value without a confirmed unit
- **WHEN** the inspector constructs an asset result
- **THEN** it preserves the raw value
- **AND** emits an uncertainty warning
- **AND** does not fabricate a normalized unit or value.

