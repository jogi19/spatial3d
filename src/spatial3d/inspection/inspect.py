"""M1 inspection use case and conservative normalizer."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from decimal import Decimal, InvalidOperation

from spatial3d.adapters.ffprobe import FfprobeAdapter, ProbeError
from spatial3d.adapters.exiftool import ExifToolAdapter


def _fraction(value: str | None) -> str | None:
    if not value or "/" not in value:
        return value
    numerator, denominator = value.split("/", 1)
    try:
        denominator_decimal = Decimal(denominator)
        if denominator_decimal == 0:
            return value
        normalized = Decimal(numerator) / denominator_decimal
        rendered = format(normalized, "f")
        if "." in rendered:
            rendered = rendered.rstrip("0").rstrip(".")
        return rendered or "0"
    except (InvalidOperation, ValueError):
        return value


def _ratio(value: str | None) -> dict[str, str | None] | None:
    if value is None:
        return None
    normalized = _fraction(value)
    return {"raw": value, "normalized": normalized}


def normalize_ffprobe(source: Path, raw: dict[str, Any], *, tool_version: str | None = None) -> dict[str, Any]:
    """Turn FFprobe's source-shaped JSON into stable, useful inspection data."""
    fmt = raw.get("format") if isinstance(raw.get("format"), dict) else {}
    tags = fmt.get("tags") if isinstance(fmt.get("tags"), dict) else {}
    streams = raw.get("streams") if isinstance(raw.get("streams"), list) else []
    normalized_streams: list[dict[str, Any]] = []
    audio_count = 0
    video_count = 0
    for stream in streams:
        if not isinstance(stream, dict):
            continue
        codec_type = stream.get("codec_type")
        if codec_type == "video":
            video_count += 1
        if codec_type == "audio":
            audio_count += 1
        normalized_streams.append(
            {
                "index": stream.get("index"),
                "type": codec_type,
                "codec": stream.get("codec_name") or stream.get("codec_tag_string"),
                "width": stream.get("width"),
                "height": stream.get("height"),
                "frame_rate": _fraction(stream.get("avg_frame_rate") or stream.get("r_frame_rate")),
                "sample_rate": stream.get("sample_rate"),
                "channels": stream.get("channels"),
                "metadata_tags": stream.get("tags", {}),
                "view_ids_available": stream.get("view_ids_available"),
                "view_pos_available": stream.get("view_pos_available"),
                "multilayer": stream.get("disposition", {}).get("multilayer"),
            }
        )
    spatial_tag = tags.get("com.apple.quicktime.spatial.format-version")
    warnings: list[dict[str, str]] = []
    if not spatial_tag:
        warnings.append(
            {
                "code": "spatial.metadata_not_observed",
                "message": "No Apple spatial format-version tag was observed by this FFprobe.",
            }
        )
    video_stream = next((s for s in streams if isinstance(s, dict) and s.get("codec_type") == "video"), {})
    side_data = video_stream.get("side_data_list", []) if isinstance(video_stream, dict) else []
    if not isinstance(side_data, list):
        side_data = []
    stereo_data = next(
        (item for item in side_data if isinstance(item, dict) and item.get("side_data_type") == "Stereo 3D"),
        {},
    )
    view_ids = str(video_stream.get("view_ids_available", "")).split(",") if video_stream.get("view_ids_available") else []
    view_positions = str(video_stream.get("view_pos_available", "")).split(",") if video_stream.get("view_pos_available") else []
    spatial_observed = bool(spatial_tag and (len(view_ids) >= 2 or stereo_data))
    is_spatial = spatial_observed
    view_ordering = "available_unmapped" if view_ids else "ambiguous"
    if spatial_observed:
        warnings.append(
            {
                "code": "spatial.view_order_unresolved",
                "message": "Left/right view ordering is not inferred by M1.",
            }
        )
    if view_ids and len(view_ids) != len(view_positions):
        warnings.append(
            {
                "code": "spatial.view_evidence_mismatch",
                "message": "View ID and view position lists have different lengths.",
            }
        )
    spatial_metadata = {
        "format_version": spatial_tag,
        "baseline": {
            "raw": stereo_data.get("baseline"),
            "millimetres": (float(stereo_data["baseline"]) / 1000.0)
            if str(stereo_data.get("baseline", "")).isdigit()
            else None,
            "unit_status": "source-scale-confirmed-for-this-field",
        }
        if stereo_data.get("baseline") is not None
        else None,
        "horizontal_field_of_view": _ratio(stereo_data.get("horizontal_field_of_view")),
        "horizontal_disparity_adjustment": _ratio(stereo_data.get("horizontal_disparity_adjustment")),
    }
    return {
        "schema_version": 1,
        "source": {"path": str(source), "suffix": source.suffix.lower()},
        "classification": "spatial_video" if is_spatial else "ordinary_or_unknown_video",
        "container": {
            "format": fmt.get("format_name"),
            "format_long_name": fmt.get("format_long_name"),
            "duration_seconds": fmt.get("duration"),
            "size_bytes": fmt.get("size"),
            "tags": tags,
        },
        "streams": normalized_streams,
        "summary": {"video_streams": video_count, "audio_streams": audio_count},
        "stereo": {
            "view_ids_available": view_ids,
            "view_positions_available": view_positions,
            "ordering": view_ordering,
            "semantic_left_right_mapping": None,
        },
        "spatial_metadata": spatial_metadata,
        "warnings": warnings,
        "tool": {"name": "ffprobe", "version": tool_version},
    }


