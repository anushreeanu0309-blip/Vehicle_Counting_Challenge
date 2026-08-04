from __future__ import annotations

from utils.geometry import Point


def estimate_speed_kmh(prev_point: Point, curr_point: Point, fps: float, meters_per_pixel: float = 0.05) -> float:
    dx = curr_point[0] - prev_point[0]
    dy = curr_point[1] - prev_point[1]
    pixel_distance = (dx ** 2 + dy ** 2) ** 0.5
    meters = pixel_distance * meters_per_pixel
    meters_per_second = meters * fps
    return meters_per_second * 3.6
