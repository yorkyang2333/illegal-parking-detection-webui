"""
Standalone FastAPI service for SAM 3 video inference.
Deploy this on a CUDA-capable machine separately from the main Flask backend.

Usage:
    pip install -e /path/to/sam3
    pip install -r requirements.txt
    uvicorn app:app --host 0.0.0.0 --port 8100
"""

import os
import tempfile

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from predictor import SAM3Predictor, analyze_violations

app = FastAPI(title="SAM 3 Vehicle Tracking Service")

USE_MOCK = os.environ.get("SAM3_MOCK", "false").lower() == "true"
predictor = SAM3Predictor(use_mock=USE_MOCK)


@app.post("/segment-video")
async def segment_video(video: UploadFile = File(...)):
    suffix = os.path.splitext(video.filename or "video.mp4")[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await video.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = predictor.process_video(tmp_path)
        if "error" in result:
            return JSONResponse(status_code=400, content=result)
        return result
    finally:
        os.unlink(tmp_path)


@app.get("/health")
async def health():
    return {"status": "ok", "mock_mode": predictor.use_mock}
