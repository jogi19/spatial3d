"""Fixture-free M1 normalizer and adapter-boundary tests."""

from __future__ import annotations

from pathlib import Path
import unittest

from spatial3d.inspection.inspect import normalize_ffprobe


class InspectionTests(unittest.TestCase):
    def test_normalizer_preserves_unknown_view_order_and_normalizes_rate(self) -> None:
        result = normalize_ffprobe(
            Path("sample.MOV"),
            {
                "streams": [
                    {
                        "index": 0,
                        "codec_type": "video",
                        "codec_name": "hevc",
                        "width": 1920,
                        "height": 1080,
                        "avg_frame_rate": "30/1",
                    },
                    {"index": 1, "codec_type": "audio", "codec_name": "aac"},
                ],
                "format": {
                    "format_name": "mov",
                    "tags": {"com.apple.quicktime.spatial.format-version": "1.0"},
                },
            },
        )
        self.assertEqual(result["classification"], "spatial_video")
        self.assertEqual(result["streams"][0]["frame_rate"], "30")
        self.assertTrue(any(w["code"] == "spatial.view_order_unresolved" for w in result["warnings"]))

