from app.counter import VehicleCounter
from app.schemas import TrackObservation


def make_track(track_id: int, cx: float, cy: float) -> TrackObservation:
    return TrackObservation(
        track_id=track_id,
        class_id=2,
        class_name='car',
        confidence=0.9,
        bbox_xyxy=(cx - 10, cy - 5, cx + 10, cy + 5),
        centroid=(cx, cy),
    )


def test_exact_once_crossing_count():
    counter = VehicleCounter(line=((0, 100), (200, 100)), count_direction='top_to_bottom')
    counter.update([make_track(1, 50, 90)], frame_index=1, fps=30)
    counter.update([make_track(1, 50, 110)], frame_index=2, fps=30)
    counter.update([make_track(1, 50, 130)], frame_index=3, fps=30)
    assert counter.total_count == 1
    assert 1 in counter.counted_track_ids


def test_no_count_without_crossing():
    counter = VehicleCounter(line=((0, 100), (200, 100)), count_direction='top_to_bottom')
    counter.update([make_track(2, 50, 50)], frame_index=1, fps=30)
    counter.update([make_track(2, 50, 70)], frame_index=2, fps=30)
    assert counter.total_count == 0
