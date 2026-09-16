"""Opt-in smoke tests against user-supplied real media files."""
import os
from pathlib import Path
import shutil
import unittest

from spatial3d.adapters.exiftool import ExifToolAdapter
from spatial3d.adapters.ffprobe import FfprobeAdapter
from spatial3d.adapters.process import SubprocessCommandRunner
from spatial3d.inspection.inspect import inspect_file


class SmokeTests(unittest.TestCase):
    def test_real_mov_inspection_when_configured(self) -> None:
        value = os.environ.get("SPATIAL3D_SMOKE_MOV")
        if not value or not shutil.which("ffprobe"):
            self.skipTest("set SPATIAL3D_SMOKE_MOV and install ffprobe to run")
        result = inspect_file(Path(value), ffprobe=FfprobeAdapter(SubprocessCommandRunner()))
        self.assertIn("streams", result)

    def test_real_heic_inspection_when_configured(self) -> None:
        value = os.environ.get("SPATIAL3D_SMOKE_HEIC")
        if not value or not shutil.which("exiftool"):
            self.skipTest("set SPATIAL3D_SMOKE_HEIC and install exiftool to run")
        result = inspect_file(Path(value), ffprobe=FfprobeAdapter(SubprocessCommandRunner()), exiftool=ExifToolAdapter(SubprocessCommandRunner()))
        self.assertIn("primary_2d", result)
