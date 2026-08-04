# AetherEdge Vehicle Counting & Flow Analysis Challenge

A production-ready, challenge-ready computer vision system for **vehicle counting, line crossing analytics, alerts, logging, annotated video generation, FastAPI serving, Streamlit interaction, batch processing, and containerized deployment**.

## Key Capabilities

- Detects **cars only** from fixed CCTV footage using **Ultralytics YOLO + ByteTrack**
- Maintains a **unique Track ID** for each car
- Counts each vehicle **exactly once** when crossing a configurable virtual line
- Prevents duplicate counting via a **counted Track ID set**
- Generates:
  - annotated output video
  - CSV event log
  - JSON event log
  - live alerts
  - cars-per-minute chart
  - session metadata
- Deployable as:
  - **CLI tool**
  - **Streamlit dashboard**
  - **FastAPI REST API**
  - **Docker / Docker Compose** stack
- Bonus features:
  - speed estimation (pixel-space, calibration-ready)
  - direction analysis
  - ONNX export script
  - OpenVINO export script

---

## Project Structure

```text
Vehicle_Counting_Challenge/
├── app/
│   ├── __init__.py
│   ├── counter.py
│   ├── detector.py
│   ├── main.py
│   ├── pipeline.py
│   ├── schemas.py
│   └── tracker.py
├── config/
│   ├── bytetrack.yaml
│   └── default.yaml
├── logs/
│   └── .gitkeep
├── models/
│   └── README.md
├── outputs/
│   └── .gitkeep
├── report/
│   ├── architecture_diagram.svg
│   ├── flowchart.svg
│   └── project_report.md
├── sample_outputs/
│   └── README.md
├── screenshots/
│   └── README.md
├── scripts/
│   ├── export_onnx.py
│   ├── export_openvino.py
│   └── run_batch.py
├── tests/
│   ├── test_config.py
│   └── test_counter.py
├── utils/
│   ├── __init__.py
│   ├── alerts.py
│   ├── config.py
│   ├── exceptions.py
│   ├── geometry.py
│   ├── graphs.py
│   ├── io.py
│   ├── logger.py
│   ├── speed.py
│   └── video.py
├── api.py
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── README.md
├── requirements.txt
└── streamlit_app.py
```

---

## Installation

### 1) Create environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\activate   # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

### 2) Optional model weights

Default config uses `yolo11n.pt`. Ultralytics will automatically download weights on first run.

---

## Quick Start: CLI

```bash
python -m app.main --input /path/to/video.mp4 --output outputs/run_cli
```

With custom thresholds:

```bash
python -m app.main \
  --input /path/to/video.mp4 \
  --output outputs/run_cli \
  --conf 0.35 \
  --iou 0.45 \
  --line-position 0.58
```

Artifacts created:

- `annotated.mp4`
- `events.csv`
- `events.json`
- `summary.json`
- `cars_per_minute.png`

---

## Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

Features included:

- Upload video
- Confidence slider
- IOU slider
- Line position slider
- Start Processing button
- Original video preview
- Processed video preview
- Total vehicle count
- Live alerts
- Logs table
- Download buttons
- FPS display

---

## FastAPI Service

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

### Endpoints

- `GET /health`
- `POST /predict`
- `GET /artifacts/{session_id}/{filename}`

### Example request

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@/path/to/video.mp4" \
  -F "conf=0.30" \
  -F "iou=0.45" \
  -F "line_position=0.55"
```

---

## Docker

### Build

```bash
docker build -t aetheredge-vehicle-counter .
```

### Run Streamlit

```bash
docker run --rm -p 8501:8501 -v $(pwd)/outputs:/app/outputs aetheredge-vehicle-counter
```

### Run API

```bash
docker run --rm -p 8000:8000 -v $(pwd)/outputs:/app/outputs aetheredge-vehicle-counter \
  uvicorn api:app --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
docker compose up --build
```

---

## Configuration

Main configuration lives in `config/default.yaml`.

Important fields:

- model name
- confidence threshold
- IOU threshold
- car class filtering
- tracker configuration
- line position / points
- alert thresholds
- speed calibration
- output toggles

---

## Counting Logic

The project maintains a `counted_track_ids` set and increments only when:

1. the previous centroid is **above** the virtual line
2. the current centroid is **below** the virtual line
3. the track ID has **not been counted before**

This ensures exact-once counting for `top_to_bottom` mode.

---

## Tests

```bash
pytest -q
```

---

## ONNX & OpenVINO Export

```bash
python scripts/export_onnx.py --model yolo11n.pt
python scripts/export_openvino.py --model yolo11n.pt
```

---

## Outputs

Each processing session writes a dedicated timestamped folder under `outputs/` containing:

- processed video
- CSV log
- JSON log
- summary JSON
- chart image

---

## Future Improvements

- multi-line origin-destination analytics
- ReID-enhanced cross-camera tracking
- true metric speed using homography calibration
- Kafka / Redis event streaming
- Grafana / Prometheus monitoring
- Triton inference serving

---

## References

- Ultralytics YOLO documentation
- ByteTrack paper and tracking methodology
- OpenCV video processing APIs
- FastAPI documentation
- Streamlit documentation
