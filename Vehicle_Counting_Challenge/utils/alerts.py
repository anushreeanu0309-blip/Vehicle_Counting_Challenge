from __future__ import annotations

from typing import Any


def build_crossing_alert(track_id: int, total_count: int, direction: str) -> str:
    return f'Track {track_id} counted crossing {direction}. Total count={total_count}'


def milestone_alert(total_count: int) -> str:
    return f'Count milestone reached: {total_count}'


def speed_alert(track_id: int, speed_kmh: float, threshold: float) -> str:
    return f'Track {track_id} estimated speed {speed_kmh:.2f} km/h exceeded threshold {threshold:.2f} km/h'


def summarize_alerts(alerts: list[dict[str, Any]]) -> list[str]:
    return [str(a.get('message', '')) for a in alerts]
