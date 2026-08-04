from __future__ import annotations

import argparse
from pathlib import Path

from app.pipeline import VehicleCountingPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Batch process a folder of videos')
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--output-root', default='outputs/batch_runs')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = VehicleCountingPipeline()
    input_dir = Path(args.input_dir)
    videos = [p for p in input_dir.iterdir() if p.suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv'}]
    for video in videos:
        session_output = Path(args.output_root) / video.stem
        summary = pipeline.process_video(video, output_dir=session_output, session_name=video.stem)
        print(f"Processed {video.name} -> count={summary['total_count']}")


if __name__ == '__main__':
    main()
