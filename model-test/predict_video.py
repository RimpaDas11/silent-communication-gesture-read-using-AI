import cv2
import sys
import os
import time
from src.predictor import GesturePredictor
from src.visualizer import Visualizer

def process_video(video_path):
    if not os.path.exists(video_path):
        print(f"Error: File {video_path} not found.")
        return

    # Paths to models
    HAND_MODEL = "models/hand_landmarker.task"
    FACE_MODEL = "models/face_detector.tflite"
    GESTURE_MODEL = "models/mobnet-v2_gesture-model.tflite"

    predictor = GesturePredictor(HAND_MODEL, FACE_MODEL, GESTURE_MODEL)
    visualizer = Visualizer()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    print(f"Processing video: {video_path}. Press 'q' to stop.")
    
    # Optional: Video writer to save results
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # For video, we can use the frame index as timestamp proxy or use actual timing
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        
        start_time = time.time()
        result = predictor.process_frame(frame, timestamp_ms)
        end_time = time.time()
        
        fps = 1 / (end_time - start_time) if (end_time - start_time) > 0 else 0

        # Visualize
        frame = visualizer.draw_info(frame, result['mode'], result['prediction'], fps)
        
        cv2.imshow("Video Prediction", frame)
        visualizer.show_roi(result['roi'])

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    predictor.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict_video.py <path_to_video>")
    else:
        process_video(sys.argv[1])
