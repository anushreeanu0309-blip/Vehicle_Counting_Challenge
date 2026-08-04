from __future__ import annotations

from dataclasses import asdict

from app.schemas import CountEvent, TrackObservation
from utils.alerts import build_crossing_alert, milestone_alert, speed_alert
from utils.geometry import has_crossed_line, movement_direction
from utils.speed import estimate_speed_kmh


class VehicleCounter:
    def __init__(self, line: tuple[tuple[float, float], tuple[float, float]], count_direction: str = 'top_to_bottom', speed_enabled: bool = True, meters_per_pixel: float = 0.05, speed_threshold_kmh: float = 35.0, milestones: list[int] | None = None):
        self.line = line
        self.count_direction = count_direction
        self.speed_enabled = speed_enabled
        self.meters_per_pixel = meters_per_pixel
        self.speed_threshold_kmh = speed_threshold_kmh
        self.milestones = set(milestones or [])
        self.track_history: dict[int, tuple[float, float]] = {}
        self.counted_track_ids: set[int] = set()
        self.total_count = 0
        self.direction_counts: dict[str, int] = {'up': 0, 'down': 0, 'left': 0, 'right': 0, 'stationary': 0}
        self.events: list[dict] = []
        self.alerts: list[dict] = []

    def update(self, tracks: list[TrackObservation], frame_index: int, fps: float) -> None:
        for track in tracks:
            prev = self.track_history.get(track.track_id)
            self.track_history[track.track_id] = track.centroid
            if prev is None:
                continue

            direction = movement_direction(prev, track.centroid)
            self.direction_counts[direction] = self.direction_counts.get(direction, 0) + 1

            crossed = has_crossed_line(prev, track.centroid, self.line, self.count_direction)
            if not crossed or track.track_id in self.counted_track_ids:
                continue

            self.counted_track_ids.add(track.track_id)
            self.total_count += 1

            speed_kmh = None
            if self.speed_enabled:
                speed_kmh = estimate_speed_kmh(prev, track.centroid, fps, self.meters_per_pixel)

            event = CountEvent.create(
                frame_index=frame_index,
                track_id=track.track_id,
                direction=direction,
                line_position={'p1': self.line[0], 'p2': self.line[1]},
                centroid=track.centroid,
                speed_kmh=speed_kmh,
                alert=build_crossing_alert(track.track_id, self.total_count, direction),
            )
            event_dict = event.to_dict()
            event_dict['fps_for_chart'] = fps
            self.events.append(event_dict)
            self.alerts.append({'frame_index': frame_index, 'track_id': track.track_id, 'message': event.alert, 'level': 'info'})

            if speed_kmh is not None and speed_kmh >= self.speed_threshold_kmh:
                self.alerts.append({'frame_index': frame_index, 'track_id': track.track_id, 'message': speed_alert(track.track_id, speed_kmh, self.speed_threshold_kmh), 'level': 'warning'})

            if self.total_count in self.milestones:
                self.alerts.append({'frame_index': frame_index, 'track_id': track.track_id, 'message': milestone_alert(self.total_count), 'level': 'success'})
