import cv2
import numpy as np
import os

def get_center_crop_coordinates(video_path: str, target_ratio: float = 9/16):
    """
    Analyzes the video to find the most active/centered subject.
    For simplicity and performance, we use Haar Cascade to find a face.
    If no face is found, we default to the center of the video.
    Returns (x_offset, y_offset, new_width, new_height).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    new_width = int(height * target_ratio)
    new_height = height
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames_to_sample = 5
    interval = int(fps) if fps > 0 else 30
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    x_centers = []
    
    for i in range(frames_to_sample):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * interval)
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            x_centers.append(x + w//2)
            break
            
    cap.release()
    
    if x_centers:
        best_x_center = int(np.median(x_centers))
    else:
        best_x_center = width // 2
        
    x_offset = best_x_center - (new_width // 2)
    x_offset = max(0, min(x_offset, width - new_width))
    y_offset = 0
    
    return x_offset, y_offset, new_width, new_height
