#FINAL CODE
import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model

# -------------------- Load Model --------------------
model = load_model("mobilenetv2_image_gus2 NEW.h5")

# -------------------- Class Labels --------------------
class_labels = ['Bathroom', 'Call', 'Drink', 'Eat', 'Help', 'Listen Up',
                'No', 'Pain', 'Stop', 'When', 'Where', 'Yes']

# -------------------- MediaPipe Initialization --------------------
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection

hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5)
face = mp_face.FaceDetection(min_detection_confidence=0.5)

# -------------------- Camera --------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not opened")
    raise SystemExit

print("Press S to save | Press Q to quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # RGB & Gray
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    bw_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)

    # -------------------- Detection --------------------
    hands_result = hands.process(rgb_frame)
    face_result = face.process(rgb_frame)

    num_hands = len(hands_result.multi_hand_landmarks) if hands_result.multi_hand_landmarks else 0
    num_faces = len(face_result.detections) if face_result.detections else 0

    # -------------------- Mode --------------------
    mode = "No Detection"
    if num_hands == 2:
        mode = "Two Hands"
    elif num_hands == 1 and num_faces == 1:
        mode = "Face + One Hand"
    elif num_hands == 1:
        mode = "One Hand"

    # -------------------- ROI Mask --------------------
    mask = np.zeros_like(bw_frame)
    all_x, all_y = [], []

    # Hand
    if hands_result.multi_hand_landmarks:
        for hand in hands_result.multi_hand_landmarks:
            points = np.array(
                [(int(lm.x * w), int(lm.y * h)) for lm in hand.landmark]
            )
            cv2.fillPoly(mask, [points], 255)
            all_x.extend(points[:, 0])
            all_y.extend(points[:, 1])

    # Face
    if num_faces == 1:
        fbox = face_result.detections[0].location_data.relative_bounding_box
        fx1 = int(fbox.xmin * w)
        fy1 = int(fbox.ymin * h)
        fx2 = int((fbox.xmin + fbox.width) * w)
        fy2 = int((fbox.ymin + fbox.height) * h)
        cv2.rectangle(mask, (fx1, fy1), (fx2, fy2), 255, -1)
        all_x.extend([fx1, fx2])
        all_y.extend([fy1, fy2])

    masked_frame = cv2.bitwise_and(bw_frame, mask)

    # -------------------- ROI --------------------
    roi = None
    if all_x and all_y:
        x1, x2 = max(min(all_x), 0), min(max(all_x), w)
        y1, y2 = max(min(all_y), 0), min(max(all_y), h)

        if x2 > x1 and y2 > y1:
            temp_roi = masked_frame[y1:y2, x1:x2]
            if temp_roi.size > 0:
                roi = cv2.resize(temp_roi, (224, 224))  # adjust if needed

    # -------------------- Prediction --------------------
    prediction = "No Prediction"

    if roi is not None and roi.size > 0:
        img = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)
        img = img / 255.0
        img = np.reshape(img, (1, 224, 224, 3))

        pred = model.predict(img, verbose=0)
        class_index = np.argmax(pred)
        prediction = class_labels[class_index]

    # -------------------- Display --------------------
    cv2.putText(frame, f"Mode: {mode}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.putText(frame, f"Gesture: {prediction}", (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Live Camera", frame)

    if roi is not None and roi.size > 0:
        cv2.imshow("ROI", roi)

    key = cv2.waitKey(1) & 0xFF

    # -------------------- Save --------------------
    if key == ord('s') and roi is not None:
        filename = f"{prediction.replace(' ', '_')}.png"
        cv2.imwrite(filename, roi)
        print(f"Saved: {filename}")
        break

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()