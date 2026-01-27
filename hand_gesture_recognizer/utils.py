"""
Utility functions for Hand Gesture Recognizer
"""

import os
import logging
import urllib.request
from typing import Optional, Tuple
import cv2
import numpy as np

from .config import (
    MODEL_URL, MODEL_PATH, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT
)


def setup_logging(level: str = LOG_LEVEL) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    return logging.getLogger("HandGestureRecognizer")


def download_model(model_path: str = MODEL_PATH, model_url: str = MODEL_URL) -> bool:
    """
    Download the hand landmarker model if not present
    
    Args:
        model_path: Path where model should be saved
        model_url: URL to download model from
        
    Returns:
        True if model is available (downloaded or already exists), False otherwise
    """
    logger = logging.getLogger("HandGestureRecognizer")
    
    if os.path.exists(model_path):
        logger.info(f"Model already exists at: {model_path}")
        return True
    
    try:
        logger.info("Downloading hand landmarker model...")
        logger.info(f"URL: {model_url}")
        logger.info(f"Destination: {model_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Download with progress
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, (downloaded / total_size) * 100)
            logger.debug(f"Download progress: {percent:.1f}%")
        
        urllib.request.urlretrieve(model_url, model_path, progress_hook)
        logger.info("✓ Model downloaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        logger.error(f"Please download manually from: {model_url}")
        return False


def calculate_fps(prev_time: float) -> Tuple[float, float]:
    """
    Calculate frames per second
    
    Args:
        prev_time: Previous frame timestamp
        
    Returns:
        Tuple of (current_time, fps)
    """
    import time
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time > 0 else 0
    return current_time, fps


def draw_fps(image: np.ndarray, fps: float, position: Tuple[int, int] = (10, 30)) -> None:
    """
    Draw FPS counter on image
    
    Args:
        image: Image to draw on
        fps: FPS value to display
        position: Position to draw FPS text
    """
    cv2.putText(
        image,
        f"FPS: {fps:.1f}",
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )


def draw_gesture_info(image: np.ndarray, gesture: str, position: Tuple[int, int] = (10, 70)) -> None:
    """
    Draw detected gesture information on image
    
    Args:
        image: Image to draw on
        gesture: Gesture name to display
        position: Position to draw text
    """
    gesture_map = {
        "fist": "✊ Fist",
        "open_palm": "🖐️ Open Palm",
        "two_fingers": "✌️ Two Fingers",
        "three_fingers": "🤟 Three Fingers",
        "four_fingers": "🖖 Four Fingers",
        "left_swipe": "⬅️ Left Swipe",
        "right_swipe": "➡️ Right Swipe"
    }
    
    display_text = gesture_map.get(gesture, gesture.replace("_", " ").title())
    
    cv2.putText(
        image,
        display_text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )


def validate_camera(camera_index: int) -> bool:
    """
    Validate if camera is accessible
    
    Args:
        camera_index: Index of camera to validate
        
    Returns:
        True if camera is accessible, False otherwise
    """
    logger = logging.getLogger("HandGestureRecognizer")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            logger.error(f"Cannot open camera at index {camera_index}")
            return False
        
        ret, _ = cap.read()
        cap.release()
        
        if not ret:
            logger.error(f"Cannot read from camera at index {camera_index}")
            return False
            
        logger.info(f"✓ Camera at index {camera_index} is accessible")
        return True
        
    except Exception as e:
        logger.error(f"Camera validation failed: {e}")
        return False


def ensure_model_available() -> bool:
    """
    Ensure the model file is available, download if necessary
    
    Returns:
        True if model is available, False otherwise
    """
    if not os.path.exists(MODEL_PATH):
        return download_model()
    return True


# ========== Skeleton Analysis Functions ==========

from collections import deque
from typing import List
import math


class SkeletonAnalyzer:
    """Analyzes hand skeleton for detailed metrics."""
    
    def __init__(self, history_size=30):
        """Initialize the analyzer with history tracking."""
        self.landmark_history = deque(maxlen=history_size)
        
    def update_history(self, landmarks):
        """Update landmark history."""
        self.landmark_history.append(landmarks)
    
    def calculate_angle(self, p1, p2, p3):
        """
        Calculate angle between three points.
        
        Args:
            p1, p2, p3: Points with x, y attributes
            
        Returns:
            Angle in degrees
        """
        # Convert to vectors
        v1 = np.array([p1.x - p2.x, p1.y - p2.y])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y])
        
        # Calculate angle
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
        
        return angle
    
    def calculate_distance(self, p1, p2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
    
    def get_finger_angles(self, landmarks):
        """Get all finger joint angles."""
        angles = {}
        
        # Finger landmark indices: [base, pip, dip, tip]
        fingers = {
            'thumb': [1, 2, 3, 4],
            'index': [5, 6, 7, 8],
            'middle': [9, 10, 11, 12],
            'ring': [13, 14, 15, 16],
            'pinky': [17, 18, 19, 20]
        }
        
        for finger_name, indices in fingers.items():
            finger_angles = []
            for i in range(len(indices) - 2):
                angle = self.calculate_angle(
                    landmarks[indices[i]],
                    landmarks[indices[i+1]],
                    landmarks[indices[i+2]]
                )
                finger_angles.append(angle)
            angles[finger_name] = finger_angles
        
        return angles
    
    def get_fingertip_distances(self, landmarks):
        """Get distances from wrist to each fingertip."""
        wrist = landmarks[0]
        fingertips = [4, 8, 12, 16, 20]
        distances = {}
        
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        for name, tip_idx in zip(finger_names, fingertips):
            distances[name] = self.calculate_distance(wrist, landmarks[tip_idx])
        
        return distances
    
    def get_analysis_summary(self, landmarks):
        """Get comprehensive analysis summary."""
        return {
            'angles': self.get_finger_angles(landmarks),
            'distances': self.get_fingertip_distances(landmarks),
            'hand_openness': self.calculate_hand_openness(landmarks)
        }
    
    def calculate_hand_openness(self, landmarks):
        """Calculate how open the hand is (0-1)."""
        distances = self.get_fingertip_distances(landmarks)
        avg_distance = sum(distances.values()) / len(distances)
        # Normalize to 0-1 range (assuming max distance ~0.5)
        return min(1.0, avg_distance / 0.5)


def draw_skeleton_analysis(image, hand_landmarks, analyzer, show_labels=True, 
                          show_angles=True, show_distances=True):
    """
    Draw comprehensive skeleton analysis on image.
    
    Args:
        image: BGR image to draw on
        hand_landmarks: MediaPipe hand landmarks
        analyzer: SkeletonAnalyzer instance
        show_labels: Whether to show landmark labels
        show_angles: Whether to show angle measurements
        show_distances: Whether to show distance measurements
    """
    h, w, _ = image.shape
    
    # Draw landmarks and connections
    from hand_gesture_recognizer.main import mp_hands, mp_drawing
    mp_drawing.draw_landmarks(
        image,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
    )
    
    # Show landmark labels
    if show_labels:
        landmark_names = {
            0: 'Wrist', 4: 'Thumb', 8: 'Index', 12: 'Middle', 16: 'Ring', 20: 'Pinky'
        }
        for idx, name in landmark_names.items():
            lm = hand_landmarks.landmark[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.putText(image, name, (x + 5, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Show angles
    if show_angles:
        angles = analyzer.get_finger_angles(hand_landmarks.landmark)
        y_offset = 100
        for finger_name, finger_angles in angles.items():
            if finger_angles:
                avg_angle = sum(finger_angles) / len(finger_angles)
                text = f"{finger_name}: {avg_angle:.1f}°"
                cv2.putText(image, text, (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                y_offset += 20
    
    # Show distances
    if show_distances:
        distances = analyzer.get_fingertip_distances(hand_landmarks.landmark)
        y_offset = 250
        for finger_name, distance in distances.items():
            text = f"{finger_name}: {distance:.3f}"
            cv2.putText(image, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 128, 0), 1)
            y_offset += 20
    
    return image


def draw_3d_skeleton(landmarks, size=400):
    """
    Create 3D visualization of hand skeleton.
    
    Args:
        landmarks: Hand landmarks with x, y, z coordinates
        size: Size of the output image
        
    Returns:
        BGR image with 3D skeleton visualization
    """
    # Create blank image
    img_3d = np.zeros((size, size, 3), dtype=np.uint8)
    
    # Extract 3D coordinates
    points_3d = []
    for lm in landmarks:
        # Scale and center the coordinates
        x = int((lm.x * 0.8 + 0.1) * size)
        y = int((lm.y * 0.8 + 0.1) * size)
        z = int((lm.z * 0.8 + 0.5) * size)  # Use z for depth
        points_3d.append((x, y, z))
    
    # Define connections (same as MediaPipe hand connections)
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),  # Index
        (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
        (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
        (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
        (5, 9), (9, 13), (13, 17)  # Palm
    ]
    
    # Draw connections with depth-based coloring
    for start_idx, end_idx in connections:
        start = points_3d[start_idx]
        end = points_3d[end_idx]
        
        # Color based on z-depth
        avg_z = (start[2] + end[2]) / 2
        color_intensity = int(255 * (avg_z / size))
        color = (color_intensity, 255 - color_intensity, 128)
        
        cv2.line(img_3d, (start[0], start[1]), (end[0], end[1]), color, 2)
    
    # Draw landmarks
    for i, point in enumerate(points_3d):
        color_intensity = int(255 * (point[2] / size))
        color = (color_intensity, 255 - color_intensity, 200)
        cv2.circle(img_3d, (point[0], point[1]), 4, color, -1)
        cv2.circle(img_3d, (point[0], point[1]), 4, (255, 255, 255), 1)
    
    return img_3d


def create_analysis_panel(analysis, width=300, height=600):
    """
    Create a panel displaying analysis data.
    
    Args:
        analysis: Dictionary with analysis data
        width: Panel width
        height: Panel height
        
    Returns:
        BGR image with analysis panel
    """
    panel = np.zeros((height, width, 3), dtype=np.uint8)
    panel[:] = (40, 40, 40)  # Dark background
    
    y_offset = 30
    
    # Title
    cv2.putText(panel, "Hand Analysis", (10, y_offset),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    y_offset += 40
    
    # Hand openness
    if 'hand_openness' in analysis:
        openness = analysis['hand_openness']
        cv2.putText(panel, f"Openness: {openness:.2f}", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        # Draw bar
        bar_width = int(openness * (width - 20))
        cv2.rectangle(panel, (10, y_offset + 10), (10 + bar_width, y_offset + 25),
                     (0, 255, 0), -1)
        y_offset += 45
    
    # Finger angles
    if 'angles' in analysis:
        cv2.putText(panel, "Finger Angles:", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        y_offset += 25
        
        for finger_name, angles in analysis['angles'].items():
            if angles:
                avg_angle = sum(angles) / len(angles)
                text = f"  {finger_name}: {avg_angle:.1f}°"
                cv2.putText(panel, text, (15, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
                y_offset += 20
    
    y_offset += 10
    
    # Distances
    if 'distances' in analysis:
        cv2.putText(panel, "Fingertip Distances:", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 128, 0), 1)
        y_offset += 25
        
        for finger_name, distance in analysis['distances'].items():
            text = f"  {finger_name}: {distance:.3f}"
            cv2.putText(panel, text, (15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            y_offset += 20
    
    return panel


def draw_landmark_coordinates(image, hand_landmarks):
    """Draw coordinate information for key landmarks."""
    h, w, _ = image.shape
    
    # Key landmarks to display
    key_landmarks = {
        0: 'Wrist',
        4: 'Thumb Tip',
        8: 'Index Tip',
        12: 'Middle Tip'
    }
    
    y_offset = h - 100
    for idx, name in key_landmarks.items():
        lm = hand_landmarks.landmark[idx]
        text = f"{name}: ({lm.x:.3f}, {lm.y:.3f}, {lm.z:.3f})"
        cv2.putText(image, text, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        y_offset += 15
    
    return image
