import cv2
import numpy as np
import joblib
from collections import deque
from detector import EyeTracker

# -------------------------------
# SETTINGS
# -------------------------------
SEQUENCE_LENGTH = 30

# Load trained model
model = joblib.load("eye_state_model.pkl")

# Initialize camera and eye tracker
cap = cv2.VideoCapture(0)
tracker = EyeTracker()

# Store last 30 EAR values
ear_sequence = deque(maxlen=SEQUENCE_LENGTH)

print("Real-time prediction started. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    ear, _ = tracker.get_frame_data(frame)

    if ear is not None:
        ear_sequence.append(ear)

        # Only predict when we have 30 frames
        if len(ear_sequence) == SEQUENCE_LENGTH:
            input_data = np.array(ear_sequence).reshape(1, -1)
            prediction = model.predict(input_data)[0]

            if prediction == 0:
                text = "EYES OPEN"
                color = (0, 255, 0)
            else:
                text = "EYES CLOSED"
                color = (0, 0, 255)

            cv2.putText(
                frame,
                text,
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                color,
                3
            )

    else:
        cv2.putText(
            frame,
            "FACE NOT DETECTED",
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    cv2.imshow("Real-Time Eye State", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
