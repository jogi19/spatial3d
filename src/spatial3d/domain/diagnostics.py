"""Structured diagnostics shared by adapters and application services."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    """Severity suitable for text and JSON presentation."""

    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A stable diagnostic that does not expose implementation exceptions."""

    code: str
    message: str
    severity: Severity
    hint: str | None = None

