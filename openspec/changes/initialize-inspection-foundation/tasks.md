# Tasks

> Implementation is in progress; approval is recorded in task 3.1. The 2026-09-16 repository audit reopened partially fulfilled tasks. See `docs/openspec-review-2026-09-16.md` for evidence and completion criteria. Do not archive this change yet.

## M0 — project foundation

- [ ] 1.1 Select and document supported Python/tooling versions and package layout.
- [x] 1.2 Create packaging, CLI entry point, test configuration, and developer documentation skeleton.
- [x] 1.3 Define domain-model, adapter, capability, and diagnostic interfaces.
- [ ] 1.4 Add fake-adapter tests proving domain/application code is isolated from subprocess execution.
- [ ] 1.5 Define fixture capture/redaction procedure and add representative non-personal tool-output fixtures.

## M1 — inspect

- [ ] 2.1 Implement FFprobe adapter version/capability discovery and structured MOV/MV-HEVC probing.
- [ ] 2.2 Implement ExifTool adapter version/capability discovery and structured HEIC/HEIF probing.
- [ ] 2.3 Implement evidence-based classification and normalization with explicit ambiguity warnings.
- [ ] 2.4 Implement human-readable `inspect` presentation and versioned `--json` serialization.
- [ ] 2.5 Add unit tests for ratios, units, missing/unknown metadata, view ambiguity, and JSON stability.
- [ ] 2.6 Add opt-in integration smoke tests against locally supplied real Spatial MOV and HEIC files; document required commands/tools.

## Approval gate

- [x] 3.1 Receive user approval of the proposal/design and any amendments before starting M0 or M1.
