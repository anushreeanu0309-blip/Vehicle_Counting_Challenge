from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import cv2

from app.counter import VehicleCounter
from app.detector import YoloCarTracker
from app.tracker import ResultParser
from utils.config import load_config
from utils.graphs import save_cars_per_minute_chart
from utils.io import ensure_dir, timestamp_slug, write_csv, write_json
from utils.logger import get_logger
from utils.video import create_video_writer, open_video


class VehicleCountingPipeline:
    def __init__(self, config_path: str = 'config/default.yaml', overrides: dict[str, Any] | None = None):
        self.cfg = load_config(config_path, overrides=overrides)
        self.logger = get_logger('vehicle_counter.pipeline', self.cfg['project']['log_root'])
        self.detector = YoloCarTracker(
            weights=self.cfg['model']['weights'],
            tracker=self.cfg['model']['tracker'],
            device=self.cfg['model']['device'],
            imgsz=int(self.cfg['model']['imgsz']),
        )

    def _resolve_line(self, width: int, height: int):
        if self.cfg['line'].get('mode') == 'points' and self.cfg['line'].get('p1') and self.cfg['line'].get('p2'):
            p1 = tuple(self.cfg['line']['p1'])
            p2 = tuple(self.cfg['line']['p2'])
            return (float(p1[0]), float(p1[1])), (float(p2[0]), float(p2[1]))
        y = int(height * float(self.cfg['line']['position_ratio']))
        return (0.0, float(y)), (float(width), float(y))

    def process_video(self, input_video: str | Path, output_dir: str | Path | None = None, session_name: str | None = None) -> dict[str, Any]:
        input_video = Path(input_video)
        session_id = session_name or timestamp_slug('vehicle_count')
        root = ensure_dir(output_dir or Path(self.cfg['project']['output_root']) / session_id)

        capture = open_video(input_video)
        fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

        line = self._resolve_line(width, height)
        counter = VehicleCounter(
            line=line,
            count_direction=self.cfg['line']['count_direction'],
            speed_enabled=bool(self.cfg['speed']['enable']),
            meters_per_pixel=float(self.cfg['speed']['meters_per_pixel']),
            speed_threshold_kmh=float(self.cfg['alerts']['speed_threshold_kmh']),
            milestones=list(self.cfg['alerts']['count_milestones']),
        )

        annotated_path = root / 'annotated.mp4'
        writer = create_video_writer(annotated_path, fps, width, height, codec=self.cfg['output']['codec'])

        conf = float(self.cfg['inference']['conf'])
        iou = float(self.cfg['inference']['iou'])
        car_class_ids = list(self.cfg['inference']['car_class_ids'])
        frame_stride = max(1, int(self.cfg['inference']['max_frame_stride']))
        line_color = tuple(int(v) for v in self.cfg['line']['color_bgr'])
        line_thickness = int(self.cfg['line']['thickness'])

        frame_index = 0
        processed_frames = 0
        started = time.perf_counter()

        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frame_index += 1
            if frame_index % frame_stride != 0:
                continue

            result = self.detector.track(frame, conf=conf, iou=iou, car_class_ids=car_class_ids)
            tracks = ResultParser.to_tracks(result)
            counter.update(tracks, frame_index=frame_index, fps=fps)

            for track in tracks:
                x1, y1, x2, y2 = map(int, track.bbox_xyxy)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (30, 255, 30), 2)
                cv2.putText(
                    frame,
                    f'ID {track.track_id} {track.confidence:.2f}',
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )
                cx, cy = map(int, track.centroid)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

            p1 = tuple(map(int, line[0]))
            p2 = tuple(map(int, line[1]))
            cv2.line(frame, p1, p2, line_color, line_thickness)
            cv2.putText(frame, f'Total Count: {counter.total_count}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(frame, f'Frame: {frame_index}', (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if counter.alerts:
                latest = counter.alerts[-1]['message'][:70]
                cv2.putText(frame, latest, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2)

            writer.write(frame)
            processed_frames += 1

        capture.release()
        writer.release()

        elapsed = max(0.001, time.perf_counter() - started)
        effective_fps = processed_frames / elapsed

        events_csv_path = write_csv(root / 'events.csv', counter.events) if self.cfg['output']['save_csv'] else None
        events_json_path = write_json(root / 'events.json', counter.events) if self.cfg['output']['save_json'] else None
        chart_path = save_cars_per_minute_chart(counter.events, root / 'cars_per_minute.png') if self.cfg['output']['save_chart'] else None

        summary = {
            'session_id': session_id,
            'input_video': str(input_video),
            'annotated_video': str(annotated_path),
            'events_csv': str(events_csv_path) if events_csv_path else None,
            'events_json': str(events_json_path) if events_json_path else None,
            'cars_per_minute_chart': str(chart_path) if chart_path else None,
            'total_count': counter.total_count,
            'counted_track_ids': sorted(counter.counted_track_ids),
            'direction_counts': counter.direction_counts,
            'alerts': counter.alerts,
            'fps_input': fps,
            'fps_effective': effective_fps,
            'processed_frames': processed_frames,
            'total_frames': total_frames,
            'line': {'p1': line[0], 'p2': line[1], 'direction': self.cfg['line']['count_direction']},
        }
        summary_path = write_json(root / 'summary.json', summary) if self.cfg['output']['save_summary'] else None
        summary['summary_json'] = str(summary_path) if summary_path else None
        self.logger.info('Processing finished | session=%s | count=%s | output=%s', session_id, counter.total_count, root)
        return summary
