"""Tests proving M0 code stays tool-process independent."""

from __future__ import annotations

from pathlib import Path
import unittest

from spatial3d.adapters.capabilities import ToolCapability, ToolLocator
from spatial3d.application.inspection import InspectAsset
from spatial3d.domain.diagnostics import Severity


class BoundaryTests(unittest.TestCase):
    def test_missing_tool_is_a_structured_status(self) -> None:
        status = ToolLocator().locate(ToolCapability.PHOTO_METADATA, "definitely-not-a-tool")

        self.assertFalse(status.available)
        self.assertIsNone(status.path)
        self.assertEqual(status.capability, ToolCapability.PHOTO_METADATA)

    def test_inspection_placeholder_does_not_probe_a_file(self) -> None:
        response = InspectAsset().unavailable(Path("private-source.heic"))

        self.assertEqual(response.diagnostic.code, "inspection.not_implemented")
        self.assertEqual(response.diagnostic.severity, Severity.ERROR)

