from __future__ import annotations

from app.schemas import TrackObservation
from utils.geometry import centroid_from_bbox


class ResultParser:
    @staticmethod
    def to_tracks(result) -> list[TrackObservation]:
        tracks: list[TrackObservation] = []
        if result is None or result.boxes is None:
            return tracks

        ids = result.boxes.id
        if ids is None:
            return tracks

        xyxy = result.boxes.xyxy.cpu().tolist()
        confs = result.boxes.conf.cpu().tolist()
        clss = result.boxes.cls.cpu().tolist()
        ids_list = ids.int().cpu().tolist()
        names = result.names

        for bbox, confidence, class_id, track_id in zip(xyxy, confs, clss, ids_list):
            bbox_tuple = tuple(float(v) for v in bbox)
            class_int = int(class_id)
            tracks.append(
                TrackObservation(
                    track_id=int(track_id),
                    class_id=class_int,
                    class_name=str(names.get(class_int, 'car')),
                    confidence=float(confidence),
                    bbox_xyxy=bbox_tuple,
                    centroid=centroid_from_bbox(bbox_tuple),
                )
            )
        return tracks
