import os
import sys
import cv2
import numpy as np
import time
import threading
import pyttsx3
import joblib

# Force path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from detector import EyeTracker 

class ALS_System:
    def __init__(self):
        self.eye_tracker = EyeTracker()
        self.model = joblib.load('eye_state_model.pkl')
        self.engine = pyttsx3.init()
        
        # --- YOUR ORIGINAL VERTICAL MENU STRUCTURE ---
        self.menu = {
            "PHYSICAL NEEDS": ["Water", "Food", "Medicine", "Restroom"],
            "COMFORT": ["Position", "Fan", "Blanket", "Light"],
            "ENTERTAINMENT": ["TV", "Music", "News"],
            "URGENT": ["ALARM", "CALL", "HELP"]
        }
        self.categories = list(self.menu.keys())
        self.current_cat_idx = 0
        self.in_sub_menu = False
        self.current_item_idx = 0
        
        self.last_switch = time.time()
        self.is_closed = False
        self.blink_start = 0

    def speak(self, text):
        def _s():
            self.engine.say(text)
            self.engine.runAndWait()
        threading.Thread(target=_s, daemon=True).start()

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret: continue

            # --- 1. DATA FIX (image_830500.png) ---
            input_data = None
            for method in ['get_eye_data', 'get_data', 'process']:
                if hasattr(self.eye_tracker, method):
                    try: input_data = getattr(self.eye_tracker, method)(frame)
                    except: input_data = getattr(self.eye_tracker, method)()
                    break

            if input_data is not None:
                # Math fix (image_829770.png)
                data_2d = np.array(input_data).reshape(1, -1)
                pred = self.model.predict(data_2d)[0] # Fix for image_827d02.png

                # --- 2. SELECTION LOGIC ---
                if pred == 1: # Eyes Closed
                    if not self.is_closed:
                        self.is_closed = True
                        self.blink_start = time.time()
                else: # Eyes Open
                    if self.is_closed:
                        if 0.2 < (time.time() - self.blink_start) < 0.8:
                            if not self.in_sub_menu:
                                self.in_sub_menu = True
                                self.speak(f"Opening {self.categories[self.current_cat_idx]}")
                            else:
                                selected = self.menu[self.categories[self.current_cat_idx]][self.current_item_idx]
                                self.speak(f"Requesting {selected}")
                                self.in_sub_menu = False # Go back to main menu
                        self.is_closed = False

            # --- 3. MENU ROTATION ---
            if time.time() - self.last_switch > 3:
                if not self.in_sub_menu:
                    self.current_cat_idx = (self.current_cat_idx + 1) % len(self.categories)
                else:
                    items = self.menu[self.categories[self.current_cat_idx]]
                    self.current_item_idx = (self.current_item_idx + 1) % len(items)
                self.last_switch = time.time()

            # --- 4. THE VERTICAL SIDEBAR DRAWING ---
            # Draw Categories one below the other
            for i, cat in enumerate(self.categories):
                bg_color = (0, 255, 0) if (i == self.current_cat_idx and not self.in_sub_menu) else (50, 50, 50)
                cv2.rectangle(frame, (10, 50 + (i*60)), (300, 100 + (i*60)), bg_color, -1)
                cv2.putText(frame, cat, (20, 85 + (i*60)), 1, 1.2, (255, 255, 255), 2)

            # If inside a category, show sub-options to the right
            if self.in_sub_menu:
                items = self.menu[self.categories[self.current_cat_idx]]
                cv2.rectangle(frame, (320, 50), (620, 350), (0, 0, 0), -1) # Sub-menu background
                for j, item in enumerate(items):
                    color = (0, 255, 255) if j == self.current_item_idx else (150, 150, 150)
                    cv2.putText(frame, f"> {item}", (340, 90 + (j*50)), 1, 1.5, color, 2)

            cv2.imshow("ALS Vertical System", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        app = ALS_System()
        app.run()
    except Exception as e:
        print(f"CRASH: {e}")
        input("Press Enter to close...")