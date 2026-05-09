"""
Model handler service — Real Gesture Prediction Pipeline.

Integrates MediaPipe for ROI extraction (Hand & Face Landmarks) and
TensorFlow Lite for gesture classification.
"""

from __future__ import annotations

import cv2
import numpy as np
import os
import csv

# Late import or standard import for heavy ML libraries
import tensorflow as tf
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

ML_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml-models')
H5_MODEL_PATH = os.path.join(ML_DIR, "mobnet-v2_gesture-model.h5")
FACE_MODEL_PATH = os.path.join(ML_DIR, "face_detector.tflite")
HAND_MODEL_PATH = os.path.join(ML_DIR, "hand_landmarker.task")
CSV_PATH = os.path.join(ML_DIR, "class_labels.csv")

class GestureCNN:
    """
    Production Gesture recognition service.
    """

    def __init__(self) -> None:
        """Initialise the models and MediaPipe detectors."""
        print("[GestureCNN] Initialising ML Models...")
        
        # Load Labels
        self._labels = []
        try:
            with open(CSV_PATH, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._labels.append(row['gesture'])
        except Exception as e:
            print(f"[GestureCNN] Error loading CSV: {e}")
            self._labels = ['Bathroom', 'Call', 'Drink', 'Eat', 'Help', 'Listen Up',
                'No', 'Pain', 'Stop', 'When', 'Where', 'Yes']

        # Load Keras Model
        try:
            self.model = tf.keras.models.load_model(H5_MODEL_PATH)
            print("[GestureCNN] Keras H5 model loaded successfully.")
        except Exception as e:
            print(f"[GestureCNN] Error loading Keras model: {e}")
            self.model = None

        # Init MediaPipe Hand Landmarker
        try:
            hand_base_options = python.BaseOptions(model_asset_path=HAND_MODEL_PATH)
            hand_options = vision.HandLandmarkerOptions(
                base_options=hand_base_options,
                num_hands=2,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5,
                running_mode=vision.RunningMode.IMAGE
            )
            self.hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)
            print("[GestureCNN] Hand landmarker loaded successfully.")
        except Exception as e:
            print(f"[GestureCNN] Error loading Hand Landmarker: {e}")
            self.hand_landmarker = None

        # Init MediaPipe Face Detector
        try:
            face_base_options = python.BaseOptions(model_asset_path=FACE_MODEL_PATH)
            face_options = vision.FaceDetectorOptions(
                base_options=face_base_options,
                min_detection_confidence=0.5,
                running_mode=vision.RunningMode.IMAGE
            )
            self.face_detector = vision.FaceDetector.create_from_options(face_options)
            print("[GestureCNN] Face detector loaded successfully.")
        except Exception as e:
            print(f"[GestureCNN] Error loading Face Detector: {e}")
            self.face_detector = None

        print(f"[GestureCNN] Initialisation complete with {len(self._labels)} classes.")

    def predict_frame(self, frame_array: np.ndarray) -> str:
        """
        Predict the gesture present in a single BGR frame.

        Args:
            frame_array: OpenCV BGR image as a NumPy array.

        Returns:
            A human-readable gesture label string.
        """
        if self.model is None or self.hand_landmarker is None:
            return "Model not loaded properly"

        h, w, _ = frame_array.shape
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame_array, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detect
        hand_result = self.hand_landmarker.detect(mp_image)
        face_result = self.face_detector.detect(mp_image) if self.face_detector else None

        all_points = []
        
        # Collect hand points
        if hand_result and hand_result.hand_landmarks:
            for landmarks in hand_result.hand_landmarks:
                for lm in landmarks:
                    all_points.append((int(lm.x * w), int(lm.y * h)))

        # Collect face points
        if face_result and face_result.detections:
            for detection in face_result.detections:
                bbox = detection.bounding_box
                all_points.append((bbox.origin_x, bbox.origin_y))
                all_points.append((bbox.origin_x + bbox.width, bbox.origin_y + bbox.height))

        if not all_points:
            return "No Detection"

        # Calculate bounding box for ROI
        pts = np.array(all_points)
        x1, y1 = np.min(pts, axis=0)
        x2, y2 = np.max(pts, axis=0)
        
        # Add padding
        padding = 20
        x1, y1 = max(0, x1 - padding), max(0, y1 - padding)
        x2, y2 = min(w, x2 + padding), min(h, y2 + padding)

        if x2 <= x1 or y2 <= y1:
            return "Invalid ROI"

        # Crop ROI
        raw_roi = frame_array[y1:y2, x1:x2]
        
        # Efficient Masking
        roi_gray = cv2.cvtColor(raw_roi, cv2.COLOR_BGR2GRAY)
        roi_mask = np.zeros_like(roi_gray)
        
        # Re-map points to ROI coordinates
        if hand_result and hand_result.hand_landmarks:
            for landmarks in hand_result.hand_landmarks:
                points_in_roi = np.array([
                    (int(lm.x * w) - x1, int(lm.y * h) - y1) for lm in landmarks
                ])
                cv2.fillPoly(roi_mask, [points_in_roi], 255)
        
        if face_result and face_result.detections:
            for detection in face_result.detections:
                bbox = detection.bounding_box
                fx1, fy1 = max(0, bbox.origin_x - x1), max(0, bbox.origin_y - y1)
                fx2, fy2 = min(raw_roi.shape[1], fx1 + bbox.width), min(raw_roi.shape[0], fy1 + bbox.height)
                cv2.rectangle(roi_mask, (fx1, fy1), (fx2, fy2), 255, -1)

        # Apply mask
        roi = cv2.bitwise_and(roi_gray, roi_mask)
        roi = cv2.resize(roi, (224, 224))

        # Preprocess for Keras
        img_input = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)
        img_input = img_input.astype(np.float32) / 255.0
        img_input = np.expand_dims(img_input, axis=0)

        # Infer
        pred = self.model.predict(img_input, verbose=0)
        
        class_index = np.argmax(pred)
        
        if class_index < len(self._labels):
            return self._labels[class_index]
        return "Unknown"

# ---------------------------------------------------------------------------
# Global singleton — import this in route handlers
# ---------------------------------------------------------------------------
cnn_service = GestureCNN()
