
import cv2
import mediapipe as mp
import numpy as np

import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
class EyeTracker:
    def __init__(self):
        # Using the direct path to avoid the 'Solutions: False' error we saw earlier
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        # Landmark indices for the LEFT eye (standard MediaPipe indices)
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]

    def calculate_ear(self, landmarks, eye_indices):
        try:
            # Extract the specific coordinates for the eye
            p = [landmarks[i] for i in eye_indices]
            
            # Vertical distances (p1-p5 and p2-p4)
            v1 = np.linalg.norm(np.array(p[1]) - np.array(p[5]))
            v2 = np.linalg.norm(np.array(p[2]) - np.array(p[4]))
            
            # Horizontal distance (p0-p3)
            h = np.linalg.norm(np.array(p[0]) - np.array(p[3]))
            
            # EAR Formula
            ear = (v1 + v2) / (2.0 * h)
            return ear
        except Exception:
            return 0.2  # Return a "closed eye" default if math fails

    def get_frame_data(self, frame):
        if frame is None:
            return None, None
            
        # Convert BGR (OpenCV) to RGB (MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            ih, iw, _ = frame.shape
            
            # Convert normalized coordinates to pixel coordinates
            mesh_coords = [(lm.x * iw, lm.y * ih) for lm in face_landmarks.landmark]
            
            # Calculate the EAR for the left eye
            ear = self.calculate_ear(mesh_coords, self.LEFT_EYE)
            return ear, mesh_coords
            

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.python.solutions import face_mesh as mp_face_mesh
from mediapipe.python.solutions import drawing_utils as mp_drawing
class EyeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        # Landmark indices for the left eye
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]

    def calculate_ear(self, landmarks, eye_indices):
        try:
            # Extracting specific coordinates for the eye
            p = [landmarks[i] for i in eye_indices]
            
            # Vertical distances (p1-p5 and p2-p4)
            v1 = np.linalg.norm(np.array(p[1]) - np.array(p[5]))
            v2 = np.linalg.norm(np.array(p[2]) - np.array(p[4]))
            
            # Horizontal distance (p0-p3)
            h = np.linalg.norm(np.array(p[0]) - np.array(p[3]))
            
            # EAR Formula
            ear = (v1 + v2) / (2.0 * h)
            return ear
        except Exception:
            return 0.2  # In case math fails return "closed eye"

    def get_frame_data(self, frame):
        if frame is None:
            return None, None
            
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            ih, iw, _ = frame.shape
            
            # Convert normalized coordinates to pixel coordinates
            mesh_coords = [(lm.x * iw, lm.y * ih) for lm in face_landmarks.landmark]
            
            # Calculate the EAR for the left eye
            ear = self.calculate_ear(mesh_coords, self.LEFT_EYE)
            return ear, mesh_coords
            

        return None, None