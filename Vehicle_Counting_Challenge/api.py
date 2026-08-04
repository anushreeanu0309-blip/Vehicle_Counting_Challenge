from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.pipeline import VehicleCountingPipeline

app = FastAPI(title='AetherEdge Vehicle Counting API', version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

outputs_dir = Path('outputs')
outputs_dir.mkdir(parents=True, exist_ok=True)
app.mount('/static', StaticFiles(directory=str(outputs_dir)), name='static')


@app.get('/health')
def health() -> dict:
    return {'status': 'ok'}


@app.post('/predict')
async def predict(
    file: UploadFile = File(...),
    conf: float = Form(0.30),
    iou: float = Form(0.45),
    line_position: float = Form(0.55),
):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / file.filename
        with open(input_path, 'wb') as handle:
            shutil.copyfileobj(file.file, handle)

        overrides = {
            'inference': {'conf': conf, 'iou': iou},
            'line': {'position_ratio': line_position},
        }
        pipeline = VehicleCountingPipeline(overrides=overrides)
        summary = pipeline.process_video(input_path)

    session_id = summary['session_id']
    base = f'/artifacts/{session_id}'
    return {
        'session_id': session_id,
        'total_count': summary['total_count'],
        'annotated_video': f"{base}/{Path(summary['annotated_video']).name}",
        'csv_log': f"{base}/{Path(summary['events_csv']).name}" if summary.get('events_csv') else None,
        'json_log': f"{base}/{Path(summary['events_json']).name}" if summary.get('events_json') else None,
        'summary': summary,
    }


@app.get('/artifacts/{session_id}/{filename}')
def get_artifact(session_id: str, filename: str):
    path = outputs_dir / session_id / filename
    return FileResponse(path)
