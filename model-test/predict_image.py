import cv2
import sys
import os
from src.predictor import GesturePredictor
from src.visualizer import Visualizer

def process_image(image_path):
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} not found.")
        return

    # Paths to models
    HAND_MODEL = "models/hand_landmarker.task"
    FACE_MODEL = "models/face_detector.tflite"
    GESTURE_MODEL = "models/mobnet-v2_gesture-model.tflite"

    predictor = GesturePredictor(HAND_MODEL, FACE_MODEL, GESTURE_MODEL)
    visualizer = Visualizer()

    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not read image {image_path}")
        return

    # Image processing doesn't strictly need a moving timestamp, but MP Tasks for VIDEO mode might expect increasing timestamps.
    # Alternatively, we could initialize MP in IMAGE mode, but for modularity we use the same predictor.
    result = predictor.process_frame(frame, 0)

    # Visualize
    frame = visualizer.draw_info(frame, result['mode'], result['prediction'], 0)
    
    print(f"Results for {image_path}:")
    print(f"  Mode: {result['mode']}")
    print(f"  Prediction: {result['prediction']}")

    cv2.imshow("Image Prediction", frame)
    visualizer.show_roi(result['roi'])
    
    print("Press any key to close...")
    cv2.waitKey(0)
    
    predictor.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict_image.py <path_to_image>")
    else:
        process_image(sys.argv[1])
