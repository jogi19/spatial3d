"""M0 placeholder for M1's inspect use case."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from spatial3d.domain.diagnostics import Diagnostic, Severity


@dataclass(frozen=True, slots=True)
class InspectionUnavailable:
    """Explicit M0 response until media inspection is introduced in M1."""

    source: Path
    diagnostic: Diagnostic


class InspectAsset:
    """Future inspection use case; it performs no media access in M0."""

    def unavailable(self, source: Path) -> InspectionUnavailable:
        return InspectionUnavailable(
            source=source,
            diagnostic=Diagnostic(
                code="inspection.not_implemented",
                message="Media inspection is planned for M1 and is not available yet.",
                severity=Severity.ERROR,
            ),
        )

