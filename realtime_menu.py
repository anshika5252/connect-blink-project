import cv2
import time
from collections import deque
from detector import EyeTracker

# Settings
EAR_THRESHOLD = 0.21

LONG_BLINK_FRAMES = 12 # Long blink ≈ 0.4–0.6 sec
SHORT_BLINK_MAX_FRAMES = 6 # Short blink
OPEN_RESET_FRAMES = 10 # Frames eyes must stay open

ACTION_COOLDOWN = 1.2

# Menu
menu = [
    "I am thirsty",
    "I am hungry",
    "I need help",
    "Call nurse"
]
menu_index = 0

# init
tracker = EyeTracker()
cap = cv2.VideoCapture(0)

blink_counter = 0
blink_events = deque(maxlen=3)

open_eye_counter = 0
LOCKED = False
SELECTION_MADE = False
last_action_time = 0

print("Blink Menu running. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    ear, _ = tracker.get_frame_data(frame)
    now = time.time()

    # Processing EAR
    if ear is not None:
        if ear < EAR_THRESHOLD:
            blink_counter += 1
            open_eye_counter = 0
        else:
            open_eye_counter += 1
            if blink_counter > 0:
                blink_events.append(blink_counter)
            blink_counter = 0
    else:
        # Face lost → safely close blink
        if blink_counter > 0:
            blink_events.append(blink_counter)
        blink_counter = 0

    # Lock and reset
    if LOCKED:
        if open_eye_counter >= OPEN_RESET_FRAMES:
            LOCKED = False
            SELECTION_MADE = False
            blink_events.clear()
        else:
            pass

    else:
        # Action handling
        if now - last_action_time > ACTION_COOLDOWN:

            # DOUBLE BLINK → SELECT
            if len(blink_events) >= 2 and not SELECTION_MADE:
                b1, b2 = blink_events[-2], blink_events[-1]
                if b1 <= SHORT_BLINK_MAX_FRAMES and b2 <= SHORT_BLINK_MAX_FRAMES:
                    print("SELECTED:", menu[menu_index])

                    SELECTION_MADE = True
                    last_action_time = now
                    LOCKED = True

                    blink_events.clear()
                    blink_counter = 0
                    open_eye_counter = 0

            # LONG BLINK → SCROLL
            elif len(blink_events) >= 1:
                if blink_events[-1] >= LONG_BLINK_FRAMES:
                    menu_index = (menu_index + 1) % len(menu)

                    last_action_time = now
                    LOCKED = True

                    blink_events.clear()
                    blink_counter = 0
                    open_eye_counter = 0

    # Debug Info
    if ear is not None:
        cv2.putText(
            frame,
            f"EAR: {ear:.2f}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

    # Draw menu
    y_start = 100
    for i, item in enumerate(menu):
        if i == menu_index:
            text = f"> {item}"
            color = (0, 255, 0)
        else:
            text = f"  {item}"
            color = (255, 255, 255)

        cv2.putText(
            frame,
            text,
            (50, y_start + i * 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2
        )

    cv2.imshow("Blink Menu", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
