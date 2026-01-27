"""
Hand Gesture Recognizer - Main Module
A professional hand gesture recognition system using MediaPipe and OpenCV
"""

import cv2
import numpy as np
import logging
import time
from typing import Optional, Callable, Dict, Set
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from .config import (
    MODEL_PATH,
    DEFAULT_MIN_DETECTION_CONFIDENCE,
    DEFAULT_MIN_TRACKING_CONFIDENCE,
    DEFAULT_MAX_NUM_HANDS,
    DEFAULT_CAMERA_INDEX,
    SWIPE_THRESHOLD,
    POSITION_HISTORY_SIZE,
    WINDOW_NAME,
    LANDMARK_COLOR,
    CONNECTION_COLOR,
    LANDMARK_THICKNESS,
    CONNECTION_THICKNESS,
    LANDMARK_RADIUS
)
from .utils import setup_logging, ensure_model_available, calculate_fps, draw_fps, draw_gesture_info


# Hand landmark indices
class HandLandmark:
    """Hand landmark point indices"""
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


# Hand connections for drawing
HAND_CONNECTIONS = frozenset([
    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),  # Index finger
    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle finger
    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring finger
    (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    (5, 9), (9, 13), (13, 17)  # Palm connections
])


class DrawingSpec:
    """Specification for drawing landmarks and connections"""
    def __init__(self, color=(0, 255, 0), thickness=2, circle_radius=2):
        self.color = color
        self.thickness = thickness
        self.circle_radius = circle_radius


class MPDrawing:
    """MediaPipe drawing utilities wrapper"""
    DrawingSpec = DrawingSpec
    
    @staticmethod
    def draw_landmarks(image, landmark_list, connections=None, 
                     landmark_drawing_spec=None, connection_drawing_spec=None):
        """
        Draw hand landmarks and connections on image
        
        Args:
            image: Image to draw on
            landmark_list: List of landmarks
            connections: Connections between landmarks
            landmark_drawing_spec: Specification for drawing landmarks
            connection_drawing_spec: Specification for drawing connections
        """
        if landmark_list is None:
            return
        
        if landmark_drawing_spec is None:
            landmark_drawing_spec = DrawingSpec(color=LANDMARK_COLOR, circle_radius=LANDMARK_RADIUS)
        if connection_drawing_spec is None:
            connection_drawing_spec = DrawingSpec(color=CONNECTION_COLOR, thickness=CONNECTION_THICKNESS)
        
        h, w, _ = image.shape
        
        # Draw connections
        if connections:
            for connection in connections:
                start_idx, end_idx = connection
                start_landmark = landmark_list.landmark[start_idx]
                end_landmark = landmark_list.landmark[end_idx]
                
                start_point = (int(start_landmark.x * w), int(start_landmark.y * h))
                end_point = (int(end_landmark.x * w), int(end_landmark.y * h))
                
                cv2.line(image, start_point, end_point, 
                       connection_drawing_spec.color, 
                       connection_drawing_spec.thickness)
        
        # Draw landmarks
        for landmark in landmark_list.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(image, (x, y), 
                     landmark_drawing_spec.circle_radius, 
                     landmark_drawing_spec.color, -1)


class MPHands:
    """MediaPipe Hands wrapper for compatibility"""
    HandLandmark = HandLandmark
    HAND_CONNECTIONS = HAND_CONNECTIONS
    
    class Hands:
        """Hand detection and tracking"""
        def __init__(self, static_image_mode=False, 
                    max_num_hands=DEFAULT_MAX_NUM_HANDS,
                    min_detection_confidence=DEFAULT_MIN_DETECTION_CONFIDENCE,
                    min_tracking_confidence=DEFAULT_MIN_TRACKING_CONFIDENCE):
            """
            Initialize hand detector
            
            Args:
                static_image_mode: Whether to treat input as static images
                max_num_hands: Maximum number of hands to detect
                min_detection_confidence: Minimum confidence for hand detection
                min_tracking_confidence: Minimum confidence for hand tracking
            """
            self.logger = logging.getLogger("HandGestureRecognizer.MPHands")
            
            # Ensure model is available
            if not ensure_model_available():
                raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
            
            try:
                base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
                options = vision.HandLandmarkerOptions(
                    base_options=base_options,
                    running_mode=vision.RunningMode.VIDEO if not static_image_mode else vision.RunningMode.IMAGE,
                    num_hands=max_num_hands,
                    min_hand_detection_confidence=min_detection_confidence,
                    min_hand_presence_confidence=min_tracking_confidence
                )
                self.landmarker = vision.HandLandmarker.create_from_options(options)
                self.timestamp = 0
                self.logger.info("Hand landmarker initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize hand landmarker: {e}")
                raise
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.landmarker.close()
        
        def process(self, image):
            """
            Process image to detect hands
            
            Args:
                image: Input image (RGB format)
                
            Returns:
                Detection results with hand landmarks
            """
            try:
                # Convert numpy array to MediaPipe Image
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
                
                # Detect hands
                self.timestamp += 1
                result = self.landmarker.detect_for_video(mp_image, self.timestamp)
                
                # Create results object compatible with old API
                class Results:
                    def __init__(self):
                        self.multi_hand_landmarks = None
                
                results = Results()
                
                if result.hand_landmarks:
                    # Convert to old format
                    class HandLandmarks:
                        def __init__(self, landmarks):
                            self.landmark = landmarks
                    
                    results.multi_hand_landmarks = []
                    for hand_landmarks in result.hand_landmarks:
                        results.multi_hand_landmarks.append(HandLandmarks(hand_landmarks))
                
                return results
            except Exception as e:
                self.logger.error(f"Error processing image: {e}")
                return None


