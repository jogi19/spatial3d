"""Tests for M0 command-line identity and help."""

from __future__ import annotations

import unittest

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

