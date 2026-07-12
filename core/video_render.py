from __future__ import annotations

from collections.abc import Callable
import os
import shutil
import subprocess
from typing import TypeAlias

import pygame


FinishFrame: TypeAlias = Callable[[pygame.Surface, int, int], None]


def setup_video_rendering(
    *,
    size: tuple[int, int],
    fps: int,
    interpolating_factor: int,
    video_params: dict[str, object],
) -> tuple[FinishFrame, Callable[[], None], int]:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    output_fps = int(video_params.get("output_fps", fps * max(1, interpolating_factor)))
    max_steps = int(video_params.get("num_frames", video_params.get("num_steps", fps * 10)))
    if max_steps < 1:
        raise ValueError("video_params['num_frames'] must be greater than or equal to 1")

    writer = _VideoFrameWriter(size, output_fps, video_params)

    def finish_frame(
        frame_surface: pygame.Surface,
        frame_fps: int,
        video_repeats: int = 1,
    ) -> None:
        writer.write_frame(frame_surface, video_repeats)

    return finish_frame, writer.close, max_steps


class _VideoFrameWriter:
    def __init__(
        self,
        size: tuple[int, int],
        fps: int,
        video_params: dict[str, object],
    ) -> None:
        ffmpeg_name = str(video_params.get("ffmpeg_path", "ffmpeg"))
        ffmpeg_path = shutil.which(ffmpeg_name)
        if ffmpeg_path is None:
            raise RuntimeError(
                "ffmpeg was not found; install it or pass video_params['ffmpeg_path']"
            )

        self.output_path = str(video_params.get("output_path", "render.mp4"))
        crf = str(video_params.get("crf", video_params.get("quality", 18)))
        preset = str(video_params.get("preset", "medium"))
        if fps < 1:
            raise ValueError("video output_fps must be greater than or equal to 1")

        width, height = size
        command = [
            ffmpeg_path,
            "-y",
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-s",
            f"{width}x{height}",
            "-pix_fmt",
            "rgb24",
            "-r",
            str(fps),
            "-i",
            "-",
            "-an",
            "-vcodec",
            "libx264",
            "-preset",
            preset,
            "-crf",
            crf,
            "-pix_fmt",
            "yuv420p",
            self.output_path,
        ]
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def write_frame(self, surface: pygame.Surface, repeats: int = 1) -> None:
        if self.process.stdin is None:
            raise RuntimeError("ffmpeg stdin is closed")

        frame_bytes = pygame.image.tostring(surface, "RGB")
        for _ in range(repeats):
            self.process.stdin.write(frame_bytes)

    def close(self) -> None:
        if self.process.stdin is not None:
            self.process.stdin.close()

        stderr = self.process.stderr.read() if self.process.stderr is not None else b""
        self.process.wait()
        if self.process.returncode != 0:
            raise RuntimeError(stderr.decode("utf-8", errors="replace"))
