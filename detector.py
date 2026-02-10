import cv2
import mediapipe as mp
import numpy as np

# These are the standard MediaPipe utilities used for face processing
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

class EyeTracker:
    def __init__(self):
        # Initializing MediaPipe Face Mesh with high confidence for the presentation
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        # Landmark indices for the LEFT eye as per MediaPipe documentation
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]

    def calculate_ear(self, landmarks, eye_indices):
        """Calculates Eye Aspect Ratio (EAR) as a backup for the ML model."""
        try:
            # Extract the specific coordinates for the eye from the mesh
            p = [landmarks[i] for i in eye_indices]
            
            # Vertical distances between eyelids
            v1 = np.linalg.norm(np.array(p[1]) - np.array(p[5]))
            v2 = np.linalg.norm(np.array(p[2]) - np.array(p[4]))
            
            # Horizontal distance across the eye
            h = np.linalg.norm(np.array(p[0]) - np.array(p[3]))
            
            # EAR Mathematical Formula
            ear = (v1 + v2) / (2.0 * h)
            return ear
        except Exception:
            # If math fails, return 0.2 (which usually signals a closed eye/blink)
            return 0.2

    def get_frame_data(self, frame):
        """Processes the frame and returns EAR and Mesh Coordinates to the GUI."""
        if frame is None:
            return None, None
            
        # Convert BGR (OpenCV) to RGB (MediaPipe) for processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            ih, iw, _ = frame.shape
            
            # Convert normalized MediaPipe coordinates to actual pixel coordinates
            mesh_coords = [(lm.x * iw, lm.y * ih) for lm in face_landmarks.landmark]
            
            # Calculate the EAR for the left eye to provide a heuristic backup
            ear = self.calculate_ear(mesh_coords, self.LEFT_EYE)
            return ear, mesh_coords
        
        # Crucial: Return two Nones if no face is detected to prevent GUI crashes
        return None, None