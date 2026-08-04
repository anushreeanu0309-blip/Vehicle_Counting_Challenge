from __future__ import annotations

from pathlib import Path

import cv2

from utils.exceptions import VideoOpenError


def open_video(path: str | Path) -> cv2.VideoCapture:
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise VideoOpenError(f'Unable to open video: {path}')
    return capture


def create_video_writer(output_path: str | Path, fps: float, width: int, height: int, codec: str = 'mp4v') -> cv2.VideoWriter:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*codec)
    return cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