# Module-level instances
mp_drawing = MPDrawing()
mp_hands = MPHands()


class GestureRecognizer:
    """
    Main class for hand gesture recognition
    
    This class handles:
    - Hand detection and tracking
    - Gesture recognition
    - Custom gesture callbacks
    - Real-time video processing
    """
    
    def __init__(self, camera_index: int = DEFAULT_CAMERA_INDEX):
        """
        Initialize the gesture recognizer
        
        Args:
            camera_index: Index of the camera to use
        """
        self.logger = setup_logging()
        self.camera_index = camera_index
        self.custom_functions: Dict[str, Callable] = {}
        self.previous_gestures: Set[str] = set()
        self.previous_positions = []
        self.running = False
        self.show_fps = True
        self.show_mask = True
        
        self.logger.info("GestureRecognizer initialized")

    def register_gesture(self, gesture_name: str, function: Callable):
        """
        Register a custom function for a specific gesture
        
        Args:
            gesture_name: Name of the gesture (e.g., 'fist', 'open_palm')
            function: Callback function to execute when gesture is detected
                     Function should accept state parameter ('appear' or 'disappear')
        """
        self.custom_functions[gesture_name] = function
        self.logger.info(f"Registered callback for gesture: {gesture_name}")

    def detect_gesture(self, hand_landmarks) -> Optional[str]:
        """
        Detect the current gesture based on hand landmarks
        
        Args:
            hand_landmarks: Detected hand landmarks from MediaPipe
            
        Returns:
            Gesture name string or None
        """
        try:
            fingers_extended = []

            # Thumb (check horizontal position)
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
            fingers_extended.append(thumb_tip.x < thumb_ip.x)

            # Other fingers (check vertical position)
            for finger_tip, finger_pip in [
                (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
                (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
                (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
                (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP),
            ]:
                tip = hand_landmarks.landmark[finger_tip]
                pip = hand_landmarks.landmark[finger_pip]
                fingers_extended.append(tip.y < pip.y)

            extended_count = sum(fingers_extended)

            # Map finger count to gesture
            gesture_map = {
                0: "fist",
                5: "open_palm",
                4: "four_fingers",
                3: "three_fingers",
                2: "two_fingers"
            }
            
            return gesture_map.get(extended_count)
            
        except Exception as e:
            self.logger.error(f"Error detecting gesture: {e}")
            return None

    def detect_swipe(self, hand_landmarks) -> Optional[str]:
        """
        Detect left or right swipes based on hand motion
        
        Args:
            hand_landmarks: Detected hand landmarks from MediaPipe
            
        Returns:
            'left_swipe', 'right_swipe', or None
        """
        try:
            # Use wrist position for swipe detection
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            current_position = (wrist.x, wrist.y)

            if self.previous_positions:
                # Calculate motion direction
                prev_position = self.previous_positions[-1]
                dx = current_position[0] - prev_position[0]

                # Determine swipe direction
                if dx > SWIPE_THRESHOLD:
                    return "right_swipe"
                elif dx < -SWIPE_THRESHOLD:
                    return "left_swipe"

            # Store current position
            self.previous_positions.append(current_position)

            # Maintain history size
            if len(self.previous_positions) > POSITION_HISTORY_SIZE:
                self.previous_positions.pop(0)

            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting swipe: {e}")
            return None

    def handle_gesture_states(self, current_gestures: Set[str]):
        """
        Handle gesture state changes (appear, disappear)
        
        Args:
            current_gestures: Set of gestures detected in current frame
        """
        # Detect newly appeared gestures
        new_gestures = current_gestures - self.previous_gestures

        # Detect disappeared gestures
        disappeared_gestures = self.previous_gestures - current_gestures

        # Handle new gestures
        for gesture in new_gestures:
            if gesture in self.custom_functions:
                try:
                    self.custom_functions[gesture]("appear")
                except Exception as e:
                    self.logger.error(f"Error in gesture callback for {gesture}: {e}")

        # Handle disappeared gestures
        for gesture in disappeared_gestures:
            if gesture in self.custom_functions:
                try:
                    self.custom_functions[gesture]("disappear")
                except Exception as e:
                    self.logger.error(f"Error in gesture callback for {gesture}: {e}")

        # Update previous gestures
        self.previous_gestures = current_gestures

    def run(self):
        """
        Start the gesture recognition system
        
        This method opens the camera, processes frames in real-time,
        detects gestures, and displays the results.
        """
        self.logger.info(f"Starting gesture recognition with camera {self.camera_index}")
        self.running = True
        
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            self.logger.error(f"Failed to open camera {self.camera_index}")
            raise RuntimeError(f"Cannot open camera {self.camera_index}")
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        prev_time = 0
        
        try:
            with mp_hands.Hands(
                min_detection_confidence=DEFAULT_MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=DEFAULT_MIN_TRACKING_CONFIDENCE
            ) as hands:
                self.logger.info("Hand detection started. Press ESC to exit.")
                
                while self.running and cap.isOpened():
                    success, image = cap.read()
                    if not success:
                        self.logger.warning("Failed to read frame from camera")
                        continue

                    # Flip and convert image
                    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    results = hands.process(image)

                    # Convert back to BGR for display
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    # Create hand mask
                    hand_mask = np.zeros_like(image)
                    current_gestures = set()

                    if results and results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            # Detect gesture
                            gesture = self.detect_gesture(hand_landmarks)
                            if gesture:
                                current_gestures.add(gesture)
                                if self.show_fps:
                                    draw_gesture_info(image, gesture)

                            # Detect swipes
                            swipe = self.detect_swipe(hand_landmarks)
                            if swipe:
                                current_gestures.add(swipe)

                            # Draw landmarks
                            mp_drawing.draw_landmarks(
                                hand_mask,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=LANDMARK_THICKNESS, circle_radius=LANDMARK_RADIUS),
                                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=CONNECTION_THICKNESS)
                            )
                            
                            mp_drawing.draw_landmarks(
                                image,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=LANDMARK_COLOR, thickness=LANDMARK_THICKNESS, circle_radius=LANDMARK_RADIUS),
                                mp_drawing.DrawingSpec(color=CONNECTION_COLOR, thickness=CONNECTION_THICKNESS)
                            )

                    # Handle gesture states
                    self.handle_gesture_states(current_gestures)

                    # Calculate and display FPS
                    if self.show_fps:
                        current_time, fps = calculate_fps(prev_time)
                        prev_time = current_time
                        draw_fps(image, fps)

                    # Display output
                    if self.show_mask:
                        # Convert mask to grayscale and threshold
                        gray_mask = cv2.cvtColor(hand_mask, cv2.COLOR_BGR2GRAY)
                        _, binary_mask = cv2.threshold(gray_mask, 10, 255, cv2.THRESH_BINARY)
                        
                        # Combine views
                        combined = np.hstack((image, cv2.cvtColor(binary_mask, cv2.COLOR_GRAY2BGR)))
                        cv2.imshow(WINDOW_NAME, combined)
                    else:
                        cv2.imshow(WINDOW_NAME, image)

                    # Handle key presses
                    key = cv2.waitKey(5) & 0xFF
                    if key == 27:  # ESC
                        self.logger.info("ESC pressed - exiting")
                        break
                    elif key == ord('f'):  # Toggle FPS
                        self.show_fps = not self.show_fps
                    elif key == ord('m'):  # Toggle mask
                        self.show_mask = not self.show_mask

        except Exception as e:
            self.logger.error(f"Error during gesture recognition: {e}", exc_info=True)
            raise
        finally:
            self.running = False
            cap.release()
            cv2.destroyAllWindows()
            self.logger.info("Gesture recognition stopped")

    def stop(self):
        """Stop the gesture recognition system"""
        self.running = False
        self.logger.info("Stop requested")


# Example usage
if __name__ == "__main__":
    recognizer = GestureRecognizer()
    
    def on_fist(state):
        print(f"Fist: {state}")
    
    def on_palm(state):
        print(f"Palm: {state}")
    
    recognizer.register_gesture("fist", on_fist)
    recognizer.register_gesture("open_palm", on_palm)
    
    try:
        recognizer.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
