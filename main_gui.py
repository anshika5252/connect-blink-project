from detector import EyeTracker
import joblib
import numpy as np
import cv2
import tkinter as tk
from tkinter import ttk, messagebox
import winsound
import threading
from datetime import datetime
import time
import os

class AuraUnifiedHUD:
    

    def __init__(self, root):
        self.root = root
        self.root.title("CONNECT-Dashboard")
        
        try:
            self.root.attributes('-fullscreen', True)
        except:
            self.root.state('zoomed')
            
        self.root.configure(bg="#EB7676")
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False)) # Press Esc to exit

        # --- DATA & STATE ---
        self.medications = [] 
        self.alarm_active = False
        self.emergency_mode = False
        self.active_alarm_meds = []
        self.session_dismissed = [] 

        self.in_sub_menu = False
        self.current_cat_idx = 0
        self.current_item_idx = 0
        # --- ADD THIS TO __init__ ---
        self.tracker = EyeTracker()
        self.model = joblib.load('eye_state_model.pkl') # Ensure path is correct
        self.blink_start_time = 0
        self.is_blinking = False

# Start the AI Background Thread
        threading.Thread(target=self.run_ai_eye_tracking, daemon=True).start()



        # --- TRANSLATIONS ---
        self.translations = {
            "English": {
                "categories": ["PHYSICAL NEEDS", "COMFORT", "ENTERTAINMENT", "URGENT"],
                "items": {
                    "PHYSICAL NEEDS": ["Water", "Food", "Medicine", "Restroom"],
                    "COMFORT": ["Position", "Fan", "Blanket", "Light"],
                    "ENTERTAINMENT": ["TV", "Music", "News"],
                    "URGENT": ["EMERGENCY ALARM"]
                },
                "labels": ["AURA OS", "LANGUAGE", "MEDICINE TRACKER", "CAREGIVER PANEL", "MED NAME:", "TIME:", "ADD MEDICINE"],
                "nurse_alert": "NURSE CALLED!"
            },
            "Hindi": {
                "categories": ["शारीरिक ज़रूरतें", "सुविधा", "मनोरंजन", "आपातकालीन"],
                "items": {
                    "शारीरिक ज़रूरतें": ["पानी", "खाना", "दवा", "शौचालय"],
                    "सुविधा": ["स्थिति", "पंख", "कंबल", "रोशनी"],
                    "मनोरंजन": ["टीवी", "संगीत", "समाचार"],
                    "आपातकालीन": ["आपातकालीन अलार्म"]
                },
                "labels": ["आभा ओएस", "भाषा", "दवा ट्रैकर", "केयरगिवर पैनल", "दवा का नाम:", "समय:", "दवा जोड़ें"],
                "nurse_alert": "नर्स को बुलाया गया!"
            },
            "Tamil": {
                "categories": ["உடல் தேவைகள்", "வசதி", "பொழுதுபோக்கு", "அவசரம்"],
                "items": {
                    "உடல் தேவைகள்": ["தண்ணீர்", "உணவு", "மருந்து", "கழிவறை"],
                    "வசதி": ["நிலை", "விசிறి", "போர்வை", "விளக்கு"],
                    "பொழுதுபோக்கு": ["டிவி", "இசை", "செய்திகள்"],
                    "அவசரம்": ["அவசர அலாரம்"]
                },
                "labels": ["ஆரா ஓஎஸ்", "மொழி", "மருந்து கண்காணிப்பு", "பராமரிப்பாளர் குழு", "பெயர்:", "நேரம்:", "சேர்"],
                "nurse_alert": "செவிலியர் அழைக்கப்பட்டார்!"
            },
            "Telugu": {
                "categories": ["శారీరక అవసరాలు", "సౌకర్యం", "వినోదం", "అత్యవసరం"],
                "items": {
                    "శారీరక అవసరాలు": ["నీరు", "ఆహారం", "మందులు", "విశ్రాంతి"],
                    "సౌకర్యం": ["స్థితి", "ఫ్యాన్", "దుప్పటి", "కాంతి"],
                    "వినోదం": ["టీవీ", "సంగీతం", "వార్తలు"],
                    "అత్యవసరం": ["అత్యవసర అలారం"]
                },
                "labels": ["ఆరా OS", "భాష", "మందుల ట్రాకర్", "సంరక్షకుని ప్యానెల్", "పేరు:", "సమయం:", "జోడించు"],
                "nurse_alert": "నర్స్ పిలువబద్ధారు!"
            },
            "Marathi": {
                "categories": ["शारीरिक गरजा", "आराम", "मनोरंजन", "तातडीचे"],
                "items": {
                    "शारीरिक गरजा": ["पाणी", "अन्न", "औषध", "शौचालय"],
                    "आराम": ["स्थिती", "पंखा", "घोंगडी", "प्रकाश"],
                    "मनोरंजन": ["टीव्ही", "संगीत", "बातमी"],
                    "तातडीचे": ["आणीबाणी अलार्म"]
                },
                "labels": ["ऑरा ओएस", "भाषा", "औषध ट्रॅकर", "केअरगिव्हर पॅनेल", "नाव:", "वेळ:", "जोडा"],
                "nurse_alert": "परिचारिकेला बोलावले!"
            },
            "Bengali": {
                "categories": ["শারীরিক প্রয়োজন", "আরাম", "বিনোদন", "জরুরী"],
                "items": {
                    "শারীরিক প্রয়োজন": ["জল", "খাবার", "ওষুধ", "বিশ্রামাগার"],
                    "আরাম": ["অবস্থান", "পাখা", "কম্বল", "আলো"],
                    "বিনোদন": ["টিভি", "সঙ্গীত", "খবর"],
                    "জরুরী": ["জরুরী অ্যালার্ম"]
                },
                "labels": ["অরা ওএস", "ভাষা", "ওষুধ ট্র্যাকার", "কেয়ারগিভার প্যানেল", "নাম:", "সময়:", "যোগ করুন"],
                "nurse_alert": "নার্সকে ডাকা হয়েছে!"
            }
        }
        
        self.current_lang = "English"
        self.setup_layout()
        self.check_alarms()

    def run_ai_eye_tracking(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            # Get data from detector.py
            ear_value, mesh_coords = self.tracker.get_frame_data(frame)
            
            # --- REPLACE your landmarks_flat logic with this ---
            if mesh_coords is not None:
    # We only want the specific indices your model was trained on
    # Assuming standard MediaPipe eye indices for 15 points
               eye_indices = [33, 160, 158, 133, 153, 144, 362, 385, 387, 263, 373, 380, 7, 163, 145]
    
               landmarks_flat = []
               for i in eye_indices:
                   pt = mesh_coords[i]
                   landmarks_flat.extend([pt[0], pt[1]]) # This creates exactly 30 features
    
    # Now this will work without the ValueError!
               prediction = self.model.predict(np.array(landmarks_flat).reshape(1, -1))[0]
               is_closed = (prediction == 1) or (ear_value < 0.21) # The Fail-safe logic
                
               if is_closed:
                    if not self.is_blinking:
                        self.blink_start_time = time.time()
                        self.is_blinking = True
            else:
                    if self.is_blinking:
                        duration = time.time() - self.blink_start_time
                        self.is_blinking = False
                        
                        # Trigger Navigation or Selection
                        if 0.1 < duration < 0.45:
                            self.root.event_generate("<<Navigate>>")
                        elif 0.5 < duration < 1.5:
                            self.root.event_generate("<<Confirm>>")

            cv2.imshow("Aura AI Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            
        cap.release()
        cv2.destroyAllWindows()


    def setup_layout(self):
        self.menu_area = tk.Frame(self.root, bg='#121212', width=750)
        self.menu_area.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.os_title = tk.Label(self.menu_area, text="AURA OS", font=("Arial", 28, "bold"), fg="#00FF9C", bg="#121212")
        self.os_title.pack(pady=20)
        self.cols = tk.Frame(self.menu_area, bg='#121212')
        self.cols.pack(fill=tk.BOTH, expand=True)
        self.cat_f = tk.Frame(self.cols, bg='#1a1a1a', width=350)
        self.cat_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.item_f = tk.Frame(self.cols, bg='#1a1a1a', width=350)
        self.item_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.right_p = tk.Frame(self.root, bg='#050505')
        self.right_p.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.setup_caregiver_ui()
        self.refresh_ui()

    def setup_caregiver_ui(self):
        self.lang_var = tk.StringVar(value=self.current_lang)
        self.lang_m = ttk.Combobox(self.right_p, textvariable=self.lang_var, values=list(self.translations.keys()), state="readonly")
        self.lang_m.pack(pady=10)
        self.lang_m.bind("<<ComboboxSelected>>", self.change_language)
        self.med_title = tk.Label(self.right_p, text="MEDICINE TRACKER", font=("Arial", 18, "bold"), fg="#FFB300", bg="#050505")
        self.med_title.pack(pady=10)
        self.med_list_f = tk.Frame(self.right_p, bg="#050505")
        self.med_list_f.pack(fill=tk.BOTH, expand=True)
        self.cp_frame = tk.LabelFrame(self.right_p, text=" CAREGIVER PANEL ", fg="#888", bg="#050505", padx=10, pady=10)
        self.cp_frame.pack(fill=tk.X, padx=20, pady=10)
        self.l_name = tk.Label(self.cp_frame, text=self.translations[self.current_lang]["labels"][4], fg="white", bg="#050505")
        self.l_name.pack(anchor=tk.W)
        self.med_in = tk.Entry(self.cp_frame, bg="#1a1a1a", fg="white", insertbackground="white")
        self.med_in.pack(fill=tk.X, pady=2)
        self.l_time = tk.Label(self.cp_frame, text=self.translations[self.current_lang]["labels"][5], fg="white", bg="#050505")
        self.l_time.pack(anchor=tk.W)
        self.t_f = tk.Frame(self.cp_frame, bg="#050505")
        self.t_f.pack(pady=5)
        self.h_v = ttk.Combobox(self.t_f, values=[f"{i:02d}" for i in range(24)], width=5, state="readonly")
        self.h_v.pack(side=tk.LEFT, padx=2); self.h_v.set("09")
        self.m_v = ttk.Combobox(self.t_f, values=[f"{i:02d}" for i in range(60)], width=5, state="readonly")
        self.m_v.pack(side=tk.LEFT, padx=2); self.m_v.set("00")
        self.add_b = tk.Button(self.cp_frame, text=self.translations[self.current_lang]["labels"][6], command=self.add_med, bg="#00FF9C", font=("Arial", 9, "bold"), borderwidth=0)
        self.add_b.pack(pady=15)

    def refresh_ui(self):
        for w in self.cat_f.winfo_children(): w.destroy()
        for w in self.item_f.winfo_children(): w.destroy()
        ld = self.translations[self.current_lang]
        for i, c in enumerate(ld["categories"]):
            active = (i == self.current_cat_idx and not self.in_sub_menu)
            bg, fg = ("#00FF9C", "black") if active else ("#252525", "#888")
            tk.Label(self.cat_f, text=c, font=("Arial", 13, "bold"), bg=bg, fg=fg, pady=20).pack(fill=tk.X, pady=2)
        items = ld["items"][ld["categories"][self.current_cat_idx]]
        for j, it in enumerate(items):
            active = (j == self.current_item_idx and self.in_sub_menu)
            bg, fg = ("#00FF9C", "black") if active else ("#252525", "#888")
            tk.Label(self.item_f, text=it, font=("Arial", 13, "bold"), bg=bg, fg=fg, pady=20).pack(fill=tk.X, pady=2)

    def navigate(self):
        ld = self.translations[self.current_lang]
        if not self.in_sub_menu:
            self.current_cat_idx = (self.current_cat_idx + 1) % len(ld["categories"])
        else:
            cat = ld["categories"][self.current_cat_idx]
            self.current_item_idx = (self.current_item_idx + 1) % len(ld["items"][cat])
        self.refresh_ui()
        winsound.Beep(600, 50)

    def action_confirm(self):
        if self.alarm_active:
            self.dismiss_alarm()
            return
        ld = self.translations[self.current_lang]
        cat = ld["categories"][self.current_cat_idx]
        if "URGENT" in cat or "आपातकालीन" in cat or "அவசரம்" in cat:
            self.trigger_nurse_alarm()
            return
        if not self.in_sub_menu:
            self.in_sub_menu = True; self.current_item_idx = 0
        else:
            selected = ld["items"][cat][self.current_item_idx]
            messagebox.showinfo("OS", f"Action: {selected}")
            self.in_sub_menu = False
        self.refresh_ui()

    def check_alarms(self):
        now = datetime.now().strftime("%H:%M")
        due_now = [m['name'] for m in self.medications if m['time'] == now and f"{m['name']}_{now}" not in self.session_dismissed]
        if due_now and not self.alarm_active:
            self.active_alarm_meds = due_now
            self.alarm_active = True
            # DISPLAY FIX: Update label with names immediately
            med_string = " & ".join(self.active_alarm_meds)
            self.med_title.config(text=f"⚠️ TAKE {med_string}!", fg="red")
            threading.Thread(target=self.alarm_sound_loop, daemon=True).start()
        self.root.after(5000, self.check_alarms)

    def alarm_sound_loop(self):
        while self.alarm_active:
            winsound.Beep(1000, 800)
            time.sleep(0.1)

    def dismiss_alarm(self):
        now = datetime.now().strftime("%H:%M")
        for m_name in self.active_alarm_meds:
            self.session_dismissed.append(f"{m_name}_{now}")
        self.alarm_active = False
        self.active_alarm_meds = []
        ld = self.translations[self.current_lang]
        self.med_title.config(text=ld["labels"][2], fg="#FFB300")
        winsound.Beep(400, 500)

    def trigger_nurse_alarm(self):
        self.emergency_mode = True
        threading.Thread(target=self.nurse_loop, daemon=True).start()
        messagebox.showwarning("URGENT", self.translations[self.current_lang]["nurse_alert"])
        self.emergency_mode = False

    def nurse_loop(self):
        while self.emergency_mode:
            winsound.Beep(2500, 1000)
            time.sleep(0.05)

    def change_language(self, e):
        self.current_lang = self.lang_var.get()
        ld = self.translations[self.current_lang]
        self.os_title.config(text=ld["labels"][0])
        self.cp_frame.config(text=f" {ld['labels'][3]} ")
        self.l_name.config(text=ld["labels"][4])
        self.l_time.config(text=ld["labels"][5])
        self.add_b.config(text=ld["labels"][6])
        self.med_title.config(text=ld["labels"][2])
        self.refresh_ui()

    def add_med(self):
        n = self.med_in.get()
        t = f"{self.h_v.get()}:{self.m_v.get()}"
        if n:
            self.medications.append({"name": n, "time": t})
            self.refresh_med_list()
            self.med_in.delete(0, tk.END)

    def refresh_med_list(self):
        for w in self.med_list_f.winfo_children(): w.destroy()
        for i, m in enumerate(self.medications):
            f = tk.Frame(self.med_list_f, bg="#121212", pady=5); f.pack(fill=tk.X, pady=2)
            tk.Label(f, text=f"💊 {m['name']} @ {m['time']}", fg="white", bg="#121212", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
            tk.Button(f, text="X", fg="red", bg="#121212", font=("Arial", 10, "bold"), borderwidth=0, command=lambda idx=i: self.delete_med(idx)).pack(side=tk.RIGHT, padx=10)

    def delete_med(self, i):
        self.medications.pop(i); self.refresh_med_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = AuraUnifiedHUD(root)
    
   # Keyboard support (Backup)
    root.bind("<Right>", lambda e: app.navigate())
    root.bind("<Return>", lambda e: app.action_confirm())
    
    # AI support (Main)
    root.bind("<<Navigate>>", lambda e: app.navigate())
    root.bind("<<Confirm>>", lambda e: app.action_confirm())
    root.bind("<Escape>", lambda e: root.destroy())
    root.mainloop()