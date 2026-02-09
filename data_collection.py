import cv2
import csv
import time
from detector import EyeTracker 

# =====================
# SETTINGS
# =====================
LABEL = 2                 # 0=normal, 1=long, 2=double
SEQUENCE_LENGTH = 60
FILENAME = f"blink_data_{LABEL}.csv"

cap = cv2.VideoCapture(0)
print("Camera opened:", cap.isOpened())

tracker = EyeTracker()
collected_data = []

print(f"RECORDING CLASS {LABEL}. Press 'R' to capture, 'S' to save and exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Get EAR
    ear, _ = tracker.get_frame_data(frame)
    
    # ---------------- LIVE VISUALIZATION ----------------
    if ear is not None:
        display_text = f"EAR: {round(ear, 2)}"
        color = (0, 255, 0) if ear > 0.21 else (0, 0, 255)
        cv2.putText(frame, display_text, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    else:
        cv2.putText(frame, "FACE NOT DETECTED", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    # ----------------------------------------------------

    cv2.imshow("Data Collector", frame)
    key = cv2.waitKey(1) & 0xFF

    # =======================
    # RECORD SEQUENCE
    # =======================
    if key == ord('r') and ear is not None:
        print("Capturing sequence...")
        temp_sequence = []

        for i in range(SEQUENCE_LENGTH):
            ret, frame = cap.read()
            e, _ = tracker.get_frame_data(frame)

            val = e if e is not None else 0.2
            temp_sequence.append(val)

            cv2.putText(
                frame,
                f"Recording {i+1}/{SEQUENCE_LENGTH}",
                (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )
            cv2.imshow("Data Collector", frame)
            cv2.waitKey(1)
            time.sleep(0.03)

        collected_data.append(temp_sequence + [LABEL])
        print(f"Capture {len(collected_data)} complete.")

    # =======================
    # SAVE & EXIT
    # =======================
    elif key == ord('s'):
        if collected_data:
            with open(FILENAME, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(collected_data)
            print(f"Saved {len(collected_data)} records to {FILENAME}")
        break

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
