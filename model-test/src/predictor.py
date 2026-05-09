import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class GesturePredictor:
    def __init__(self, hand_model_path, face_model_path, gesture_model_path):
        # -------------------- Load Gesture Model (TFLite) --------------------
        self.interpreter = tf.lite.Interpreter(model_path=gesture_model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # -------------------- Class Labels --------------------
        self.class_labels = [
            'Bathroom', 'Call', 'Drink', 'Eat', 'Help', 'Listen Up',
            'No', 'Pain', 'Stop', 'When', 'Where', 'Yes'
        ]

        # -------------------- MediaPipe Hand Landmarker --------------------
        hand_base_options = python.BaseOptions(model_asset_path=hand_model_path)
        hand_options = vision.HandLandmarkerOptions(
            base_options=hand_base_options,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=vision.RunningMode.VIDEO
        )
        self.hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)

        # -------------------- MediaPipe Face Detector --------------------
        face_base_options = python.BaseOptions(model_asset_path=face_model_path)
        face_options = vision.FaceDetectorOptions(
            base_options=face_base_options,
            min_detection_confidence=0.5,
            running_mode=vision.RunningMode.VIDEO
        )
        self.face_detector = vision.FaceDetector.create_from_options(face_options)

    def process_frame(self, frame, timestamp_ms):
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # 1. Detection
        hand_result = self.hand_landmarker.detect_for_video(mp_image, timestamp_ms)
        face_result = self.face_detector.detect_for_video(mp_image, timestamp_ms)

        num_hands = len(hand_result.hand_landmarks) if hand_result.hand_landmarks else 0
        num_faces = len(face_result.detections) if face_result.detections else 0

        # 2. Determine Mode
        mode = "No Detection"
        if num_hands == 2:
            mode = "Two Hands"
        elif num_hands == 1 and num_faces == 1:
            mode = "Face + One Hand"
        elif num_hands == 1:
            mode = "One Hand"

        # 3. ROI Extraction & Prediction
        roi = None
        prediction = "No Prediction"
        all_points = []
        
        if hand_result.hand_landmarks:
            for landmarks in hand_result.hand_landmarks:
                for lm in landmarks:
                    all_points.append((int(lm.x * w), int(lm.y * h)))

        if face_result.detections:
            for detection in face_result.detections:
                bbox = detection.bounding_box
                all_points.append((bbox.origin_x, bbox.origin_y))
                all_points.append((bbox.origin_x + bbox.width, bbox.origin_y + bbox.height))

        if all_points:
            pts = np.array(all_points)
            x1, y1 = np.min(pts, axis=0)
            x2, y2 = np.max(pts, axis=0)
            
            padding = 20
            x1, y1 = max(0, x1 - padding), max(0, y1 - padding)
            x2, y2 = min(w, x2 + padding), min(h, y2 + padding)

            if x2 > x1 and y2 > y1:
                raw_roi = frame[y1:y2, x1:x2]
                roi_gray = cv2.cvtColor(raw_roi, cv2.COLOR_BGR2GRAY)
                roi_mask = np.zeros_like(roi_gray)
                
                for landmarks in hand_result.hand_landmarks:
                    points_in_roi = np.array([
                        (int(lm.x * w) - x1, int(lm.y * h) - y1) for lm in landmarks
                    ])
                    cv2.fillPoly(roi_mask, [points_in_roi], 255)
                
                for detection in face_result.detections:
                    bbox = detection.bounding_box
                    fx1, fy1 = max(0, bbox.origin_x - x1), max(0, bbox.origin_y - y1)
                    fx2, fy2 = min(raw_roi.shape[1], fx1 + bbox.width), min(raw_roi.shape[0], fy1 + bbox.height)
                    cv2.rectangle(roi_mask, (fx1, fy1), (fx2, fy2), 255, -1)

                roi = cv2.bitwise_and(roi_gray, roi_mask)
                roi = cv2.resize(roi, (224, 224))

                # Prediction
                img_input = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)
                img_input = img_input.astype(np.float32) / 255.0
                img_input = np.expand_dims(img_input, axis=0)

                self.interpreter.set_tensor(self.input_details[0]['index'], img_input)
                self.interpreter.invoke()
                pred = self.interpreter.get_tensor(self.output_details[0]['index'])
                
                class_index = np.argmax(pred)
                prediction = self.class_labels[class_index]

        return {
            "mode": mode,
            "prediction": prediction,
            "roi": roi,
            "hand_result": hand_result,
            "face_result": face_result
        }

    def close(self):
        self.hand_landmarker.close()
        self.face_detector.close()
