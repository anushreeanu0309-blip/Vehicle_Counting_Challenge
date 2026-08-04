from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.pipeline import VehicleCountingPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='AetherEdge vehicle counting CLI')
    parser.add_argument('--input', required=True, help='Path to input video')
    parser.add_argument('--output', default='outputs/run_cli', help='Output directory')
    parser.add_argument('--config', default='config/default.yaml', help='Config path')
    parser.add_argument('--conf', type=float, default=None, help='Confidence threshold override')
    parser.add_argument('--iou', type=float, default=None, help='IOU threshold override')
    parser.add_argument('--line-position', type=float, default=None, help='Line position ratio override')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    overrides = {}
    if args.conf is not None:
        overrides.setdefault('inference', {})['conf'] = args.conf
    if args.iou is not None:
        overrides.setdefault('inference', {})['iou'] = args.iou
    if args.line_position is not None:
        overrides.setdefault('line', {})['position_ratio'] = args.line_position

    pipeline = VehicleCountingPipeline(config_path=args.config, overrides=overrides or None)
    summary = pipeline.process_video(input_video=Path(args.input), output_dir=Path(args.output))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
