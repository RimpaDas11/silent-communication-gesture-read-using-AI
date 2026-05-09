"""
Prediction routes — handles image and video gesture prediction.

Router prefix: /api/predict
"""

from __future__ import annotations

import base64
import tempfile
import os
from typing import List

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from schemas.prediction import PredictionResponse
from services.model_handler import cnn_service

router = APIRouter(prefix="/api/predict", tags=["predict"])


# ---------------------------------------------------------------------------
# POST /api/predict/image
# ---------------------------------------------------------------------------

@router.post(
    "/image",
    response_model=PredictionResponse,
    summary="Predict gesture from a single image",
)
async def predict_image(file: UploadFile = File(...)) -> PredictionResponse:
    """
    Upload a JPEG / PNG image and receive a gesture prediction.

    - Reads the raw bytes
    - Decodes via OpenCV
    - Runs the mock (or real) GestureCNN model
    """
    try:
        raw_bytes = await file.read()
        np_arr = np.frombuffer(raw_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            raise ValueError("Could not decode image — unsupported format or corrupt file.")

        prediction = cnn_service.predict_frame(frame)

        return PredictionResponse(
            status="success",
            filename=file.filename or "upload.jpg",
            prediction=prediction,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# POST /api/predict/video
# ---------------------------------------------------------------------------

@router.post(
    "/video",
    response_model=PredictionResponse,
    summary="Predict dominant gesture from a video",
)
async def predict_video(file: UploadFile = File(...)) -> PredictionResponse:
    """
    Upload a video file and receive the most common gesture prediction.

    - Saves the video to a temp file
    - Samples every 10th frame
    - Aggregates predictions via majority vote
    """
    tmp_path: str | None = None
    try:
        raw_bytes = await file.read()

        # Write to a temporary file (OpenCV VideoCapture needs a file path)
        suffix = os.path.splitext(file.filename or "video.mp4")[1] or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(raw_bytes)
            tmp_path = tmp.name

        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            raise ValueError("Could not open video — unsupported format or corrupt file.")

        predictions: List[str] = []
        frame_index = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_index % 10 == 0:
                predictions.append(cnn_service.predict_frame(frame))
            frame_index += 1

        cap.release()

        if not predictions:
            raise ValueError("No frames could be extracted from the video.")

        # Majority vote
        dominant = max(set(predictions), key=predictions.count)

        return PredictionResponse(
            status="success",
            filename=file.filename or "upload.mp4",
            prediction=dominant,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {exc}",
        ) from exc
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
