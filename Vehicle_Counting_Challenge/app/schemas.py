from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class TrackObservation:
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    bbox_xyxy: tuple[float, float, float, float]
    centroid: tuple[float, float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CountEvent:
    timestamp: str
    frame_index: int
    track_id: int
    direction: str
    line_position: dict[str, Any]
    centroid: tuple[float, float]
    speed_kmh: float | None
    alert: str

    @classmethod
    def create(
        cls,
        frame_index: int,
        track_id: int,
        direction: str,
        line_position: dict[str, Any],
        centroid: tuple[float, float],
        speed_kmh: float | None,
        alert: str,
    ) -> "CountEvent":
        return cls(
            timestamp=datetime.now(UTC).isoformat().replace('+00:00', 'Z'),
            frame_index=frame_index,
            track_id=track_id,
            direction=direction,
            line_position=line_position,
            centroid=centroid,
            speed_kmh=speed_kmh,
            alert=alert,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
