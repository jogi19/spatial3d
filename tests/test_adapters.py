from pathlib import Path
import unittest

from spatial3d.adapters.exiftool import ExifToolAdapter, ExifToolError
from spatial3d.adapters.ffprobe import FfprobeAdapter, ProbeError
from spatial3d.adapters.runner import CommandResult


class FakeRunner:
    def __init__(self, result: CommandResult) -> None:
        self.result = result
        self.calls: list[tuple[str, ...]] = []

    def run(self, arguments: tuple[str, ...], *, working_directory: Path | None = None) -> CommandResult:
        self.calls.append(arguments)
        return self.result


class AdapterTests(unittest.TestCase):
    def test_ffprobe_reads_structured_fixture(self) -> None:
        runner = FakeRunner(CommandResult(("ffprobe",), 0, '{"streams": [], "format": {}}', ""))
        result = FfprobeAdapter(runner).probe(Path("sample.mov"))
        self.assertEqual(result["streams"], [])
        self.assertIn("-show_streams", runner.calls[0])

    def test_ffprobe_rejects_invalid_json_and_tool_failure(self) -> None:
        invalid = FakeRunner(CommandResult(("ffprobe",), 0, "not-json", ""))
        with self.assertRaises(ProbeError):
            FfprobeAdapter(invalid).probe(Path("sample.mov"))
        failed = FakeRunner(CommandResult(("ffprobe",), 1, "", "invalid input"))
        with self.assertRaisesRegex(ProbeError, "invalid input"):
            FfprobeAdapter(failed).probe(Path("sample.mov"))

    def test_exiftool_reads_json_fixture_and_rejects_failure(self) -> None:
        runner = FakeRunner(CommandResult(("exiftool",), 0, '[{"File:ImageWidth": 100}]', ""))
        self.assertEqual(ExifToolAdapter(runner).inspect(Path("sample.heic"))["File:ImageWidth"], 100)
        failed = FakeRunner(CommandResult(("exiftool",), 1, "", "cannot read file"))
        with self.assertRaisesRegex(ExifToolError, "cannot read file"):
            ExifToolAdapter(failed).inspect(Path("sample.heic"))
