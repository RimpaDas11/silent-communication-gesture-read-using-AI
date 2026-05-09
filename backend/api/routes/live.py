"""
WebSocket route — live webcam gesture stream.

Endpoint: /ws/live

Protocol:
  Client → Server: raw Base64-encoded JPEG frame string
  Server → Client: plain-text gesture prediction
"""

from __future__ import annotations

import base64

import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.model_handler import cnn_service

router = APIRouter(tags=["live"])


@router.websocket("/ws/live")
async def live_gesture_stream(websocket: WebSocket) -> None:
    """
    Accept a WebSocket connection and process live gesture frames.

    Flow:
      1. Accept the connection.
      2. Wait for a Base64 JPEG frame from the client.
      3. Decode and run prediction.
      4. Send back the gesture label as plain text.
      5. Repeat until the client disconnects.
    """
    await websocket.accept()
    print(f"[WebSocket] Client connected: {websocket.client}")

    try:
        while True:
            # Expect a Base64-encoded JPEG string
            data: str = await websocket.receive_text()

            try:
                # Strip optional data-URI prefix (e.g. "data:image/jpeg;base64,")
                if "," in data:
                    data = data.split(",", 1)[1]

                raw_bytes = base64.b64decode(data)
                np_arr = np.frombuffer(raw_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is None:
                    await websocket.send_text("Error: could not decode frame")
                    continue

                prediction = cnn_service.predict_frame(frame)
                await websocket.send_text(prediction)

            except Exception as exc:  # noqa: BLE001
                # Send error back rather than crashing the connection
                await websocket.send_text(f"Error: {exc}")

    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected: {websocket.client}")
