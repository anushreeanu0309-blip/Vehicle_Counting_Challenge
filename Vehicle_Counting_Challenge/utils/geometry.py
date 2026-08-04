from __future__ import annotations

from typing import Literal

Point = tuple[float, float]
Line = tuple[Point, Point]


def centroid_from_bbox(bbox_xyxy: tuple[float, float, float, float]) -> Point:
    x1, y1, x2, y2 = bbox_xyxy
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def point_side(point: Point, line: Line) -> float:
    (x1, y1), (x2, y2) = line
    px, py = point
    return (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)


def has_crossed_line(prev_point: Point, curr_point: Point, line: Line, direction: str = 'top_to_bottom') -> bool:
    prev_side = point_side(prev_point, line)
    curr_side = point_side(curr_point, line)

    if direction == 'top_to_bottom':
        return prev_side < 0 <= curr_side
    if direction == 'bottom_to_top':
        return prev_side > 0 >= curr_side
    return prev_side == 0 or curr_side == 0 or (prev_side < 0 < curr_side) or (prev_side > 0 > curr_side)


def movement_direction(prev_point: Point, curr_point: Point) -> Literal['up', 'down', 'left', 'right', 'stationary']:
    dx = curr_point[0] - prev_point[0]
    dy = curr_point[1] - prev_point[1]
    if abs(dx) < 1 and abs(dy) < 1:
        return 'stationary'
    if abs(dy) >= abs(dx):
        return 'down' if dy > 0 else 'up'
    return 'right' if dx > 0 else 'left'
