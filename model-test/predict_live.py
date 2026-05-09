import cv2
import time
from src.predictor import GesturePredictor
from src.visualizer import Visualizer

def main():
    # Paths to models
    HAND_MODEL = "models/hand_landmarker.task"
    FACE_MODEL = "models/face_detector.tflite"
    GESTURE_MODEL = "models/mobnet-v2_gesture-model.tflite"

    predictor = GesturePredictor(HAND_MODEL, FACE_MODEL, GESTURE_MODEL)
    visualizer = Visualizer()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Live Prediction Started. Press 'q' to quit, 's' to save ROI.")
    
    prev_time = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        curr_time = time.time()
        timestamp_ms = int(curr_time * 1000)
        
        # Calculate FPS
        fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
        prev_time = curr_time

        # Process frame
        result = predictor.process_frame(frame, timestamp_ms)
        
        # Visualize
        frame = visualizer.draw_info(frame, result['mode'], result['prediction'], fps)
        cv2.imshow("Live Gesture Recognition", frame)
        visualizer.show_roi(result['roi'])

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s') and result['roi'] is not None:
            filename = f"saved_roi_{int(time.time())}.png"
            cv2.imwrite(filename, result['roi'])
            print(f"Saved: {filename}")

    cap.release()
    predictor.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
