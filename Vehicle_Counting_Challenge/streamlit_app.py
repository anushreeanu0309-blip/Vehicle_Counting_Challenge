from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from app.pipeline import VehicleCountingPipeline

st.set_page_config(page_title='AetherEdge Vehicle Counter', layout='wide')
st.title('AetherEdge Vehicle Counting & Flow Analysis')
st.caption('Upload a CCTV video, configure thresholds, and generate annotated outputs.')

uploaded_file = st.file_uploader('Upload Video', type=['mp4', 'avi', 'mov', 'mkv'])
col1, col2, col3 = st.columns(3)
conf = col1.slider('Confidence', min_value=0.10, max_value=0.95, value=0.30, step=0.05)
iou = col2.slider('IOU', min_value=0.10, max_value=0.95, value=0.45, step=0.05)
line_position = col3.slider('Line Position', min_value=0.10, max_value=0.90, value=0.55, step=0.01)
start = st.button('Start Processing', type='primary', use_container_width=True)

if uploaded_file is not None:
    st.subheader('Original Video Preview')
    st.video(uploaded_file)

if start and uploaded_file is not None:
    with st.spinner('Processing video... this may take a moment depending on video length and hardware.'):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / uploaded_file.name
            input_path.write_bytes(uploaded_file.getbuffer())

            overrides = {
                'inference': {'conf': conf, 'iou': iou},
                'line': {'position_ratio': line_position},
            }
           pipeline = VehicleCountingPipeline(overrides=overrides)
            summary = pipeline.process_video(input_path)

    st.success('Processing complete')
    m1, m2, m3 = st.columns(3)
    m1.metric('Total Vehicle Count', summary['total_count'])
    m2.metric('Input FPS', f"{summary['fps_input']:.2f}")
    m3.metric('Processing FPS', f"{summary['fps_effective']:.2f}")

    st.subheader('Processed Video Preview')
    st.video(summary['annotated_video'])

    st.subheader('Live Alerts')
    alerts = summary.get('alerts', [])
    if alerts:
        for item in alerts[-20:]:
            st.write(f"- [{item['level'].upper()}] {item['message']}")
    else:
        st.info('No alerts were generated for this run.')

    st.subheader('Logs Table')
    events_csv = summary.get('events_csv')
    if events_csv and Path(events_csv).exists():
        df = pd.read_csv(events_csv)
        st.dataframe(df.head(200), use_container_width=True)
    else:
        st.warning('No CSV log found.')

    st.subheader('Downloads')
    d1, d2, d3 = st.columns(3)
    for col, label, key in [
        (d1, 'Annotated Video', 'annotated_video'),
        (d2, 'CSV Log', 'events_csv'),
        (d3, 'JSON Log', 'events_json'),
    ]:
        file_path = summary.get(key)
        if file_path and Path(file_path).exists():
            with open(file_path, 'rb') as handle:
                col.download_button(label=label, data=handle.read(), file_name=Path(file_path).name, use_container_width=True)
