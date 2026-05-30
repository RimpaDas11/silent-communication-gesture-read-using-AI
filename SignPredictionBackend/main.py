from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

import cv2
import numpy as np
import mediapipe as mp
import base64

from tensorflow.keras.models import load_model

# -------------------- FastAPI --------------------

app = FastAPI()

# -------------------- CORS --------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Load Model --------------------

model = load_model(
    "gesture_predict_model.h5",
    compile=False
)

# -------------------- Class Labels --------------------

class_labels = [
    'Bathroom',
    'Call',
    'Drink',
    'Eat',
    'Help',
    'Listen Up',
    'No',
    'Pain',
    'Stop',
    'When',
    'Where',
    'Yes'
]

# -------------------- Mediapipe --------------------

BaseOptions = mp.tasks.BaseOptions

HandLandmarker = mp.tasks.vision.HandLandmarker

HandLandmarkerOptions = (
    mp.tasks.vision.HandLandmarkerOptions
)

VisionRunningMode = (
    mp.tasks.vision.RunningMode
)

base_options = BaseOptions(
    model_asset_path="hand_landmarker.task"
)

options = HandLandmarkerOptions(
    base_options=base_options,
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2
)

hand_detector = HandLandmarker.create_from_options(
    options
)

# -------------------- Face Detection --------------------

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# -------------------- Root --------------------

@app.get("/")
def home():

    return {
        "message": "Gesture Prediction API Running"
    }

# -------------------- Prediction Function --------------------

def process_frame(frame):

    if frame is None:

        return {
            "prediction": "Invalid Frame",
            "mode": "No Detection"
        }

    h, w, _ = frame.shape

    # RGB & Gray

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    bw_frame = cv2.cvtColor(
        rgb_frame,
        cv2.COLOR_RGB2GRAY
    )

    # Face Detection

    faces = face_cascade.detectMultiScale(
        bw_frame,
        scaleFactor=1.1,
        minNeighbors=5
    )

    num_faces = len(faces)

    # Mediapipe Image

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Hand Detection

    detection_result = hand_detector.detect(
        mp_image
    )

    num_hands = (
        len(detection_result.hand_landmarks)
        if detection_result.hand_landmarks
        else 0
    )

    # Mode

    mode = "No Detection"

    if num_hands == 2:

        mode = "Two Hands"

    elif num_hands == 1 and num_faces >= 1:

        mode = "Face + One Hand"

    elif num_hands == 1:

        mode = "One Hand"

    # ROI Mask

    mask = np.zeros_like(bw_frame)

    all_x = []
    all_y = []

    # Hand Landmarks

    if detection_result.hand_landmarks:

        for hand_landmarks in (
            detection_result.hand_landmarks
        ):

            points = np.array([
                (
                    int(lm.x * w),
                    int(lm.y * h)
                )
                for lm in hand_landmarks
            ])

            cv2.fillPoly(
                mask,
                [points],
                255
            )

            all_x.extend(points[:, 0])
            all_y.extend(points[:, 1])

    # Face Mask

    if num_faces >= 1:

        fx, fy, fw, fh = faces[0]

        fx1, fy1 = fx, fy
        fx2, fy2 = fx + fw, fy + fh

        cv2.rectangle(
            mask,
            (fx1, fy1),
            (fx2, fy2),
            255,
            -1
        )

        all_x.extend([fx1, fx2])
        all_y.extend([fy1, fy2])

    # Masked Frame

    masked_frame = cv2.bitwise_and(
        bw_frame,
        mask
    )

    roi = None

    if all_x and all_y:

        x1 = max(min(all_x), 0)
        x2 = min(max(all_x), w)

        y1 = max(min(all_y), 0)
        y2 = min(max(all_y), h)

        if x2 > x1 and y2 > y1:

            temp_roi = masked_frame[
                y1:y2,
                x1:x2
            ]

            if temp_roi.size > 0:

                roi = cv2.resize(
                    temp_roi,
                    (224, 224)
                )

    prediction = "No Prediction"

    if roi is not None and roi.size > 0:

        img = cv2.cvtColor(
            roi,
            cv2.COLOR_GRAY2RGB
        )

        img = img / 255.0

        img = np.reshape(
            img,
            (1, 224, 224, 3)
        )

        pred = model.predict(
            img,
            verbose=0
        )

        class_index = np.argmax(pred)

        prediction = class_labels[class_index]

    return {
        "prediction": prediction,
        "mode": mode
    }

# -------------------- REST API --------------------

@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):

    contents = await file.read()

    np_arr = np.frombuffer(
        contents,
        np.uint8
    )

    frame = cv2.imdecode(
        np_arr,
        cv2.IMREAD_COLOR
    )

    result = process_frame(frame)

    return result

# -------------------- WebSocket API --------------------

@app.websocket("/ws/live")
async def websocket_live(
    websocket: WebSocket
):

    await websocket.accept()

    try:

        while True:

            data = await websocket.receive_text()

            img_data = base64.b64decode(data)

            np_arr = np.frombuffer(
                img_data,
                np.uint8
            )

            frame = cv2.imdecode(
                np_arr,
                cv2.IMREAD_COLOR
            )

            result = process_frame(frame)

            await websocket.send_json(result)

    except WebSocketDisconnect:

        print("Client disconnected")

    except Exception as e:

        print("WebSocket Error:", e)