def normalize_exiftool(source: Path, raw: dict[str, Any], *, tool_version: str | None = None) -> dict[str, Any]:
    """Normalize the small, evidence-backed subset needed for HEIC inspection."""
    primary_width = raw.get("File:ImageWidth") or raw.get("ExifIFD:ExifImageWidth")
    primary_height = raw.get("File:ImageHeight") or raw.get("ExifIFD:ExifImageHeight")
    extent = raw.get("QuickTime:ImageSpatialExtent")
    if (primary_width is None or primary_height is None) and isinstance(extent, str) and "x" in extent:
        primary_width, primary_height = extent.split("x", 1)
    auxiliary_type = raw.get("XMP-apdi:AuxiliaryImageType") or raw.get("QuickTime:AuxiliaryImageType")
    image_size_text = str(raw.get("Meta:MetaImageSize", ""))
    import re

    dimensions: list[dict[str, int]] = []
    for width, height in re.findall(r"(\d+)x(\d+)", image_size_text):
        dimensions.append({"width": int(width), "height": int(height)})
    # ExifTool's HEIF item summary encodes some auxiliary extents as
    # ``773 width height`` rather than ``widthxheight``.
    for width, height in re.findall(r"\b773\s+(\d+)\s+(\d+)", image_size_text):
        dimensions.append({"width": int(width), "height": int(height)})
    primary = {"width": primary_width, "height": primary_height}
    candidates = [item for item in dimensions if item != {"width": int(primary_width), "height": int(primary_height)}] if str(primary_width).isdigit() and str(primary_height).isdigit() else dimensions
    depth_version = raw.get("XMP-depthData:DepthDataVersion")
    gain_map_version = raw.get("XMP-HDRGainMap:HDRGainMapVersion")
    warnings = [{"code": "spatial.photo_auxiliary_order_unresolved", "message": "HEIC auxiliary image ordering and semantic view mapping are not inferred by M1."}]
    if not auxiliary_type:
        warnings.append({"code": "spatial.photo_auxiliary_type_unknown", "message": "No explicit spatial auxiliary-image type was observed by ExifTool."})
    is_spatial = bool(auxiliary_type == "disparity" or (depth_version is not None and len(candidates) >= 2))
    return {
        "schema_version": 1,
        "source": {"path": str(source), "suffix": source.suffix.lower()},
        "classification": "spatial_photo" if is_spatial else "ordinary_or_unknown_photo",
        "primary_2d": primary,
        "stereo": {"candidates": candidates, "ordering": "available_unmapped" if candidates else "ambiguous", "semantic_left_right_mapping": None},
        "auxiliary": {
            "type": auxiliary_type,
            "image_dimensions": dimensions,
            "disparity_observed": str(raw.get("XMP-apdi:AuxiliaryImageType", "")).lower() == "disparity",
            "depth_observed": depth_version is not None,
            "depth_data_version": depth_version,
            "gain_map_observed": gain_map_version is not None,
            "gain_map_version": gain_map_version,
        },
        "camera": {"make": raw.get("IFD0:Make"), "model": raw.get("IFD0:Model"), "focal_length": raw.get("ExifIFD:FocalLength")},
        "observations": {"primary_item_reference": raw.get("Meta:PrimaryItemReference"), "image_spatial_extent": extent},
        "warnings": warnings,
        "tool": {"name": "exiftool", "version": tool_version or raw.get("ExifTool:ExifToolVersion")},
    }
def inspect_file(source: Path, *, ffprobe: FfprobeAdapter, exiftool: ExifToolAdapter | None = None, tool_version: str | None = None) -> dict[str, Any]:
    """Inspect one supported M1 input without writing beside it."""
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() in {".heic", ".heif"}:
        if exiftool is None:
            return {"schema_version": 1, "source": {"path": str(source), "suffix": source.suffix.lower()}, "classification": "heic_uninspected", "warnings": [{"code": "dependency.exiftool_unavailable", "message": "HEIC inspection requires the ExifTool adapter; no photo metadata was guessed."}]}
        return normalize_exiftool(source, exiftool.inspect(source), tool_version=tool_version)
    try:
        raw = ffprobe.probe(source)
    except ProbeError:
        raise
    return normalize_ffprobe(source, raw, tool_version=tool_version)
