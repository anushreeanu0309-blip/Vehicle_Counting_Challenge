# AetherEdge Vehicle Counting & Flow Analysis Challenge Report

## 1. Introduction
This project delivers an end-to-end traffic video analytics pipeline for counting cars crossing a virtual line in fixed CCTV footage. The solution emphasizes repeatable counting, strong engineering practices, deployment readiness, and explainability.

## 2. Problem Statement
The challenge requires detecting only cars, tracking each car with a unique identity, and counting each vehicle exactly once when it crosses a configurable virtual line. The system must prevent duplicate counts, generate logs and alerts, produce an annotated video, and expose both dashboard and API interfaces.

## 3. Objectives
- Detect only cars from CCTV video
- Track every car with a stable track ID
- Count each car once and only once
- Generate artifacts for review and submission
- Provide a reproducible and deployable application stack

## 4. Dataset
The solution is designed for fixed-angle CCTV traffic footage. It assumes a stable camera and supports MP4/AVI/MOV/MKV formats. Since challenge footage may vary, thresholds are configurable without code changes.

## 5. Methodology
### 5.1 Detection
Ultralytics YOLO is used to detect cars (`COCO class id 2`). Confidence and IOU thresholds are configurable.

### 5.2 Tracking
ByteTrack is used to assign and maintain consistent track IDs across frames.

### 5.3 Counting Logic
The system stores centroid history by track ID and maintains a `counted_track_ids` set. A car is counted only when its centroid transitions from above the line to below the line and the track ID has not been counted previously.

### 5.4 Alerts
Alerts are generated when:
- a vehicle crossing occurs
- a speed estimate exceeds threshold
- total count crosses configured milestones

## 6. Architecture Diagram
See `architecture_diagram.svg`.

## 7. Flowchart
See `flowchart.svg`.

## 8. Detection, Tracking, and Counting Pipeline
1. Read frame from video source
2. Run YOLO inference for car detections
3. Apply ByteTrack to maintain track IDs
4. Update track history and compute centroid transitions
5. Count valid line crossings once per track ID
6. Annotate frame, write logs, save artifacts

## 9. Results
The produced outputs include:
- annotated MP4
- CSV event log
- JSON event log
- summary JSON
- cars-per-minute chart

## 10. Challenges
- temporary occlusions affecting tracker continuity
- perspective distortion for speed estimation
- scene-specific threshold tuning
- night-time or low-contrast footage

## 11. Future Scope
- multi-zone analytics
- true speed calibration with homography
- vehicle type expansion
- ReID-based long-term tracking
- streaming analytics deployment

## 12. Conclusion
The project provides a production-minded implementation of vehicle detection, tracking, counting, and reporting with dashboard, API, and Docker deployment paths.

## 13. References
- Ultralytics YOLO documentation
- ByteTrack methodology
- OpenCV video I/O and rendering
- FastAPI and Streamlit documentation
