import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# -------------------- Load Model (TFLite) --------------------
TFLITE_MODEL_PATH = "mobnet-v2_gesture-model.tflite"
interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']

# -------------------- Class Labels --------------------
class_labels = [
    'Bathroom', 'Call', 'Drink', 'Eat', 'Help', 'Listen Up',
    'No', 'Pain', 'Stop', 'When', 'Where', 'Yes'
]

# -------------------- MediaPipe Initialization (Tasks API) --------------------
# Hand Landmarker setup
hand_base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
hand_options = vision.HandLandmarkerOptions(
    base_options=hand_base_options,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    running_mode=vision.RunningMode.VIDEO
)
hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)

# Face Detector setup
face_base_options = python.BaseOptions(model_asset_path='face_detector.tflite')
face_options = vision.FaceDetectorOptions(
    base_options=face_base_options,
    min_detection_confidence=0.5,
    running_mode=vision.RunningMode.VIDEO
)
face_detector = vision.FaceDetector.create_from_options(face_options)

# -------------------- Camera --------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera not opened")
    raise SystemExit

print("Press S to save | Press Q to quit")

prev_time = 0
fps = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    curr_time = time.time()
    
    # Calculate FPS
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time

    # Convert to MediaPipe Image
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # MediaPipe Tasks require timestamp in ms
    timestamp_ms = int(curr_time * 1000)

    # -------------------- Detection --------------------
    hand_result = hand_landmarker.detect_for_video(mp_image, timestamp_ms)
    face_result = face_detector.detect_for_video(mp_image, timestamp_ms)

    num_hands = len(hand_result.hand_landmarks) if hand_result.hand_landmarks else 0
    num_faces = len(face_result.detections) if face_result.detections else 0

    # -------------------- Mode --------------------
    mode = "No Detection"
    if num_hands == 2:
        mode = "Two Hands"
    elif num_hands == 1 and num_faces == 1:
        mode = "Face + One Hand"
    elif num_hands == 1:
        mode = "One Hand"

    # -------------------- ROI Logic --------------------
    roi = None
    prediction = "No Prediction"
    
    all_points = []
    
    # Collect hand points
    if hand_result.hand_landmarks:
        for landmarks in hand_result.hand_landmarks:
            for lm in landmarks:
                all_points.append((int(lm.x * w), int(lm.y * h)))

    # Collect face points
    if face_result.detections:
        for detection in face_result.detections:
            bbox = detection.bounding_box
            all_points.append((bbox.origin_x, bbox.origin_y))
            all_points.append((bbox.origin_x + bbox.width, bbox.origin_y + bbox.height))

    if all_points:
        # Calculate bounding box for ROI
        pts = np.array(all_points)
        x1, y1 = np.min(pts, axis=0)
        x2, y2 = np.max(pts, axis=0)
        
        # Add padding
        padding = 20
        x1, y1 = max(0, x1 - padding), max(0, y1 - padding)
        x2, y2 = min(w, x2 + padding), min(h, y2 + padding)

        if x2 > x1 and y2 > y1:
            # Crop ROI
            raw_roi = frame[y1:y2, x1:x2]
            
            # Efficient Masking (only on ROI)
            roi_gray = cv2.cvtColor(raw_roi, cv2.COLOR_BGR2GRAY)
            roi_mask = np.zeros_like(roi_gray)
            
            # Re-map points to ROI coordinates
            for landmarks in hand_result.hand_landmarks:
                points_in_roi = np.array([
                    (int(lm.x * w) - x1, int(lm.y * h) - y1) for lm in landmarks
                ])
                cv2.fillPoly(roi_mask, [points_in_roi], 255)
            
            if face_result.detections:
                for detection in face_result.detections:
                    bbox = detection.bounding_box
                    fx1, fy1 = max(0, bbox.origin_x - x1), max(0, bbox.origin_y - y1)
                    fx2, fy2 = min(raw_roi.shape[1], fx1 + bbox.width), min(raw_roi.shape[0], fy1 + bbox.height)
                    cv2.rectangle(roi_mask, (fx1, fy1), (fx2, fy2), 255, -1)

            # Apply mask
            roi = cv2.bitwise_and(roi_gray, roi_mask)
            roi = cv2.resize(roi, (224, 224))

            # -------------------- Prediction --------------------
            # Preprocess
            img_input = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)
            img_input = img_input.astype(np.float32) / 255.0
            img_input = np.expand_dims(img_input, axis=0)

            # TFLite Inference
            interpreter.set_tensor(input_details[0]['index'], img_input)
            interpreter.invoke()
            pred = interpreter.get_tensor(output_details[0]['index'])
            
            class_index = np.argmax(pred)
            prediction = class_labels[class_index]

    # -------------------- Display --------------------
    # Draw FPS
    cv2.putText(frame, f"FPS: {int(fps)}", (w - 150, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    cv2.putText(frame, f"Mode: {mode}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.putText(frame, f"Gesture: {prediction}", (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Live Camera", frame)

    if roi is not None:
        cv2.imshow("ROI", roi)

    key = cv2.waitKey(1) & 0xFF

    # -------------------- Save --------------------
    if key == ord('s') and roi is not None:
        filename = f"{prediction.replace(' ', '_')}_{int(time.time())}.png"
        cv2.imwrite(filename, roi)
        print(f"Saved: {filename}")

    if key == ord('q'):
        break

cap.release()
hand_landmarker.close()
face_detector.close()
cv2.destroyAllWindows()