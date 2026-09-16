# Repository and OpenSpec review — 2026-09-16

## Result

The repository contains a working inspection prototype, not a completed M0/M1
contract. Keep `initialize-inspection-foundation` active. Formal OpenSpec
validation passes, but it does not validate implementation conformance.

The review includes the existing uncommitted video/HEIC changes. No runtime
code was changed by this review. The existing approval record (task 3.1) is
retained; this review does not independently establish its historical provenance.

## Verified baseline

- OpenSpec CLI 1.3.1: `openspec validate --all` passes (one change).
- `openspec status --change initialize-inspection-foundation` finds all four
  planning artifacts. Artifact completion does not mean implementation completion.
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: eight tests pass
  on this macOS host, including the automatically activated local MOV test.
- No Linux validation was performed. No tracked tool-output fixtures or JSON
  schema snapshots exist. Local personal media is ignored by Git.
- There are only change-local delta specs; no `openspec/specs` baseline exists
  yet. Establish that baseline when the implemented change is ready to archive.

## Findings and required follow-up

### 1. Classification is too permissive (high priority)

`src/spatial3d/inspection/inspect.py:161` classifies any auxiliary type, depth
version, gain-map version, or multiple image dimensions as a spatial photo.
Reproduction: passing only `{"XMP-HDRGainMap:HDRGainMapVersion": "1"}` to
`normalize_exiftool` returns `spatial_photo`, without any stereo evidence.
Image dimensions also do not establish item identity or stereo membership.

At line 80, any nonempty view-ID list establishes spatial video.
A video stream with only `view_ids_available: "0"` returns `spatial_video`.

Define positive, fixture-backed classification evidence, preserve generic
auxiliary evidence separately, and add ordinary/ambiguous negative cases.
Do not invent left/right mappings. The existing unmapped-view policy is sound.

### 2. Numeric and evidence contracts are incomplete (high priority)

`_fraction` uses binary floating point and default `g` formatting:
`123456789/100000000` becomes `1.23457`. A zero denominator is returned as
the purported normalized value. Use Decimal-based normalization with a
documented precision policy; invalid ratios need raw preservation and diagnostics.

Disparity output lacks the required explicit uncertain semantic status.
The baseline scale is declared confirmed without a fixture/provenance reference
in the repository. Unknown units need warnings. Preserve raw observations:
normalizers currently discard unselected tool fields and side data.

### 3. Error handling and execution limits are incomplete (high priority)

The process runner has no timeout despite the design requirement. CLI errors
are plain text on stdout, including in JSON mode, and do not use the existing
structured diagnostic model. Permission/process errors are not comprehensively
translated. `side_data_list: null` reproducibly raises `TypeError`.

Add bounded execution and structured diagnostics for missing tools, invalid
files/output and timeouts. Define and test JSON error output and exit status.
Validate source existence before invoking tool version discovery.

### 4. Presentation and architecture diverge from the design

Human output omits facts available in JSON, including per-stream codec,
geometry, frame rate, camera facts and tool version. The JSON contract is not
documented beyond `schema_version`. Complete and test presentation parity.

The application service still returns an M0 placeholder. Actual orchestration
returns mutable dictionaries from `inspection/inspect.py`; the proposed immutable
asset model is not implemented. Either implement the documented boundary/model
or explicitly amend the design before claiming conformance.

### 5. Test completion claims exceed coverage

The boundary tests exercise an unused placeholder and tool lookup, not fake
adapters through the real inspection path. There are no adapter parsing/error
tests, JSON snapshots or representative committed redacted fixtures.

The MOV smoke test runs automatically when a fixed local file exists. It is
not explicitly opt-in and does not skip missing tools. There is no HEIC smoke
test. Add explicit environment-variable inputs, tool availability checks and
documented commands, keeping normal tests independent of personal media/tools.

### 6. Planning documentation needs reconciliation

Proposal/design retain historical wording saying implementation has not begun;
README and fixture policy also retain stale M0/future-tense statements.
Python/setuptools/unittest/argparse are visible in code; pytest/ruff are optional
dependencies, but the full tooling/type-checker decision is not documented.

The foundation spec promises no timestamp changes. Reading can affect access
time depending on the filesystem. Clarify the intended guarantee (source bytes,
embedded metadata and modification time) before adding portable preservation tests.

## Checklist reconciliation

Reopened tasks indicate partial work, not discarded implementation:

| Task | Remaining completion evidence |
| --- | --- |
| 1.1 | Document final tooling choices and package boundaries. |
| 1.4 | Fake-runner/adapter tests covering the actual inspection path. |
| 1.5 | Committed non-personal fixtures and provenance; schema snapshots. |
| 2.1–2.2 | Capability reporting, bounded execution and adapter error tests. |
| 2.3 | Conservative classification, precise normalization, raw evidence and uncertainty. |
| 2.4 | Text/JSON parity and documented output/error contract. |
| 2.5 | Negative cases, malformed metadata, unit/ratio and JSON stability coverage. |
| 2.6 | Explicit opt-in MOV/HEIC smoke tests and Linux validation instructions. |

Recommended implementation order: classification regressions and numeric
normalization; adapter/process diagnostics; presentation and schema; fixtures
and integration tests; design reconciliation and Linux verification. Archive
only after the corresponding requirements and scenarios are satisfied.
