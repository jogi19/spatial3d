"""M1 inspection use case and conservative normalizer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from spatial3d.adapters.ffprobe import FfprobeAdapter, ProbeError


def _fraction(value: str | None) -> str | None:
    if not value or "/" not in value:
        return value
    numerator, denominator = value.split("/", 1)
    try:
        if int(denominator) == 0:
            return value
        return f"{int(numerator) / int(denominator):g}"
    except ValueError:
        return value


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
            }
        )
    spatial_tag = tags.get("com.apple.quicktime.spatial.format-version")
    is_spatial = spatial_tag is not None or any(
        stream.get("codec_tag_string") == "hvc1" and stream.get("codec_type") == "video"
        for stream in streams
        if isinstance(stream, dict)
    ) and "spatial" in str(source).lower()
    warnings: list[dict[str, str]] = []
    if not spatial_tag:
        warnings.append(
            {
                "code": "spatial.metadata_not_observed",
                "message": "No Apple spatial format-version tag was observed by this FFprobe.",
            }
        )
    warnings.append(
        {
            "code": "spatial.view_order_unresolved",
            "message": "Left/right view ordering is not inferred by M1.",
        }
    )
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
        "spatial_metadata": {
            "format_version": spatial_tag,
            "baseline": None,
            "horizontal_field_of_view": None,
            "horizontal_disparity_adjustment": None,
        },
        "warnings": warnings,
        "tool": {"name": "ffprobe", "version": tool_version},
    }


def inspect_file(source: Path, *, ffprobe: FfprobeAdapter, tool_version: str | None = None) -> dict[str, Any]:
    """Inspect one supported M1 input without writing beside it."""
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() in {".heic", ".heif"}:
        return {
            "schema_version": 1,
            "source": {"path": str(source), "suffix": source.suffix.lower()},
            "classification": "heic_uninspected",
            "warnings": [
                {
                    "code": "dependency.exiftool_unavailable",
                    "message": "HEIC inspection requires the ExifTool adapter; no photo metadata was guessed.",
                }
            ],
        }
    try:
        raw = ffprobe.probe(source)
    except ProbeError:
        raise
    return normalize_ffprobe(source, raw, tool_version=tool_version)
