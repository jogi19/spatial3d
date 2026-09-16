"""Tests for M0 command-line identity and help."""

from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from spatial3d import __version__
from spatial3d.cli import build_parser, main


class CliTests(unittest.TestCase):
    def test_version_is_exposed(self) -> None:
        with self.assertRaises(SystemExit) as exited:
            main(["--version"])

        self.assertEqual(exited.exception.code, 0)
        self.assertEqual(__version__, "0.1.0.dev0")

    def test_parser_accepts_no_arguments(self) -> None:
        self.assertEqual(main([]), 0)
        self.assertEqual(build_parser().prog, "spatial3d")

    def test_json_mode_is_machine_readable_for_local_video(self) -> None:
        sample = Path("testdata/IMG_0831.MOV")
        if not sample.is_file():
            self.skipTest("local smoke-test media is not present")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["inspect", str(sample), "--json"]), 0)
        import json
        result = json.loads(output.getvalue())
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["classification"], "spatial_video")

    def test_json_mode_reports_missing_source_structurally(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["inspect", "does-not-exist.mov", "--json"]), 2)
        import json
        result = json.loads(output.getvalue())
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["classification"], "inspection_error")
        self.assertEqual(result["error"]["code"], "inspection.failed")

    def test_human_output_includes_stream_facts(self) -> None:
        sample = Path("testdata/IMG_0831.MOV")
        if not sample.is_file():
            self.skipTest("local smoke-test media is not present")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["inspect", str(sample)]), 0)
        self.assertIn("stream 0:", output.getvalue())
