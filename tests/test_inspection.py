"""Fixture-free M1 normalizer and adapter-boundary tests."""

from __future__ import annotations

from pathlib import Path
import unittest

from spatial3d.inspection.inspect import normalize_exiftool, normalize_ffprobe


class InspectionTests(unittest.TestCase):
    def test_gain_map_alone_is_not_spatial_photo(self) -> None:
        result = normalize_exiftool(Path("ordinary.heic"), {"XMP-HDRGainMap:HDRGainMapVersion": "1"})
        self.assertEqual(result["classification"], "ordinary_or_unknown_photo")

    def test_single_view_is_not_spatial_video(self) -> None:
        result = normalize_ffprobe(Path("ordinary.mov"), {"streams": [{"codec_type": "video", "view_ids_available": "0"}]})
        self.assertEqual(result["classification"], "ordinary_or_unknown_video")

    def test_malformed_side_data_is_tolerated(self) -> None:
        result = normalize_ffprobe(Path("broken.mov"), {
            "streams": [{"codec_type": "video", "side_data_list": None}],
        })
        self.assertEqual(result["classification"], "ordinary_or_unknown_video")

    def test_ratio_normalization_preserves_decimal_precision(self) -> None:
        result = normalize_ffprobe(Path("sample.mov"), {"streams": [], "format": {"tags": {}}})
        self.assertEqual(result["spatial_metadata"]["horizontal_field_of_view"], None)
        self.assertEqual(normalize_ffprobe.__globals__["_fraction"]("123456789/100000000"), "1.23456789")
    def test_heic_normalizer_reports_primary_and_auxiliary_candidates(self) -> None:
        result = normalize_exiftool(
            Path("sample.HEIC"),
            {
                "ExifTool:ExifToolVersion": "13.55",
                "File:ImageWidth": 5712,
                "File:ImageHeight": 4284,
                "Meta:MetaImageSize": "5712x4284 0 2688x2016 0 2688x2016",
                "XMP-apdi:AuxiliaryImageType": "disparity",
                "XMP-depthData:DepthDataVersion": 65541,
                "XMP-HDRGainMap:HDRGainMapVersion": "0.2.0.0",
                "IFD0:Make": "Apple",
                "IFD0:Model": "iPhone 16",
            },
        )
        self.assertEqual(result["classification"], "spatial_photo")
        self.assertEqual(result["primary_2d"], {"width": 5712, "height": 4284})
        self.assertEqual(result["stereo"]["candidates"], [{"width": 2688, "height": 2016}, {"width": 2688, "height": 2016}])
        self.assertTrue(result["auxiliary"]["depth_observed"])
        self.assertTrue(result["auxiliary"]["gain_map_observed"])
        self.assertIsNone(result["stereo"]["semantic_left_right_mapping"])

    def test_ordinary_video_classification_does_not_depend_on_source_path(self) -> None:
        raw = {"streams": [{"codec_type": "video", "codec_name": "hevc"}]}

        for source in (Path("normal.mov"), Path("spatial/normal.mov")):
            with self.subTest(source=source):
                result = normalize_ffprobe(source, raw)
                self.assertEqual(result["classification"], "ordinary_or_unknown_video")
                self.assertFalse(any(w["code"] == "spatial.view_order_unresolved" for w in result["warnings"]))

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
                        "view_ids_available": "0,1",
                        "view_pos_available": "2,1",
                        "side_data_list": [
                            {
                                "side_data_type": "Stereo 3D",
                                "baseline": 17737,
                                "horizontal_field_of_view": "63400/1000",
                                "horizontal_disparity_adjustment": "200/10000",
                            }
                        ],
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
        self.assertEqual(result["stereo"]["ordering"], "available_unmapped")
        self.assertEqual(result["spatial_metadata"]["baseline"]["millimetres"], 17.737)
        self.assertEqual(result["spatial_metadata"]["horizontal_field_of_view"]["normalized"], "63.4")
        self.assertEqual(
            result["spatial_metadata"]["horizontal_disparity_adjustment"]["normalized"], "0.02"
        )
        self.assertTrue(any(w["code"] == "spatial.view_order_unresolved" for w in result["warnings"]))
