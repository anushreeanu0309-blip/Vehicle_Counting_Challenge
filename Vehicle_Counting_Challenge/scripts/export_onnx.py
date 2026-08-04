from __future__ import annotations

import argparse

from ultralytics import YOLO


def main() -> None:
    parser = argparse.ArgumentParser(description='Export YOLO model to ONNX')
    parser.add_argument('--model', default='yolo11n.pt')
    parser.add_argument('--imgsz', type=int, default=960)
    args = parser.parse_args()

    model = YOLO(args.model)
    result = model.export(format='onnx', imgsz=args.imgsz)
    print(result)


if __name__ == '__main__':
    main()
