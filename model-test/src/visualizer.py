import cv2

class Visualizer:
    @staticmethod
    def draw_info(frame, mode, prediction, fps):
        h, w, _ = frame.shape
        # Draw Mode
        cv2.putText(frame, f"Mode: {mode}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw Prediction
        cv2.putText(frame, f"Gesture: {prediction}", (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # Draw FPS
        cv2.putText(frame, f"FPS: {int(fps)}", (w - 150, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return frame

    @staticmethod
    def show_roi(roi):
        if roi is not None:
            cv2.imshow("ROI", roi)
