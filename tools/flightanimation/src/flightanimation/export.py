from __future__ import annotations

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

from .render import Renderer


def ffmpeg_command(frame_pattern: str, output: str, fps: int, codec: str = "libx264") -> list[str]:
    if fps not in (25, 30):
        raise ValueError("fps must be 25 or 30")
    return ["ffmpeg", "-y", "-framerate", str(fps), "-i", frame_pattern, "-c:v", codec, "-pix_fmt", "yuv420p", output]


def export_video(renderer: Renderer, output: str | Path, codec: str = "libx264", ffmpeg: str = "ffmpeg", progress: Callable[[int, int], None] | None = None, status: Callable[[str], None] | None = None) -> int:
    count = renderer.settings.frame_count()
    if status:
        status(f"Erzeuge {count} SBS-Frames …")
    with TemporaryDirectory(prefix="flightanimation-") as temp:
        pattern = str(Path(temp) / "frame-%06d.png")
        for index in range(count):
            renderer.frame(index / max(1, count - 1)).save(Path(temp) / f"frame-{index + 1:06d}.png")
            if progress:
                progress(index + 1, count)
        command = [ffmpeg, "-y", "-framerate", str(renderer.settings.fps), "-i", pattern, "-c:v", codec, "-pix_fmt", "yuv420p", str(output)]
        if status:
            status("Frames fertig, FFmpeg kodiert das Video …")
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise RuntimeError("FFmpeg wurde nicht gefunden") from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"FFmpeg fehlgeschlagen: {exc.stderr[-1000:]}") from exc
    return count
