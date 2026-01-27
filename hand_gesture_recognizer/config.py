"""
Configuration module for Hand Gesture Recognizer
Contains all configurable parameters and constants
"""

import os
from typing import Tuple

# Model Configuration
MODEL_NAME = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_NAME)

# Detection Parameters
DEFAULT_MIN_DETECTION_CONFIDENCE = 0.5
DEFAULT_MIN_TRACKING_CONFIDENCE = 0.5
DEFAULT_MAX_NUM_HANDS = 2

# Gesture Recognition Thresholds
SWIPE_THRESHOLD = 0.1  # Minimum movement for swipe detection
POSITION_HISTORY_SIZE = 5  # Number of frames to track for motion

# Camera Settings
DEFAULT_CAMERA_INDEX = 0
CAMERA_FRAME_WIDTH = 640
CAMERA_FRAME_HEIGHT = 480

# Display Settings
WINDOW_NAME = "Hand Gesture Recognition"
COMBINED_VIEW = True  # Show original and mask side by side
FPS_DISPLAY = True  # Show FPS counter

# Drawing Specifications
LANDMARK_COLOR: Tuple[int, int, int] = (0, 255, 0)  # Green
CONNECTION_COLOR: Tuple[int, int, int] = (255, 255, 255)  # White
LANDMARK_THICKNESS = 2
CONNECTION_THICKNESS = 2
LANDMARK_RADIUS = 4

# Text Display Settings
TEXT_FONT = 1  # cv2.FONT_HERSHEY_SIMPLEX
TEXT_SCALE = 1.0
TEXT_COLOR: Tuple[int, int, int] = (0, 255, 0)  # Green
TEXT_THICKNESS = 2
TEXT_POSITION = (10, 30)

# Gesture Names
GESTURE_FIST = "fist"
GESTURE_OPEN_PALM = "open_palm"
GESTURE_TWO_FINGERS = "two_fingers"
GESTURE_THREE_FINGERS = "three_fingers"
GESTURE_FOUR_FINGERS = "four_fingers"
GESTURE_LEFT_SWIPE = "left_swipe"
GESTURE_RIGHT_SWIPE = "right_swipe"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Performance Settings
SKIP_FRAMES = 0  # Number of frames to skip for processing (0 = process all)
TARGET_FPS = 30  # Target frames per second
