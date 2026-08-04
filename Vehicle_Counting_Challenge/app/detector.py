from __future__ import annotations

from ultralytics import YOLO

from utils.logger import get_logger


class YoloCarTracker:
    def __init__(self, weights: str, tracker: str, device: str = 'cpu', imgsz: int = 960):
        self.logger = get_logger('vehicle_counter.detector')
        self.model = YOLO(weights)
        self.tracker = tracker
        self.device = device
        self.imgsz = imgsz

    def track(self, frame, conf: float, iou: float, car_class_ids: list[int]):
        results = self.model.track(
            frame,
            persist=True,
            tracker=self.tracker,
            conf=conf,
            iou=iou,
            classes=car_class_ids,
            verbose=False,
            device=self.device,
            imgsz=self.imgsz,
        )
        return results[0]
